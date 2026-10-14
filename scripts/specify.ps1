# Ejecuta la CLI oficial en la misma revision utilizada para inicializar este proyecto.
# uv mantiene la herramienta en su cache; no requiere una instalacion global de specify.
$ErrorActionPreference = 'Stop'
if (-not (Get-Command uvx -ErrorAction SilentlyContinue)) {
    throw 'Se requiere uv/uvx para ejecutar Spec Kit.'
}
& uvx --from 'git+https://github.com/github/spec-kit.git@51b6d170aa7368205bee629d75a7059185272d19' specify @args
exit $LASTEXITCODE
