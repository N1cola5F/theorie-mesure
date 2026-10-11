"""Verify the published DS-marked reader and a few representative resources."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import quote, urljoin
import hashlib, json, re, subprocess, time

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent

def fetch(url, method='GET'):
    request=Request(quote(url,safe=':/?&=#%'),method=method,headers={'Cache-Control':'no-cache'})
    with urlopen(request,timeout=30) as response:
        return response.status,response.read() if method=='GET' else b''

def main():
    config=json.loads((BASE/'course.json').read_text(encoding='utf-8'))
    release=json.loads((BASE/'发布记录.json').read_text(encoding='utf-8'))
    assert release['published'] and release['version']==config['version']
    target=release['gh_pages']['commit'];repository=config['hosting']['repository']
    deadline=time.monotonic()+360;previous=None
    while True:
        call=subprocess.run(['gh','api',f'repos/{repository}/pages/builds/latest'],capture_output=True,text=True,encoding='utf-8',errors='replace')
        if call.returncode:
            if time.monotonic()>deadline:raise RuntimeError(call.stderr)
            time.sleep(20);continue
        build=json.loads(call.stdout);state=(build['status'],build.get('commit'))
        if state!=previous:print('Pages:',state[0],state[1],flush=True);previous=state
        if state==('built',target):break
        if build['status']=='errored' and build.get('commit')==target:raise RuntimeError(str(build.get('error')))
        if time.monotonic()>deadline:raise TimeoutError('Pages did not publish the requested commit within six minutes')
        time.sleep(20)
    url=config['hosting']['pages_url'];folder=ROOT/'site/reader';responses=[]
    status,payload=fetch(url+'?edition='+config['version'])
    html=payload.decode('utf-8')
    boot=json.loads(re.search(r'<script id="reader-config" type="application/json">(.*?)</script>',html,re.S)[1])
    assert boot['version']==config['version'] and len(boot['cards'])==122
    assert 'DS ·' in html and '100' in html and '70' in html
    local=(folder/'index.html').read_text(encoding='utf-8')
    assert html.replace('\r\n','\n')==local.replace('\r\n','\n')
    responses.append({'path':'reader/','status':status,'version':boot['version'],'bytes':len(payload),'same_as_local':True})
    status,payload=fetch(urljoin(url,boot['chapters']['ch3']))
    chapter=json.loads(payload);card=chapter['templates']['lebesgue-rn']
    assert 'DS ·' in card and 'c3-04' in card and 'ds-added' in card
    assert '../ds/#c3-04' in card and 'Programme_DS_FR_theorie-de-la-mesure.pdf#page=' in card
    responses.append({'path':boot['chapters']['ch3'],'status':status,'new_card_ds_marker':True})
    manifest=json.loads((folder/'resource-manifest.json').read_text(encoding='utf-8'))
    status,payload=fetch(urljoin(url,manifest['search']['url']))
    search=json.loads(payload)
    assert sum(bool(c['ds_ids']) for c in search)==70
    assert {i for c in search for i in c['ds_ids']}==set(configured_ids())
    responses.append({'path':manifest['search']['url'],'status':status,'ds_marked_cards':70})
    asset=manifest['assets']['lebesgue-rn-body-narrow']
    for item in [asset,manifest['script'],manifest['style']]:
        status,payload=fetch(urljoin(url,item['url']))
        assert hashlib.sha256(payload).hexdigest()==item['sha256'],item['url']+' differs online'
        responses.append({'path':item['url'],'status':status,'hash_matches':True})
    pdf='../origin/'+config['sources']['ds-programme']['path'].removeprefix('origin/')
    status,_=fetch(urljoin(url,pdf),'HEAD');responses.append({'path':pdf,'status':status})
    ds_url=urljoin(url,'../ds/')
    status,payload=fetch(ds_url)
    local_ds=(ROOT/'site/ds/index.html').read_text(encoding='utf-8')
    assert payload.decode('utf-8').replace('\r\n','\n')==local_ds.replace('\r\n','\n'),'Independent DS page changed'
    responses.append({'path':'ds/','status':status,'same_html_after_git_newline_normalization':True})
    status,_=fetch(urljoin(url,'../'),'HEAD');responses.append({'path':'site root','status':status})
    report=json.loads((BASE/'网站检查.json').read_text(encoding='utf-8'))
    report['live']={'checked_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'url':url,
                    'pages_build_status':'built','pages_commit':target,'responses':responses}
    (BASE/'网站检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['live'],ensure_ascii=False,indent=2),flush=True)

def configured_ids():
    return json.loads((BASE/'ds-map.json').read_text(encoding='utf-8'))['statements']

if __name__=='__main__':main()
