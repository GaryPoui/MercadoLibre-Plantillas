/* Run after browser-smoke.cjs, on the SAME isolated synthetic backend. */
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const os = require('node:os');
const suffix = require('node:crypto').randomUUID().slice(0,8);
const { chromium } = require(process.env.MLPL_PLAYWRIGHT_MODULE ?? path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const base = process.env.MLPL_SMOKE_URL;
if (!base || process.env.MLPL_SMOKE_ALLOW_WRITE !== '1' || !process.env.MLPL_SMOKE_PASSWORD || !['localhost', '127.0.0.1'].includes(new URL(base).hostname)) throw Error('Requiere servidor local aislado y variables MLPL_SMOKE_*; ejecutar antes browser-smoke.cjs.');
(async () => {
  const browser = await chromium.launch({headless:true, channel:process.env.MLPL_SMOKE_BROWSER_CHANNEL || 'chrome'});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000}}), errors=[];
    page.on('pageerror', e => errors.push(e.message)); page.on('dialog', d => d.accept());
    await page.goto(base); await page.locator('#password').fill(process.env.MLPL_SMOKE_PASSWORD); await page.locator('#auth-submit').click(); await page.locator('#shell').waitFor({state:'visible'});
    const get = async url => {const r=await page.request.get(base+url); assert.equal(r.status(),200); return r.json();};
    const state = () => get('/api/ops/state');
    const post = async (url, body) => {const auth=await get('/api/auth/status'); const r=await page.request.post(base+'/api/ops'+url,{data:body,headers:{'X-CSRF-Token':auth.csrf}}); assert.equal(r.status(),200,await r.text()); return r.json();};
    const visit = async view => {await page.locator(`[data-view="ops-${view}"]`).click(); await page.locator(`#view-ops-${view}`).waitFor({state:'visible'}); await page.waitForFunction(() => !!document.querySelector('[data-local-form="accounts"] select option[value=""]'));};
    const fill = async (key, values) => {
      const form=page.locator(`[data-local-form="${key}"]`);
      for(const [name,value] of Object.entries(values)) {
        const input=form.locator(`[name="${name}"]`), tag=await input.evaluate(n=>n.tagName), type=await input.getAttribute('type');
        if(type==='checkbox') await input.setChecked(value); else if(tag==='SELECT') await input.selectOption(value); else await input.fill(String(value));
      }
      const resultPromise=page.waitForResponse(r=>r.url().includes('/api/ops/') && r.request().method()==='POST');
      await form.locator('button[type=submit]').click(); const r=await resultPromise; assert.equal(r.status(),200,await r.text());
      await page.waitForFunction(key=>!document.querySelector(`[data-local-form="${key}"]`).hasAttribute('aria-busy'),key);
      assert.equal(await page.locator('#error').isVisible(),false,await page.locator('#error').innerText()); return r.json();
    };
    await visit('catalog');
    const account=await fill('accounts',{name:'Cuenta ficticia local Chrome '+suffix,active:true});
    const product=await fill('products',{sku:'0001-CHROME-'+suffix,name:'Producto sintético Chrome',unit:'unidad ficticia'});
    const suppliers=await get('/api/suppliers'), scope=suppliers.flatMap(s=>s.scopes).find(s=>s.current_version_id);
    assert.ok(scope,'La prueba anterior debe haber activado una lista sintética');
    const listing=await fill('listings',{account_id:account.id,listing_id:'PUBLICACION-CHROME',currency:scope.currency,price_kind:'Destino ficticio',price:'80',logistics:'own',simulated_editable:true});
    await fill('links',{product_id:product.id,listing_record_id:listing.id,accept:true});
    await fill('supplier-links',{product_id:product.id,scope_id:scope.id,supplier_sku:'0001-UNIFICADO',accept:true});
    await visit('prices');
    await fill('price-rules',{account_id:account.id,scope_id:scope.id,factor:'1.5',charge:'2',digits:2,target_price_kind:'Destino ficticio',confirmed:true});
    const preview=await fill('price-previews',{account_id:account.id,scope_id:scope.id});
    assert.equal(preview.rows[0].status,'ready'); assert.match(await page.locator('#ops-price-detail').innerText(),/PUBLICACION-CHROME/);
    const job=await fill('simulate',{preview_id:preview.id,scenario:'timeout_after',confirmed:true}); assert.equal(job.status,'uncertain');
    const once=(await state()).listing[0];
    await page.locator(`[data-ops-action=retry][data-id="${job.id}"]`).click(); await page.locator(`[data-ops-action=retry][data-id="${job.id}"]`).waitFor({state:'detached'});
    const twice=(await state()).listing[0]; assert.equal(twice.revision,once.revision); assert.equal(twice.price,once.price);
    await page.locator(`[data-ops-action=jobdetail][data-id="${job.id}"]`).click();
    assert.match(await page.locator('#ops-price-detail').innerText(),/no se volvió a aplicar/);
    await visit('inventory');
    const location=await fill('locations',{name:'Depósito sintético Chrome '+suffix,kind:'own'});
    const lot=await fill('lots',{product_id:product.id,location_id:location.id,initial_quantity:10,safety:1,minimum:2});
    await page.locator('#view-ops-inventory details').evaluate(n=>n.open=true);
    await fill('allocations',{lot_id:lot.id,account_id:account.id,quantity:6});
    await fill('reconciliations',{lot_id:lot.id,observed_quantity:8,reference:'Conteo sintético de prueba'});
    const fullLocation=await fill('locations',{name:'Full sintético Chrome '+suffix,kind:'full',account_id:account.id});
    const fullLot=await fill('lots',{product_id:product.id,location_id:fullLocation.id,minimum:2});
    assert.equal((await state()).lot.find(r=>r.id===fullLot.id).on_hand,null);
    await fill('full-captures',{lot_id:fullLot.id,quantity:20,reference:'Observación manual sintética'});
    await visit('orders'); await fill('inventory-policy',{confirmed:true});
    const order=await fill('order-events',{account_id:account.id,lot_id:lot.id,order_ref:'VENTA-CHROME',sequence:1,status:'reserved',quantity:2});
    let snapshot=await state(); assert.equal(snapshot.lot.find(r=>r.id===lot.id).reserved,2); assert.equal(snapshot.lot.find(r=>r.id===lot.id).on_hand,10);
    await page.locator(`[data-ops-action=order][data-id="${order.order.id}"]`).click(); await fill('order-events',{status:'shipped'});
    snapshot=await state(); assert.equal(snapshot.lot.find(r=>r.id===lot.id).on_hand,8); assert.equal(snapshot.lot.find(r=>r.id===lot.id).reserved,0);
    const duplicate={account_id:account.id,lot_id:lot.id,order_ref:'VENTA-CHROME',event_id:'otro-evento-misma-secuencia',sequence:2,status:'shipped',quantity:2,returned_total:0,receipt_confirmed:false};
    assert.equal((await post('/order-events',duplicate)).status,'ignored_same'); assert.equal((await state()).lot.find(r=>r.id===lot.id).on_hand,8);
    await visit('alerts'); await page.locator('[data-ops-table=alert]').getByText(/Último conteo/).first().waitFor();
    const alert=(await state()).alert.find(r=>r.kind==='inventory_difference' && r.resource_id===lot.id);
    await page.locator(`[data-ops-action=ack][data-id="${alert.id}"]`).click(); await page.locator(`[data-ops-action=ack][data-id="${alert.id}"]`).waitFor({state:'detached'});
    const notice=await fill('notices',{alert_id:alert.id,recipient:'operador@example.invalid'}); assert.equal(notice.sent,false);
    const email=await page.request.get(base+`/api/ops/notices/${notice.id}/download`); assert.equal(email.status(),200); assert.match(await email.text(),/NO enviado/);
    await page.locator('[data-local-form=audit] [name=action]').fill('local_order_'); await page.locator('[data-local-form=audit] [name=account_id]').selectOption(account.id); await page.locator('[data-local-form=audit] button').click();
    await page.waitForFunction(()=>document.querySelectorAll('#ops-audit-table tbody tr').length===2);
    await page.locator('#ops-audit-table').getByText('local_order_shipped',{exact:true}).waitFor();
    assert.equal(await page.locator('#ops-audit-table tbody tr').count(),2);
    const exported=await page.request.get(base+'/api/ops/export'); assert.equal((await exported.body()).subarray(0,2).toString(),'PK');
    await page.screenshot({path:path.join(os.tmpdir(),'mlpl-ops-alerts-desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    for(const view of ['catalog','prices','inventory','orders','alerts']) {
      await visit(view); assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,view+' overflow móvil');
    }
    await page.screenshot({path:path.join(os.tmpdir(),'mlpl-ops-mobile.png'),fullPage:true});
    await page.setViewportSize({width:1440,height:1000}); await visit('inventory');
    await page.screenshot({path:path.join(os.tmpdir(),'mlpl-ops-inventory-desktop.png'),fullPage:true});
    assert.deepEqual(errors,[]); await page.locator('#logout').click(); await page.locator('#auth').waitFor({state:'visible'}); assert.equal(await page.locator('#local-views').innerHTML(),'');
    console.log('PASS: catálogo/vínculos, precios inciertos y reintento sin doble cambio, inventario/asignación/reserva/despacho, duplicados, Full manual, conciliación, alertas/aviso no enviado, auditoría/exportación y cinco vistas móviles; sin errores JS.');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
