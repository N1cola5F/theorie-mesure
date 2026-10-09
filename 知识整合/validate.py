"""Validate the final local reader and compare protected sources with v1.1.0."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,re

ROOT=Path(__file__).resolve().parent.parent

class Reader(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.links=[];self.remote=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag in {'script','img','link','iframe'}:
            url=a.get('src',a.get('href',''))
            if url.startswith(('http:','https:','//')):self.remote.append(url)

def main():
    path=ROOT/'测量理论_知识整合.html';body=path.read_text(encoding='utf-8')
    parser=Reader();parser.feed(body);missing=[]
    assert len(parser.ids)==len(set(parser.ids)),'Duplicate IDs'
    for link in parser.links:
        u=urlsplit(link)
        if u.scheme:continue
        if u.path:
            if not (ROOT/unquote(u.path)).is_file():missing.append(link)
        elif u.fragment and u.fragment not in parser.ids:missing.append(link)
    assert not missing,missing
    assert not parser.remote,parser.remote
    assert not re.search(r'@import|https?://[^"\'\s)]+\.(?:js|css)',body),'Remote stylesheet or script'
    manifest=json.loads((ROOT/'维护记录/版本清单/v1.1.0.json').read_text(encoding='utf-8'))
    protected=[f for f in manifest['files'] if f['path'].startswith(('按周划分/','output/source/TD02_前五题/','output/pdf/TD02_'))]
    changed=[f['path'] for f in protected if not (ROOT/f['path']).exists() or hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()!=f['sha256']]
    assert not changed,changed
    report=json.loads((ROOT/'知识整合/构建记录.json').read_text(encoding='utf-8'))
    assert report['html_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
    result={'version':report['version'],'date':report['date'],'html_sha256':report['html_sha256'],
            'links_checked':len(parser.links),'missing_links':missing,'remote_runtime_resources':parser.remote,
            'protected_files_checked':len(protected),'protected_files_changed':changed}
    (ROOT/'知识整合/静态校验记录.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
