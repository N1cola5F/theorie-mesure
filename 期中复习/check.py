"""Small build/resource checks; no rendering, screenshots or blanket math audit."""
from pathlib import Path
import hashlib,json,re

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'期中复习'
SITE=ROOT/'site/ds'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    manifest=load(SITE/'resource-manifest.json');report=load(BASE/'构建记录.json');paths=set();ids=set();proofs=set()
    def asset(value):
        if isinstance(value,dict):
            if 'src' in value:
                paths.add(value['src']);assert value['width']>0 and value['height']>0
            else:
                for child in value.values():asset(child)
        elif isinstance(value,list):
            for child in value:asset(child)
    for chapter in manifest['chapters']:
        paths.add(chapter['data']);data=load(SITE/chapter['data'])
        assert len(data['cards'])==chapter['count']
        for card in data['cards']:
            assert card['id'] not in ids;ids.add(card['id']);asset(card)
    for proof in manifest['proofs']:
        paths.add(proof['data']);data=load(SITE/proof['data']);proofs.add(data['id']);asset(data)
        assert data['card'] in ids and set(data['requires'])<=ids
    assert len(ids)==100 and len(proofs)==15
    for chapter in manifest['chapters']:
        for card in load(SITE/chapter['data'])['cards']:assert set(card['requires'])<=ids
    asset(manifest['guides']);paths|={manifest['search'],manifest['catalog']}
    search=load(SITE/manifest['search']);assert {c['id'] for c in search}==ids|proofs
    html=(SITE/'index.html').read_text(encoding='utf-8')
    paths.update(re.findall(r'(?:href|src)="((?:styles|scripts)/[^"]+)"',html))
    for path in paths:assert (SITE/path).is_file(),'Missing resource '+path
    source_hashes={}
    for key,s in manifest['sources'].items():
        target=(SITE/s['href']).resolve();assert target.is_relative_to(ROOT/'site/origin')
        assert target.is_file() and sha(target)==s['sha256'];source_hashes[key]=s['sha256']
    for td in manifest['td']:
        assert all(e['part'] in (1,2) and e['card'] in ids for e in td['exercises'])
    previous=load(ROOT/'维护记录/版本清单/v1.6.1.json')
    protected=[r for r in previous['files'] if r['path'].startswith('site/reader/') or r['path'] in ['测量理论_知识整合.html','测量理论_知识整合_v1.5.0_备份.html','测量理论_知识整合_按需加载.html']]
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in protected),'Existing reader changed'
    log=(BASE/'build/fragments.log').read_text(encoding='utf-8',errors='replace')
    faults=re.findall(r'^(?:Overfull[^\n]*|Missing character[^\n]*|![^\n]*)',log,re.M)
    assert not faults
    proof_text=(BASE/'content/proofs.tex').read_text(encoding='utf-8')
    chunks=re.split(r'^% @note ',proof_text,flags=re.M)[1:]
    assert all(c.count(r'\dep{')>=c.count(r'\item ') for c in chunks),'Proof step missing dependency'
    result={'version':manifest['version'],'date':manifest['updated'],'scope':'Build diagnostics, mappings and actual referenced resources only; no screenshots or exhaustive math audit',
      'statements':len(ids),'proofs':len(proofs),'sources':len(source_hashes),'referenced_assets':len(paths),'latex_faults':faults,
      'all_pdf_hashes_match':True,'existing_reader_and_three_offline_files_preserved':True,'protected_files':len(protected),'runtime_math_renderer':False,
      'browser_checks':None,'publication_checks':None}
    (BASE/'必要检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
