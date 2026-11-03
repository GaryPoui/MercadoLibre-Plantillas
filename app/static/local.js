'use strict';
// Controls are built once; business values remain explicit and no fixtures are inserted.
let opsState = null, opsSuppliers = [], opsUI = null, opsGeneration = 0, opsAudit = [], opsCursor = null;
const opsPages = {};
const opsField = (name, label, type = 'text', source = null, optional = false) => ({ name, label, type, source, optional });
const of = opsField;
const opsForms = {
  accounts: ['Guardar referencia local', [of('id', 'Editar referencia (vacío para crear)', 'select', 'account', true), of('name', 'Nombre de cuenta local'), of('active', 'Habilitada para operaciones locales', 'checkbox')]],
  products: ['Crear producto', [of('sku', 'SKU interno'), of('name', 'Nombre del producto'), of('unit', 'Unidad indivisible (por ejemplo, caja o unidad)')]],
  listings: ['Guardar captura manual', [of('edit', 'Editar captura (vacío para crear)', 'select', 'listing', true), of('account_id', 'Cuenta local', 'select', 'activeAccount'), of('listing_id', 'Referencia de publicación'), of('variation_id', 'Referencia de variante', 'text', null, true), of('user_product_id', 'Referencia de producto del vendedor', 'text', null, true), of('currency', 'Moneda declarada (3 letras)'), of('price_kind', 'Qué representa el precio'), of('price', 'Precio capturado (punto decimal)'), of('logistics', 'Logística', 'select', [['own', 'Propia'], ['full', 'Full']]), of('simulated_editable', 'Permitir cambios solo en el simulador', 'checkbox')]],
  links: ['Confirmar vínculo', [of('product_id', 'Producto interno', 'select', 'product'), of('listing_record_id', 'Publicación capturada', 'select', 'listing'), of('accept', 'Confirmo la equivalencia de estos productos', 'checkbox')]],
  'supplier-links': ['Confirmar SKU del proveedor', [of('product_id', 'Producto interno', 'select', 'product'), of('scope_id', 'Lista vigente', 'select', 'scope'), of('supplier_sku', 'SKU exacto del proveedor'), of('accept', 'Confirmo la equivalencia de este SKU', 'checkbox')]],
  'price-rules': ['Confirmar regla local', [of('account_id', 'Cuenta local', 'select', 'activeAccount'), of('scope_id', 'Lista vigente', 'select', 'scope'), of('factor', 'Multiplicador (punto decimal)'), of('charge', 'Cargo (punto decimal)'), of('digits', 'Decimales de redondeo (0 a 6)', 'number'), of('target_price_kind', 'Qué representa el precio de destino'), of('confirmed', 'Confirmo esta fórmula para esta cuenta y lista', 'checkbox')]],
  'price-previews': ['Preparar propuesta', [of('account_id', 'Cuenta local', 'select', 'activeAccount'), of('scope_id', 'Lista vigente', 'select', 'scope')]],
  simulate: ['Simular cambios locales', [of('preview_id', 'Propuesta', 'select', 'price_preview'), of('scenario', 'Escenario', 'select', [['success', 'Respuesta correcta simulada'], ['reject', 'Rechazo simulado'], ['timeout_before', 'Fallo antes del cambio'], ['timeout_after', 'Timeout después del cambio'], ['accepted_unchanged', 'Aceptado sin cambiar el precio']]), of('confirmed', 'Confirmo la ejecución solo en datos locales', 'checkbox')]],
  locations: ['Crear ubicación', [of('name', 'Nombre de ubicación'), of('kind', 'Tipo', 'select', [['own', 'Propia compartida'], ['full', 'Full observado']]), of('account_id', 'Cuenta (solo para Full)', 'select', 'activeAccount', true)]],
  lots: ['Crear existencia', [of('product_id', 'Producto', 'select', 'product'), of('location_id', 'Ubicación', 'select', 'location'), of('initial_quantity', 'Conteo propio inicial', 'number', null, true), of('safety', 'Margen propio', 'number', null, true), of('minimum', 'Mínimo para alertar (opcional)', 'number', null, true)]],
  adjustments: ['Registrar ajuste', [of('lot_id', 'Existencia propia', 'select', 'ownLot'), of('delta', 'Cambio en unidades (positivo o negativo)', 'number'), of('reason', 'Motivo'), of('event_id', '', 'hidden')]],
  allocations: ['Guardar asignación disponible', [of('lot_id', 'Existencia propia', 'select', 'ownLot'), of('account_id', 'Cuenta local', 'select', 'activeAccount'), of('quantity', 'Cantidad disponible asignada', 'number')]],
  settings: ['Guardar margen y mínimo', [of('lot_id', 'Existencia', 'select', 'lot'), of('safety', 'Margen propio', 'number', null, true), of('minimum', 'Mínimo para alertar (vacío lo desactiva)', 'number', null, true)]],
  reconciliations: ['Registrar conteo sin ajustar', [of('lot_id', 'Existencia', 'select', 'lot'), of('observed_quantity', 'Cantidad contada', 'number'), of('reference', 'Referencia del conteo')]],
  'full-captures': ['Guardar observación manual', [of('lot_id', 'Existencia Full', 'select', 'fullLot'), of('quantity', 'Cantidad observada', 'number'), of('reference', 'Fuente o referencia de la observación'), of('event_id', '', 'hidden')]],
  'inventory-policy': ['Confirmar política local', [of('confirmed', 'Acepto la política de reserva, despacho y devolución indicada arriba', 'checkbox')]],
  'order-events': ['Registrar estado de venta local', [of('account_id', 'Cuenta local', 'select', 'account'), of('lot_id', 'Existencia', 'select', 'lot'), of('order_ref', 'Referencia de venta'), of('sequence', 'Secuencia (1 primero; luego 2, 3…)', 'number'), of('status', 'Estado', 'select', [['reserved', 'Reservada'], ['shipped', 'Despachada'], ['cancelled', 'Cancelada antes del despacho'], ['returned', 'Devolución recibida']]), of('quantity', 'Cantidad total de la venta', 'number'), of('returned_total', 'Total acumulado devuelto (solo devolución)', 'number', null, true), of('receipt_confirmed', 'Confirmo la recepción física de la devolución', 'checkbox'), of('event_id', '', 'hidden')]],
  notices: ['Preparar aviso (no se envía)', [of('alert_id', 'Alerta', 'select', 'alert'), of('recipient', 'Destinatario para el archivo', 'email')]],
  audit: ['Aplicar filtros', [of('action', 'Acción contiene', 'text', null, true), of('resource', 'Identificador de recurso exacto', 'text', null, true), of('account_id', 'Cuenta', 'select', 'account', true), of('status', 'Estado registrado', 'select', [['reserved','Reservada'],['shipped','Despachada'],['cancelled','Cancelada'],['returned','Devolución'],['simulated','Simulada localmente'],['uncertain','Incierta'],['failed','Fallida'],['conflict','Conflicto'],['acknowledged','Reconocida'],['resolved','Resuelta'],['prepared_not_sent','Aviso preparado, no enviado']], true), of('since', 'Desde', 'datetime-local', null, true), of('until', 'Hasta', 'datetime-local', null, true)]]
};
const opsLabels = { ready: 'Lista para simular', blocked: 'Bloqueada', unchanged: 'Sin cambio', simulated: 'Simulada localmente', simulated_verified: 'Comprobado solo en el simulador', uncertain: 'Incierta', failed: 'Fallida', conflict: 'Conflicto: preparar otra propuesta', cancelled: 'Cancelada', reserved: 'Reservada', shipped: 'Despachada', returned: 'Devolución', open: 'Abierta', acknowledged: 'Reconocida', resolved: 'Resuelta', prepared_not_sent: 'Preparado, no enviado', manual_snapshot: 'Captura manual', local_simulator: 'Simulador local', manual_full_observation: 'Observación manual Full', local_own_ledger: 'Registro propio', own: 'Propio', full: 'Full observado' };
const opsLabel = value => opsLabels[value] ?? value ?? '—';
const opsRows = kind => opsState?.[kind] ?? [];
const opsFind = (kind, id) => opsRows(kind).find(row => row.id === id);
function opsName(kind, id) {
  const row = opsFind(kind, id); if (!row) return id || '—';
  if (kind === 'product') return `${row.sku} — ${row.name} (${row.unit})`;
  if (kind === 'listing') return `${opsName('account', row.account_id)} / ${row.listing_id}${row.variation_id ? ' / '+row.variation_id : ''}`;
  if (kind === 'lot') return `${opsName('product', row.product_id)} / ${opsName('location', row.location_id)}`;
  if (kind === 'alert') return `${opsLabel(row.status)}: ${row.message}`;
  if (kind === 'price_preview') return `${date(row.created_at)} / ${opsName('account', row.account_id)} / ${row.rows.length} filas`;
  if (kind === 'account') return row.name + (row.active ? '' : ' (deshabilitada)');
  return row.name ?? row.id;
}
function opsOptions(source) {
  if (Array.isArray(source)) return source;
  if (source === 'scope') return opsSuppliers.filter(s => s.current_version_id && !s.retired).map(s => [s.id, `${s.name} / ${s.currency}`]);
  const kind = { activeAccount: 'account', ownLot: 'lot', fullLot: 'lot' }[source] ?? source;
  return opsRows(kind).filter(row => source !== 'activeAccount' || row.active).filter(row => source !== 'ownLot' || row.kind === 'own').filter(row => source !== 'fullLot' || row.kind === 'full').map(row => [row.id, opsName(kind, row.id)]);
}
async function ensureLocalUI() {
  if (opsUI) return opsUI;
  opsUI = (async () => {
    const response = await fetch('/static/local.html'); if (!response.ok) throw new Error('No se pudieron cargar las pantallas locales.');
    $('local-views').innerHTML = await response.text();
    for (const [key, [button, fields]] of Object.entries(opsForms)) {
      const container = document.querySelector(`[data-ops-form="${key}"]`);
      container.innerHTML = `<form data-local-form="${key}" class="ops-form">${fields.map(f => {
        const id = `ops-${key}-${f.name}`;
        if (f.type === 'hidden') return `<input type="hidden" name="${f.name}" value="${crypto.randomUUID()}">`;
        const required = !f.optional && !['checkbox'].includes(f.type) ? ' required' : '';
        const control = f.type === 'select' ? `<select id="${id}" name="${f.name}"${required}></select>` : `<input id="${id}" name="${f.name}" type="${f.type}"${required}${f.type === 'number' ? ' step="1"' : ''}${f.name === 'active' ? ' checked' : ''}>`;
        return `<label class="${f.type === 'checkbox' ? 'ops-check' : ''}" for="${id}">${control}${f.type === 'checkbox' ? '' : '<span class="ops-label">'}${esc(f.label)}${f.type === 'checkbox' ? '' : '</span>'}</label>`;
      }).join('')}<button type="submit" class="primary">${esc(button)}</button></form>`;
      const form = container.querySelector('form'); form.addEventListener('submit', run(() => opsSubmit(key, form)));
      form.addEventListener('change', event => opsPrefill(key, form, event.target.name));
    }
    document.querySelectorAll('.ops-refresh').forEach(button => button.addEventListener('click', run(() => loadLocal(location.hash.slice(1)))));
    $('ops-alert-filter').addEventListener('change', opsRenderTables);
    $('ops-audit-more').addEventListener('click', run(() => opsLoadAudit(true)));
    $('local-views').addEventListener('click', event => { if (!event.target.closest('[data-ops-action]')) return; run(async event => {
      const button = event.target.closest('[data-ops-action]'); if (!button) return;
      const { opsAction: action, id, kind } = button.dataset;
      if (action === 'page') { opsPages[kind] = Number(id); opsRenderTables(); return; }
      if (action === 'detail') { opsPriceDetail(id); return; }
      if (action === 'jobdetail') { opsPriceDetail(id, true); return; }
      if (action === 'order') {
        const row = opsFind('order', id), form = document.querySelector('[data-local-form="order-events"]');
        for (const name of ['account_id', 'lot_id', 'order_ref', 'quantity', 'status', 'returned_total']) form.elements[name].value = row[name] ?? '';
        form.elements.sequence.value = row.sequence + 1; form.elements.event_id.value = crypto.randomUUID();
        form.scrollIntoView({ behavior: 'smooth', block: 'center' }); return;
      }
      if (action === 'retire' && !confirm('¿Retirar este vínculo confirmado? Las propuestas anteriores quedarán bloqueadas si dependían de él.')) return;
      if (action === 'retry' && !confirm('¿Reintentar esta operación solo en el simulador local?')) return;
      const path = action === 'retire' ? `/links/${kind}/${id}/retire` : action === 'ack' ? `/alerts/${id}/ack` : action === 'cancel' ? `/price-previews/${id}/cancel` : `/jobs/${id}/retry`;
      const body = action === 'retire' ? { expected_revision: opsFind(kind, id).revision } : action === 'retry' ? { scenario: $('ops-retry-scenario').value, confirmed: true } : {};
      await api('/api/ops'+path, { method: 'POST', body }); await loadLocal(location.hash.slice(1)); message('Operación local registrada.');
    })(event); });
  })().catch(error => { opsUI = null; throw error; });
  return opsUI;
}
function clearLocalUI() { opsGeneration++; opsState = null; opsSuppliers = []; opsUI = null; opsAudit = []; opsCursor = null; $('local-views').replaceChildren(); }
async function loadLocal(view) {
  const generation = ++opsGeneration;
  const [data, suppliers] = await Promise.all([api('/api/ops/state'), api('/api/suppliers')]);
  if (generation !== opsGeneration || $('shell').hidden) return;
  opsState = data; opsSuppliers = suppliers.flatMap(supplier => supplier.scopes.map(scope => ({ ...scope, retired: supplier.retired })));
  document.querySelectorAll('[data-local-form]').forEach(form => {
    const key = form.dataset.localForm;
    for (const field of opsForms[key][1].filter(f => f.type === 'select')) {
      const control = form.elements[field.name], value = control.value;
      control.innerHTML = `<option value="">${field.optional ? 'Sin selección' : 'Elegí una opción'}</option>`+opsOptions(field.source).map(([id, label]) => `<option value="${esc(id)}">${esc(label)}</option>`).join('');
      if ([...control.options].some(option => option.value === value)) control.value = value;
    }
  });
  opsRenderTables();
  $('ops-policy-state').textContent = data.inventory_policy ? `Política local confirmada · revisión ${data.inventory_policy.revision}` : 'Todavía falta confirmar la política antes de registrar ventas.';
  if (view === 'ops-alerts') await opsLoadAudit();
}
function opsPrefill(key, form, changed) {
  // Only selector changes populate persisted values; typing never overwrites another field.
  if (key === 'accounts' && changed === 'id') {
    const row = opsFind('account', form.elements.id.value); form.elements.name.value = row?.name ?? ''; form.elements.active.checked = row?.active ?? true;
  }
  if (key === 'listings' && changed === 'edit') {
    const row = opsFind('listing', form.elements.edit.value);
    for (const field of opsForms.listings[1].filter(f => f.name !== 'edit')) { const control = form.elements[field.name]; if (field.type === 'checkbox') control.checked = row?.[field.name] ?? false; else control.value = row?.[field.name] ?? ''; }
    for (const name of ['account_id', 'listing_id', 'variation_id']) form.elements[name].disabled = !!row;
  }
  if (key === 'settings' && changed === 'lot_id') {
    const row = opsFind('lot', form.elements.lot_id.value); form.elements.safety.value = row?.safety ?? ''; form.elements.minimum.value = row?.minimum ?? ''; form.elements.safety.disabled = row?.kind === 'full';
  }
  if (key === 'lots' && changed === 'location_id') {
    const full = opsFind('location', form.elements.location_id.value)?.kind === 'full';
    for (const name of ['initial_quantity', 'safety']) { form.elements[name].disabled = full; form.elements[name].required = !full; if (full) form.elements[name].value = ''; }
  }
  if (key === 'locations' && changed === 'kind') { const full = form.elements.kind.value === 'full'; form.elements.account_id.disabled = !full; form.elements.account_id.required = full; if (!full) form.elements.account_id.value = ''; }
  if (key === 'allocations' && ['lot_id', 'account_id'].includes(changed)) { const row = opsRows('allocation').find(r => r.lot_id === form.elements.lot_id.value && r.account_id === form.elements.account_id.value); form.elements.quantity.value = row?.quantity ?? ''; }
  if (key === 'price-rules' && ['account_id', 'scope_id'].includes(changed)) {
    const row = opsRows('price_rule').find(r => r.account_id === form.elements.account_id.value && r.scope_id === form.elements.scope_id.value);
    for (const name of ['factor', 'charge', 'digits', 'target_price_kind']) form.elements[name].value = row?.[name] ?? '';
    form.elements.confirmed.checked = false;
  }
}
async function opsSubmit(key, form) {
  if (key === 'audit') { await opsLoadAudit(); return; }
  const body = {};
  for (const field of opsForms[key][1]) {
    const input = form.elements[field.name]; let value = input.value.trim();
    if (field.type === 'checkbox') value = input.checked;
    else if (field.type === 'number') value = value === '' ? null : Number(value);
    else if (field.type === 'select' && field.optional && !value) value = null;
    body[field.name] = value;
  }
  if (Object.hasOwn(body, 'accept')) { if (!body.accept) throw new Error('Confirmá la equivalencia antes de guardar el vínculo.'); delete body.accept; }
  if (['price-rules', 'simulate', 'inventory-policy'].includes(key) && !body.confirmed) throw new Error('Falta confirmar explícitamente esta operación local.');
  let path = '/'+key, previous;
  if (key === 'accounts' && body.id) previous = opsFind('account', body.id);
  if (key === 'listings') { previous = opsFind('listing', body.edit); delete body.edit; }
  if (key === 'links') previous = opsRows('product_link').find(r => r.listing_record_id === body.listing_record_id);
  if (key === 'supplier-links') previous = opsRows('supplier_link').find(r => r.scope_id === body.scope_id && r.supplier_sku === body.supplier_sku);
  if (key === 'price-rules') previous = opsRows('price_rule').find(r => r.account_id === body.account_id && r.scope_id === body.scope_id);
  if (key === 'allocations') previous = opsRows('allocation').find(r => r.account_id === body.account_id && r.lot_id === body.lot_id);
  if (['settings', 'adjustments'].includes(key)) previous = opsFind('lot', body.lot_id);
  if (key === 'inventory-policy') previous = opsState.inventory_policy;
  if (previous) body.expected_revision = previous.revision;
  if (key === 'settings') { path = `/lots/${body.lot_id}/settings`; delete body.lot_id; }
  if (key === 'simulate') { path = `/price-previews/${body.preview_id}/simulate`; delete body.preview_id; }
  if (key === 'notices') { path = `/alerts/${body.alert_id}/notices`; delete body.alert_id; }
  if (key === 'order-events') body.returned_total ??= 0;
  const result = await api('/api/ops'+path, { method: 'POST', body });
  // Reset only after success; a network failure preserves the event key for safe retry.
  form.reset(); for (const input of form.querySelectorAll('input[type=hidden]')) input.value = crypto.randomUUID();
  form.querySelectorAll('[disabled]').forEach(input => input.disabled = false);
  await loadLocal(location.hash.slice(1));
  if (key === 'price-previews') { document.querySelector('[data-local-form="simulate"]').elements.preview_id.value = result.id; opsPriceDetail(result.id); }
  message('Guardado en este equipo. No se enviaron cambios ni mensajes externos.');
}
function opsTable(kind, headers, rows) {
  const target = document.querySelector(`[data-ops-table="${kind}"]`); if (!target) return;
  if (!rows.length) { target.innerHTML = '<p class="empty-state">Todavía no hay registros en esta sección. Usá los formularios de arriba para comenzar.</p>'; return; }
  const pages = Math.ceil(rows.length / 50), page = Math.min(opsPages[kind] ?? 1, pages); opsPages[kind] = page;
  const button = (n, label) => `<button type="button" class="secondary" data-ops-action="page" data-kind="${kind}" data-id="${n}">${label}</button>`;
  target.innerHTML = `<div class="table-wrap" tabindex="0" role="region" aria-label="${esc(headers.join(', '))}"><table><thead><tr>${headers.map(h => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.slice((page-1)*50, page*50).map(cells => `<tr>${cells.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')}</tbody></table></div><div class="ops-pagination"><span>${rows.length} registros · página ${page} de ${pages}</span>${page > 1 ? button(page-1, 'Anterior') : ''}${page < pages ? button(page+1, 'Siguiente') : ''}</div>`;
}
const opsCells = values => values.map(v => esc(display(v)));
const opsButton = (action, id, label, kind = '') => `<button type="button" class="secondary" data-ops-action="${action}" data-id="${esc(id)}" data-kind="${kind}">${esc(label)}</button>`;
function opsRenderTables() {
  if (!opsState) return;
  opsTable('listing', ['Cuenta / publicación / variante', 'Precio', 'Tipo de precio', 'Logística', 'Origen / revisión'], opsRows('listing').map(r => opsCells([opsName('listing', r.id), `${r.price} ${r.currency}`, r.price_kind, opsLabel(r.logistics), `${opsLabel(r.source)} / ${r.revision} · capacidad remota desconocida`])));
  for (const kind of ['product_link', 'supplier_link']) opsTable(kind, ['Producto', 'Destino', 'Estado', 'Acción'], opsRows(kind).map(r => [...opsCells([opsName('product', r.product_id), kind === 'product_link' ? opsName('listing', r.listing_record_id) : `${r.supplier_sku} / ${opsSuppliers.find(s => s.id === r.scope_id)?.name ?? r.scope_id}`, r.active ? 'Confirmado localmente' : 'Retirado']), r.active ? opsButton('retire', r.id, 'Retirar vínculo', kind) : '—']));
  opsTable('price_preview', ['Fecha / cuenta', 'Filas listas / bloqueadas', 'Filas', 'Acciones'], opsRows('price_preview').map(r => [...opsCells([`${date(r.created_at)} / ${opsName('account', r.account_id)}`, `${r.rows.filter(v => v.status === 'ready').length} / ${r.rows.filter(v => v.status === 'blocked').length}`, r.rows.length]), opsButton('detail', r.id, 'Ver propuesta')+' '+(opsRows('price_job').some(j => j.preview_id === r.id) ? '' : opsButton('cancel', r.id, 'Cancelar')) ]));
  opsTable('price_job', ['Fecha / cuenta', 'Resultado local', 'Intentos', 'Acción'], opsRows('price_job').map(r => [...opsCells([`${date(r.created_at)} / ${opsName('account', r.account_id)}`, `${opsLabel(r.status)} · sin verificación remota`, r.attempts.length]), opsButton('jobdetail', r.id, 'Ver resultado')+' '+(['failed', 'uncertain'].includes(r.status) && r.attempts.length < 3 ? opsButton('retry', r.id, 'Reintentar simulación') : '')]));
  opsTable('lot', ['Producto / ubicación', 'Tipo', 'Físico u observado', 'Reservado', 'Asignado', 'Libre sin asignar', 'Margen / mínimo', 'Origen / fecha'], opsRows('lot').map(r => opsCells([opsName('lot', r.id), opsLabel(r.kind), r.on_hand === null ? 'Desconocido' : `${r.on_hand} ${r.unit}`, r.reserved, r.allocated, r.available, `${r.safety ?? '—'} / ${r.minimum ?? 'Sin alerta'}`, `${opsLabel(r.source)} / ${r.observed_at ? date(r.observed_at) : 'Sin observación'}`])));
  opsTable('allocation', ['Existencia', 'Cuenta', 'Disponible asignado'], opsRows('allocation').map(r => opsCells([opsName('lot', r.lot_id), opsName('account', r.account_id), r.quantity])));
  opsTable('movement', ['Fecha', 'Existencia', 'Cambio físico', 'Cambio reservado', 'Motivo'], opsRows('movement').map(r => opsCells([date(r.created_at), opsName('lot', r.lot_id), r.delta, r.reserved_delta, r.reason])));
  opsTable('reconciliation', ['Fecha / existencia', 'Base registrada', 'Conteo', 'Diferencia', 'Referencia'], opsRows('reconciliation').map(r => opsCells([`${date(r.created_at)} / ${opsName('lot', r.lot_id)}`, r.book_quantity, r.observed_quantity, r.difference, r.reference])));
  opsTable('order', ['Venta / cuenta', 'Existencia', 'Estado', 'Cantidad / devuelto', 'Secuencia', 'Acción'], opsRows('order').map(r => [...opsCells([`${r.order_ref} / ${opsName('account', r.account_id)}`, opsName('lot', r.lot_id), opsLabel(r.status), `${r.quantity} / ${r.returned_total}`, r.sequence]), opsButton('order', r.id, 'Preparar siguiente estado')]));
  const filter = $('ops-alert-filter').value;
  opsTable('alert', ['Estado / apariciones', 'Gravedad', 'Problema local', 'Primera / última evidencia', 'Acción'], opsRows('alert').filter(r => filter === 'all' || (filter === 'resolved' ? r.status === 'resolved' : r.status !== 'resolved')).map(r => [...opsCells([`${opsLabel(r.status)} / ${r.occurrences}`, r.severity === 'error' ? 'Error' : 'Atención', r.message, `${date(r.first_seen)} / ${date(r.last_seen)}`]), r.status === 'open' ? opsButton('ack', r.id, 'Reconocer') : '—']));
  opsTable('notice', ['Destinatario', 'Estado', 'Fecha', 'Archivo'], opsRows('notice').map(r => [...opsCells([r.recipient, 'Preparado, no enviado', date(r.created_at)]), `<a href="/api/ops/notices/${encodeURIComponent(r.id)}/download">Descargar .eml</a>`]));
}
function opsPriceDetail(id, job = false) {
  const row = opsFind(job ? 'price_job' : 'price_preview', id); if (!row) return;
  $('ops-price-detail').innerHTML = `<section class="panel"><h3>${job ? 'Resultado e intentos simulados' : 'Detalle de propuesta local'}</h3><p>Origen: simulador local. Nunca verifica Mercado Libre. Moneda: ${esc(opsSuppliers.find(s => s.id === row.scope_id)?.currency ?? 'Desconocida')}.</p>${job ? '<p>'+esc(row.attempts.map(a => `Intento ${a.number}: ${a.scenario} (${date(a.at)})`).join(' · '))+'</p>' : ''}<div class="table-wrap" tabindex="0"><table><thead><tr><th>Publicación</th><th>Precio capturado</th><th>Propuesto</th><th>Estado</th><th>Motivos</th></tr></thead><tbody>${row.rows.map(r => `<tr>${opsCells([opsName('listing', r.listing_id), r.previous_price, r.proposed_price, opsLabel(r.status), r.reasons.join(' · ')]).map(v => `<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div></section>`;
}
async function opsLoadAudit(append = false) {
  const form = document.querySelector('[data-local-form="audit"]'), params = new URLSearchParams({ limit: '50' });
  for (const name of ['action', 'resource', 'account_id', 'status', 'since', 'until']) { let value = form.elements[name].value; if (value) { if (['since', 'until'].includes(name)) value = new Date(value).toISOString(); params.set(name, value); } }
  if (append && opsCursor) params.set('before', opsCursor);
  const generation = opsGeneration, result = await api('/api/ops/audit?'+params);
  if (generation !== opsGeneration || $('shell').hidden) return;
  opsAudit = append ? [...opsAudit, ...result.rows] : result.rows; opsCursor = result.next_cursor;
  $('ops-audit-table').innerHTML = `<div class="table-wrap" tabindex="0"><table><thead><tr><th>Fecha</th><th>Acción</th><th>Recurso</th><th>Cuenta</th><th>Estado registrado</th></tr></thead><tbody>${opsAudit.map(r => `<tr>${opsCells([date(r.at), r.action, r.resource_id, r.context.account_id ? opsName('account', r.context.account_id) : '—', opsLabel(r.context.status)]).map(v => `<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div><p>${opsAudit.length} registros cargados</p>`;
  $('ops-audit-more').hidden = !opsCursor;
}
