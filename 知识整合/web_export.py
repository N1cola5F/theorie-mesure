"""Export immutable, individually cacheable resources for the online reader."""
from pathlib import Path
import hashlib,json,re,shutil
import xml.etree.ElementTree as ET

SVG='http://www.w3.org/2000/svg'

def write_resource(folder,group,payload,suffix):
    content=payload.encode('utf-8') if isinstance(payload,str) else payload
    digest=hashlib.sha256(content).hexdigest()
    relative=f'{group}/{digest[:24]}.{suffix}'
    target=folder/relative;target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists() or target.read_bytes()!=content:target.write_bytes(content)
    return {'url':relative,'sha256':digest,'bytes':len(content)}

def json_resource(folder,group,value):
    return write_resource(folder,group,json.dumps(value,ensure_ascii=False,separators=(',',':')),'json')

def export_resources(base,folder,config,chapters,assets,glyphs,index,font_root):
    folder.mkdir(parents=True,exist_ok=True)
    resources={}
    for key,data in assets.items():
        node=ET.fromstring(data['markup']);node.tag='{'+SVG+'}svg'
        box=[float(v) for v in node.get('viewBox').split()]
        node.set('width',str(box[2]));node.set('height',str(box[3]))
        defs=node.find('{'+SVG+'}defs')
        if defs is None:
            defs=ET.Element('{'+SVG+'}defs');node.insert(0,defs)
        for gid in data['glyphs']:defs.append(ET.fromstring(glyphs[gid]))
        ids=[n.get('id') for n in node.iter() if n.get('id')]
        assert len(ids)==len(set(ids)),'Duplicate SVG ID: '+key
        refs=[v[1:] for n in node.iter() for a,v in n.attrib.items() if a.endswith('href') and v.startswith('#')]
        assert set(refs)<=set(ids),'Missing SVG glyph: '+key
        resources[key]={**write_resource(folder,'assets',ET.tostring(node,encoding='unicode'),'svg'),'width':box[2],'height':box[3],'kind':data['kind']}
    chapter_urls={}
    for chapter_id,data in chapters.items():
        keys=set(re.findall(r'data-(?:asset|narrow)="([^"]+)"',''.join(data['contents'].values())))
        chapter_urls[chapter_id]=json_resource(folder,'chapters',{**data,'assets':{k:resources[k] for k in sorted(keys)}})['url']
    search=json_resource(folder,'search',index)
    font_css=''
    for style,name in [('normal','lmroman10-regular.otf'),('italic','lmroman10-italic.otf')]:
        font=write_resource(folder,'fonts',(font_root/'lm'/name).read_bytes(),'otf')
        font_css+="@font-face{font-family:StudyLatin;font-style:"+style+";font-weight:400;src:url('../"+font['url']+"') format('opentype');font-display:swap}"
    shutil.copyfile(base/'assets/GUST-FONT-LICENSE.TXT',folder/'fonts/GUST-FONT-LICENSE.TXT')
    css=font_css+'\n'+'\n'.join((base/p).read_text(encoding='utf-8') for p in ['assets/style.css','assets/lazy.css','assets/web.css'])
    style=write_resource(folder,'styles',css,'css')
    script=write_resource(folder,'scripts',(base/'assets/web.js').read_bytes(),'js')
    metadata=[{k:c[k] for k in ['id','chapter','type','title','fr','original_title']} for c in index]
    boot={'schema':1,'version':config['version'],'updated':config['updated'],'chapters':chapter_urls,'cards':metadata,'search':search['url'],'sources':'../origin/index.json'}
    (folder/'resource-manifest.json').write_text(json.dumps({'version':config['version'],'assets':resources,'chapters':chapter_urls,'search':search,'style':style,'script':script},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (folder/'.nojekyll').write_text('',encoding='utf-8')
    return {'boot':boot,'style':style['url'],'script':script['url']}

def publish_origin(root,site,config):
    """Copy PDFs only, without touching or renaming any original input."""
    files={root/source['path'] for source in config['sources'].values()}
    original=root/'按周划分'
    if not original.exists():original=root/'origin/按周划分'
    for path in original.rglob('*.pdf'):
        relative=path.relative_to(original)
        if 'build' not in relative.parts and '中文详解' not in path.name:files.add(path)
    report=[]
    labels={source['path'].removeprefix('origin/'):source for source in config['sources'].values()}
    for path in sorted(files):
        relative=path.relative_to(root)
        if relative.parts[0]=='origin':relative=Path(*relative.parts[1:])
        destination=site/'origin'/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,destination)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert hashlib.sha256(destination.read_bytes()).hexdigest()==digest
        meta=labels.get(relative.as_posix(),{})
        report.append({'path':('origin'/relative).as_posix(),'sha256':digest,'bytes':path.stat().st_size,
                       'label':meta.get('label',path.name),'fr_label':meta.get('fr_label',path.name),
                       'kind':meta.get('kind','原始资料'),'fr_kind':meta.get('fr_kind','Document original')})
    (site/'origin/index.json').write_text(json.dumps({'version':config['version'],'updated':config['updated'],'files':report},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
