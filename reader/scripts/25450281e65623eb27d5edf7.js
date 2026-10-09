(() => {
  'use strict';
  const boot = JSON.parse(document.getElementById('reader-config').textContent);
  const main = document.getElementById('main');
  const chapters = [...document.querySelectorAll('.chapter:not(#search-results)')];
  const chapterById = new Map(chapters.map(ch => [ch.id, ch]));
  const byId = new Map(boot.cards.map(card => [card.id, card]));
  const navigation = [...document.querySelectorAll('.nav-link')];
  const search = document.getElementById('search');
  const results = document.getElementById('search-results');
  const status = document.getElementById('search-status');
  const empty = document.getElementById('search-empty');
  const loading = document.getElementById('reader-loading');
  const errorBox = document.getElementById('reader-error');
  const languageButtons = [...document.querySelectorAll('[data-reading-mode]')];
  const menu = document.getElementById('menu');
  const scrim = document.getElementById('scrim');
  const mobile = matchMedia('(max-width:900px)');
  const narrow = matchMedia('(max-width:640px)');
  const chapterCache = new Map(), detailState = new Map(), positions = new Map();
  let currentData, normalizedIndex, indexPromise, lastChapter = 'overview';
  let readingMode = 'zh', timer, revision = 0, positionRevision = 0, printing = false, printPosition;
  let retryAction = route;

  function normalize(text) { return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }
  function escape(text) { return String(text).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])); }
  async function fetchJSON(url) {
    // Hashed URLs are immutable. The entry page supplies the current version.
    const response = await fetch(new URL(url, document.baseURI), {cache:'force-cache'});
    if (!response.ok) throw new Error('HTTP ' + response.status);
    return response.json();
  }
  function chapterData(id) {
    if (!boot.chapters[id]) return Promise.resolve(null);
    if (!chapterCache.has(id)) {
      const promise = fetchJSON(boot.chapters[id]).catch(error => { chapterCache.delete(id); throw error; });
      chapterCache.set(id, promise);
      if (chapterCache.size > 4 && !printing) chapterCache.delete(chapterCache.keys().next().value);
    }
    return chapterCache.get(id);
  }
  function searchData() {
    if (normalizedIndex) return Promise.resolve(normalizedIndex);
    if (!indexPromise) indexPromise = fetchJSON(boot.search).then(index => {
      normalizedIndex = index.map(item => ({...item, chinese:normalize(item.text), french:normalize(item.fr_text)}));
      return normalizedIndex;
    }).catch(error => { indexPromise = null; throw error; });
    return indexPromise;
  }
  async function sourceCatalog() {
    const response=await fetch(new URL(boot.sources,document.baseURI),{cache:'no-store'});
    if(!response.ok)throw new Error('HTTP '+response.status);
    const data=await response.json();
    return data.files.map(file=>'<tr><td><span class="lang-zh">'+escape(file.kind)+'</span><span class="lang-fr" lang="fr">'+escape(file.fr_kind)+'</span></td><td><a target="_blank" rel="noopener" href="../'+escape(file.path)+'"><span class="lang-zh">'+escape(file.label)+'</span><span class="lang-fr" lang="fr">'+escape(file.fr_label)+'</span></a></td><td>'+Math.round(file.bytes/1024)+' KiB</td></tr>').join('');
  }
  function setBusy(value, print = false) {
    main.setAttribute('aria-busy', String(value)); loading.hidden = !value;
    loading.textContent = readingMode === 'fr' ? (print ? 'Préparation de l’impression…' : 'Chargement du chapitre…') : (print ? '正在准备打印内容…' : '正在加载章节…');
    if (value) errorBox.hidden = true;
  }
  function act(action) {
    retryAction = action;
    Promise.resolve().then(action).catch(error => {
      console.error('Reader request failed:', error);
      setBusy(false); errorBox.hidden = false;
      errorBox.querySelector('p').textContent = readingMode === 'fr' ? 'Le contenu n’a pas pu être chargé. Vérifiez la connexion puis réessayez.' : '内容加载失败，请检查网络连接后重试。';
    });
  }
  document.getElementById('reader-retry').addEventListener('click', () => act(retryAction));
  function cards() { return [...main.querySelectorAll('.card')]; }
  function stateKey(detail) { return detail.closest('.card').id + ':' + detail.dataset.state; }
  function saveDetails() { main.querySelectorAll('.card details[data-state]').forEach(detail => detailState.set(stateKey(detail), detail.open)); }
  function position() {
    const top = document.querySelector('.topbar').getBoundingClientRect().bottom;
    const anchor = cards().find(card => { const rect=card.getBoundingClientRect(); return rect.bottom>top+36 && rect.top<innerHeight-24; });
    return {id:anchor?.id,offset:anchor?.getBoundingClientRect().top,y:scrollY};
  }
  function restorePosition(saved, cardId) {
    const ticket = ++positionRevision;
    requestAnimationFrame(() => {
      if (ticket !== positionRevision) return;
      const target = document.getElementById(cardId || saved?.id);
      if (cardId && target) target.scrollIntoView({block:'start',behavior:'instant'});
      else if (target && saved) window.scrollBy({top:target.getBoundingClientRect().top-saved.offset,behavior:'instant'});
      else window.scrollTo({top:saved?.y || 0,behavior:'instant'});
    });
  }
  function clearMounted() {
    saveDetails(); chapters.forEach(ch => ch.querySelector('.cards')?.replaceChildren()); currentData = null;
  }
  function eligible(node) {
    if (printing && node.closest('.proof,.tex-source')) return false;
    if (readingMode === 'fr' && (node.closest('.zh-reading') || node.closest('.tex-source'))) return false;
    if (readingMode === 'zh' && node.closest('.fr-reading')) return false;
    for (let parent=node.parentElement;parent && parent!==main;parent=parent.parentElement) {
      if (parent.tagName === 'DETAILS' && !parent.open) return false;
    }
    return true;
  }
  function fillDeferred(container,data) {
    container.querySelectorAll('.lazy-detail[data-content]').forEach(slot => {
      if (slot.childNodes.length || !eligible(slot)) return;
      const content=data.contents[slot.dataset.content];
      if (content === undefined) throw new Error('Missing chapter content: '+slot.dataset.content);
      slot.innerHTML=content;
    });
  }
  function syncImages(container,data) {
    container.querySelectorAll('.lazy-asset').forEach(slot => {
      if (!eligible(slot)) return;
      const key=!printing && narrow.matches && slot.dataset.narrow ? slot.dataset.narrow : slot.dataset.asset;
      if (slot.dataset.mountedAsset === key) return;
      const asset=data.assets[key];
      if (!asset) throw new Error('Missing vector asset: '+key);
      const image=document.createElement('img');
      image.className=asset.kind === 'symbol' ? 'original-svg' : 'tex-svg';
      image.alt=slot.dataset.label || byId.get(slot.closest('.card').id)?.title || '';
      image.loading=printing ? 'eager' : 'lazy'; image.decoding='async';
      image.width=Math.max(1,Math.round(asset.width)); image.height=Math.max(1,Math.round(asset.height));
      image.style.aspectRatio=asset.width+' / '+asset.height;
      image.src=new URL(asset.url,document.baseURI).href;
      slot.replaceChildren(image); slot.dataset.mountedAsset=key;
    });
  }
  function mountChapter(id,data) {
    const list=chapterById.get(id)?.querySelector('.cards'); if (!list || !data) return;
    list.innerHTML=data.ids.map(key=>data.templates[key]).join('');
    list.querySelectorAll('[data-pane]').forEach(pane => {
      if ((readingMode==='fr' && pane.classList.contains('zh-reading')) || (readingMode==='zh' && pane.classList.contains('fr-reading'))) return;
      pane.insertAdjacentHTML('beforeend',data.contents[pane.dataset.pane]);
    });
    list.querySelectorAll('details[data-state]').forEach(detail=>{detail.open=detailState.get(stateKey(detail)) || false;});
    fillDeferred(list,data); syncImages(list,data);
  }
  function updateMenu() {
    const expanded=mobile.matches ? document.body.classList.contains('mobile-menu') : !document.body.classList.contains('sidebar-collapsed');
    menu.setAttribute('aria-expanded',String(expanded)); scrim.hidden=!(mobile.matches && expanded);
    document.getElementById('sidebar').inert=!expanded;
  }
  function closeMobile() { document.body.classList.remove('mobile-menu'); updateMenu(); }
  menu.addEventListener('click',()=>{document.body.classList.toggle(mobile.matches ? 'mobile-menu' : 'sidebar-collapsed');updateMenu();});
  scrim.addEventListener('click',closeMobile); mobile.addEventListener('change',closeMobile);
  narrow.addEventListener('change',()=>{
    if (printing || !currentData || readingMode==='fr') return;
    const saved=position(); syncImages(chapterById.get(lastChapter),currentData); restorePosition(saved);
  });
  async function showChapter(id,{saved,cardId}={}) {
    if (!chapterById.has(id)) id='overview';
    const ticket=++revision;
    if (!document.body.classList.contains('search-mode') && currentData) positions.set(lastChapter,position());
    clearMounted(); lastChapter=id;
    document.body.classList.remove('search-mode'); results.hidden=true; results.replaceChildren(); status.hidden=true; empty.hidden=true;
    chapters.forEach(ch=>ch.hidden=ch.id!==id);
    navigation.forEach(a=>a.hash==='#'+id ? a.setAttribute('aria-current','page') : a.removeAttribute('aria-current'));
    setBusy(!!boot.chapters[id] || id==='resources');
    try {
      const data=await chapterData(id);
      const sourceRows=id==='resources' ? await sourceCatalog() : null;
      if (ticket!==revision) return;
      if(sourceRows){const table=document.getElementById('source-catalog');table.tBodies[0].innerHTML=sourceRows;table.tHead.rows[0].cells[2].textContent='KiB';}
      currentData=data; mountChapter(id,data); setBusy(false); errorBox.hidden=true; restorePosition(saved,cardId);
    } catch(error) { if (ticket===revision) throw error; }
  }
  async function route() {
    if (printing) return;
    let id=location.hash.slice(1) || 'overview';try{id=decodeURIComponent(id);}catch{id='overview';}
    if (id==='main') { main.focus();return; }
    const item=byId.get(id); const chapter=item?.chapter || (chapterById.has(id) ? id : 'overview');
    search.value='';clearTimeout(timer);closeMobile();
    await showChapter(chapter,{saved:item ? null : positions.get(chapter),cardId:item?.id});
  }
  window.addEventListener('hashchange',()=>act(route));
  document.addEventListener('click',event=>{
    const a=event.target.closest('a[href^="#"]');
    if (a && a.hash===location.hash) {event.preventDefault();act(route);}
  });
  async function performSearch(scroll=true) {
    if (printing) return;
    const query=search.value.trim();const terms=normalize(query).split(/\s+/).filter(Boolean);
    if (!terms.length) {await showChapter(lastChapter,{saved:positions.get(lastChapter)});return;}
    const ticket=++revision;
    if (!document.body.classList.contains('search-mode')) positions.set(lastChapter,position());
    clearMounted();document.body.classList.add('search-mode');chapters.forEach(ch=>ch.hidden=true);
    navigation.forEach(a=>a.removeAttribute('aria-current'));results.hidden=true;empty.hidden=true;status.hidden=true;setBusy(true);
    try {
      const index=await searchData();if(ticket!==revision)return;
      const found=index.filter(item=>{const text=readingMode==='fr' ? item.french : readingMode==='compare' ? item.chinese+' '+item.french : item.chinese;return terms.every(term=>text.includes(term));});
      const heading=readingMode==='fr' ? 'Résultats de recherche' : '搜索结果';
      const hint=readingMode==='fr' ? 'Ouvrir la notion dans son chapitre' : '点击条目，进入所在章节';
      results.innerHTML='<h1 class="search-heading">'+heading+'</h1><ol class="search-list">'+found.map(item=>{
        const chapterTitle=chapterById.get(item.chapter).querySelector('h1 '+(readingMode==='fr' ? '.lang-fr' : '.lang-zh')).textContent;
        const title=readingMode==='fr' ? item.original_title : item.title;
        return '<li><a class="search-result" href="#'+item.id+'"><small>'+escape(chapterTitle)+'</small><strong>'+escape(title)+'</strong>'+(readingMode==='compare' ? '<span lang="fr">'+escape(item.original_title)+'</span>' : '')+'<em>'+hint+' ↗</em></a></li>';
      }).join('')+'</ol>';
      results.hidden=found.length===0;status.hidden=false;empty.hidden=found.length!==0;setBusy(false);
      status.textContent=readingMode==='fr' ? '« '+query+' » · '+found.length+' notions' : '“'+query+'” · 找到 '+found.length+' 个相关条目';
      if(scroll)restorePosition({y:0});
    } catch(error) {if(ticket===revision)throw error;}
  }
  function updateLanguage(mode) {
    readingMode=['zh','fr','compare'].includes(mode) ? mode : 'zh';document.body.dataset.lang=readingMode;
    document.documentElement.lang=readingMode==='fr' ? 'fr' : 'zh-CN';
    languageButtons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.readingMode===readingMode)));
    search.placeholder=readingMode==='fr' ? 'Rechercher dans le texte original…' : readingMode==='compare' ? '搜索中文与法语原文…' : '搜索中文、法语或 LaTeX…';
    document.querySelector('[data-reading-mode="compare"]').textContent=readingMode==='fr' ? 'Comparer' : '对照';
    search.setAttribute('aria-label',readingMode==='fr' ? 'Rechercher dans le texte original' : '搜索全部知识正文');
    menu.setAttribute('aria-label',readingMode==='fr' ? 'Afficher le sommaire' : '切换章节目录');
    try{localStorage.setItem('measure-reading-mode-online',readingMode);}catch{}
  }
  async function setReadingMode(mode) {
    if (printing || mode===readingMode) return;
    const saved=position();clearMounted();updateLanguage(mode);
    if (search.value.trim()) {const ticket=revision+1;await performSearch(false);if(ticket===revision)restorePosition(saved);}
    else await showChapter(lastChapter,{saved});
  }
  languageButtons.forEach(button=>button.addEventListener('click',()=>act(()=>setReadingMode(button.dataset.readingMode))));
  main.addEventListener('toggle',event=>{
    const detail=event.target;
    if(printing || !detail.isConnected || !detail.matches('details[data-state]') || !currentData)return;
    detailState.set(stateKey(detail),detail.open);
    if(detail.open) {fillDeferred(detail,currentData);syncImages(detail,currentData);}
    else detail.querySelector(':scope > .lazy-detail')?.replaceChildren();
  },true);
  search.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>act(performSearch),140);});
  document.getElementById('reset-search').addEventListener('click',()=>{search.value='';act(performSearch);search.focus();});
  async function printOutline() {
    if(printing)return;
    printPosition=position();clearMounted();printing=true;++revision;setBusy(true,true);
    try {
      const ids=Object.keys(boot.chapters);const data=await Promise.all(ids.map(chapterData));
      ids.forEach((id,i)=>mountChapter(id,data[i]));document.body.classList.add('printing');
      await Promise.all([...main.querySelectorAll('.lazy-asset img')].map(image=>image.decode()));
      setBusy(false);window.print();
    } finally {
      printing=false;document.body.classList.remove('printing');clearMounted();
      if(search.value.trim())await performSearch(false);
      else await showChapter(lastChapter,{saved:printPosition});
      while(chapterCache.size>4)chapterCache.delete(chapterCache.keys().next().value);
    }
  }
  document.getElementById('print').addEventListener('click',()=>act(printOutline));
  document.addEventListener('keydown',event=>{
    if((event.ctrlKey || event.metaKey) && event.key.toLowerCase()==='p') {event.preventDefault();act(printOutline);}
    if(event.key==='/' && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) {event.preventDefault();search.focus();}
    if(event.key==='Escape') {if(search.value){search.value='';act(performSearch);}else closeMobile();}
  });
  let savedMode='zh';try{savedMode=localStorage.getItem('measure-reading-mode-online') || localStorage.getItem('measure-reading-mode-lazy') || 'zh';}catch{}
  updateLanguage(savedMode);updateMenu();act(route);
})();
