"""Necessary checks for DS annotations, compiled assets, and preserved inputs."""
from pathlib import Path
import argparse, hashlib, json, re
from datetime import datetime, timezone
from build import load_cards

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--browser-report',type=Path)
    args=parser.parse_args()
    config=json.loads((BASE/'course.json').read_text(encoding='utf-8'))
    cards=load_cards(config);mapping=config['ds_scope']['summary']['mapping']
    folder=ROOT/'site/reader'
    manifest=json.loads((folder/'resource-manifest.json').read_text(encoding='utf-8'))
    assert manifest['version']==config['version']
    seen=set();marked={};proofs=set();links=0
    for chapter_id,url in manifest['chapters'].items():
        data=json.loads((folder/url).read_text(encoding='utf-8'))
        for identifier in data['ids']:
            assert identifier not in seen
            seen.add(identifier)
            template=data['templates'][identifier]
            matches=re.findall(r'class="ds-statement" href="\.\./ds/#(c[1-8]-\d{2})"',template)
            if matches:marked[identifier]=matches
            proofs.update(re.findall(r'class="ds-proofs">(.*?)</div>',template,re.S))
            assert ('ds-added' in template)==bool(next(c for c in cards if c['id']==identifier).get('ds_added'))
            if chapter_id in ['ch7','ch8']:assert not matches or 'Énoncés uniquement' in template
            if int(chapter_id[2:])>=9:assert not matches
            for path,page in re.findall(r'class="ds-page" href="([^"#]+)#page=(\d+)"',template):
                assert (folder/path).exists() and 1<=int(page)<=15
                links+=1
        for asset in data['assets'].values():assert (folder/asset['url']).exists()
    expected={c['id']:[m['id'] for m in c['ds']] for c in cards if c['ds']}
    assert marked==expected and len(seen)==len(cards)==122
    assert {m for ids in marked.values() for m in ids}==set(mapping)
    assert 'dynkin' not in marked and 'measure-uniqueness' not in marked
    proof_numbers=set(re.findall(r'#p(\d{2})', ''.join(proofs)))
    assert proof_numbers=={f'{n:02d}' for n in range(1,16)}
    for asset in [*manifest['assets'].values(),manifest['search'],manifest['style'],manifest['script']]:
        assert sha(folder/asset['url'])==asset['sha256'],'Asset hash mismatch: '+asset['url']
    index=json.loads((folder/manifest['search']['url']).read_text(encoding='utf-8'))
    assert len(index)==len(cards)
    for item in index:
        assert item['ds_ids']==expected.get(item['id'],[])
        assert all(id in item['text'] and id in item['fr_text'] for id in item['ds_ids'])
    old=json.loads((ROOT/'维护记录/版本清单/v1.7.1.json').read_text(encoding='utf-8'))
    kept=[];pdfs=0
    for record in old['files']:
        path=record['path']
        preserve=path.startswith(('site/ds/','期中复习/')) or path in ['测量理论_知识整合.html','测量理论_知识整合_v1.5.0_备份.html','测量理论_知识整合_按需加载.html','测量理论_DS期中复习.html']
        preserve=preserve or record['category']=='source_pdf' or (path.startswith('site/origin/') and path.endswith('.pdf'))
        if preserve:
            assert sha(ROOT/path)==record['sha256'],'Unintended change: '+path
            kept.append(path)
            if path.endswith('.pdf'):pdfs+=1
    log=(BASE/'build/fragments.log').read_text(encoding='utf-8',errors='replace')
    assert not re.findall(r'^(?:Overfull[^\n]*|Missing character[^\n]*|![^\n]*)',log,re.M)
    report={'version':config['version'],'release':config['repository_release'],'date':config['updated'],
        'checked_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'scope':'Only DS mapping, affected links/search/layout, compile log, resources, and preserved inputs; no screenshots or mathematical/visual audit.',
        'local':{'cards':len(cards),'chapters':len(manifest['chapters']),'official_statements':len(mapping),
                 'marked_cards':len(marked),'added_cards':config['ds_scope']['summary']['added_cards'],
                 'official_page_links':links,'designated_proof_links':15,'search_includes_ds_ids_in_both_languages':True,
                 'hashed_vectors':len(manifest['assets']),'latex_faults':0,'preserved_ds_and_inputs':len(kept),
                 'preserved_pdf_files':pdfs,'preserved_offline_html':3,'entry_bytes':(folder/'index.html').stat().st_size},
        'browser':None,'live':None}
    if args.browser_report:
        report['browser']=json.loads(args.browser_report.read_text(encoding='utf-8'))
        assert report['browser']['errors']==[] and report['browser']['failed_requests']==[]
        assert report['browser']['search_ds']['count']==70 and report['browser']['search_id']['ids']==['#lebesgue-rn']
        assert not report['browser']['mobile']['overflow']
    (BASE/'网站检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['local'],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
