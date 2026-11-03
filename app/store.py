"""Persistence is local, private, transactional and independent of the input workbook."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4


def now():
    return datetime.now(timezone.utc).isoformat()


def uid():
    return uuid4().hex


class Conflict(ValueError):
    pass


class Store:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.originals = self.directory / "originals"
        self.originals.mkdir(exist_ok=True)
        self.database = self.directory / "state.sqlite3"
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS records (
                    kind TEXT NOT NULL, id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS records_kind ON records(kind);
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY, csrf TEXT NOT NULL, expires REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS audit (
                    id INTEGER PRIMARY KEY, action TEXT NOT NULL, resource_id TEXT, at TEXT NOT NULL);
            """)

    @contextmanager
    def connect(self, write=False):
        db = sqlite3.connect(self.database, timeout=5, isolation_level=None)
        db.execute("PRAGMA foreign_keys=ON")
        try:
            if write:
                db.execute("BEGIN IMMEDIATE")
            yield db
            if write:
                db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    @staticmethod
    def _put(db, kind, record):
        db.execute("INSERT INTO records(kind,id,payload) VALUES(?,?,?)",
                   (kind, record["id"], json.dumps(record, ensure_ascii=False, allow_nan=False)))

    @staticmethod
    def _get(db, kind, ident):
        row = db.execute("SELECT payload FROM records WHERE kind=? AND id=?", (kind, ident)).fetchone()
        return json.loads(row[0]) if row else None

    def get(self, kind, ident):
        with self.connect() as db:
            return self._get(db, kind, ident)

    def list(self, kind):
        with self.connect() as db:
            return [json.loads(r[0]) for r in db.execute(
                "SELECT payload FROM records WHERE kind=? ORDER BY rowid DESC", (kind,))]

    def configured(self):
        with self.connect() as db:
            return db.execute("SELECT 1 FROM settings WHERE key='password'").fetchone() is not None

    def configure(self, password):
        salt = secrets.token_hex(32)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600_000).hex()
        with self.connect(write=True) as db:
            if db.execute("SELECT 1 FROM settings WHERE key='password'").fetchone():
                raise Conflict("La contraseña inicial ya está configurada.")
            db.execute("INSERT INTO settings VALUES('password',?)", (json.dumps([salt, digest]),))

    def verify_password(self, password):
        with self.connect() as db:
            row = db.execute("SELECT value FROM settings WHERE key='password'").fetchone()
        if not row:
            return False
        salt, digest = json.loads(row[0])
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600_000).hex()
        return hmac.compare_digest(actual, digest)

    def new_session(self):
        token, csrf = secrets.token_urlsafe(40), secrets.token_urlsafe(32)
        with self.connect(write=True) as db:
            db.execute("DELETE FROM sessions WHERE expires<?", (time.time(),))
            db.execute("INSERT INTO sessions VALUES(?,?,?)",
                       (hashlib.sha256(token.encode()).hexdigest(), csrf, time.time() + 8 * 3600))
        return token, csrf

    def session(self, token):
        if not token or len(token) > 200:
            return None
        with self.connect() as db:
            row = db.execute("SELECT csrf,expires FROM sessions WHERE token_hash=?",
                             (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
        return {"csrf": row[0], "expires": row[1]} if row and row[1] > time.time() else None

    def logout(self, token):
        if token:
            with self.connect(write=True) as db:
                db.execute("DELETE FROM sessions WHERE token_hash=?",
                           (hashlib.sha256(token.encode()).hexdigest(),))

    def create_import(self, filename, content, workbook):
        ident = uid()
        sha = hashlib.sha256(content).hexdigest()
        original = self.originals / (ident + Path(filename).suffix.lower())
        original.write_bytes(content)
        try:
            with self.connect(write=True) as db:
                prior = db.execute("SELECT id FROM records WHERE kind='import' AND "
                                   "json_extract(payload,'$.sha256')=? LIMIT 1", (sha,)).fetchone()
                record = {"id": ident, "filename": filename, "sha256": sha,
                          "created_at": now(), "duplicate_of": prior[0] if prior else None,
                          "latest_review_id": None, "workbook": workbook}
                self._put(db, "import", record)
                db.execute("INSERT INTO audit(action,resource_id,at) VALUES('import',?,?)", (ident, now()))
            return record
        except Exception:
            original.unlink(missing_ok=True)
            raise

    def create_review(self, import_id, review, parent_id=None, profile_version_id=None):
        review = {**review, "id": uid(), "import_id": import_id, "parent_id": parent_id,
                  "profile_version_id": profile_version_id, "created_at": now()}
        with self.connect(write=True) as db:
            source = self._get(db, "import", import_id)
            if source is None:
                raise KeyError(import_id)
            if source["latest_review_id"] != parent_id:
                raise Conflict("La revisión cambió. Abrí la última versión antes de continuar.")
            self._put(db, "review", review)
            source["latest_review_id"] = review["id"]
            db.execute("UPDATE records SET payload=? WHERE id=?", (json.dumps(source, ensure_ascii=False), import_id))
            db.execute("INSERT INTO audit(action,resource_id,at) VALUES('review',?,?)", (review["id"], now()))
        return review

    def create_profile(self, name, supplier, config, profile_id=None):
        profile_id = profile_id or uid()
        with self.connect(write=True) as db:
            versions = [json.loads(x[0]) for x in db.execute(
                "SELECT payload FROM records WHERE kind='profile' AND "
                "json_extract(payload,'$.profile_id')=?", (profile_id,))]
            if versions and any(v["supplier"] != supplier for v in versions):
                raise Conflict("Un perfil no puede cambiar de proveedor; creá otro perfil.")
            record = {"id": uid(), "profile_id": profile_id, "version": len(versions)+1,
                      "name": name, "supplier": supplier, "config": config,
                      "retired": False, "created_at": now()}
            self._put(db, "profile", record)
        return record

    def retire(self, ident):
        with self.connect(write=True) as db:
            profile = self._get(db, "profile", ident)
            if profile is None:
                raise KeyError(ident)
            profile["retired"] = True
            db.execute("UPDATE records SET payload=? WHERE id=?", (json.dumps(profile), ident))
        return profile

    def catalog(self):
        with self.connect() as db:
            row = db.execute("SELECT value FROM settings WHERE key='catalog'").fetchone()
        return json.loads(row[0]) if row else []

    def set_catalog(self, entries):
        with self.connect(write=True) as db:
            db.execute("INSERT INTO settings VALUES('catalog',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                       (json.dumps(entries, ensure_ascii=False, allow_nan=False),))


def default_directory():
    configured = os.environ.get("MLPL_DATA_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local/share"))) / "MercadoLibrePlantillas"
