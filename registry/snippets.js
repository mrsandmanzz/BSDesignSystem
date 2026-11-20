// Helper untuk figma_execute (Plugin API). Tempel blok yang dibutuhkan; semua async.
// STATUS: [diuji] = dijalankan di Figma 2026-11-10 (instance dibuat lalu dihapus, tidak ada sisa); [belum diuji] = disusun dari API, uji dulu.
// PRASYARAT: library Foundation + SHIELD + GUN sudah di-enable di file target (Assets → Libraries).

// 1) Impor komponen dari key (key dari: python3 registry/plan.py ... atau registry/find.py ...)   [diuji]
async function importComp(key, kind /* 'set' | 'component' */) {
  return kind === 'set' ? figma.importComponentSetByKeyAsync(key) : figma.importComponentByKeyAsync(key);
}

// 2) Buat instance + set properti. propsVariant = {Kind:'filled',Size:'md*'} (string persis, 'md*' memang memakai bintang)
//    propsOther = {'Label Text#1728:306':'Simpan'} (pakai key lengkap dari find.py --full / plan.py textProps)   [diuji]
async function makeInstance(key, kind, propsVariant = {}, propsOther = {}) {
  const c = await importComp(key, kind);
  const base = kind === 'set' ? c.defaultVariant : c;
  const inst = base.createInstance();
  const all = { ...propsVariant, ...propsOther };
  if (Object.keys(all).length) inst.setProperties(all);   // lempar error bila nama/nilai salah → perbaiki dari registry
  return inst;
}

// 3) Ganti icon lewat instance-swap: iconKey dari `find.py --icon nama` (key komponen 'Icon / nama')   [diuji]
async function swapIcon(inst, swapPropKey, iconKey) {
  const icon = await figma.importComponentByKeyAsync(iconKey);
  inst.setProperties({ [swapPropKey]: icon.id });
}

// 4) Isi SLOT (mis. Page Layout Template: 'Navigation Rail' | 'Sidebar' | 'Header' | 'Body')   [diuji dengan node teks]
function fillSlot(inst, slotName, node) {
  const slot = inst.findAllWithCriteria({ types: ['SLOT'] }).find(s => s.name === slotName);
  if (!slot) throw new Error('slot tidak ditemukan: ' + slotName);
  slot.appendChild(node);
  return slot;
}

// 5) Ubah teks yang TIDAK terekspos sebagai property (mis. Title di Header Nav). Tetap instance, bukan detach.   [diuji]
async function setInnerText(inst, layerName, text) {
  const t = inst.findAllWithCriteria({ types: ['TEXT'] }).find(n => n.name === layerName);
  if (!t) throw new Error('layer teks tidak ada: ' + layerName);
  await figma.loadFontAsync(t.fontName);
  t.characters = text;
}

// 6) Posisikan frame layar di kanvas tanpa menimpa isi lain
function placeFrame(frame, page = figma.currentPage) {
  const right = Math.max(0, ...page.children.map(n => n.x + n.width));
  frame.x = right + 200; frame.y = 0; page.appendChild(frame);
}

// 7) Token pada node kustom. JANGAN pakai figma.variables.importVariableByKeyAsync: menggantung & mematikan plugin (teramati 2×).
//    getVariableByIdAsync hanya bekerja untuk variable yang SUDAH terikat di file (id remote dibentuk oleh Figma, tidak bisa dirakit dari registry).
//    Cara aman: ambil variable dari node contoh yang sudah terikat, lalu ikat ke node baru.   [diuji]
async function boundVariableByName(rootNode, tokenName) {
  for (const n of rootNode.findAll(x => Array.isArray(x.fills))) {
    for (const f of n.fills) {
      const b = f.boundVariables && f.boundVariables.color;
      if (b) { const v = await figma.variables.getVariableByIdAsync(b.id); if (v && v.name === tokenName) return v; }
    }
  }
  return null;
}
function bindFill(node, variable) {
  node.fills = [figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', variable)];
}
// Preferensi: hindari frame kustom. Pakai Section Layout / slot yang sudah terikat token.

// 8) Verifikasi cepat sebelum menyerahkan hasil   [belum diuji penuh]
async function lintFrame(frame) {
  const r = { instances: 0, detached: 0, unboundFills: 0, nonLibrary: 0 };
  for (const n of frame.findAll(() => true)) {
    if (n.type === 'INSTANCE') { r.instances++; const m = await n.getMainComponentAsync(); if (!m) r.detached++; else if (!m.remote) r.nonLibrary++; }
    if (Array.isArray(n.fills) && n.fills.some(f => f.type === 'SOLID' && f.visible !== false && !(f.boundVariables && f.boundVariables.color)) && n.type !== 'INSTANCE') r.unboundFills++;
  }
  return r;
}

// 9) Ambil SET dari instance yang sudah ada di file (WAJIB untuk set bersloT: Section Layout, Key Value, dll.; importComponentSetByKeyAsync menggantung)   [diuji 2026-11-10]
async function setFromExistingInstance(rootFrame, setName) {
  for (const i of rootFrame.findAllWithCriteria({ types: ['INSTANCE'] })) {
    const c = await i.getMainComponentAsync();
    const s = c && ((c.parent && c.parent.type === 'COMPONENT_SET') ? c.parent : c);
    if (s && s.name === setName) return s;   // lalu: s.defaultVariant.createInstance()
  }
  return null;
}

// 10) Mode gelap untuk satu frame   [diuji]
async function setDark(frame, anyBoundVariableNode) {
  const f = anyBoundVariableNode.fills.find(f => f.boundVariables && f.boundVariables.color);
  const v = await figma.variables.getVariableByIdAsync(f.boundVariables.color.id);
  const col = await figma.variables.getVariableCollectionByIdAsync(v.variableCollectionId);
  frame.setExplicitVariableModeForCollection(col, col.modes.find(m => m.name === 'Dark').modeId);
}
