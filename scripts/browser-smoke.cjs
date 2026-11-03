/* Run only against an isolated local test data directory. No commercial fixtures. */
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const os = require('node:os');
const bundled = path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { chromium } = require(process.env.MLPL_PLAYWRIGHT_MODULE ?? bundled);
const baseURL = process.env.MLPL_SMOKE_URL ?? 'http://127.0.0.1:8765';
if (process.env.MLPL_SMOKE_ALLOW_WRITE !== '1' || !process.env.MLPL_SMOKE_PASSWORD) throw new Error('Usar backend aislado y definir MLPL_SMOKE_ALLOW_WRITE=1 y MLPL_SMOKE_PASSWORD.');
if (!['127.0.0.1', 'localhost'].includes(new URL(baseURL).hostname)) throw new Error('El recorrido solo admite un servidor local.');
(async () => {
  const browser = await chromium.launch({ headless: true, ...(process.env.MLPL_SMOKE_BROWSER_CHANNEL ? { channel: process.env.MLPL_SMOKE_BROWSER_CHANNEL } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = []; page.on('pageerror', error => errors.push(error.message));
    page.on('dialog', dialog => dialog.accept());
    await page.goto(baseURL);
    await page.locator('#password').fill(process.env.MLPL_SMOKE_PASSWORD);
    await page.locator('#auth-submit').click();
    await page.locator('#shell').waitFor({ state: 'visible' });
    const demoResponse = await page.request.get(`${baseURL}/api/demo.xlsx`); assert.equal(demoResponse.status(), 200);
    await page.locator('#file').setInputFiles({ name: 'muestra_sintetica.xlsx', mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', buffer: await demoResponse.body() });
    await page.locator('#upload-form button').click(); await page.locator('#workspace').waitFor({ state: 'visible' });
    await page.locator('#map-code').selectOption('A'); await page.locator('#map-description').selectOption('B'); await page.locator('#map-base').selectOption('D');
    await page.locator('#config-form button[type=submit]').click(); await page.locator('#review-panel').waitFor({ state: 'visible' });
    await page.locator('#review-table').getByText('001-EJEMPLO', { exact: true }).waitFor();
    assert.match(await page.locator('#review-table').innerText(), /Falta valor base/);
    await page.locator('[data-correct="2"]').click(); await page.locator('#correction-column').selectOption('D'); await page.locator('#correction-type').selectOption('number'); await page.locator('#correction-value').fill('175'); await page.locator('#correction-reason').fill('Corrección sintética del recorrido de verificación');
    await page.locator('#correction-form button[type=submit]').click(); await page.locator('#correction-dialog').waitFor({ state: 'hidden' });
    assert.match(await page.locator('#review-table').innerText(), /175/);
    const exportURL = await page.locator('#export').getAttribute('href'); assert.match(exportURL, /^\/api\/reviews\/[^/]+\/export$/);
    const exportResponse = await page.request.get(`${baseURL}${exportURL}`); assert.equal(exportResponse.status(), 200); const bytes = await exportResponse.body(); assert.equal(bytes.subarray(0, 2).toString(), 'PK');
    await page.locator('#profile-name').fill('Perfil de prueba sintética'); await page.locator('#supplier').fill('Proveedor ficticio de prueba'); await page.locator('#save-profile button[type=submit]').click();
    await page.locator('#notice').filter({ hasText: 'Perfil guardado' }).waitFor();
    await page.locator('[data-view=history]').click(); await page.locator('[data-import]').first().click(); await page.locator('[data-review]').first().click(); await page.locator('#view-work').waitFor({ state: 'visible' });
    await page.locator('#row-filter').selectOption('pending'); assert.match(await page.locator('#page-info').innerText(), /1 filas/); await page.locator('#row-filter').selectOption('all');
    await page.locator('[data-view=catalog]').click(); await page.locator('#catalog-json').fill(JSON.stringify([{ account_id: 'cuenta-prueba', product_key: '001-EJEMPLO', listing_id: 'ITEM-PRUEBA', price: '100', quantity: '0', logistics: 'full', writable_verified: false }])); await page.locator('#catalog-form button[type=submit]').click(); await page.locator('#notice').filter({ hasText: 'Catálogo controlado guardado' }).waitFor();
    await page.locator('[data-view=work]').click(); await page.locator('#account').fill('cuenta-prueba'); await page.locator('#compare-form button').click(); await page.locator('#comparison').getByText('Full es de solo lectura.', { exact: true }).waitFor();
    await page.evaluate(() => window.scrollTo(0, 0)); await page.screenshot({ path: process.env.MLPL_SMOKE_SCREENSHOT ?? path.join(os.tmpdir(), 'mlpl-browser-smoke.png'), fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 }); assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth), false); await page.screenshot({ path: path.join(os.tmpdir(), 'mlpl-browser-mobile.png'), fullPage: true });
    await page.setViewportSize({ width: 1440, height: 1000 });
    const csv = ['CODIGO,DESCRIPCION,BASE', ...Array.from({ length: 60 }, (_, i) => `00${i}-FICTICIO,Producto sintético ${i},${i}`)].join('\n');
    await page.locator('#file').setInputFiles({ name: 'paginacion_sintetica.csv', mimeType: 'text/csv', buffer: Buffer.from(csv) }); await page.locator('#upload-form button').click(); await page.locator('#filename').filter({ hasText: 'paginacion_sintetica.csv' }).waitFor();
    await page.locator('.rules').evaluate(node => node.open = true); await page.locator('#advanced-config').evaluate(node => node.closest('details').open = true);
    await page.locator('#advanced-config').fill(JSON.stringify({ sheet: 'CSV', header_rows: [1], data_start: 2, mapping: { code: 'A', description: 'B', base: 'D' }, parameters: { factor: '0' }, formulas: { D: '=C{row}*factor' } }));
    // CSV sheet naming is taken from metadata rather than assumed.
    const config = JSON.parse(await page.locator('#advanced-config').inputValue()); config.sheet = await page.locator('#sheet').inputValue(); await page.locator('#advanced-config').fill(JSON.stringify(config));
    await page.locator('#load-json').click(); await page.locator('#config-form button[type=submit]').click(); await page.locator('#page-info').filter({ hasText: '61 filas' }).waitFor(); assert.equal(await page.locator('#review-table tbody tr').count(), 25); await page.locator('#next').click(); assert.match(await page.locator('#page-info').innerText(), /Página 2 de 3/);
    await page.locator('#row-filter').selectOption('pending'); assert.match(await page.locator('#page-info').innerText(), /0 filas/); await page.locator('#row-filter').selectOption('all');
    await page.locator('#profile-name').fill('Perfil CSV sintético'); await page.locator('#supplier').fill('Proveedor CSV ficticio'); await page.locator('#save-profile button[type=submit]').click(); await page.locator('#notice').filter({ hasText: 'Perfil guardado' }).waitFor();
    const option = await page.locator('#profile-select option').filter({ hasText: 'Perfil CSV sintético' }).getAttribute('value'); await page.locator('#profile-select').selectOption(option); await page.locator('#new-version').check(); await page.locator('#save-profile button[type=submit]').click(); await page.locator('#notice').filter({ hasText: 'Perfil guardado' }).waitFor();
    await page.locator('[data-view=profiles]').click(); await page.locator('#profiles-list').getByText('Perfil CSV sintético · versión 2', { exact: true }).waitFor(); await page.locator('[data-retire]').first().click(); await page.locator('#notice').filter({ hasText: 'Versión retirada' }).waitFor();
    assert.deepEqual(errors, []); await page.locator('#logout').click(); await page.locator('#auth').waitFor({ state: 'visible' });
    console.log('PASS: autenticación, XLSX/CSV, mapeo, regla con factor cero, paginación60, pendientes, corrección, exportación, perfiles/versiones/retiro, historial, comparación Full y móvil; sin errores JS.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
