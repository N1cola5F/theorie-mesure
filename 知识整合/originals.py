"""Display French from source PDF glyphs; never retype course text or formulas."""
from pathlib import Path
import copy,hashlib,json,re,shutil,subprocess
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
import pdfplumber
from pypdf import PdfReader,PdfWriter,PageObject
from pypdf.generic import RectangleObject

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
CACHE=BASE/'build/originals'
HEAD=re.compile(r'^(Définition|Propriété|Proposition|Théorème|Corollaire|Lemme|Remarque|Attention|Exemple|Méthode|Exercice|Rappel de L[123](?:[–-]L[123])?)\s+(\d+\.\d+)\b(?!\s*«)')
SECTION=re.compile(r'^\d+(?:\.\d+)*\s+[A-ZÀÉÈÎÔŒ]')

def source_index(source, config, reuse=True):
    path=ROOT/config['sources'][source]['path']
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    cache=CACHE/(source+'-index.json')
    if reuse and cache.exists():
        data=json.loads(cache.read_text(encoding='utf-8'))
        if data['sha256']==digest and data.get('index_version')==3:return data
    pages=[];heads=[]
    with pdfplumber.open(path) as pdf:
        for number,page in enumerate(pdf.pages,1):
            lines=page.extract_text_lines()
            footer=min([x['top'] for x in lines if x['text'].startswith('ZFAI – L4')]+[page.height-18 if page.width<400 else page.height-40])
            # Handbook and slides have different margins; retain all original drawings.
            left,right=(40,page.width-40) if source=='w4' else (7,page.width-7)
            top=35 if source=='w4' else 4
            bottom=footer-3
            content=[x for x in lines if x['top']>=top-1 and x['bottom']<=bottom+1]
            chars=[{k:x[k] for k in ['x0','x1','top','bottom','text','fontname']}
                   for x in page.chars if x['bottom']<=bottom+1 and x['top']>=top-1]
            # Keep marginal formula glyphs as well as the normal text column.
            left=min([left]+[x['x0']-1 for x in chars])
            right=max([right]+[x['x1']+1 for x in chars])
            emphasis=[]
            # Original coloured theorem boxes identify conditions and conclusions.
            for rect in page.rects:
                color=rect.get('non_stroking_color')
                if isinstance(color,tuple) and len(color)==3 and max(color)-min(color)>.015 and rect['width']>100 and rect['height']>10:
                    emphasis.append([rect['x0'],rect['top'],rect['x1'],rect['bottom']])
            for x in chars:
                if 'BX' in x['fontname'] or 'Bold' in x['fontname']:
                    emphasis.append([x['x0']-1,x['top']-1,x['x1']+1,x['bottom']+1])
            pages.append(dict(page=number,width=page.width,height=page.height,bounds=[left,top,right,bottom],
                              lines=[{k:x[k] for k in ['text','top','bottom']} for x in content],
                              chars=chars,emphasis=emphasis))
            if source=='w4' and number>=4:
                for x in content:
                    m=HEAD.match(x['text'])
                    section=SECTION.match(x['text'])
                    first=min((c for c in x['chars'] if c['text'].strip()),key=lambda c:c['x0'],default={})
                    bold='BX' in first.get('fontname','') or 'Bold' in first.get('fontname','')
                    if (m or section) and bold:
                        heads.append(dict(page=number,top=x['top'],bottom=x['bottom'],text=x['text'],
                                          number=m[2] if m else None,exercise=bool(m and m[1]=='Exercice')))
    # A heading is a boundary even if it is a section or an exercise we never import.
    blocks={}
    for i,h in enumerate(heads):
        if not h['number']:continue
        end=heads[i+1] if i+1<len(heads) else dict(page=len(pages)+1,top=0)
        pieces=[]
        for number in range(h['page'],min(end['page'],len(pages))+1):
            p=pages[number-1];left,top,right,bottom=p['bounds']
            if number==h['page']:top=max(top,h['top']-8)
            if number==end['page']:bottom=min(bottom,end['top']-9)
            if bottom-top>4:
                selected=[x for x in p['chars'] if x['top']>=top-.5 and x['bottom']<=bottom+.5]
                text='\n'.join(x['text'] for x in p['lines'] if x['top']>=top-.5 and x['bottom']<=bottom+.5)
                if selected or text:
                    pieces.append(dict(page=number,clip=[left,round(top,3),right,round(bottom,3)],text=text))
        if h['number'] not in blocks:
            blocks[h['number']]=dict(title=h['text'],exercise=h['exercise'],pieces=pieces)
    data=dict(source=source,sha256=digest,index_version=3,pages=pages,blocks=blocks)
    CACHE.mkdir(parents=True,exist_ok=True);cache.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    return data

def crop_pdf(reader,piece,index,target):
    p=reader.pages[piece['page']-1]
    left,top,right,bottom=piece['clip']
    page=copy.copy(p)
    # pypdf merges the existing content stream inside this crop rectangle.
    page.cropbox=RectangleObject([left,float(p.mediabox.height)-bottom,right,float(p.mediabox.height)-top])
    page.trimbox=page.cropbox
    out=PageObject.create_blank_page(width=right-left,height=bottom-top)
    out.merge_translated_page(page,-left,-(float(p.mediabox.height)-bottom))
    writer=PdfWriter();writer.add_page(out)
    with target.open('wb') as f:writer.write(f)

def validate_clip(piece,index):
    left,top,right,bottom=piece['clip']
    for c in index['pages'][piece['page']-1]['chars']:
        if not c['text'].strip():continue
        if c['x1']>left+.1 and c['x0']<right-.1 and c['bottom']>top+.1 and c['top']<bottom-.1:
            assert c['top']>=top-.1 and c['bottom']<=bottom+.1 and c['x0']>=left-.1 and c['x1']<=right+.1, f"Source glyph crosses clip boundary: {index['source']} p.{piece['page']}"

def emphasise(svg,piece,index):
    root=ET.fromstring(svg.read_text(encoding='utf-8'))
    left,top,_,_=piece['clip']
    regions=index['pages'][piece['page']-1]['emphasis']
    count=0
    for node in root.iter():
        if node.tag.endswith('}use') and node.get('x') and node.get('y'):
            x,y=float(node.get('x'))+left,float(node.get('y'))+top
            if any(a-1<=x<=c+1 and b-2<=y<=d+2 for a,b,c,d in regions):
                node.set('style','fill:#000;stroke:#000;stroke-width:0.14;stroke-linejoin:round;paint-order:stroke fill')
                count+=1
    svg.write_text(ET.tostring(root,encoding='unicode'),encoding='utf-8')
    return count

def build_originals(config,cards,reuse):
    mapping=json.loads((BASE/'french/originals.json').read_text(encoding='utf-8'))
    assert set(mapping['cards'])=={c['id'] for c in cards},'French mapping must cover every card'
    sources={spec['source'] for group in mapping['cards'].values() for spec in group['extracts']}
    indices={s:source_index(s,config,reuse) for s in sources}
    readers={s:PdfReader(ROOT/config['sources'][s]['path']) for s in sources}
    data={};files={};jobs={};records=[]
    for card in cards:
        spec=mapping['cards'][card['id']];extracts=[]
        for item in spec['extracts']:
            source=item['source'];idx=indices[source]
            if 'block' in item:
                block=idx['blocks'].get(item['block'])
                assert block and not block['exercise'],f"Missing lecture block: {card['id']} {item}"
                pieces=block['pieces'];title=block['title']
            else:
                title=item.get('title',config['sources'][source]['label'])
                pieces=[]
                for number in item['pages']:
                    p=idx['pages'][number-1]
                    pieces.append(dict(page=number,clip=p['bounds'],text='\n'.join(x['text'] for x in p['lines'])))
            assert pieces,f"Empty original: {card['id']} {item}"
            fragments=[]
            for piece in pieces:
                key='fr-'+hashlib.sha256(json.dumps([source,idx['sha256'],piece['page'],piece['clip'],'bold-v1']).encode()).hexdigest()[:18]
                fragments.append(dict(key=key,page=piece['page'],text=piece['text']))
                if key not in jobs:
                    validate_clip(piece,idx);jobs[key]=(source,piece)
                records.append(dict(card=card['id'],source=source,page=piece['page'],clip=piece['clip'],key=key))
            extracts.append(dict(source=source,title=title,fragments=fragments))
        data[card['id']]=dict(extracts=extracts,note=spec.get('note',''))
    # Write PDFs sequentially: shared PDF readers are not used concurrently.
    pending=[]
    for key,(source,piece) in jobs.items():
        pdf=CACHE/(key+'.pdf');svg=CACHE/(key+'.svg')
        if not(reuse and svg.exists()):
            crop_pdf(readers[source],piece,indices[source],pdf);pending.append((key,source,piece))
        files[key]=svg
    def svg_convert(job):
        key,source,piece=job;svg=files[key]
        r=subprocess.run([shutil.which('pdftocairo'),'-svg',str(CACHE/(key+'.pdf')),str(svg)],capture_output=True)
        if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace'))
        emphasise(svg,piece,indices[source])
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(svg_convert,pending))
    report=dict(method='Original PDF vector content clipped, with black stroke emphasis; no OCR or retranscription.',
                mapped_cards=len(data),unique_fragments=len(jobs),source_sha256={s:indices[s]['sha256'] for s in sources},
                excerpt_locations=records,excluded_exercise_blocks=True,glyph_boundary_check='passed')
    (BASE/'french/原文构建记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data,files

if __name__=='__main__':
    config=json.loads((BASE/'course.json').read_text(encoding='utf-8'))
    index=source_index('w4',config)
    print('\n'.join(f"{k} | p.{v['pieces'][0]['page'] if v['pieces'] else '?'} | {v['title']}" for k,v in index['blocks'].items() if not v['exercise']))
