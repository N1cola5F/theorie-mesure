(() => {
  'use strict';
  const M=JSON.parse(document.getElementById('manifest').textContent);
  const main=document.getElementById('main'),nav=document.getElementById('nav'),search=document.getElementById('search');
  const cache=new Map(),narrow=window.matchMedia('(max-width:1100px)');
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const stored=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key))??fallback}catch{return fallback}};
  const save=(key,value)=>{try{localStorage.setItem(key,JSON.stringify(value))}catch{}};
  const sidebar=document.getElementById('sidebar'),menu=document.getElementById('menu'),scrim=document.getElementById('scrim'),mobile=matchMedia('(max-width:760px)');
  document.body.classList.toggle('sidebar-collapsed',stored('mesure-ds-sidebar-collapsed',false)===true);
  function updateMenu(){
    const open=mobile.matches?document.body.classList.contains('mobile-menu'):!document.body.classList.contains('sidebar-collapsed');
    menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'收起目录':'展开目录');
    menu.title=open?'收起目录':'展开目录';document.getElementById('menu-label').textContent=mobile.matches?'目录':open?'收起目录':'展开目录';
    sidebar.inert=!open;scrim.hidden=!(mobile.matches&&open);
  }
  function closeMobile(){document.body.classList.remove('mobile-menu');updateMenu()}
  menu.addEventListener('click',()=>{
    document.body.classList.toggle(mobile.matches?'mobile-menu':'sidebar-collapsed');
    if(!mobile.matches)save('mesure-ds-sidebar-collapsed',document.body.classList.contains('sidebar-collapsed'));
    updateMenu();
  });
  scrim.addEventListener('click',closeMobile);mobile.addEventListener('change',closeMobile);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&mobile.matches&&document.body.classList.contains('mobile-menu')){closeMobile();menu.focus()}});
  new ResizeObserver(([entry])=>document.documentElement.style.setProperty('--top',entry.target.offsetHeight+'px')).observe(document.querySelector('.topbar'));
  updateMenu();
  let mode=stored('mesure-ds-mode','zh'),read=stored('mesure-ds-read',{}),serial=0,current={kind:'home'},searchTimer;
  if(!['zh','fr','compare'].includes(mode))mode='zh';
  const source=(key,page)=>encodeURI(M.sources[key].href)+(page?'#page='+page:'');
  const link=(key,page,label)=>`<a href="${esc(source(key,page))}" target="_blank" rel="noopener">${esc(label||M.sources[key].label)} ↗</a>`;
  const image=(asset,alt,lazy=true)=>`<img src="${esc(asset.src)}" width="${asset.width}" height="${asset.height}" alt="${esc(alt)}" loading="${lazy?'lazy':'eager'}" decoding="async">`;
  const compiled=(item,lazy=true,french=false)=>{const assets=french?item.french:item.compiled;return `<picture class="tex-picture"><source media="(max-width:1100px)" srcset="${esc(assets.narrow.src)}" width="${assets.narrow.width}" height="${assets.narrow.height}">${image(assets.wide,french?item.title_fr:item.title,lazy)}</picture>`};
  const guide=id=>mode==='fr'&&/^i[1-8]$/.test(id)?'':`<section class="panel">${compiled(M.guides[id],false)}</section>`;
  const heading=(eyebrow,title,subtitle='')=>`<p class="eyebrow">${esc(eyebrow)}</p><h1>${esc(title)}</h1>${subtitle?`<p class="subtitle">${esc(subtitle)}</p>`:''}`;
  async function get(url){if(cache.has(url))return cache.get(url);const promise=fetch(url).then(r=>{if(!r.ok)throw Error('资源返回 '+r.status);return r.json()}).catch(e=>{cache.delete(url);throw e});cache.set(url,promise);return promise}
  function chapterOf(id){const m=/^c([1-8])-/.exec(id);return m?Number(m[1]):null}
  const chapter=n=>M.chapters.find(c=>c.id===n);
  function refs(item){return `<div class="refs">${(item.requires||[]).map(id=>`<a href="#${id}" title="前置知识">依据 ${id}</a>`).join('')}${item.proof?`<a class="proof-link" href="#p${String(item.proof).padStart(2,'0')}">读指定证明 ${String(item.proof).padStart(2,'0')} →</a>`:''}</div>`}
  function official(item){return `${compiled(item,true,true)}<div class="source-line">${item.originals.map(p=>link(item.source,p.page,'官方 PDF p.'+p.page)).join('')}<button class="text-button" data-zoom="${esc(item.french.wide.src)}" data-alt="${esc(item.title_fr)}">放大正文</button></div>`}
  function body(item){const cn=`<div class="column"><div class="column-label">中文 · 理解说明与依据</div>${compiled(item)}</div>`;
    const fr=`<div class="column fr-reading" lang="fr"><div class="column-label">FRANÇAIS · TEXTE OFFICIEL</div>${official(item)}</div>`;
    return `<div class="columns ${mode==='compare'?'compare':''}">${mode==='zh'?cn:mode==='fr'?fr:cn+fr}</div>`}
  function card(item){return `<article class="card" id="${item.id}" data-read="${!!read[item.id]}"><div class="card-head"><div><div class="card-id">${esc(item.id)}</div><h2>${esc(mode==='fr'?item.title_fr:item.title)}</h2>${mode==='compare'?`<p class="official-title" lang="fr">${esc(item.title_fr)}</p>`:''}</div><label class="read-check"><input type="checkbox" data-read="${item.id}" ${read[item.id]?'checked':''}> 已读</label></div>${body(item)}${refs(item)}${mode==='zh'?`<div class="source-line">${link(item.source,item.originals[0].page,'对应官方条目 · p.'+item.originals[0].page)}</div>`:''}</article>`}
  function updateNav(){nav.innerHTML=`<a href="#home" data-route="home">范围与阅读顺序</a><a href="#basics" data-route="basics">起步：符号与对象</a><span class="section-label">按考纲过知识 · 100 条</span>${M.chapters.map(c=>`<a href="#ch${c.id}" data-route="ch${c.id}">${String(c.id).padStart(2,'0')} · ${esc(mode==='fr'?c.fr:c.title.split('：')[0])}${c.statements_only?' · 表述':''}</a>`).join('')}<span class="section-label">理解与补充</span><a href="#proofs" data-route="proofs">15 个指定证明</a><a href="#pitfalls" data-route="pitfalls">条件与易错点</a><a href="#td" data-route="td">学完后的练习建议</a><a href="#sources" data-route="sources">官方资料与待确认信息</a>`;
    const active=current.kind==='chapter'?'ch'+current.chapter:current.kind==='proof'?'proofs':current.kind;
    nav.querySelector(`[data-route="${active}"]`)?.setAttribute('aria-current','page');
    document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)))}
  function home(){return heading('DS / 20 OCTOBRE 2026','先过知识，再理解证明','按教师最终考纲独立整理。适合从零建立主线；每条先看中文理解，再对照法语正式表述。')+
    `<div class="facts"><div class="fact"><strong>10 月 20 日</strong><span>2026 · 北京时间 · 开考时刻待确认</span></div><div class="fact"><strong>闭卷</strong><span>不允许资料和计算器</span></div><div class="fact"><strong>100 个条目</strong><span>第 1–8 章的定义、性质与定理</span></div><div class="fact"><strong>15 个证明</strong><span>名单内考 1 个 · 每步附依据</span></div></div>`+
    `<section class="panel note"><h2>先分清考试范围</h2><p><strong>知识问答包括第 1–8 章。</strong>第 7 章 Lᵖ、第 8 章测度分解只要求定义和结论，不要求证明和习题。“到多重积分为止”是习题与证明的范围，不能据此跳过 CM05。</p><p>老师的详细通知写 2–5 道知识问答，较早通知写 3 道；另有 1 个指定证明、3 道 Part 1 类型题及 1 道 Part 2 类型题。没有官方时长；90–120 分钟只是你的估计。</p><div class="source-line">${link('programme',1,'官方范围 p.1')}${link('programme',15,'证明清单 p.15')}</div></section>`+
    guide('intro')+
    `<section class="panel"><h2>从零开始的顺序</h2><p>先读“符号与对象”，再依次读第 1–6 章。在每章后理解相应指定证明；接着读第 7–8 章的定义与结论，最后回看条件与反例。一次读不透时，用依据链接回到前置知识。</p><p>10 月 11–19 日是复习窗口。可把第 1–3 章、第 4–5 章、第 6 章、第 7–8 章依次安排在前四个阶段，末尾留时间回读证明和薄弱处；这是建议顺序，不是已经掌握程度的预测。</p><a href="#basics">从基础符号开始 →</a></section>`+
    `<div class="route-grid">${M.chapters.map(c=>`<a class="route" href="#ch${c.id}"><span class="number">CHAPITRE ${String(c.id).padStart(2,'0')} · ${c.count} 条</span><b>${esc(c.title)}</b><small>${esc(c.subtitle)}</small></a>`).join('')}</div>`}
  function proofList(){return heading('PREUVES EXIGIBLES','15 个指定证明','名单来自官方最终清单。先读对应知识，再沿逐步依据理解；没有新增 Fubini、控制收敛等清单外的必背证明。')+`<section class="panel note"><p>中文是讲解稿，法语按官方 PDF 的文字和公式重新排版。证明 06 调整了差集公式与容斥的讲解顺序；证明 11 展开生成族判别的等价论证，法语侧保留原文。</p>${link('preuves',2,'官方完整证明')}</section><ol class="proof-list">${M.proofs.map(p=>`<li><a href="#${p.id}"><span class="pnumber">${String(p.number).padStart(2,'0')}</span><span>${esc(p.title)}<small>对应 ${p.card} · ${p.requires.length} 项前置知识</small></span></a></li>`).join('')}</ol>`}
  function tdAdvice(filter){const list=filter?M.td.filter(t=>t.chapters.includes(filter)):M.td;
    return `<section class="panel"><h2>学完后的练习建议</h2><p>先能解释知识，再选一两题看它怎样使用。下面是阅读后的建议，不是预测出题。打开官方答案会同时看到题目；先遮住解答写出思路，再对照所用定义或定理。</p>${list.map(t=>`<details><summary>TD${t.number} · ${esc(t.title)} · Part 1 / Part 2</summary><p class="source-note">官方题解含 Part 1 的 ${t.counts['1']} 题与 Part 2 的 ${t.counts['2']} 题。第 3 部分不在 DS 范围。</p><ul class="exercise-list">${t.exercises.map(e=>`<li>${link(t.source,e.page,'Ex. '+e.number+' · '+e.title)}<span>先读 <a href="#${e.card}">${e.card}</a> · ${e.part===1?'基础应用':'进阶理解'} · 官方题解 p.${e.page}</span></li>`).join('')}</ul><div class="source-line">${link(t.source,null,'TD'+t.number+' 全部题目与官方解答')}</div></details>`).join('')}${!list.length?'<p class="source-note">本章仅准备知识表述，不安排 DS 习题。</p>':''}</section>`}
  function sources(){return heading('SOURCES & INFORMATIONS','资料已足够开始复习','TD2、TD3、TD4 新增官方答案包含题目；不需要个人答案或往年 DS 试卷作为启动条件。')+
    `<section class="panel note"><h2>还缺什么</h2><p><strong>目前没有阻塞复习的必需文件缺口。</strong>已有 CM1–CM5、官方考纲、15 个官方证明和 TD1–TD4 官方题目与答案。TD4 不必再重复上传单独题单。</p><p>只有考试信息仍待确认：具体时长、开考时间与地点。课堂特别强调、删改的条目或新的教师通知，如有，再补充即可。个人错题与往年试卷属于可选材料。</p></section>`+
    `<section class="panel"><h2>本次排除内容</h2><ul>${M.excluded.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p class="source-note">概率测度的定义、第一 Borel–Cantelli 引理、Cantor 测度仍在官方清单中；不因名字出现“概率”就删除。移除的“测度的和”是独立课程表述条目，TD2 已列入考试的有限 Dirac 和等题仍按老师 TD 范围保留。</p></section>`+
    `<section class="panel"><h2>直接打开原 PDF</h2><table class="source-table"><thead><tr><th>教师资料</th><th>页数</th></tr></thead><tbody>${Object.entries(M.sources).map(([key,s])=>`<tr><td>${link(key)}</td><td>${s.pages}</td></tr>`).join('')}</tbody></table><p class="source-note">原文件存于同一 GitHub 仓库的 origin/，点击时才加载。${link('programme',1,'以最新官方考纲为范围依据')}</p></section>`}
  function parseRoute(){const id=location.hash.slice(1)||'home';if(/^c[1-8]-\d{2}$/.test(id))return{kind:'chapter',chapter:chapterOf(id),target:id};if(/^ch[1-8]$/.test(id))return{kind:'chapter',chapter:Number(id.slice(2))};if(/^p\d{2}$/.test(id)&&M.proofs.some(p=>p.id===id))return{kind:'proof',target:id};if(['home','basics','proofs','pitfalls','td','sources'].includes(id))return{kind:id};return{kind:'home'}}
  async function render(preserve=false){const ticket=++serial;
    const anchor=preserve?[...main.querySelectorAll('.card')].find(e=>e.getBoundingClientRect().bottom>110):null;
    const position=anchor?{id:anchor.id,top:anchor.getBoundingClientRect().top}:null;
    current=parseRoute();updateNav();main.setAttribute('aria-busy','true');
    try{let html;
      if(current.kind==='chapter'){
        const c=chapter(current.chapter),data=await get(c.data);if(ticket!==serial)return;
        html=heading('CHAPITRE '+String(c.id).padStart(2,'0')+' / '+c.count+' ÉNONCÉS',mode==='fr'?c.fr:c.title,c.subtitle)+
          `<span class="badge">知识问答</span>${c.statements_only?'<span class="badge only">仅定义与结论</span>':'<span class="badge">理解与应用</span>'}`+guide('i'+c.id)+
          `<section class="panel"><h2>本章条目</h2><ol class="toc">${data.cards.map(item=>`<li><a href="#${item.id}">${esc(mode==='fr'?item.title_fr:item.title)}</a></li>`).join('')}</ol></section>`+data.cards.map(card).join('')+
          (c.statements_only?'':tdAdvice(c.id))+
          `<div class="nav-next"><a href="${c.id===1?'#basics':'#ch'+(c.id-1)}">← 上一步</a><a href="${c.id===8?'#pitfalls':'#ch'+(c.id+1)}">${c.id===8?'回看条件与易错点':'继续第 '+(c.id+1)+' 章'} →</a></div>`;
      }else if(current.kind==='proof'){
        const metadata=M.proofs.find(p=>p.id===current.target),p=await get(metadata.data);if(ticket!==serial)return;
        html=heading('PREUVE '+String(p.number).padStart(2,'0')+' / 15',p.title,'先回到对应知识条目确认条件，再逐步看每一步的依据。')+
          `<section class="panel"><h2>先读这些知识</h2><div class="refs">${p.requires.map(id=>`<a href="#${id}">${id}</a>`).join('')}</div><p class="source-note" style="margin-top:12px">对应结论：<a href="#${p.card}">${p.card}</a> · ${link('preuves',p.originals[0].page,'官方证明')}</p></section>`+card(p)+
          `<div class="nav-next"><a href="#proofs">← 15 证明目录</a>${p.number<15?`<a href="#p${String(p.number+1).padStart(2,'0')}">下一证明 →</a>`:'<a href="#pitfalls">回看关键条件 →</a>'}</div>`;
      }else if(current.kind==='home')html=home();
      else if(current.kind==='basics')html=heading('COMMENCER','起步：符号与对象','不假设你已经学过测度论。先用这页把后面会反复出现的概念辨认出来。')+guide('basics')+'<a href="#ch1">进入第 1 章 →</a>';
      else if(current.kind==='proofs')html=proofList();
      else if(current.kind==='pitfalls')html=heading('HYPOTHÈSES','条件与易错点','复习时先问条件满足了没有，再写结论。')+guide('pitfalls');
      else if(current.kind==='td')html=heading('APRÈS LE COURS','知识之后的练习建议','只覆盖 TD1–TD4 的前两部分，先读知识再使用官方题解。')+tdAdvice();
      else html=sources();
      if(ticket!==serial)return;main.innerHTML=html;
      document.title=(current.kind==='chapter'?chapter(current.chapter).title:current.kind==='proof'?M.proofs.find(p=>p.id===current.target).title:'测量理论')+' · DS 知识复习';
      if(position){const e=document.getElementById(position.id);if(e)window.scrollBy(0,e.getBoundingClientRect().top-position.top)}
      else if(current.target)document.getElementById(current.target)?.scrollIntoView();else if(!preserve)window.scrollTo(0,0);
    }catch(e){if(ticket===serial)main.innerHTML=`<div class="error"><p>内容暂时未能加载。${esc(e.message)}</p><p>本地文件请用 HTTP 预览或打开在线入口。</p><button id="retry">重试</button> · <a href="https://n1cola5f.github.io/theorie-mesure/ds/">在线阅读</a></div>`}
    finally{if(ticket===serial)main.removeAttribute('aria-busy')}
  }
  async function find(){const query=search.value.trim();if(!query){render();return}const ticket=++serial;current={kind:'search'};updateNav();
    main.innerHTML=heading('RECHERCHE','查找知识与证明',query)+'<div class="loading">正在查找…</div>';
    const normalize=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
    try{const items=await get(M.search);if(ticket!==serial)return;const terms=normalize(query).split(/\s+/);
      const matches=items.filter(item=>terms.every(t=>normalize(item.title+' '+item.title_fr+' '+item.text).includes(t)));
      main.innerHTML=heading('RECHERCHE','查找知识与证明',matches.length+' 个结果 · '+query)+matches.map(item=>`<a class="result" href="#${item.id}">${esc(item.title)}<small>${item.id} · ${esc(item.title_fr)}</small></a>`).join('')+(matches.length?'':'<p class="empty">没有结果。可试中文概念或不带重音的法语关键词。</p>');
    }catch(e){if(ticket===serial)main.innerHTML='<p>搜索索引未能加载，请重新输入后重试。</p>'}
  }
  document.addEventListener('click',e=>{
    const button=e.target.closest('[data-mode]');if(button){mode=button.dataset.mode;save('mesure-ds-mode',mode);search.value?find():render(true);return}
    const zoom=e.target.closest('[data-zoom]');if(zoom){const dialog=document.getElementById('zoom');document.getElementById('zoom-content').innerHTML=`<img src="${esc(zoom.dataset.zoom)}" alt="${esc(zoom.dataset.alt)}">`;dialog.showModal();return}
    if(e.target.closest('.close-zoom'))document.getElementById('zoom').close();
    if(e.target.closest('#retry'))render();
    if(e.target.closest('a[href^="#"]')){
      search.value='';clearTimeout(searchTimer);closeMobile();
      const hash=e.target.closest('a').getAttribute('href');if(hash===location.hash)render();
    }
  });
  document.addEventListener('change',e=>{if(e.target.matches('[data-read]')){read[e.target.dataset.read]=e.target.checked;save('mesure-ds-read',read);e.target.closest('.card').dataset.read=String(e.target.checked)}});
  search.addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(find,160)});
  window.addEventListener('hashchange',()=>{search.value='';clearTimeout(searchTimer);render()});
  narrow.addEventListener('change',()=>{ /* picture selects the precompiled layout without retypesetting. */ });
  render();
})();
