// executor.js — pembangun layar untuk Figma Plugin API (jalan lewat figma_execute).
// Cara pakai: build.py --emit menghasilkan skrip lengkap = isi file ini + SPEC. Jalankan BERULANG sampai {done:true}.
// Prinsip: langkah kecil, resumable (state di clientStorage), aman terhadap hang/crash plugin.
// STATUS ENGINE: op page/frame/inst/slotFill/text/swap/stretch/fit/theme = teknik teruji 2026-11-10 (lihat registry/README.md).
//                Impor via varian (vkey) = TERUJI 2026-11-19 (set bersloT OK). Teruji: page, frame, inst, slotAlign, theme(Dark), verify, fit, text (ubah teks tetap instance), stretch. swapVariant (varian saudara dari set yang sudah ada). Jebakan: impor variant key 'Wizard Item - Create Booking SWT' (c2d731fb…) timeout 15 dtk.

const RACE_MS = 7000;
const race = (p, ms = RACE_MS) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error('timeout ' + ms + 'ms')), ms))]);

async function getNode(id) { const n = await figma.getNodeByIdAsync(id); if (!n) throw new Error('node hilang: ' + id); return n; }

// --- ambil komponen: urutan terjamin tidak menggantung --------------------------------------------
async function seedSet(name) {
  // fallback: cari instance yang sudah ada di halaman sandbox / halaman _seed untuk set bersloT
  const pages = figma.root.children.filter(p => p.name === '_seed' || p.id === figma.currentPage.id);
  for (const p of pages) {
    await p.loadAsync();
    for (const i of p.findAllWithCriteria({ types: ['INSTANCE'] })) {
      const c = await i.getMainComponentAsync();
      const s = c && ((c.parent && c.parent.type === 'COMPONENT_SET') ? c.parent : c);
      if (s && s.name === name) return s;
    }
  }
  return null;
}
// POOL (TERUJI 2026-11-19): komponen yang sudah dipakai oleh frame contoh di file target bisa dibuat instance-nya TANPA impor
// (getMainComponentAsync). Ini jalur paling aman; impor via key hanya cadangan (beberapa impor menggantung/mematikan plugin).
let _pool = null;
async function getPool(ex) {
  // ex: ID node (frame contoh) ATAU 'page:<nama halaman>' (maks 12 frame teratas, batas 8 dtk). Biaya ~ jumlah instance di frame contoh (±0,1 dtk per layar).
  if (_pool) return _pool; _pool = {};
  if (!ex) return _pool;
  let roots = [];
  if (typeof ex === 'string' && ex.startsWith('page:')) {
    const pg = figma.root.children.find(p => p.name === ex.slice(5));
    if (!pg) throw new Error('halaman contoh tak ada: ' + ex.slice(5));
    await pg.loadAsync();
    roots = pg.children.filter(n => n.type === 'FRAME' || n.type === 'SECTION' || n.type === 'COMPONENT').slice(0, 12);
  } else { const n = await figma.getNodeByIdAsync(ex); if (n) roots = [n]; }
  const t0 = Date.now();
  for (const r of roots) {
    if (Date.now() - t0 > 8000) break;
    for (const i of r.findAllWithCriteria({ types: ['INSTANCE'] })) {
      const m = await i.getMainComponentAsync(); if (!m) continue;
      const set = m.parent && m.parent.type === 'COMPONENT_SET' ? m.parent : null;
      if (set) { if (!_pool[set.key]) _pool[set.key] = { comp: set.defaultVariant, set }; if (!_pool[set.name]) _pool[set.name] = _pool[set.key]; }
      else { if (!_pool[m.key]) _pool[m.key] = { comp: m }; if (!_pool[m.name]) _pool[m.name] = _pool[m.key]; }
    }
  }
  return _pool;
}
async function getComp(ref, spec) {
  const pool = await getPool(spec && spec.example);
  const hit = pool[ref.key] || pool[ref.name];
  if (hit) return { comp: hit.comp, set: hit.set, via: 'pool' };
  const tried = [];
  if (ref.vkey) { try { return { comp: await race(figma.importComponentByKeyAsync(ref.vkey), 10000), via: 'vkey' }; } catch (e) { tried.push('vkey:' + e.message); } }
  if (ref.kind === 'component') { try { return { comp: await race(figma.importComponentByKeyAsync(ref.key), 10000), via: 'component' }; } catch (e) { tried.push('component:' + e.message); } }
  else if (!ref.slotSet) { try { const set = await race(figma.importComponentSetByKeyAsync(ref.key), 10000); return { comp: set.defaultVariant, set, via: 'set' }; } catch (e) { tried.push('set:' + e.message); } }
  const sd = await seedSet(ref.name);
  if (sd) return { comp: sd.defaultVariant || sd, set: sd, via: 'seed' };
  throw new Error('komponen tak bisa diambil: ' + ref.name + ' [' + tried.join('; ') + '] — beri spec.example (frame contoh yang memakai komponen ini) atau halaman "_seed"');
}

// --- util layout -------------------------------------------------------------------------------------
function applyLayout(node, L) {
  if (!L) return;
  if (L.layoutAlign) node.layoutAlign = L.layoutAlign;
  if (L.layoutGrow != null) node.layoutGrow = L.layoutGrow;
}
async function attach(node, parent, st) {
  // parent: 'page' | {frame:id} | {slot:{inst:id, name:'Body'}}
  if (parent === 'page') { figma.currentPage.appendChild(node); return; }
  if (parent.frame) { (await getNode(st.ids[parent.frame])).appendChild(node); return; }
  if (parent.slot) {
    const inst = await getNode(st.ids[parent.slot.inst]);
    const slot = inst.findAllWithCriteria({ types: ['SLOT'] }).find(s => s.name === parent.slot.name);
    if (!slot) throw new Error('slot tidak ada: ' + parent.slot.name + ' di ' + inst.name);
    slot.appendChild(node); return;
  }
  throw new Error('parent tak dikenal');
}

// --- operasi -------------------------------------------------------------------------------------------
const OPS = {
  async page(s, st) {
    let pg = figma.root.children.find(p => p.name === s.name);
    if (!pg) { pg = figma.createPage(); pg.name = s.name; }
    await figma.setCurrentPageAsync(pg); st.pageId = pg.id;
  },
  async frame(s, st) {
    const f = figma.createFrame(); f.name = s.name; f.fills = []; f.clipsContent = false;
    const sz = s.size || [100, 100]; f.resize(sz[0], sz[1]);
    if (s.layout) {
      f.layoutMode = s.layout.mode; f.itemSpacing = s.layout.gap || 0;
      f.counterAxisSizingMode = s.layout.counterSizing || 'AUTO'; f.primaryAxisSizingMode = s.layout.primarySizing || 'AUTO';
      if (s.layout.counterSizing === 'FIXED' || s.layout.primarySizing === 'FIXED') f.resize(sz[0], sz[1]);
      if (s.layout.align) f.counterAxisAlignItems = s.layout.align;
    }
    await attach(f, s.parent, st);
    if (s.x != null) f.x = s.x; if (s.y != null) f.y = s.y;
    applyLayout(f, s.place); st.ids[s.id] = f.id;
  },
  async inst(s, st) {
    const { comp, via } = await getComp(s.ref, st.spec);
    const inst = comp.createInstance(); await attach(inst, s.parent, st);
    const all = { ...(s.props || {}), ...(s.textProps || {}) };
    if (Object.keys(all).length) inst.setProperties(all);
    if (s.swap) for (const [k, ref] of Object.entries(s.swap)) {        // instance-swap: butuh id komponen varian
      const r = await getComp(ref, st.spec); let target = r.comp;
      if (ref.variantName && r.set) target = r.set.children.find(c => c.name.includes(ref.variantName)) || target;
      const key = Object.keys(inst.componentProperties).find(x => x === k || x.startsWith(k + '#') || x.replace(/ ?#.*/, '') === k);
      inst.setProperties({ [key || k]: target.id });
    }
    applyLayout(inst, s.place); st.ids[s.id] = inst.id; (st.via = st.via || {})[s.id] = via;
  },
  async text(s, st) {                                  // ubah TEXT di dalam instance (tetap instance)
    const inst = await getNode(st.ids[s.inst]);
    const ts = inst.findAllWithCriteria({ types: ['TEXT'] }).filter(t => t.name === s.layer);
    const t = ts[s.index || 0]; if (!t) throw new Error('teks tak ada: ' + s.layer + ' di ' + inst.name);
    await figma.loadFontAsync(t.fontName); t.characters = s.value;
  },
  async slotAlign(s, st) {                             // mis. Body: tengah horizontal
    const inst = await getNode(st.ids[s.inst]); const slot = inst.findAllWithCriteria({ types: ['SLOT'] }).find(x => x.name === s.slot);
    if (s.counter) slot.counterAxisAlignItems = s.counter; if (s.primary) slot.primaryAxisAlignItems = s.primary;
  },
  async stretch(s, st) {                               // isi penuh lebar/tinggi slot
    const inst = await getNode(st.ids[s.inst]);
    for (const name of s.slots) {
      const slot = inst.findAllWithCriteria({ types: ['SLOT'] }).find(x => x.name === name);
      for (const c of (slot ? slot.children : [])) { c.layoutAlign = 'STRETCH'; if (s.grow !== false) c.layoutGrow = 1; }   // grow:false = hanya lebar (Body/Content); default: isi penuh (Sidebar/Rail)
    }
  },
  async fit(s, st) {                                   // tinggi frame = posisi slot + tinggi slot + padding bawah (TERUJI 2026-11-19)
    const inst = await getNode(st.ids[s.inst]); const frame = await getNode(st.ids[s.frame]);
    const slot = inst.findAllWithCriteria({ types: ['SLOT'] }).find(x => x.name === s.slot);
    const top = Math.round(slot.absoluteTransform[1][2] - inst.absoluteTransform[1][2]);
    const need = Math.max(s.min || 0, top + Math.round(slot.height) + (s.pad != null ? s.pad : 24));
    inst.resize(inst.width, need); frame.resize(frame.width, need);
  },
  async swapVariant(s, st) {                           // TERUJI 2026-11-19: ganti instance-swap ke varian saudara dari set yang SUDAH ada di dalam instance
    // s: {inst, prop:'Wizard Item', nested:'Wizard Item', variant:'Property 1=Individual'}  -> TANPA impor baru (impor vkey varian ini menggantung)
    const inst = await getNode(st.ids[s.inst]);
    const key = Object.keys(inst.componentProperties).find(k => k === s.prop || k.startsWith(s.prop + '#'));
    if (!key) throw new Error('prop swap tak ada: ' + s.prop);
    const item = inst.findAllWithCriteria({ types: ['INSTANCE'] }).find(i => i.name.includes(s.nested || s.prop));
    if (!item) throw new Error('instance bersarang tak ada: ' + (s.nested || s.prop));
    const set = (await item.getMainComponentAsync()).parent;
    const target = set && set.children && set.children.find(c => c.name === s.variant);
    if (!target) throw new Error('varian tak ada: ' + s.variant + ' [' + (set && set.children ? set.children.map(c => c.name) : '') + ']');
    inst.setProperties({ [key]: target.id });
  },
  async theme(s, st) {                                 // mode Light/Dark untuk satu frame
    const frame = await getNode(st.ids[s.frame]);
    let v = null;
    for (const n of frame.findAll(x => Array.isArray(x.fills) && x.fills.length)) {
      const f = n.fills.find(f => f.boundVariables && f.boundVariables.color);
      if (f) { const cand = await figma.variables.getVariableByIdAsync(f.boundVariables.color.id); if (cand && cand.name.startsWith('color/')) { v = cand; break; } }
    }
    if (!v) throw new Error('tidak ada variable terikat untuk menentukan collection tema');
    const col = await figma.variables.getVariableCollectionByIdAsync(v.variableCollectionId);
    const mode = col.modes.find(m => m.name === s.mode); if (!mode) throw new Error('mode tak ada: ' + s.mode);
    frame.setExplicitVariableModeForCollection(col, mode.modeId);
  },
  async verify(s, st) {                                // ringkasan cek cepat
    const f = await getNode(st.ids[s.frame]); const r = { instances: 0, detached: 0, nonLibrary: 0, size: [Math.round(f.width), Math.round(f.height)] };
    for (const i of f.findAllWithCriteria({ types: ['INSTANCE'] })) { r.instances++; const m = await i.getMainComponentAsync(); if (!m) r.detached++; else if (!m.remote) r.nonLibrary++; }
    st.verify = r;
  },
};

// --- eksekutor resumable ------------------------------------------------------------------------------
async function exec(spec, opt = {}) {
  const budget = opt.budgetMs || 18000, t0 = Date.now(), key = 'exec:' + spec.id;
  let st = opt.reset ? null : await figma.clientStorage.getAsync(key);
  if (!st) st = { i: 0, ids: {}, log: [] };
  st.spec = spec; _pool = null;
  while (st.i < spec.steps.length && Date.now() - t0 < budget) {
    const s = spec.steps[st.i]; const t1 = Date.now();
    try { await race(OPS[s.op](s, st), 25000); st.log.push(st.i + ' ' + s.op + ' ' + (s.id || s.name || s.layer || '') + ' ' + (Date.now() - t1) + 'ms'); st.i++; }
    catch (e) { await figma.clientStorage.setAsync(key, st); return { done: false, failed: true, step: st.i, op: s.op, error: String(e && e.message || e), log: st.log.slice(-6) }; }
    await figma.clientStorage.setAsync(key, st);
  }
  const done = st.i >= spec.steps.length;
  if (done) await figma.clientStorage.setAsync(key, null);
  return { done, next: st.i, total: spec.steps.length, rootId: st.ids[spec.root], via: st.via, verify: st.verify, log: st.log.slice(-5), ms: Date.now() - t0 };
}
