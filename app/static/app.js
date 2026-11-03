'use strict';
const $ = id => document.getElementById(id);
const state = { csrf: '', configured: false, imported: null, review: null, profiles: [], page: 1, config: {} };
const roles = { code: 'Código de producto', description: 'Descripción', base: 'Valor base', listing: 'Publicación', quantity: 'Cantidad', logistics: 'Logística' };
const labels = { usable: 'Utilizable', pending: 'Pendiente', rejected: 'Rechazada', context: 'Contexto', empty: 'Vacía' };
const comparisonLabels = { ready: 'Propuesta local', unlinked: 'Sin vínculo', ambiguous: 'Vínculo ambiguo', full: 'Full: solo lectura', unverified: 'Capacidad no verificada', invalid: 'Datos pendientes' };
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const display = value => value === null || value === undefined ? '—' : typeof value === 'object' ? JSON.stringify(value) : String(value);
const nfmt = value => new Intl.NumberFormat('es-AR').format(value);
const date = value => { const d = new Date(value); return Number.isNaN(d.getTime()) ? display(value) : new Intl.DateTimeFormat('es-AR', { dateStyle: 'short', timeStyle: 'short' }).format(d); };
function columnName(index) { let result = ''; for (let n = index + 1; n > 0; n = Math.floor((n - 1) / 26)) result = String.fromCharCode(65 + (n - 1) % 26) + result; return result; }
function message(text) { $('notice').textContent = text; $('notice').hidden = !text; }
function showError(error) { $('error').textContent = error.message ?? String(error); $('error').hidden = false; if ($('correction-dialog').open) $('correction-error').textContent = error.message ?? String(error); }
function clearError() { $('error').hidden = true; $('auth-error').textContent = ''; $('correction-error').textContent = ''; }
async function api(path, options = {}) {
  const headers = new Headers(options.headers ?? {});
  if (options.body && !(options.body instanceof FormData)) { headers.set('Content-Type', 'application/json'); options.body = JSON.stringify(options.body); }
  if (options.method && options.method !== 'GET' && state.csrf) headers.set('X-CSRF-Token', state.csrf);
  const response = await fetch(path, { ...options, headers, credentials: 'same-origin' });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && !path.includes('/auth/')) { await authStatus(); }
    const detail = data?.detail ?? data?.message ?? `No se pudo completar la operación (${response.status}).`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return data;
}
function run(action) { return async event => { event?.preventDefault(); clearError(); const form = event?.target?.closest?.('form'); const buttons = form ? [...form.querySelectorAll('button')] : []; buttons.forEach(b => b.disabled = true); try { await action(event); } catch (error) { showError(error); if (!$('auth').hidden) $('auth-error').textContent = error.message; } finally { buttons.forEach(b => b.disabled = false); } }; }
async function authStatus() {
  const result = await api('/api/auth/status'); state.configured = result.configured; state.csrf = result.csrf ?? '';
  $('auth').hidden = !!result.authenticated; $('shell').hidden = !result.authenticated;
  $('auth-help').textContent = result.configured ? 'Ingresá para revisar tus archivos.' : 'Creá una contraseña para proteger las listas de este equipo. Usá al menos 12 caracteres.';
  $('auth-submit').textContent = result.configured ? 'Ingresar' : 'Crear acceso local';
  $('password').autocomplete = result.configured ? 'current-password' : 'new-password';
  return result.authenticated;
}
async function navigate() {
  let view = location.hash.slice(1).split('?')[0] || 'work'; if (!['work', 'history', 'profiles', 'catalog'].includes(view)) view = 'work';
  document.querySelectorAll('.view').forEach(node => node.hidden = node.id !== `view-${view}`);
  document.querySelectorAll('[data-view]').forEach(node => node.dataset.view === view ? node.setAttribute('aria-current', 'page') : node.removeAttribute('aria-current'));
  if ($('shell').hidden) return;
  if (view === 'history') await loadHistory();
  if (view === 'profiles') await loadProfiles();
  if (view === 'catalog') await loadCatalog();
}
function sheetMetadata() { return state.imported?.sheets?.find(sheet => sheet.name === $('sheet').value); }
function renderColumns(mapping = {}) {
  const sheet = sheetMetadata(); const count = Number(sheet?.columns ?? 0);
  const formulaColumns = [...Object.keys(state.config.formulas ?? {}), ...[...$('formula-rows').querySelectorAll('.rule-key')].map(input => input.value.trim())].filter(key => /^[A-Z]{1,2}$/.test(key));
  const formulaWidth = Math.max(0, ...formulaColumns.map(key => [...key].reduce((total, letter) => total * 26 + letter.charCodeAt(0) - 64, 0)));
  const options = Array.from({ length: Math.min(100, Math.max(count, formulaWidth)) }, (_, i) => columnName(i));
  $('mapping').innerHTML = Object.entries(roles).map(([key, label]) => `<div><label for="map-${key}">${label}</label><select id="map-${key}" data-role="${key}"><option value="">Sin asignar</option>${options.map(col => `<option value="${col}" ${mapping[key] === col ? 'selected' : ''}>${col}</option>`).join('')}</select></div>`).join('');
  $('correction-column').innerHTML = options.map(col => `<option>${col}</option>`).join('');
  const preview = sheet?.preview ?? [];
  $('source-preview').innerHTML = preview.length ? `<table><caption class="sr-only">Primeras ${preview.length} filas de ${esc(sheet.name)}</caption><thead><tr><th scope="col">Fila</th>${options.map(col => `<th scope="col">${col}</th>`).join('')}</tr></thead><tbody>${preview.map((row, i) => `<tr><th scope="row">${i + 1}</th>${options.map((col, j) => `<td>${esc(display(row[j]))}</td>`).join('')}</tr>`).join('')}</tbody></table>` : '<p class="empty">Esta hoja no tiene una vista previa disponible.</p>';
}
function ruleRow(type, key = '', value = '') {
  const holder = document.createElement('div'); holder.className = 'rule-row';
  const name = document.createElement('label'); name.textContent = type === 'parameter' ? 'Nombre' : 'Columna'; const keyInput = document.createElement('input'); keyInput.value = key; keyInput.className = 'rule-key'; keyInput.autocomplete = 'off'; keyInput.spellcheck = false; name.append(keyInput);
  if (type === 'formula') keyInput.onchange = () => { keyInput.value = keyInput.value.toUpperCase(); renderColumns(Object.fromEntries([...document.querySelectorAll('[data-role]')].map(select => [select.dataset.role, select.value]))); };
  const valLabel = document.createElement('label'); valLabel.textContent = type === 'parameter' ? 'Valor numérico' : 'Fórmula'; const val = document.createElement('input'); val.value = value; val.className = 'rule-value'; val.autocomplete = 'off'; val.spellcheck = false; valLabel.append(val);
  const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'secondary'; remove.textContent = 'Quitar'; remove.setAttribute('aria-label', type === 'parameter' ? 'Quitar parámetro' : 'Quitar fórmula'); remove.onclick = () => holder.remove(); holder.append(name, valLabel, remove);
  $(type === 'parameter' ? 'parameter-rows' : 'formula-rows').append(holder);
}
function collectRules(id) { const result = {}; for (const row of $(id).children) { const key = row.querySelector('.rule-key').value.trim(); const value = row.querySelector('.rule-value').value.trim(); if (!key && !value) continue; if (!key || !value) throw new Error('Completá el nombre y el valor de cada regla, o quitá la fila.'); if (Object.hasOwn(result, key)) throw new Error(`La regla ${key} aparece repetida.`); result[key] = value; } return result; }
function getConfig() {
  const headerText = $('header-rows').value.trim(); const headers = headerText === '' ? [] : headerText.split(',').map(value => Number(value.trim()));
  if (headers.some(value => !Number.isInteger(value) || value < 1)) throw new Error('Las filas de encabezado deben ser números enteros positivos separados por coma.');
  const mapping = {}; document.querySelectorAll('[data-role]').forEach(select => { if (select.value) mapping[select.dataset.role] = select.value; });
  const config = { ...state.config, sheet: $('sheet').value, sheet_kind: $('sheet-kind').value, header_rows: headers, data_start: Number($('data-start').value), mapping, parameters: collectRules('parameter-rows'), formulas: collectRules('formula-rows') };
  const profile = state.profiles.find(item => String(item.id ?? item.version_id) === $('profile-select').value);
  if (profile) { config.profile_version_id = profile.id ?? profile.version_id; config.supplier = profile.supplier; }
  else { delete config.profile_version_id; delete config.supplier; delete config._schema; }
  const parent = state.review?.id ?? state.imported?.latest_review_id;
  if (parent) config.parent_id = parent; else delete config.parent_id;
  return config;
}
function setConfig(config) {
  state.config = structuredClone(config ?? {});
  if (config.sheet && state.imported?.sheets?.some(sheet => sheet.name === config.sheet)) $('sheet').value = config.sheet;
  $('header-rows').value = (config.header_rows ?? [1]).join(', '); $('data-start').value = config.data_start ?? 2; $('sheet-kind').value = config.sheet_kind ?? 'catalog';
  renderColumns(config.mapping ?? {}); $('parameter-rows').replaceChildren(); $('formula-rows').replaceChildren();
  Object.entries(config.parameters ?? {}).forEach(([key, value]) => ruleRow('parameter', key, value));
  Object.entries(config.formulas ?? {}).forEach(([key, value]) => ruleRow('formula', key, value));
  $('advanced-config').value = JSON.stringify(config, null, 2);
}
function openImport(imported) {
  state.imported = imported; state.review = null; state.config = {}; $('workspace').hidden = false; $('review-panel').hidden = true;
  $('profile-select').value = ''; $('new-version').checked = false; $('row-filter').value = 'all'; $('row-search').value = '';
  $('filename').textContent = imported.filename ?? 'Archivo cargado'; $('duplicate').textContent = imported.duplicate_of ? 'Archivo repetido: original conservado' : 'Archivo recibido';
  $('sheet').innerHTML = (imported.sheets ?? []).map(sheet => `<option value="${esc(sheet.name)}">${esc(sheet.name)} · ${nfmt(Number(sheet.rows ?? 0))} filas</option>`).join('');
  setConfig({ sheet: imported.sheets?.[0]?.name ?? '', header_rows: [1], data_start: 2, mapping: {}, parameters: {}, formulas: {} });
}
function renderReview(review) {
  state.review = review; state.page = 1; $('review-panel').hidden = false;
  $('review-info').textContent = `Hoja ${review.sheet} · revisión ${review.id} · ${date(review.created_at)}${review.parent_id ? ' · corrección de una revisión anterior' : ''}`;
  $('export').href = `/api/reviews/${encodeURIComponent(review.id)}/export`;
  const summary = review.summary ?? {};
  $('summary').innerHTML = [['total', 'Filas leídas'], ['usable', 'Utilizables'], ['pending', 'Pendientes'], ['rejected', 'Rechazadas'], ['context', 'Contexto'], ['empty', 'Vacías']].map(([key, label]) => `<div class="summary-item"><strong>${nfmt(summary[key] ?? 0)}</strong><span>${label}</span></div>`).join('');
  $('comparison').replaceChildren(); drawRows();
}
function filteredRows() {
  const filter = $('row-filter').value; const search = $('row-search').value.trim().toLocaleLowerCase('es');
  return (state.review?.rows ?? []).filter(row => (filter === 'all' || (filter === 'issues' ? row.issues?.length > 0 : filter === 'context' ? ['context', 'header'].includes(row.kind) : filter === 'empty' ? row.kind === 'empty' : row.kind === 'product' && row.status === filter)) && (!search || JSON.stringify(row).toLocaleLowerCase('es').includes(search)));
}
function drawRows() {
  if (!state.review) return;
  const rows = filteredRows(); const size = Number($('page-size').value); const pages = Math.max(1, Math.ceil(rows.length / size)); state.page = Math.min(state.page, pages);
  const pageRows = rows.slice((state.page - 1) * size, state.page * size); const headers = state.review.headers ?? [];
  const cols = [...new Set([...headers.map(header => header.column), ...pageRows.flatMap(row => Object.keys(row.values ?? {}))])];
  const heading = Object.fromEntries(headers.map(header => [header.column, header.label]));
  $('review-table').innerHTML = pageRows.length ? `<table><caption class="sr-only">Revisión completa por fila con datos e incidencias</caption><thead><tr><th scope="col">Fila</th><th scope="col">Estado</th>${cols.map(col => `<th scope="col">${esc(col)} · ${esc(heading[col] ?? '')}</th>`).join('')}<th scope="col">Incidencias</th><th scope="col">Acción</th></tr></thead><tbody>${pageRows.map(row => `<tr><th class="row-number" scope="row">${esc(row.row_number)}</th><td><span class="badge ${esc(row.kind === 'product' ? row.status : row.kind)}">${esc(row.kind === 'header' ? 'Encabezado' : row.kind === 'product' ? labels[row.status] ?? row.status : labels[row.kind] ?? row.kind)}</span></td>${cols.map(col => {
    const value = row.values?.[col]; const evidence = row.evidence?.[col]; const original = evidence?.value ?? row.original?.[col]; const formula = evidence?.formula ?? row.formulas?.[col] ?? (value && typeof value === 'object' ? value.formula : null);
    const main = value && typeof value === 'object' && Object.hasOwn(value, 'value') ? value.value : value;
    return `<td><span class="cell-main">${esc(display(main))}</span>${formula ? `<span class="cell-formula">Fórmula: ${esc(formula)}</span>` : ''}${evidence ? `<details><summary class="cell-formula">Ver origen</summary><span class="cell-formula">Ingresado: ${esc(display(original))}</span><span class="cell-formula">Resultado guardado: ${esc(display(evidence.cached))}</span><span class="cell-formula">Presentación: ${esc(display(evidence.display))}</span></details>` : original !== undefined ? `<span class="cell-formula">Origen: ${esc(display(original))}</span>` : ''}</td>`;
  }).join('')}<td>${(row.issues ?? []).map(issue => `<span class="issue">${esc(issue.column ? `${issue.column}: ` : '')}${esc(issue.message ?? display(issue))}</span>`).join('') || '<span class="muted">Sin incidencias</span>'}</td><td><button type="button" class="secondary small" data-correct="${esc(row.row_number)}">Corregir fila ${esc(row.row_number)}</button></td></tr>`).join('')}</tbody></table>` : '<p class="empty">No hay filas para este filtro. Cambiá el estado o la búsqueda.</p>';
  $('page-info').textContent = `Página ${nfmt(state.page)} de ${nfmt(pages)} · ${nfmt(rows.length)} filas`;
  $('prev').disabled = state.page <= 1; $('next').disabled = state.page >= pages;
  $('review-table').querySelectorAll('[data-correct]').forEach(button => button.onclick = () => { $('correction-row').value = button.dataset.correct; $('correction-value').value = ''; $('correction-reason').value = ''; $('correction-type').value = 'text'; $('correction-dialog').showModal(); });
}
async function loadProfiles() {
  state.profiles = await api('/api/profiles');
  const current = $('profile-select').value;
  $('profile-select').innerHTML = '<option value="">Configurar esta carga</option>' + state.profiles.filter(profile => !profile.retired && !profile.retired_at).map(profile => `<option value="${esc(profile.id ?? profile.version_id)}">${esc(profile.name)} · v${esc(profile.version)} · ${esc(profile.supplier)}</option>`).join('');
  if ([...$('profile-select').options].some(option => option.value === current)) $('profile-select').value = current;
  $('profiles-list').innerHTML = state.profiles.length ? state.profiles.map(profile => `<article class="record"><div class="grow"><strong>${esc(profile.name)} · versión ${esc(profile.version)}</strong><p>${esc(profile.supplier)} · ${date(profile.created_at)}</p><details><summary>Ver estructura y reglas</summary><pre>${esc(JSON.stringify(profile.config, null, 2))}</pre></details></div><span class="tag">${profile.retired || profile.retired_at ? 'Retirada' : 'Disponible'}</span>${profile.retired || profile.retired_at ? '' : `<button type="button" class="secondary" data-retire="${esc(profile.id ?? profile.version_id)}">Retirar versión</button>`}</article>`).join('') : '<p class="empty">Todavía no hay perfiles. Creá una revisión y guardá sus criterios para reutilizarlos.</p>';
  $('profiles-list').querySelectorAll('[data-retire]').forEach(button => button.onclick = run(async () => { if (!confirm('¿Retirar esta versión? Dejará de ofrecerse para nuevas cargas. Sus revisiones se conservan.')) return; await api(`/api/profiles/${encodeURIComponent(button.dataset.retire)}/retire`, { method: 'POST' }); await loadProfiles(); message('Versión retirada. El historial permanece disponible.'); }));
}
async function loadHistory() {
  const imports = await api('/api/imports');
  $('history-list').innerHTML = imports.length ? imports.map(item => `<article class="record"><div class="grow"><strong>${esc(item.filename)}</strong><p>${date(item.created_at)}${item.duplicate_of ? ' · carga repetida' : ''}</p><small>${esc(item.sha256 ?? '')}</small></div><button type="button" class="secondary" data-import="${esc(item.id)}">Abrir archivo y revisiones</button></article>`).join('') : '<p class="empty">Aún no cargaste archivos. Empezá en Importar y revisar o descargá la muestra sintética.</p>';
  $('history-list').querySelectorAll('[data-import]').forEach(button => button.onclick = run(async () => {
    const imported = await api(`/api/imports/${encodeURIComponent(button.dataset.import)}`); openImport(imported);
    const reviews = imported.reviews ?? [];
    $('history-reviews').innerHTML = `<h2>Revisiones de ${esc(imported.filename)}</h2>` + (reviews.length ? reviews.map(review => `<article class="record"><div class="grow"><strong>${esc(review.sheet ?? review.config?.sheet ?? 'Revisión')} · ${esc(review.id)}</strong><p>${date(review.created_at)}</p></div><button class="secondary" type="button" data-review="${esc(review.id)}">Consultar revisión</button></article>`).join('') : '<p class="empty">No hay revisiones guardadas para esta carga.</p>') + '<button type="button" class="primary" id="resume-import">Preparar nueva revisión</button>';
    $('resume-import').onclick = () => { location.hash = 'work'; };
    $('history-reviews').querySelectorAll('[data-review]').forEach(b => b.onclick = run(async () => { const review = await api(`/api/reviews/${encodeURIComponent(b.dataset.review)}`); setConfig(review.config ?? {}); renderReview(review); location.hash = 'work'; }));
    $('history-reviews').scrollIntoView({ block: 'start' });
  }));
}
let catalogRequest = 0;
let catalogEditVersion = 0;
$('catalog-json').addEventListener('input', () => { catalogEditVersion += 1; });
async function loadCatalog() {
  const request = ++catalogRequest;
  const editVersion = catalogEditVersion;
  const entries = await api('/api/catalog');
  if (request !== catalogRequest) return;
  // A delayed navigation/refresh response must not overwrite a draft being edited.
  if (catalogEditVersion === editVersion) $('catalog-json').value = JSON.stringify(entries, null, 2);
  $('catalog-help').textContent = `${nfmt(entries.length)} entradas guardadas. Campos: account_id, product_key, listing_id, variation_id, price, quantity, logistics (own o full), writable_verified (true o false). No se verifican capacidades remotas.`;
}
function drawComparison(result) {
  const differences = result.differences ?? [];
  $('comparison').innerHTML = `<p>${nfmt(differences.length)} resultados para la cuenta elegida. Ninguno se envía a Mercado Libre.</p><div class="table-wrap comparison-table" tabindex="0"><table><caption class="sr-only">Comparación con catálogo controlado</caption><thead><tr><th scope="col">Fila / código</th><th scope="col">Publicación</th><th scope="col">Precio previo / propuesto</th><th scope="col">Cantidad previa / propuesta</th><th scope="col">Estado y motivos</th></tr></thead><tbody>${differences.map(item => `<tr><td>${esc(item.row_number)} · ${esc(item.product_key)}</td><td>${esc(item.listing_id)}</td><td>${esc(display(item.current_price))} / ${esc(display(item.proposed_price))}</td><td>${esc(display(item.current_quantity))} / ${esc(display(item.proposed_quantity))}</td><td>${esc(comparisonLabels[item.status] ?? item.status)}${item.blocked ? ' · Bloqueado' : ' · Solo propuesta local'}${(item.reasons ?? []).map(reason => `<span class="issue">${esc(reason)}</span>`).join('')}</td></tr>`).join('')}</tbody></table></div>`;
}
$('auth-form').addEventListener('submit', run(async () => { await api(`/api/auth/${state.configured ? 'login' : 'setup'}`, { method: 'POST', body: { password: $('password').value } }); $('password').value = ''; if (await authStatus()) { await loadProfiles(); await navigate(); } }));
$('logout').onclick = run(async () => { await api('/api/auth/logout', { method: 'POST' }); state.imported = null; state.review = null; $('workspace').hidden = true; $('history-list').replaceChildren(); $('history-reviews').replaceChildren(); $('catalog-json').value = '[]'; await authStatus(); });
$('upload-form').addEventListener('submit', run(async () => { const file = $('file').files[0]; if (!file) throw new Error('Elegí un archivo antes de cargar.'); if (file.size > 10 * 1024 * 1024) throw new Error('El archivo supera 10 MiB. Prepará una copia más pequeña.'); const body = new FormData(); body.append('file', file); openImport(await api('/api/imports', { method: 'POST', body })); message('Archivo conservado. Elegí su estructura para crear la revisión.'); }));
$('sheet').onchange = () => { const mapping = Object.fromEntries([...document.querySelectorAll('[data-role]')].map(select => [select.dataset.role, select.value])); renderColumns(mapping); };
$('profile-select').onchange = run(async () => { const profile = state.profiles.find(item => String(item.id ?? item.version_id) === $('profile-select').value); if (!profile) return; if (!state.imported) throw new Error('Cargá primero un archivo.'); if (!state.imported.sheets.some(sheet => sheet.name === profile.config.sheet)) throw new Error('El perfil usa una hoja que no existe en esta carga. Revisá su compatibilidad antes de reutilizarlo.'); setConfig(profile.config); $('profile-note').textContent = `Perfil ${profile.name}, versión ${profile.version}; proveedor ${profile.supplier}. Revisá la correspondencia antes de crear la revisión.`; $('profile-name').value = profile.name; $('supplier').value = profile.supplier; });
$('add-parameter').onclick = () => ruleRow('parameter'); $('add-formula').onclick = () => ruleRow('formula');
$('show-json').onclick = run(() => { $('advanced-config').value = JSON.stringify(getConfig(), null, 2); });
$('load-json').onclick = run(() => { const config = JSON.parse($('advanced-config').value); if (!config || typeof config !== 'object' || Array.isArray(config)) throw new Error('La configuración debe ser un objeto JSON.'); setConfig(config); message('Configuración aplicada al formulario. Revisala antes de crear la revisión.'); });
$('config-form').addEventListener('submit', run(async () => { if (!state.imported) throw new Error('Cargá un archivo.'); const config = getConfig(); const review = await api(`/api/imports/${encodeURIComponent(state.imported.id)}/reviews`, { method: 'POST', body: config }); state.config = config; renderReview(review); message('Revisión guardada. Los pendientes y errores se incluyen en el informe.'); $('review-panel').scrollIntoView({ block: 'start' }); }));
for (const id of ['row-filter', 'page-size']) $(id).onchange = () => { state.page = 1; drawRows(); };
$('row-search').oninput = () => { state.page = 1; drawRows(); }; $('prev').onclick = () => { state.page--; drawRows(); }; $('next').onclick = () => { state.page++; drawRows(); };
$('close-dialog').onclick = () => $('correction-dialog').close();
$('correction-form').addEventListener('submit', run(async () => { let value = $('correction-value').value; if ($('correction-type').value === 'empty') value = null; if ($('correction-type').value === 'number') { if (value.trim() === '' || !Number.isFinite(Number(value))) throw new Error('Ingresá un número válido con punto decimal o elegí Texto para conservarlo.'); value = Number(value); } const review = await api(`/api/reviews/${encodeURIComponent(state.review.id)}/corrections`, { method: 'POST', body: { changes: [{ row_number: Number($('correction-row').value), column: $('correction-column').value, value }], reason: $('correction-reason').value } }); $('correction-dialog').close(); state.config = structuredClone(review.config); setConfig(review.config); renderReview(review); message('Corrección guardada en una revisión nueva; no se convirtió en regla general.'); }));
$('save-profile').addEventListener('submit', run(async () => { const config = structuredClone(state.review.config); delete config.overrides; const body = { name: $('profile-name').value, supplier: $('supplier').value, config }; if ($('new-version').checked) { const selected = state.profiles.find(profile => String(profile.id ?? profile.version_id) === $('profile-select').value); if (!selected) throw new Error('Seleccioná un perfil existente para crear su nueva versión.'); body.profile_id = selected.profile_id ?? selected.id; } await api('/api/profiles', { method: 'POST', body }); await loadProfiles(); message('Perfil guardado con reglas explícitas; las correcciones de fila permanecen locales.'); }));
$('compare-form').addEventListener('submit', run(async () => drawComparison(await api(`/api/reviews/${encodeURIComponent(state.review.id)}/compare`, { method: 'POST', body: { account_id: $('account').value } }))));
$('catalog-form').addEventListener('submit', run(async () => { const entries = JSON.parse($('catalog-json').value); if (!Array.isArray(entries)) throw new Error('El catálogo debe ser un arreglo JSON de entradas.'); if (!confirm('¿Reemplazar todo el catálogo controlado de este equipo por estas entradas?')) return; await api('/api/catalog', { method: 'POST', body: { entries } }); await loadCatalog(); message('Catálogo controlado guardado. No se modificó Mercado Libre.'); }));
$('refresh-history').onclick = run(loadHistory); $('refresh-profiles').onclick = run(loadProfiles); $('refresh-catalog').onclick = run(loadCatalog);
window.addEventListener('hashchange', run(navigate));
run(async () => { if (await authStatus()) { await loadProfiles(); await navigate(); } })();
