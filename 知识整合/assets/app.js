(() => {
  'use strict';
  const chapters = [...document.querySelectorAll('.chapter')];
  const cards = [...document.querySelectorAll('.card')];
  const navigation = [...document.querySelectorAll('.nav-link')];
  const search = document.getElementById('search');
  const index = JSON.parse(document.getElementById('search-index').textContent);
  const normalizedIndex = index.map(x => ({...x, normalized: normalize(x.text), french: normalize(x.fr_text)}));
  const languageButtons = [...document.querySelectorAll('[data-reading-mode]')];
  const menu = document.getElementById('menu');
  const scrim = document.getElementById('scrim');
  const status = document.getElementById('search-status');
  const empty = document.getElementById('search-empty');
  const mobile = matchMedia('(max-width:900px)');
  let lastChapter = 'overview', timer, readingMode = 'zh';
  function normalize(s) { return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }
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
  function showChapter(id, scroll = true) {
    if (!chapters.some(c => c.id === id)) id = 'overview';
    lastChapter = id; document.body.classList.remove('search-mode');
    status.hidden = true; empty.hidden = true;
    chapters.forEach(c => c.hidden = c.id !== id);
    cards.forEach(c => { c.hidden = false; c.classList.remove('search-match'); });
    navigation.forEach(a => a.getAttribute('href') === '#' + id ? a.setAttribute('aria-current','page') : a.removeAttribute('aria-current'));
    if (scroll) window.scrollTo({top:0,behavior:'instant'});
  }
  function route() {
    let id = location.hash.slice(1) || 'overview';
    try { id = decodeURIComponent(id); } catch { id = 'overview'; }
    if (id === 'main') { document.getElementById('main').focus(); return; }
    const target = document.getElementById(id), ch = target?.closest('.chapter');
    search.value = ''; clearTimeout(timer);
    showChapter(ch?.id || 'overview', !target?.classList.contains('card'));
    closeMobile();
    if (target?.classList.contains('card')) requestAnimationFrame(() => target.scrollIntoView({block:'start',behavior:'instant'}));
  }
  window.addEventListener('hashchange', route);
  document.addEventListener('click', event => {
    const a = event.target.closest('a[href^="#"]');
    if (a && a.hash === location.hash) route();
  });
  function performSearch(scroll = true) {
    const terms = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    if (!terms.length) { showChapter(lastChapter); return; }
    document.body.classList.add('search-mode');
    navigation.forEach(a=>a.removeAttribute('aria-current'));
    const found = new Set(normalizedIndex.filter(c => {
      const text = readingMode === 'fr' ? c.french : readingMode === 'compare' ? c.normalized + ' ' + c.french : c.normalized;
      return terms.every(t => text.includes(t));
    }).map(c=>c.id));
    cards.forEach(c => { c.hidden=!found.has(c.id); c.classList.toggle('search-match',found.has(c.id)); });
    chapters.forEach(ch=>ch.hidden=!cards.some(c=>c.dataset.chapter===ch.id && found.has(c.id)));
    status.hidden=false;
    status.textContent=readingMode === 'fr' ? '« '+search.value.trim()+' » · '+found.size+' notions' : '“'+search.value.trim()+'” · 找到 '+found.size+' 个相关条目';
    empty.hidden=found.size!==0;
    if (scroll) window.scrollTo({top:0,behavior:'instant'});
  }
  function setReadingMode(mode, preserve = true) {
    if (!['zh','fr','compare'].includes(mode)) mode='zh';
    const top = document.querySelector('.topbar').getBoundingClientRect().bottom;
    const anchor = preserve && cards.find(c => !c.hidden && !c.closest('.chapter').hidden &&
      c.getBoundingClientRect().bottom > top + 36 && c.getBoundingClientRect().top < innerHeight - 24);
    const offset = anchor ? anchor.getBoundingClientRect().top : 0;
    readingMode=mode; document.body.dataset.lang=mode;
    document.documentElement.lang=mode === 'fr' ? 'fr' : 'zh-CN';
    languageButtons.forEach(button => button.setAttribute('aria-pressed',String(button.dataset.readingMode===mode)));
    search.placeholder=mode === 'fr' ? 'Rechercher dans le texte original…' : mode === 'compare' ? '搜索中文与法语原文…' : '搜索中文、法语或 LaTeX…';
    document.querySelector('[data-reading-mode="compare"]').textContent=mode === 'fr' ? 'Comparer' : '对照';
    menu.setAttribute('aria-label',mode === 'fr' ? 'Afficher le sommaire' : '切换章节目录');
    search.setAttribute('aria-label',mode === 'fr' ? 'Rechercher dans le texte original' : '搜索全部知识正文');
    try { localStorage.setItem('measure-reading-mode',mode); } catch {}
    if (search.value.trim()) performSearch(false);
    if (anchor && !anchor.hidden) requestAnimationFrame(() => {
      window.scrollBy({top:anchor.getBoundingClientRect().top-offset,behavior:'instant'});
    });
  }
  languageButtons.forEach(button => button.addEventListener('click',()=>setReadingMode(button.dataset.readingMode)));
  search.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(performSearch,140);});
  document.getElementById('reset-search').addEventListener('click',()=>{search.value='';performSearch();search.focus();});
  document.addEventListener('keydown', e=>{
    if (e.key==='/' && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) { e.preventDefault();search.focus(); }
    if (e.key==='Escape') {
      if (search.value) {search.value='';performSearch();} else closeMobile();
    }
  });
  document.getElementById('print').addEventListener('click',()=>window.print());
  let savedMode='zh';
  try { savedMode=localStorage.getItem('measure-reading-mode') || 'zh'; } catch {}
  setReadingMode(savedMode,false);route();updateMenu();
})();
