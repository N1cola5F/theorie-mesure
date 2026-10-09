"""Build a self-contained HTML reader with XeLaTeX-compiled prose and formulas."""
from pathlib import Path
import argparse,copy,hashlib,json,os,re,shutil,subprocess
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader,PdfWriter
from render import render_book
from originals import build_originals

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=BASE/'build'
OUTPUT=ROOT/'测量理论_知识整合_按需加载.html'
SVG='http://www.w3.org/2000/svg'
ET.register_namespace('',SVG)
ET.register_namespace('xlink','http://www.w3.org/1999/xlink')

def run(cmd,**kwargs):
    r=subprocess.run(cmd,text=True,encoding='utf-8',errors='replace',capture_output=True,**kwargs)
    if r.returncode:raise RuntimeError(str(cmd)+'\n'+r.stdout[-6000:]+r.stderr[-2000:])
    return r.stdout

def load_cards(config):
    text=(ROOT/'output/source/TD02_前五题/TD02_前五题_原题与逐步解答.md').read_text(encoding='utf-8') if any('05-td2' in ch['file'] for ch in config['chapters']) else ''
    parts=re.split(r'^## Exercice (\d+\.\d+).*\n',text,flags=re.M)
    solutions={parts[i]:parts[i+1] for i in range(1,len(parts),2)}
    cards=[]
    for chapter in config['chapters']:
        text=(BASE/chapter['file']).read_text(encoding='utf-8')
        matches=list(re.finditer(r'^% @card ([^\r\n]+)\n(.*?)^% @end\s*$',text,flags=re.M|re.S))
        assert len(matches)==len(re.findall(r'^% @card ',text,flags=re.M)), 'Unclosed card in '+chapter['file']
        for match in matches:
            c=json.loads(match[1]);c['chapter']=chapter['id']
            assert len(re.findall(r'^% @proof\s*$',match[2],flags=re.M))<=1, 'Duplicate proof marker'
            pieces=re.split(r'^% @proof\s*$',match[2],maxsplit=1,flags=re.M)
            c['body']=pieces[0].strip();c['proof']=pieces[1].strip() if len(pieces)>1 else ''
            if 'import_solution' in c:
                md=solutions[c['import_solution']]
                fence=chr(96)*3
                md=re.sub(fence+r'{=latex}\s*(.*?)'+fence,lambda m:
                    '\n@@CORRECTION@@\n' if r'\begin{correction}' in m[1] and r'\end{correction}' not in m[1] else '',md,flags=re.S)
                statement,proof=md.split('@@CORRECTION@@',1)
                for key,value in [('body',statement),('proof',proof)]:
                    c[key]=run([shutil.which('pandoc'),'-f','markdown+tex_math_dollars+raw_tex','-t','latex','--wrap=none'],
                               input=value.replace(r'\clearpage','')).strip()
                # Reflow long displays for the reader without editing canonical solutions.
                if c['import_solution']=='1.2':
                    c['proof']=c['proof'].replace(
                        '\\sum_{n\\in F}a_n\n=\\sum_{k\\in K_F}\\sum_{n\\in F\\cap E_k}a_n\n\\le\\sum_{k\\in K_F}\\mu(E_k)\n\\le\\sum_{k\\ge1}\\mu(E_k).',
                        '\\begin{aligned}\n\\sum_{n\\in F}a_n\n&=\\sum_{k\\in K_F}\\sum_{n\\in F\\cap E_k}a_n\\\\\n&\\le\\sum_{k\\in K_F}\\mu(E_k)\\\\\n&\\le\\sum_{k\\ge1}\\mu(E_k).\n\\end{aligned}')
                if c['import_solution']=='1.5':
                    c['body']=c['body'].replace(
                        '\\mu(A)=\\operatorname{Card}(A)\\text{ si }A\\text{ est fini},\n\\qquad\\mu(A)=+\\infty\\text{ sinon}.',
                        '\\begin{gathered}\\mu(A)=\\operatorname{Card}(A)\\text{ si }A\\text{ est fini},\\\\\n\\mu(A)=+\\infty\\text{ sinon}.\\end{gathered}')
            assert re.fullmatch('[a-z0-9-]+',c['id'])
            assert c['type'] in {'definition','theorem','proposition','example','warning','exercise'} and c['body']
            cards.append(c)
    index={c['id']:c for c in cards}
    assert len(index)==len(cards),'Duplicate card IDs'
    for c in cards:
        assert c['refs'],'Missing source'
        for d in c['requires']:assert d in index,'Unknown dependency '+d
        for s,start,end in c['refs']:
            assert s in config['sources'] and 1<=start<=end<=config['sources'][s]['pages']
    for s in config['sources'].values():
        assert len(PdfReader(ROOT/s['path']).pages)==s['pages'],'PDF page count changed'
    return cards

def typeset(cards,font_root,reuse):
    fragments=[]
    for c in cards:
        for part in ['body','proof']:
            if c[part]:
                for layout,width in [('wide',340),('narrow',220)]:
                    fragments.append({'id':f"{c['id']}-{part}-{layout}",'tex':c[part],'width':width})
    preamble=(BASE/'排版配置.tex').read_text(encoding='utf-8')
    preamble+='\n'+r'\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}'
    preamble+='\n'+r'\newcommand{\dependency}[1]{\par{\small\color{muted}#1}\par}'
    doc=[r'\documentclass{article}',rf'\def\FontRoot{{{font_root.as_posix()}}}',preamble,
         r'\usepackage[active,tightpage]{preview}',r'\setlength\PreviewBorder{1pt}',r'\begin{document}']
    for f in fragments:
        doc+=['% '+f['id'],r'\begin{preview}',rf'\begin{{minipage}}{{{f["width"]}pt}}',
              r'\fontsize{11}{16}\selectfont\color{ink}',f['tex'],r'\end{minipage}',r'\end{preview}']
    doc+=[r'\end{document}'];combined='\n'.join(doc)
    digest=hashlib.sha256(combined.encode()).hexdigest()
    (BUILD/'fragments.tex').write_text(combined,encoding='utf-8')
    stamp=BUILD/'typeset.sha256'
    if not(reuse and stamp.exists() and stamp.read_text()==digest and (BUILD/'fragments.pdf').exists()):
        print(f'Compiling {len(fragments)} fragments...',flush=True)
        run([shutil.which('xelatex'),'-interaction=nonstopmode','-halt-on-error','-no-shell-escape','fragments.tex'],cwd=BUILD)
        stamp.write_text(digest)
    log=(BUILD/'fragments.log').read_text(encoding='utf-8',errors='replace')
    faults=re.findall(r'^(?:Overfull[^\n]*|Missing character[^\n]*|![^\n]*)',log,flags=re.M)
    if faults:raise RuntimeError('Typesetting issues:\n'+'\n'.join(faults))
    reader=PdfReader(BUILD/'fragments.pdf');assert len(reader.pages)==len(fragments)
    pages=BUILD/'pages';pages.mkdir(exist_ok=True)
    for n,f in enumerate(fragments):
        writer=PdfWriter();writer.add_page(reader.pages[n])
        with (pages/(f['id']+'.pdf')).open('wb') as stream:writer.write(stream)
    def convert(f):
        target=pages/(f['id']+'.svg')
        if not(reuse and target.exists() and target.stat().st_mtime>=(BUILD/'fragments.pdf').stat().st_mtime):
            run([shutil.which('pdftocairo'),'-svg',str(pages/(f['id']+'.pdf')),str(target)])
        return f['id'],target
    with ThreadPoolExecutor(max_workers=4) as pool:svgs=dict(pool.map(convert,fragments))
    return fragments,svgs

def inline_vectors(files):
    shared={};rendered={}
    for key,path in files.items():
        root=ET.fromstring(path.read_text(encoding='utf-8'));defs=root.find('{'+SVG+'}defs');mapping={}
        if defs is not None:
            for node in defs.iter():
                old=node.get('id','')
                if old.startswith('glyph'):
                    geom=''.join(ET.tostring(child,encoding='unicode') for child in node)
                    gid='g'+hashlib.sha256(geom.encode()).hexdigest()[:18];mapping[old]=gid
                    if gid not in shared:
                        group=ET.Element('{'+SVG+'}g',{'id':gid})
                        for child in node:group.append(child)
                        shared[gid]=ET.tostring(group,encoding='unicode')
            for parent in list(defs.iter()):
                for node in list(parent):
                    if node.get('id','') in mapping:parent.remove(node)
        for node in root.iter():
            if node.get('id'):
                old=node.get('id');new=key+'-'+old;mapping[old]=new;node.set('id',new)
        for node in root.iter():
            for attr,value in list(node.attrib.items()):
                if value.startswith('#') and value[1:] in mapping:node.set(attr,'#'+mapping[value[1:]])
                if 'url(#' in value:
                    for old,new in mapping.items():value=value.replace('url(#'+old+')','url(#'+new+')')
                    node.set(attr,value)
        root.set('class','tex-svg');root.set('aria-hidden','true');root.set('focusable','false')
        root.attrib.pop('width',None);root.attrib.pop('height',None)
        rendered[key]=ET.tostring(root,encoding='unicode')
    return '<svg class="glyph-bank" aria-hidden="true"><defs>'+''.join(shared.values())+'</defs></svg>',rendered,len(shared)

def main():
    p=argparse.ArgumentParser();p.add_argument('--reuse',action='store_true')
    delivery=p.add_mutually_exclusive_group()
    delivery.add_argument('--web-only',action='store_true',help='Export split online resources (the default)')
    delivery.add_argument('--offline',action='store_true',help='Explicitly regenerate the standalone offline HTML')
    p.add_argument('--font-root',type=Path,default=Path(os.environ.get('LOCALAPPDATA',''))/'Programs/MiKTeX/fonts/opentype/public');args=p.parse_args()
    missing=[name for name in ['xelatex','pandoc','pdftocairo'] if not shutil.which(name)]
    if missing:raise RuntimeError('Required commands not found in PATH: '+', '.join(missing))
    BUILD.mkdir(parents=True,exist_ok=True);config=json.loads((BASE/'course.json').read_text(encoding='utf-8'))
    cards=load_cards(config);fragments,files=typeset(cards,args.font_root,args.reuse)
    originals,original_files=build_originals(config,cards,args.reuse)
    bank,vectors,glyphs=inline_vectors({**files,**original_files})
    if not args.offline:
        from web_export import publish_origin
        site=ROOT/'site';folder=site/'reader';site_config=copy.deepcopy(config)
        for source in site_config['sources'].values():
            path=source['path'];source['path']='../'+(path if path.startswith('origin/') else 'origin/'+path)
        result=render_book(BASE,site_config,cards,vectors,bank,args.font_root,originals,lazy=True,web_dir=folder)
        output=folder/'index.html';output.write_text(result,encoding='utf-8')
        origins=publish_origin(ROOT,site,config)
        report={'version':config['version'],'date':config['updated'],'html_file':'site/reader/index.html','html_bytes':output.stat().st_size,
                'html_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'cards':len(cards),'chapters':len(config['chapters']),
                'proofs':sum(bool(c['proof']) for c in cards),'compiled_fragments':len(fragments),'original_vector_fragments':len(original_files),
                'delivery':'external-hashed-svg-and-chapter-json','search':'separate-index-loaded-on-first-search','source_files':origins,
                'runtime_tex_compilation':False,'repository':'CuteYzm/theorie-mesure','pages_url':'https://cuteyzm.github.io/theorie-mesure/reader/'}
        (BASE/'网站构建记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k!='source_files'},ensure_ascii=False,indent=2),flush=True);print(output,flush=True);return
    OUTPUT.write_text(render_book(BASE,config,cards,vectors,bank,args.font_root,originals,lazy=True),encoding='utf-8')
    report={'version':config['version'],'date':config['updated'],'cards':len(cards),'chapters':len(config['chapters']),
            'proofs':sum(bool(c['proof']) for c in cards),'compiled_fragments':len(fragments),'shared_glyphs':glyphs,
            'html_bytes':OUTPUT.stat().st_size,'html_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
            'external_runtime_dependencies':0,'source_pdfs_verified':len(config['sources']),'card_ids':[c['id'] for c in cards],
            'french_cards':len(originals),'original_vector_fragments':len(original_files),'reading_modes':['zh','fr','compare'],
            'html_file':OUTPUT.name,'delivery':'chapter-and-language-on-demand',
            'backup_file':'测量理论_知识整合_v1.5.0_备份.html','deferred_asset_payloads':len(vectors)}
    (BASE/'构建记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True);print(OUTPUT,flush=True)

if __name__=='__main__':main()
