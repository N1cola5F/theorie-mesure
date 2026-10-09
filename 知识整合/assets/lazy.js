(() => {
  'use strict';
  // Payload caches contain strings only. SVG nodes belong to the visible chapter.
  const main = document.getElementById('main');
  const chapters = [...document.querySelectorAll('.chapter:not(#search-results)')];
  const chapterById = new Map(chapters.map(ch => [ch.id, ch]));
  const navigation = [...document.querySelectorAll('.nav-link')];
  const search = document.getElementById('search');
  const results = document.getElementById('search-results');
  const status = document.getElementById('search-status');
  const empty = document.getElementById('search-empty');
  const index = readJSON('search-index');
  const byId = new Map(index.map(item => [item.id, item]));
  const normalizedIndex = index.map(item => ({...item, chinese: normalize(item.text), french: normalize(item.fr_text)}));
  const languageButtons = [...document.querySelectorAll('[data-reading-mode]')];
  const menu = document.getElementById('menu');
  const scrim = document.getElementById('scrim');
  const mobile = matchMedia('(max-width:900px)');
  const narrow = matchMedia('(max-width:640px)');
  const liveGlyphs = document.getElementById('live-glyphs');
  const liveOriginals = document.getElementById('live-originals');
  const chapterCache = new Map(), assetCache = new Map();
  const detailState = new Map(), positions = new Map();
  const mountedGlyphs = new Set(), mountedOriginals = new Set();
  let glyphs, lastChapter = 'overview', readingMode = 'zh', timer, printing = false, printPosition;
  let positionRevision = 0;

  function readJSON(id) {
    const source = document.getElementById(id);
    if (!source) throw new Error('Missing reader payload: ' + id);
    return JSON.parse(source.textContent);
  }
  function normalize(text) { return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }
  function escape(text) { return String(text).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])); }
  function chapterData(id) {
    if (!chapterCache.has(id)) chapterCache.set(id, readJSON('chapter-data-' + id));
    return chapterCache.get(id);
  }
  function assetData(key) {
    if (assetCache.has(key)) {
      const value = assetCache.get(key);
      assetCache.delete(key); assetCache.set(key, value);
      return value;
    }
    const value = readJSON('asset-data-' + key);
    assetCache.set(key, value);
    // Bound duplicate parsed vector strings; the authoritative JSON remains inert.
    if (assetCache.size > 64) assetCache.delete(assetCache.keys().next().value);
    return value;
  }
  function cards() { return [...main.querySelectorAll('.card')]; }
  function stateKey(detail) { return detail.closest('.card').id + ':' + detail.dataset.state; }
  function saveDetails() {
    main.querySelectorAll('.card details[data-state]').forEach(detail => detailState.set(stateKey(detail), detail.open));
  }
  function position() {
    const top = document.querySelector('.topbar').getBoundingClientRect().bottom;
    const anchor = cards().find(card => {
      const rect = card.getBoundingClientRect();
      return rect.bottom > top + 36 && rect.top < innerHeight - 24;
    });
    return {id: anchor?.id, offset: anchor?.getBoundingClientRect().top, y: scrollY};
  }
  function restorePosition(saved) {
    const revision = ++positionRevision;
    requestAnimationFrame(() => {
      if (revision !== positionRevision || !saved) return;
      const target = saved.id && document.getElementById(saved.id);
      if (target) window.scrollBy({top: target.getBoundingClientRect().top - saved.offset, behavior:'instant'});
      else window.scrollTo({top: saved.y || 0, behavior:'instant'});
    });
  }
  function clearMounted() {
    saveDetails();
    chapters.forEach(ch => ch.querySelector('.cards')?.replaceChildren());
    liveGlyphs.replaceChildren(); liveOriginals.replaceChildren();
    mountedGlyphs.clear(); mountedOriginals.clear();
  }
  function eligible(node) {
    if (printing && node.closest('.proof, .tex-source')) return false;
    if (!printing && node.closest('.chapter')?.hidden) return false;
    if (readingMode === 'fr' && (node.closest('.zh-reading') || node.closest('.tex-source'))) return false;
    if (readingMode === 'zh' && node.closest('.fr-reading')) return false;
    for (let parent = node.parentElement; parent && parent !== main; parent = parent.parentElement) {
      if (parent.tagName === 'DETAILS' && !parent.open) return false;
    }
    return true;
  }
  function fillDeferred(container) {
    let changed = false;
    container.querySelectorAll('.lazy-detail[data-content]').forEach(slot => {
      if (slot.childNodes.length || !eligible(slot)) return;
      const data = chapterData(slot.closest('.card').dataset.chapter);
      const content = data.contents[slot.dataset.content];
      if (content === undefined) throw new Error('Missing reader content: ' + slot.dataset.content);
      slot.innerHTML = content; changed = true;
    });
    return changed;
  }
  function mountChapter(id) {
    const section = chapterById.get(id), list = section?.querySelector('.cards');
    if (!list) return;
    const data = chapterData(id);
    list.innerHTML = data.ids.map(key => data.templates[key]).join('');
    list.querySelectorAll('[data-pane]').forEach(pane => {
      if ((readingMode === 'fr' && pane.classList.contains('zh-reading')) ||
          (readingMode === 'zh' && pane.classList.contains('fr-reading'))) return;
      pane.insertAdjacentHTML('beforeend', data.contents[pane.dataset.pane]);
    });
    list.querySelectorAll('details[data-state]').forEach(detail => {
      detail.open = detailState.get(stateKey(detail)) || false;
    });
    fillDeferred(list);
  }
  function syncAssets() {
    const slots = [...main.querySelectorAll('.lazy-asset')].filter(eligible);
    const neededGlyphs = new Set(), neededOriginals = new Set();
    const selected = slots.map(slot => {
      const key = !printing && narrow.matches && slot.dataset.narrow ? slot.dataset.narrow : slot.dataset.asset;
      const data = assetData(key);
      data.glyphs.forEach(gid => neededGlyphs.add(gid));
      if (data.kind === 'symbol') neededOriginals.add(key);
      return {slot, key, data};
    });
    if (neededGlyphs.size && !glyphs) glyphs = readJSON('glyph-data');
    const additions = [];
    neededGlyphs.forEach(gid => {
      if (mountedGlyphs.has(gid)) return;
      if (!glyphs[gid]) throw new Error('Missing vector glyph: ' + gid);
      additions.push(glyphs[gid]); mountedGlyphs.add(gid);
    });
    if (additions.length) liveGlyphs.insertAdjacentHTML('beforeend', additions.join(''));
    const originals = [];
    selected.forEach(({key, data}) => {
      if (data.kind !== 'symbol' || mountedOriginals.has(key)) return;
      originals.push(data.markup); mountedOriginals.add(key);
    });
    if (originals.length) liveOriginals.insertAdjacentHTML('beforeend', originals.join(''));
    selected.forEach(({slot, key, data}) => {
      if (slot.dataset.mountedAsset === key) return;
      slot.innerHTML = data.kind === 'svg' ? data.markup :
        '<svg class="original-svg" viewBox="' + escape(data.viewBox) + '" role="img" aria-label="' + escape(slot.dataset.label || '') + '"><use href="#' + key + '"></use></svg>';
      slot.dataset.mountedAsset = key;
    });
    [...liveOriginals.children].forEach(node => {
      if (!neededOriginals.has(node.id)) { mountedOriginals.delete(node.id); node.remove(); }
    });
    [...liveGlyphs.children].forEach(node => {
      if (!neededGlyphs.has(node.id)) { mountedGlyphs.delete(node.id); node.remove(); }
    });
  }
  function updateMenu() {
    const expanded = mobile.matches ? document.body.classList.contains('mobile-menu') : !document.body.classList.contains('sidebar-collapsed');
    menu.setAttribute('aria-expanded', String(expanded));
    scrim.hidden = !(mobile.matches && expanded);
    document.getElementById('sidebar').inert = !expanded;
  }
  function closeMobile() { document.body.classList.remove('mobile-menu'); updateMenu(); }
  menu.addEventListener('click', () => {
    document.body.classList.toggle(mobile.matches ? 'mobile-menu' : 'sidebar-collapsed'); updateMenu();
  });
  scrim.addEventListener('click', closeMobile);
  mobile.addEventListener('change', closeMobile);
  narrow.addEventListener('change', () => {
    if (printing || !cards().length || readingMode === 'fr') return;
    const saved = position(); syncAssets(); restorePosition(saved);
  });
  function showChapter(id, scroll = true) {
    if (!chapterById.has(id)) id = 'overview';
    const searching = document.body.classList.contains('search-mode');
    if (!searching) positions.set(lastChapter, position());
    clearMounted(); lastChapter = id;
    document.body.classList.remove('search-mode');
    results.hidden = true; results.replaceChildren(); status.hidden = true; empty.hidden = true;
    chapters.forEach(ch => ch.hidden = ch.id !== id);
    navigation.forEach(a => a.getAttribute('href') === '#' + id ? a.setAttribute('aria-current','page') : a.removeAttribute('aria-current'));
    mountChapter(id); syncAssets();
    if (scroll) { ++positionRevision; window.scrollTo({top:0, behavior:'instant'}); }
  }
  function route() {
    let id = location.hash.slice(1) || 'overview';
    try { id = decodeURIComponent(id); } catch { id = 'overview'; }
    if (id === 'main') { main.focus(); return; }
    const item = byId.get(id);
    const returning = document.body.classList.contains('search-mode');
    search.value = ''; clearTimeout(timer);
    const chapter = item?.chapter || (chapterById.has(id) ? id : 'overview');
    const saved = positions.get(chapter);
    showChapter(chapter, !item && !saved); closeMobile();
    if (item) {
      const revision = ++positionRevision;
      requestAnimationFrame(() => {
        if (revision === positionRevision) document.getElementById(id)?.scrollIntoView({block:'start', behavior:'instant'});
      });
    } else if (saved && !returning) restorePosition(saved);
  }
  window.addEventListener('hashchange', route);
  document.addEventListener('click', event => {
    const a = event.target.closest('a[href^="#"]');
    if (a && a.hash === location.hash) { event.preventDefault(); route(); }
  });
  function performSearch(scroll = true) {
    const terms = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    if (!terms.length) { showChapter(lastChapter, false); restorePosition(positions.get(lastChapter)); return; }
    if (!document.body.classList.contains('search-mode')) positions.set(lastChapter, position());
    clearMounted(); document.body.classList.add('search-mode');
    chapters.forEach(ch => ch.hidden = true);
    navigation.forEach(a => a.removeAttribute('aria-current'));
    const found = normalizedIndex.filter(item => {
      const text = readingMode === 'fr' ? item.french : readingMode === 'compare' ? item.chinese + ' ' + item.french : item.chinese;
      return terms.every(term => text.includes(term));
    });
    const heading = readingMode === 'fr' ? 'Résultats de recherche' : '搜索结果';
    const hint = readingMode === 'fr' ? 'Ouvrir la notion dans son chapitre' : '点击条目，进入所在章节';
    results.innerHTML = '<h1 class="search-heading">' + heading + '</h1><ol class="search-list">' + found.map(item => {
      const ch = chapterById.get(item.chapter).querySelector('h1');
      const chapterTitle = ch.querySelector(readingMode === 'fr' ? '.lang-fr' : '.lang-zh').textContent;
      const title = readingMode === 'fr' ? item.original_title : item.title;
      return '<li><a class="search-result" href="#' + item.id + '"><small>' + escape(chapterTitle) + '</small><strong>' + escape(title) + '</strong>' +
        (readingMode === 'compare' ? '<span lang="fr">' + escape(item.original_title) + '</span>' : '') + '<em>' + hint + ' ↗</em></a></li>';
    }).join('') + '</ol>';
    results.hidden = found.length === 0;
    status.hidden = false;
    status.textContent = readingMode === 'fr' ? '« ' + search.value.trim() + ' » · ' + found.length + ' notions' : '“' + search.value.trim() + '” · 找到 ' + found.length + ' 个相关条目';
    empty.hidden = found.length !== 0;
    if (scroll) { ++positionRevision; window.scrollTo({top:0, behavior:'instant'}); }
  }
  function setReadingMode(mode, preserve = true) {
    if (!['zh','fr','compare'].includes(mode)) mode = 'zh';
    if (preserve && mode === readingMode) return;
    const saved = preserve ? position() : null;
    clearMounted();
    // Change the global language after removing the previous SVG instances.
    readingMode = mode; document.body.dataset.lang = mode;
    document.documentElement.lang = mode === 'fr' ? 'fr' : 'zh-CN';
    languageButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.readingMode === mode)));
    search.placeholder = mode === 'fr' ? 'Rechercher dans le texte original…' : mode === 'compare' ? '搜索中文与法语原文…' : '搜索中文、法语或 LaTeX…';
    document.querySelector('[data-reading-mode="compare"]').textContent = mode === 'fr' ? 'Comparer' : '对照';
    menu.setAttribute('aria-label', mode === 'fr' ? 'Afficher le sommaire' : '切换章节目录');
    search.setAttribute('aria-label', mode === 'fr' ? 'Rechercher dans le texte original' : '搜索全部知识正文');
    try { localStorage.setItem('measure-reading-mode-lazy', mode); } catch {}
    if (search.value.trim()) performSearch(false);
    else { mountChapter(lastChapter); syncAssets(); }
    if (saved) restorePosition(saved);
  }
  languageButtons.forEach(button => button.addEventListener('click', () => setReadingMode(button.dataset.readingMode)));
  main.addEventListener('toggle', event => {
    const detail = event.target;
    if (printing || !detail.isConnected || !detail.matches('details[data-state]')) return;
    detailState.set(stateKey(detail), detail.open);
    if (detail.open) { if (fillDeferred(detail)) syncAssets(); }
    else {
      const slot = detail.querySelector(':scope > .lazy-detail');
      if (slot?.childNodes.length) { slot.replaceChildren(); syncAssets(); }
    }
  }, true);
  search.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(performSearch, 140); });
  document.getElementById('reset-search').addEventListener('click', () => { search.value = ''; performSearch(); search.focus(); });
  document.addEventListener('keydown', event => {
    if (event.key === '/' && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) { event.preventDefault(); search.focus(); }
    if (event.key === 'Escape') {
      if (search.value) { search.value = ''; performSearch(); } else closeMobile();
    }
  });
  function preparePrint() {
    if (printing) return;
    printPosition = position(); clearMounted(); printing = true;
    chapters.forEach(ch => mountChapter(ch.id)); syncAssets();
    document.body.classList.add('printing');
  }
  function finishPrint() {
    if (!printing) return;
    printing = false; document.body.classList.remove('printing'); clearMounted();
    if (search.value.trim()) performSearch(false);
    else { mountChapter(lastChapter); syncAssets(); }
    restorePosition(printPosition);
  }
  window.addEventListener('beforeprint', preparePrint);
  window.addEventListener('afterprint', finishPrint);
  document.getElementById('print').addEventListener('click', () => {
    preparePrint(); requestAnimationFrame(() => { try { window.print(); } finally { finishPrint(); } });
  });
  let savedMode = 'zh';
  try { savedMode = localStorage.getItem('measure-reading-mode-lazy') || localStorage.getItem('measure-reading-mode') || 'zh'; } catch {}
  setReadingMode(savedMode, false); route(); updateMenu();
})();
