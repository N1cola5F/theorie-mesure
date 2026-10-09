"""HTML shell and semantic navigation; course prose is rendered by XeLaTeX."""
import base64,html,json
import xml.etree.ElementTree as ET
def esc(value):return html.escape(str(value),quote=True)
LABELS={'definition':'定义','theorem':'定理','proposition':'性质','example':'例题','warning':'辨析','exercise':'习题'}
FR_LABELS={'definition':'Définition','theorem':'Théorème','proposition':'Propriété','example':'Exemple','warning':'Attention','exercise':'Exercice'}
def bi(zh,fr):
    return f'<span class="lang-zh">{esc(zh)}</span><span class="lang-fr" lang="fr">{esc(fr)}</span>'

def render_book(base,config,cards,vectors,bank,font_root,originals,lazy=False,web_dir=None):
    index={c['id']:c for c in cards}
    payloads={ch['id']:{'ids':[],'templates':{},'contents':{}} for ch in config['chapters']}
    assets={};glyphs={}
    if lazy:
        root=ET.fromstring(bank)
        glyphs={node.get('id'):ET.tostring(node,encoding='unicode') for node in root[0]}
    def remember(c,key,content):
        payloads[c['chapter']]['contents'][key]=content
        return f'<div class="lazy-detail" data-content="{esc(key)}"></div>'
    symbols={};original_boxes={}
    for group in originals.values():
        for extract in group['extracts']:
            for fragment in extract['fragments']:
                key=fragment['key']
                if key not in symbols:
                    node=ET.fromstring(vectors[key]);node.tag='{http://www.w3.org/2000/svg}symbol'
                    original_boxes[key]=node.get('viewBox')
                    node.set('id',key)
                    for attr in ['class','aria-hidden','focusable']:node.attrib.pop(attr,None)
                    symbols[key]=ET.tostring(node,encoding='unicode')
    if lazy:
        for key,xml in vectors.items():
            markup=symbols[key] if key in symbols else xml
            node=ET.fromstring(markup)
            refs={value[1:] for item in node.iter() for name,value in item.attrib.items() if name.endswith('href') and value.startswith('#') and value[1:] in glyphs}
            assets[key]={'kind':'symbol' if key in symbols else 'svg','markup':markup,'glyphs':sorted(refs),'viewBox':node.get('viewBox')}
        bank='<svg class="glyph-bank" lang="zxx" aria-hidden="true"><defs id="live-glyphs"></defs><defs id="live-originals"></defs></svg>'
    else:
        bank+='<svg class="glyph-bank" aria-hidden="true"><defs>'+''.join(symbols.values())+'</defs></svg>'
    def original_view(c):
        group=originals[c['id']];parts=[]
        for n,extract in enumerate(group['extracts']):
            source=config['sources'][extract['source']]
            figures=[]
            for fragment in extract['fragments']:
                link=f'{source["path"]}#page={fragment["page"]}'
                visual=(f'<div class="lazy-asset lazy-original" data-asset="{fragment["key"]}" data-label="{esc(extract["title"])}"></div>' if lazy else f'<svg class="original-svg" viewBox="{original_boxes[fragment["key"]]}" role="img" aria-label="{esc(extract["title"])}"><use href="#{fragment["key"]}"/></svg>')
                figures.append(f'<figure class="original-excerpt"><figcaption><a href="{esc(link)}" target="_blank" rel="noopener">{esc(source.get("fr_label",source["label"]))} · p. {fragment["page"]} ↗</a></figcaption>{visual}<span class="sr-only" lang="fr">{esc(fragment["text"])}</span></figure>')
            content=''.join(figures)
            if n==0:parts.append(content)
            elif lazy:
                deferred=remember(c,f'{c["id"]}:extra-{n}',content)
                parts.append(f'<details class="source-extra" data-state="extra-{n}"><summary>{esc(extract["title"])}</summary>{deferred}</details>')
            else:parts.append(f'<details class="source-extra"><summary>{esc(extract["title"])}</summary>{content}</details>')
        note=group['note']
        return (f'<p class="original-note">{bi(note["zh"],note["fr"])}</p>' if note else '')+''.join(parts)
    def source_link(ref):
        source,start,end=ref;s=config['sources'][source];pages=str(start) if start==end else f'{start}–{end}'
        return f'<a href="{esc(s["path"])}#page={start}" target="_blank" rel="noopener">{bi(s["label"],s.get("fr_label",s["label"]))} · p. {pages}</a>'
    def texblock(c,part):
        if lazy:
            return f'<div class="compiled lazy-asset" data-asset="{c["id"]}-{part}-wide" data-narrow="{c["id"]}-{part}-narrow"></div><span class="sr-only">{esc(c[part])}</span>'
        return (f'<div class="compiled wide">{vectors[c["id"]+"-"+part+"-wide"]}</div>'
                f'<div class="compiled narrow">{vectors[c["id"]+"-"+part+"-narrow"]}</div>'
                f'<span class="sr-only">{esc(c[part])}</span>')
    def card(c):
        proof=f'<details class="proof"><summary>证明与依据 <span>Preuve</span></summary>{texblock(c,"proof")}</details>' if c['proof'] else ''
        if lazy and c['proof']:
            proof=f'<details class="proof" data-state="proof"><summary>证明与依据 <span>Preuve</span></summary>{remember(c,c["id"]+":proof",texblock(c,"proof"))}</details>'
        zh=texblock(c,'body')+proof;fr=original_view(c)
        if lazy:
            payloads[c['chapter']]['contents'][c['id']+':zh']=zh
            payloads[c['chapter']]['contents'][c['id']+':fr']=fr
            zh=fr=''
        source=f'<pre tabindex="0">{esc(c["body"]+chr(10)+c["proof"])}</pre>'
        if lazy:source=remember(c,c['id']+':source',source)
        deps=''.join(f'<a class="dep-link" href="#{d}">{bi(index[d]["title"],index[d]["fr"])}</a>' for d in c['requires'])
        return (f'<article class="card {c["type"]}" id="{c["id"]}" data-type="{c["type"]}" data-chapter="{c["chapter"]}">'
                f'<div class="card-kicker">{bi(LABELS[c["type"]],FR_LABELS[c["type"]])} <span class="lang-zh">{esc(c["fr"])}</span><a class="anchor" href="#{c["id"]}" aria-label="定位到{esc(c["title"])}">#</a></div>'
                f'<h3>{bi(c["title"],originals[c["id"]]["extracts"][0]["title"])}</h3>'
                f'<div class="reading-columns"><div class="zh-reading" lang="zh-CN" data-pane="{c["id"]}:zh"><div class="reading-label">中文整合</div>{zh}</div><div class="fr-reading" lang="fr" data-pane="{c["id"]}:fr"><div class="reading-label">Français · Texte original</div>{fr}</div></div>'
                f'<div class="card-meta"><div class="sources">{"".join(source_link(r) for r in c["refs"])}</div>'
                +(f'<div class="dependencies"><span>{bi("依赖","Prérequis")}</span>{deps}</div>' if deps else '')
                +f'<details class="tex-source" data-state="source"><summary>LaTeX 源文</summary>{source}</details></div></article>')
    nav=''.join(f'<a class="nav-link" href="#{c["id"]}"><b>{c["number"]}</b><span>{bi(c["title"],c["fr"])}<small class="lang-zh">{esc(c["fr"])}</small></span><em>{bi(c["week"],c["week"].replace("手册","manuel"))}</em></a>' for c in config['chapters'])
    chapters=[]
    for ch in config['chapters']:
        selected=[c for c in cards if c['chapter']==ch['id']]
        rendered={c['id']:card(c) for c in selected}
        if lazy:
            payloads[ch['id']]['ids']=list(rendered)
            payloads[ch['id']]['templates']=rendered
        chapters.append(f'<section class="chapter" id="{ch["id"]}" hidden><header class="chapter-head"><div class="eyebrow">{bi(ch["week"],ch["week"].replace("手册","manuel"))} / THÈME {ch["number"]}</div><h1>{bi(ch["title"],ch["fr"])}</h1><p class="chapter-fr lang-zh">{esc(ch["fr"])}</p><p class="chapter-intro lang-zh">{esc(ch["intro"])}</p><p class="chapter-intro lang-fr" lang="fr">Extraits originaux du cours, avec leurs pages sources. Les encadrés et mots-clés sont mis en noir et en gras pour la lecture.</p></header><div class="cards">{"" if lazy else "".join(rendered.values())}</div></section>')
    tiles=''.join(f'<a class="chapter-tile {c["color"]}" href="#{c["id"]}"><span class="tile-number">{c["number"]}</span><div><h3>{bi(c["title"],c["fr"])}</h3><p class="lang-zh">{esc(c["fr"])}</p><small>{bi(c["week"],c["week"].replace("手册","manuel"))} · {sum(x["chapter"]==c["id"] for x in cards)} {bi("个知识条目","notions")}</small></div><span aria-hidden="true">↗</span></a>' for c in config['chapters'])
    roadmap=''.join(f'<li><span>{n}</span><div>{esc(zh)}<small>{esc(fr)}</small></div><em>待后续更新</em></li>' for n,zh,fr in config['roadmap'])
    roadmap_section=(f'<div class="section-label"><h2>本学期的后续章节</h2><span>Programme du semestre</span></div><p class="muted roadmap-note">后续章节仅列计划，暂不纳入本版知识正文。</p><ol class="roadmap">{roadmap}</ol>' if roadmap else
                     f'<div class="section-label"><h2>{bi("资料覆盖与授课进度","Périmètre des notes")}</h2><span>Programme du semestre</span></div><p class="muted roadmap-note">{bi(config.get("scope_note","课程手册的全部主题已建立，后续按新资料持续补充修订。"),"Les 13 thèmes du manuel sont disponibles. Le CM04 porte sur les intégrales multiples ; la disponibilité du manuel ne représente pas l’avancement des cours.")}</p>')
    rows=''.join(f'<tr><td>{bi(s["kind"],s.get("fr_kind",s["kind"]))}</td><td><a href="{esc(s["path"])}" target="_blank" rel="noopener">{bi(s["label"],s.get("fr_label",s["label"]))}</a></td><td>{s["pages"]} {bi("页","pages")}</td></tr>' for s in config['sources'].values())
    overview=f'''<section class="chapter overview" id="overview"><header class="chapter-head overview-head">
<div class="eyebrow">MA 7002 / 7003 · {esc(config['semester'])}</div>
<h1><span class="heading-primary">{bi("测量理论","Théorie de la mesure")}</span><span class="heading-subtitle">{bi("知识整合","Notes de cours")}</span></h1><p class="chapter-fr lang-zh">Théorie de la mesure · Notes de cours</p>
<p class="chapter-intro">{bi(config.get('overview_intro','从集合的长度，到可测函数与 Lebesgue 积分。沿着定义、定理与证明，逐章建立本学期的知识结构。'),"Mesure, intégration, variables aléatoires et théorèmes limites : un parcours de lecture par définitions, résultats et preuves.")}</p>
<div class="edition"><span class="live-dot"></span>{bi("已整合","Sources")} {bi(config['coverage'],config.get('coverage_fr',config['coverage']))} <i></i> v{config['version']} <i></i> {bi("更新于","Mise à jour")} {config['updated']}</div></header>
<div class="reading-guide">{bi("顶部一键选择中文、Français 或中法对照。法语正文为原 PDF 的矢量摘录，保留措辞、公式和编号；重点加黑加粗。","Choisissez 中文, Français ou Comparer en haut. Le texte français provient directement des PDF : formulation, formules et numérotation conservées, avec mise en noir et en gras des points essentiels.")}</div>
<div class="section-label"><h2>{bi("从这里开始","Commencer ici")}</h2><span>Parcours de lecture</span></div><div class="chapter-tiles">{tiles}</div>
<div class="guide-row"><div><span class="guide-num">01</span><h3>{bi("先确认条件","Vérifier les hypothèses")}</h3><p>{bi("区分外测度与测度、有限与 σ-有限，并留意可数性和可测性。","Distinguez mesure extérieure et mesure, finitude et σ-finitude ; vérifiez dénombrabilité et mesurabilité.")}</p></div><div><span class="guide-num">02</span><h3>{bi("顺着依据读证明","Suivre les preuves")}</h3><p>{bi("展开证明查看推理，点击“依赖”回到前置知识，点击页码核对原讲义。","Dépliez les preuves et extraits complémentaires ; les prérequis et pages sources permettent de revenir aux textes.")}</p></div><div><span class="guide-num">03</span><h3>{bi("对照原文巩固","Comparer les deux lectures")}</h3><p>{bi("切换语言保留当前条目位置；对照模式同时显示中文整理与法语原文。","Le changement de langue conserve la notion en cours ; la comparaison affiche les notes chinoises et le texte français original.")}</p></div></div>
{roadmap_section}
<footer class="chapter-foot"><span>{bi(config['coverage'],config.get('coverage_fr',config['coverage']))} · {len(cards)} {bi("个条目","notions")}</span><span>Mesure → Intégration → Probabilités</span></footer></section>'''
    resources=f'''<section class="chapter resources" id="resources" hidden><header class="chapter-head"><div class="eyebrow">SOURCES & ÉDITIONS</div><h1>{bi("资料与版本","Sources et éditions")}</h1><p class="chapter-fr">Revenir aux sources</p></header>
<div class="resource-box"><h2>{bi("本版依据","Textes sources")}</h2><p>{bi("页码使用 PDF 的实际页序。中文为知识整合稿；法语直接展示原 PDF 内容，并保留原有措辞与公式。","Les pages indiquées correspondent aux pages PDF. Le français affiche le contenu vectoriel original ; le chinois est une synthèse de travail.")}</p><table><thead><tr><th>{bi("类别","Type")}</th><th>{bi("资料","Document")}</th><th>{bi("篇幅","Longueur")}</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="resource-box"><h2>v{config['version']} · {config['updated']}</h2><ul class="lang-zh">{''.join('<li>'+esc(n)+'</li>' for n in config['release_notes'])}</ul><ul class="lang-fr">{''.join('<li>'+esc(n)+'</li>' for n in config.get('release_notes_fr',[]))}</ul><p class="lang-zh">W2 文件夹中的 CM1 英文讲义仍是第一章内容，不视为 CM2 英文版。</p><div class="resource-links"><a href="CHANGELOG.md">{bi("完整更新记录","Historique complet")} ↗</a><a href="知识整合/README.md">{bi("维护说明","Maintenance")} ↗</a></div></div>
<div class="resource-box"><h2>{bi("阅读与排版","Lecture et typographie")}</h2><p>{bi("中文正文与公式共用 XeLaTeX 配置；法语使用原 PDF 已编译的矢量字形，公式、文字、编号与原文件一致。加黑加粗只改变强调方式。页面离线可读，原始 PDF 链接需要保留仓库目录。","La version chinoise est compilée avec XeLaTeX. La version française réutilise les glyphes vectoriels des PDF, sans retranscrire le texte ni les formules ; seule leur mise en évidence change. La page se lit hors ligne.")}</p><p>{bi("中文、法语和对照模式分别检索相应正文。切换保留当前位置与展开状态；语言选择会在浏览器中保存。打印输出当前语言的内容。","La recherche suit la langue choisie. La comparaison permet de lire les deux colonnes ; position, extraits dépliés et préférence de langue sont conservés. L’impression suit le mode choisi.")}</p></div></section>'''
    if lazy:
        resources=resources.replace('</section>',f'<div class="resource-box"><h2>{bi("保留的旧版","Version précédente")}</h2><p><a href="测量理论_知识整合_v1.5.0_备份.html">{bi("打开 v1.5.0 完整备份","Ouvrir la copie complète v1.5.0")} ↗</a></p></div></section>')
    data=[{'id':c['id'],'chapter':c['chapter'],'type':c['type'],'title':c['title'],'fr':c['fr'],'original_title':originals[c['id']]['extracts'][0]['title'],'text':c['title']+' '+c['fr']+' '+c['body']+' '+c['proof'],
           'fr_text':c['fr']+' '+' '.join(e['title']+' '+' '.join(f['text'] for f in e['fragments']) for e in originals[c['id']]['extracts'])} for c in cards]
    if web_dir:
        from web_export import export_resources
        web=export_resources(base,web_dir,config,payloads,assets,glyphs,data,font_root)
    script=(base/('assets/lazy.js' if lazy else 'assets/app.js')).read_text(encoding='utf-8');css=(base/'assets/style.css').read_text(encoding='utf-8')
    if lazy:css+='\n'+(base/'assets/lazy.css').read_text(encoding='utf-8')
    def json_tag(identifier,value):
        return f'<script id="{identifier}" type="application/json">{json.dumps(value,ensure_ascii=False,separators=(",",":")).replace("<",chr(92)+"u003c")}</script>'
    deferred=(json_tag('glyph-data',glyphs)+''.join(json_tag('asset-data-'+key,value) for key,value in assets.items())+''.join(json_tag('chapter-data-'+key,value) for key,value in payloads.items())) if lazy and not web_dir else ''
    font_css='/* Embedded unmodified Latin Modern fonts.\n'+(base/'assets/GUST-FONT-LICENSE.TXT').read_text(encoding='utf-8').replace('*/','* /')+'\n*/'
    for style,file in [('normal','lmroman10-regular.otf'),('italic','lmroman10-italic.otf')]:
        font=base64.b64encode((font_root/'lm'/file).read_bytes()).decode()
        font_css+=f"@font-face{{font-family:StudyLatin;font-style:{style};font-weight:400;src:url(data:font/otf;base64,{font}) format('opentype');font-display:swap}}"
    head_styles=(f'<link rel="stylesheet" href="{web["style"]}">' if web_dir else f'<style>{font_css}{css}</style>')
    scripts=(json_tag('reader-config',web['boot'])+f'<script defer src="{web["script"]}"></script>' if web_dir else json_tag('search-index',data)+deferred+'<script>'+script+'</script>')
    if web_dir:
        repository_url='https://github.com/'+config['hosting']['repository']
        resources=resources.replace('页面离线可读，原始 PDF 链接需要保留仓库目录。','网页按需读取仓库中的章节与矢量片段，原始资料位于 origin 目录。').replace('La page se lit hors ligne.','Les chapitres et extraits sont chargés depuis le dépôt.')
        resources=resources.replace('<table>','<table id="source-catalog">',1)
        resources=resources.replace('测量理论_知识整合_v1.5.0_备份.html',repository_url+'/tree/main/reader-source/历史记录')
        resources=resources.replace('打开 v1.5.0 完整备份','查看历史版本记录').replace('Ouvrir la copie complète v1.5.0','Consulter les éditions précédentes')
        resources=resources.replace('href="CHANGELOG.md"','href="'+repository_url+'/blob/main/reader-source/CHANGELOG.md"').replace('href="知识整合/README.md"','href="'+repository_url+'/blob/main/知识整合/README.md"')
        noscript='本版需要 JavaScript 加载章节，可点击“资料与版本”中的 PDF 链接阅读原始讲义。'
    else:
        noscript='本版需要 JavaScript 加载章节；可打开 <a href="测量理论_知识整合_v1.5.0_备份.html">v1.5.0 完整备份</a>阅读。' if lazy else 'JavaScript 未启用：全部正文仍可阅读，搜索和章节切换不可用。'
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><link rel="icon" href="data:,"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="测量理论知识整合，中文 XeLaTeX 与法语原 PDF 矢量对照。"><title>测量理论 · 知识整合{' · 在线阅读' if web_dir else ' · 按需加载' if lazy else ''}</title>{head_styles}</head><body data-lang="zh"{' data-delivery="web"' if web_dir else ' data-delivery="lazy"' if lazy else ''}>{'' if web_dir else bank}<a class="skip-link" href="#main">{bi("跳到正文","Aller au contenu")}</a>
<header class="topbar"><button id="menu" class="icon-button" aria-label="切换章节目录" aria-expanded="true" aria-controls="sidebar">☰</button><a class="brand" href="#overview"><span class="brand-symbol">μ</span>{bi("测量理论","Mesure")} <em>Théorie de la mesure</em></a><div class="tools"><div class="language-switch" role="group" aria-label="阅读语言 / Langue"><button type="button" data-reading-mode="zh" aria-pressed="true" title="中文整合">中文</button><button type="button" data-reading-mode="fr" aria-pressed="false" title="Français · Texte original">Français</button><button type="button" data-reading-mode="compare" aria-pressed="false" title="中法对照 / Comparaison">对照</button></div><label class="searchbox"><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="搜索中文、法语或 LaTeX…" aria-label="搜索全部知识正文" autocomplete="off"><kbd>/</kbd></label><button id="print">{bi("打印提纲","Imprimer")}</button></div></header>
<button class="scrim" id="scrim" aria-label="关闭章节目录" hidden></button><aside id="sidebar" class="sidebar"><div class="sidebar-label">SOMMAIRE <span class="lang-zh">目录</span></div><nav aria-label="章节目录"><a class="nav-link" href="#overview"><b>§</b><span>{bi("学期概览","Vue d’ensemble")}<small class="lang-zh">Vue d’ensemble</small></span></a>{nav}<a class="nav-link" href="#resources"><b>↗</b><span>{bi("资料与版本","Sources & éditions")}<small class="lang-zh">Sources & éditions</small></span></a></nav><div class="sidebar-bottom"><div class="legend">{''.join(f'<span class="{kind}">{bi(LABELS[kind],FR_LABELS[kind])}</span>' for kind in ['definition','theorem','proposition','example','warning'])}</div><p>v{config['version']}<br>{config['updated']} · {bi(config['coverage'],config.get('coverage_fr',config['coverage']))}</p></div></aside>
<main id="main" class="main" tabindex="-1">{'<div id="reader-loading" class="reader-notice" role="status" hidden></div><div id="reader-error" class="reader-notice reader-error" role="alert" hidden><p></p><button id="reader-retry">重试 / Réessayer</button></div>' if web_dir else ''}<div id="search-status" class="search-status" role="status" hidden></div><div id="search-empty" class="empty-state" hidden><h2>{bi("没有找到匹配内容","Aucun résultat")}</h2><p>{bi("试试“可测”“continuité”或公式中的 LaTeX 命令。","Essayez « mesurable », « continuité » ou « intégrable ».")}</p><button id="reset-search">{bi("清除搜索","Effacer")}</button></div>{'<section id="search-results" class="chapter search-results" hidden></section>' if lazy else ''}{overview}{''.join(chapters)}{resources}</main>
<noscript><style>.topbar .tools{{display:none}}{'.resources[hidden]{display:block!important}' if web_dir else ''}</style><p class="noscript-note">{noscript}</p></noscript>
{scripts}</body></html>'''


