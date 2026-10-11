"""Build an independent, knowledge-first DS book; never rebuild the semester reader."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,copy,hashlib,importlib.util,json,os,re,shutil,sys
import xml.etree.ElementTree as ET
import pdfplumber
from pypdf import PdfReader

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=BASE/'build'
SITE=ROOT/'site/ds'
sys.path.insert(0,str(ROOT/'知识整合'))
from originals import crop_pdf,validate_clip,emphasise
from render import render_book  # Resolve the existing typesetter's imports.

def existing_typesetter():
    spec=importlib.util.spec_from_file_location('semester_typesetter',ROOT/'知识整合/build.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.BUILD=BUILD
    return module

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write_json(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def load_notes(filename):
    text=(BASE/'content'/filename).read_text(encoding='utf-8')
    assert '\x00' not in text,'Invalid NUL in TeX source'
    matches=list(re.finditer(r'^% @note ([a-z0-9-]+)\|([^\r\n]+)\n(.*?)^% @end\s*$',text,re.M|re.S))
    assert len(matches)==len(re.findall(r'^% @note ',text,re.M)),filename+' has an unclosed note'
    return [{'id':m[1],'title':m[2],'body':m[3].strip(),'proof':''} for m in matches]

def index_pdf(source,config,reuse):
    path=ROOT/config['sources'][source]['path'];sha=digest(path)
    cache=BUILD/(source+'-index.json')
    if reuse and cache.exists():
        result=json.loads(cache.read_text(encoding='utf-8'))
        if result['sha256']==sha and result.get('schema')==1:return result
    pages=[];boundaries=[];chapter=None;ordinal={}
    with pdfplumber.open(path) as pdf:
        for n,page in enumerate(pdf.pages,1):
            lines=page.extract_text_lines()
            footer=min([line['top'] for line in lines if re.fullmatch(r'\d+',line['text'].strip()) and line['top']>page.height*.9]+[page.height-25])
            top,bottom=35,footer-3
            chars=[{k:c[k] for k in ['x0','x1','top','bottom','text','fontname']} for c in page.chars if c['top']>=top and c['bottom']<=bottom]
            left=min([40]+[c['x0']-1 for c in chars]);right=max([page.width-40]+[c['x1']+1 for c in chars])
            emphasis=[[c['x0']-1,c['top']-1,c['x1']+1,c['bottom']+1] for c in chars if 'Bold' in c['fontname'] or 'BX' in c['fontname']]
            content=[{k:l[k] for k in ['text','top','bottom']} for l in lines if l['top']>=top and l['bottom']<=bottom]
            pages.append(dict(page=n,width=page.width,height=page.height,bounds=[left,top,right,bottom],chars=chars,lines=content,emphasis=emphasis))
            if n==1:continue # Cover, scope and table of contents are linked, not treated as statements.
            for line in content:
                text=line['text'];card=None
                if source=='programme':
                    cm=re.match(r'^1\.(\d)\s+Chapitre',text)
                    if cm:chapter=int(cm[1])
                    is_section=bool(cm or re.match(r'^[12]\s+(Définitions|Liste)',text))
                    heading=re.match(r'^(Définition|Propriété|Théorème|Corollaire|Lemme)\s*[–—-]',text)
                    if heading:
                        assert chapter in range(1,9)
                        ordinal[chapter]=ordinal.get(chapter,0)+1;card=f'c{chapter}-{ordinal[chapter]:02}'
                else:
                    pm=re.match(r'^\d+\.\d+\s+(\d+)\.',text)
                    is_section=bool(re.match(r'^\d+\s+Chapitre',text))
                    if pm:card=f'p{int(pm[1]):02}'
                if card or is_section:
                    boundaries.append(dict(page=n,top=line['top'],bottom=line['bottom'],title=text,id=card,chapter=chapter))
    blocks=[]
    for i,head in enumerate(boundaries):
        if not head['id']:continue
        end=boundaries[i+1] if i+1<len(boundaries) else dict(page=len(pages)+1,top=0)
        pieces=[]
        for n in range(head['page'],min(end['page'],len(pages))+1):
            page=pages[n-1];left,top,right,bottom=page['bounds']
            if n==head['page']:top=max(top,head['top']-2)
            if n==end['page']:bottom=min(bottom,end['top']-3)
            selected=[c for c in page['chars'] if c['top']>=top-.1 and c['bottom']<=bottom+.1]
            if bottom>top and selected:
                text='\n'.join(l['text'] for l in page['lines'] if l['top']>=top-.1 and l['bottom']<=bottom+.1)
                piece=dict(page=n,clip=[left,round(top,3),right,round(bottom,3)],text=text)
                validate_clip(piece,dict(source=source,pages=pages));pieces.append(piece)
        assert pieces,'Empty official block '+head['id']
        blocks.append({**head,'pieces':pieces})
    result=dict(source=source,sha256=sha,schema=1,pages=pages,blocks=blocks)
    write_json(cache,result);return result

def make_originals(indices,config,reuse):
    out=BUILD/'originals';out.mkdir(exist_ok=True);files={};cards={};jobs=[]
    readers={s:PdfReader(ROOT/config['sources'][s]['path']) for s in indices}
    for source,index in indices.items():
        for block in index['blocks']:
            fragments=[]
            for piece in block['pieces']:
                key='fr-'+hashlib.sha256(json.dumps([source,index['sha256'],piece['page'],piece['clip'],'bold-v1']).encode()).hexdigest()[:20]
                target=out/(key+'.svg');files[key]=target
                if not(reuse and target.exists()):
                    crop_pdf(readers[source],piece,index,out/(key+'.pdf'));jobs.append((source,piece,key))
                fragments.append(dict(key=key,page=piece['page']))
            cards[block['id']]={'title_fr':block['title'],'source':source,'originals':fragments,'original_text':'\n'.join(p['text'] for p in block['pieces'])}
    def convert(job):
        source,piece,key=job;target=files[key]
        existing.run([shutil.which('pdftocairo'),'-svg',str(out/(key+'.pdf')),str(target)])
        emphasise(target,piece,indices[source])
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(convert,jobs))
    return cards,files

def export_asset(path,folder):
    content=path.read_bytes()
    # Git normalises generated text to LF. Hash those exact published bytes too.
    if path.suffix in {'.svg','.json','.css','.js'}:
        content=content.replace(b'\r\n',b'\n')
    hash_=hashlib.sha256(content).hexdigest()[:18]
    target=SITE/folder/(hash_+path.suffix);target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():target.write_bytes(content)
    return target.relative_to(SITE).as_posix()

def exercise_advice(config):
    # Actual exercise numbers and headings, with page numbers read from the official correction PDFs.
    selections=[
      (1,'外测度与可测性',[1,2],[('1.1','可数集为什么零测','c1-10'),('1.2','有限覆盖与可数覆盖的区别','c1-06'),('1.5','Lipschitz 映射与零测集','c1-08'),('1.8','连续函数的 Borel 原像','c4-08'),('2.1','用测试集合理解可测判据','c1-11')]),
      (2,'σ-代数与测度',[2,3],[('1.1','有限分割生成的 σ-代数','c2-03'),('1.3','有限并封闭为何不够','c2-01'),('1.4','可列可加与连续性的联系','c3-07'),('1.5','计数测度','c3-01'),('1.9','集合极限与测度','c3-09'),('2.1','在子集上的可测族','c2-01'),('2.3','计数测度的 σ-有限性','c3-01')]),
      (3,'可测函数与积分',[4,5],[('1.1','原像运算','c4-01'),('1.2','单调函数可测','c4-07'),('1.4','有限离散测度上的积分','c5-04'),('1.6','简单函数直接积分','c5-04'),('2.1','max 与 min 可测','c4-11'),('2.4','非负级数与离散积分','c5-13'),('2.6','sup、limsup 与点态极限','c4-13')]),
      (4,'多重积分',[6],[('1.1','用截面算单纯形体积','c6-03'),('1.2','用 Tonelli 算圆盘面积','c6-05'),('1.4','乘积函数的积分','c6-05'),('1.5','线性换元与 Jacobian','c6-07'),('1.6','非负级数与积分','c5-13'),('2.3','绝对可积阈值','c6-05'),('2.4','曲线之间的区域','c6-06'),('2.5','选择适合 x+y 的坐标','c6-07')])
    ]
    result=[]
    for td,title,chapters,selected in selections:
        source='corrige'+str(td);path=ROOT/config['sources'][source]['path'];locations={};counts={1:0,2:0};all_heads=[]
        with pdfplumber.open(path) as pdf:
            for n,page in enumerate(pdf.pages,1):
                if n==1:continue
                lines=page.extract_text_lines()
                for line in lines:
                    m=re.match(r'^Exercice ([12]\.\d+)\b',line['text'])
                    if m and m[1] not in locations:
                        locations[m[1]]=n;counts[int(m[1][0])]+=1
                        all_heads.append({'number':m[1],'page':n})
        # TD1's selection is explicit below; fail on a changed exercise number instead of inventing a location.
        exercises=[]
        for number,label,card in selected:
            assert number in locations,f'Unknown TD{td} exercise {number}'
            exercises.append(dict(number=number,title=label,card=card,page=locations[number],part=int(number[0])))
        result.append(dict(number=td,title=title,chapters=chapters,source=source,exercises=exercises,counts=counts,all_exercise_locations=all_heads))
    return result

def main():
    global existing
    parser=argparse.ArgumentParser();parser.add_argument('--reuse',action='store_true');args=parser.parse_args()
    BUILD.mkdir(parents=True,exist_ok=True);SITE.mkdir(parents=True,exist_ok=True)
    config=json.loads((BASE/'exam.json').read_text(encoding='utf-8'))
    notes=load_notes('knowledge.tex');proofs=load_notes('proofs.tex');guides=load_notes('guides.tex')
    assert len(notes)==100 and len(proofs)==15
    assert [p['id'] for p in proofs]==[f'p{n:02}' for n in range(1,16)]
    ids={c['id'] for c in notes}
    for chapter in config['chapters']:
        assert sum(n['id'].startswith('c'+str(chapter['id'])+'-') for n in notes)==chapter['count']
    for p in config['proof_cards']:
        assert p['card'] in ids and all(i in ids for i in p['requires'])
    source_records={}
    for key,source in config['sources'].items():
        path=ROOT/source['path'];pages=len(PdfReader(path).pages)
        if 'pages' in source:assert pages==source['pages'],'Page count changed: '+key
        target=ROOT/'site/origin'/source['path'].removeprefix('origin/');target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists() or digest(target)!=digest(path):shutil.copy2(path,target)
        assert digest(target)==digest(path)
        source_records[key]={**source,'pages':pages,'sha256':digest(path),'href':'../origin/'+source['path'].removeprefix('origin/')}
    indices={s:index_pdf(s,config,args.reuse) for s in ['programme','preuves']}
    assert {b['id'] for b in indices['programme']['blocks']}==ids
    assert {b['id'] for b in indices['preuves']['blocks']}=={p['id'] for p in proofs}
    fontroot=Path(os.environ['LOCALAPPDATA'])/'Programs/MiKTeX/fonts/opentype/public'
    existing=existing_typesetter()
    for n in notes+proofs+guides:
        for char,tex in [('σ',r'\ensuremath{\sigma}'),('μ',r'\ensuremath{\mu}')]:
            n['body']=n['body'].replace(char,tex)
        n['body']=r'\providecommand{\Z}{\mathbb Z}\renewcommand{\textbf}[1]{{\bfseries\color{black}#1}}'+'\n'+n['body']
    fragments,files=existing.typeset(notes+proofs+guides,fontroot,args.reuse)
    originals,fr_files=make_originals(indices,config,args.reuse)
    vector_urls={key:export_asset(path,'vectors') for key,path in {**files,**fr_files}.items()}
    def asset(key):
        svg=ET.parse(({**files,**fr_files})[key]).getroot()
        box=svg.get('viewBox')
        if box:w,h=map(float,box.split()[2:])
        else:w,h=(float(re.sub('[a-z]+','',svg.get(k))) for k in ['width','height'])
        return {'src':vector_urls[key],'width':round(w,3),'height':round(h,3)}
    def compiled(note):
        return {'wide':asset(note['id']+'-body-wide'),'narrow':asset(note['id']+'-body-narrow')}
    proof_numbers={p['card']:p['number'] for p in config['proof_cards']};search=[];chapters=[]
    for chapter in config['chapters']:
        cards=[]
        for note in notes:
            if not note['id'].startswith('c'+str(chapter['id'])+'-'):continue
            original=copy.deepcopy(originals[note['id']]);original['originals']=[{**p,'svg':asset(p['key'])} for p in original['originals']]
            searchable=original.pop('original_text')+'\n'+note['body']
            dependencies=list(dict.fromkeys(re.findall(r'\bc[1-8]-\d{2}\b',note['body'])))
            card={'id':note['id'],'title':note['title'],'compiled':compiled(note),'proof':proof_numbers.get(note['id']),'requires':[d for d in dependencies if d in ids and d!=note['id']],**original}
            cards.append(card);search.append({'id':note['id'],'title':note['title'],'title_fr':original['title_fr'],'chapter':chapter['id'],'text':searchable})
        data={'chapter':chapter['id'],'cards':cards}
        filename=BUILD/f'chapter-{chapter["id"]}.json';write_json(filename,data)
        chapters.append({**chapter,'data':export_asset(filename,'data')})
    proof_metadata=[]
    for note,spec in zip(proofs,config['proof_cards']):
        orig=copy.deepcopy(originals[note['id']]);orig.pop('original_text')
        orig['originals']=[{**p,'svg':asset(p['key'])} for p in orig['originals']]
        data={'id':note['id'],'title':note['title'],'number':spec['number'],'compiled':compiled(note),'requires':spec['requires'],'card':spec['card'],**orig}
        filename=BUILD/(note['id']+'.json');write_json(filename,data)
        proof_metadata.append({k:data[k] for k in ['id','title','number','requires','card']})
        proof_metadata[-1]['data']=export_asset(filename,'data')
        search.append({'id':note['id'],'title':note['title'],'title_fr':orig['title_fr'],'chapter':None,'text':note['body']})
    write_json(BUILD/'search.json',search);search_url=export_asset(BUILD/'search.json','data')
    guide_map={n['id']:{'title':n['title'],'compiled':compiled(n)} for n in guides}
    td=exercise_advice(config)
    write_json(BUILD/'sources.json',{'version':config['version'],'updated':config['updated'],'sources':source_records})
    catalog_url=export_asset(BUILD/'sources.json','data')
    # The older reader keeps its own source catalogue and version unchanged.
    write_json(ROOT/'site/origin/ds-index.json',{'version':config['version'],'sources':source_records})
    font_url=export_asset(fontroot/'lm/lmroman10-regular.otf','fonts')
    css_text=(BASE/'assets/ds.css').read_text(encoding='utf-8').replace('{{FONT}}','../'+font_url)
    (BUILD/'ds.css').write_text(css_text,encoding='utf-8')
    css=export_asset(BUILD/'ds.css','styles');js=export_asset(BASE/'assets/ds.js','scripts')
    manifest={'version':config['version'],'updated':config['updated'],'exam':config['exam'],'chapters':chapters,'proofs':proof_metadata,'guides':guide_map,'search':search_url,'sources':source_records,'catalog':catalog_url,'td':td,'excluded':config['excluded'],'missing_required_files':config['missing_required_files'],'pending_exam_information':config['pending_exam_information']}
    write_json(SITE/'resource-manifest.json',manifest)
    manifest_json=json.dumps(manifest,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    template=(BASE/'assets/index.html').read_text(encoding='utf-8').replace('{{CSS}}',css).replace('{{JS}}',js).replace('{{MANIFEST}}',manifest_json)
    (SITE/'index.html').write_text(template,encoding='utf-8')
    (SITE/'.nojekyll').write_text('',encoding='utf-8')
    # A small separate local launcher; compiled resources stay external.
    (ROOT/'测量理论_DS期中复习.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=site/ds/index.html"><title>DS 期中复习</title><a href="site/ds/index.html">本地入口</a> · <a href="'+config['url']+'">在线阅读</a><p>本地按章节加载需启动 HTTP 预览；可直接使用在线地址。</p></html>',encoding='utf-8')
    report={'version':config['version'],'repository_release':config['repository_release'],'date':config['updated'],'statements':len(notes),'proofs':len(proofs),'intro_guides':len(guides),'compiled_chinese_fragments':len(fragments),'official_vector_fragments':len(fr_files),'runtime_latex':False,'official_method':'PDF vector clips; original wording retained, black emphasis','glyph_boundary_check':'passed','latex_faults':0,'html_bytes':(SITE/'index.html').stat().st_size,'td_parts_1_2':{f'TD{t["number"]}':t['counts'] for t in td},'sources':source_records,'url':config['url']}
    write_json(BASE/'构建记录.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='sources'},ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
