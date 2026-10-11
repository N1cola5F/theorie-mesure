"""Read-only Pages build and a few published resource checks, without browser screenshots."""
from pathlib import Path
import hashlib,json,subprocess,urllib.parse,urllib.request

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'期中复习'

def main():
    release=json.loads((BASE/'发布记录.json').read_text(encoding='utf-8'))
    call=subprocess.run(['gh','api','repos/'+release['repository']+'/pages/builds/latest'],capture_output=True,text=True,encoding='utf-8')
    if call.returncode:raise RuntimeError(call.stderr)
    build=json.loads(call.stdout)
    if build['status']!='built' or build['commit']!=release['gh_pages']['commit']:
        print(json.dumps({'ready':False,'status':build['status'],'commit':build['commit']},ensure_ascii=False));return
    base=release['url'];opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    results=[]
    def fetch(path,method='GET'):
        url=urllib.parse.quote(urllib.parse.urljoin(base,path),safe=':/%')
        with opener.open(urllib.request.Request(url,method=method,headers={'User-Agent':'DS-reader-release-check'}),timeout=30) as r:
            body=r.read() if method=='GET' else b''
            results.append({'url':url,'status':r.status,'method':method})
            assert r.status==200;return body
    html=fetch('').decode('utf-8');assert 'DS · 知识复习' in html and '2026-10-20' in html
    manifest=json.loads(fetch('resource-manifest.json'));assert manifest['version']==release['version']
    chapter=json.loads(fetch(manifest['chapters'][5]['data']));assert chapter['chapter']==6 and len(chapter['cards'])==7
    card=chapter['cards'][0]
    for vector in [card['compiled']['wide'],card['originals'][0]['svg']]:
        body=fetch(vector['src']);assert b'<svg' in body
        assert hashlib.sha256(body).hexdigest().startswith(Path(vector['src']).stem)
    fetch(manifest['sources']['corrige4']['href'],'HEAD')
    old=fetch('../reader/').decode('utf-8');assert '1.6.1' in old
    fetch('../','HEAD')
    folder=ROOT/'tmp/github'/ (release['repository'].split('/')[-1]+'-pages')
    diff=subprocess.check_output(['git','diff','--name-only','259036907d6b458cc518462b64c52446de0673dd',release['gh_pages']['commit']],cwd=folder,text=True,encoding='utf-8').splitlines()
    assert all(p.startswith(('ds/','origin/')) or p=='.nojekyll' for p in diff),'Existing website file modified'
    result={'pages_status':build['status'],'pages_commit':build['commit'],'url':base,'responses':results,'existing_site_paths_preserved':True,'scope':'Published entrance, manifest, chapter6, two vectors, TD4 PDF HEAD and retained reader/root'}
    check=json.loads((BASE/'必要检查.json').read_text(encoding='utf-8'));check['publication_checks']=result
    (BASE/'必要检查.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
