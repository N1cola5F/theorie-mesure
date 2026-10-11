"""Publish the DS book alongside reader/, retaining the existing Pages site."""
from pathlib import Path
import argparse,importlib.util,json,shutil

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent

def copy_sources(main_dir,config):
    def ignored(path,names):return {n for n in names if n in {'build','__pycache__'}}
    shutil.copytree(BASE,main_dir/'期中复习',dirs_exist_ok=True,ignore=ignored)
    remote_config=json.loads((main_dir/'期中复习/exam.json').read_text(encoding='utf-8'))
    for source in remote_config['sources'].values():source['path']='origin/'+source['path'].removeprefix('origin/')
    (main_dir/'期中复习/exam.json').write_text(json.dumps(remote_config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    docs=main_dir/'reader-source';docs.mkdir(exist_ok=True)
    text=(ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
    for old,new in [('期中复习/','../期中复习/'),('知识整合/','../知识整合/'),('维护记录/','历史记录/')]:
        text=text.replace(']('+old,']('+new)
    (docs/'CHANGELOG.md').write_text(text,encoding='utf-8')
    readme=docs/'README.md';text=readme.read_text(encoding='utf-8') if readme.exists() else '# 课程阅读器维护\n'
    marker='<!-- ds-maintenance -->'
    entry=marker+'\n\n独立 DS 期中版 v1.0.0（资料登记 v1.7.0）：[在线复习册]('+config['url']+') · [维护说明](../期中复习/README.md)。全学期版继续为 v1.6.1。\n\n<!-- /ds-maintenance -->\n\n'
    if marker in text:
        import re
        text=re.sub(r'<!-- ds-maintenance -->.*?<!-- /ds-maintenance -->\s*',lambda m:entry,text,flags=re.S)
    else:text=entry+text
    readme.write_text(text,encoding='utf-8')
    shutil.copytree(ROOT/'维护记录',docs/'历史记录',dirs_exist_ok=True,ignore=ignored)

def main():
    p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');p.add_argument('--finalize-records',action='store_true');args=p.parse_args()
    config=json.loads((BASE/'exam.json').read_text(encoding='utf-8'))
    hosting=json.loads((ROOT/'知识整合/course.json').read_text(encoding='utf-8'))['hosting']
    spec=importlib.util.spec_from_file_location('reader_publisher',ROOT/'知识整合/publish.py')
    publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
    manifest=json.loads((ROOT/'site/ds/resource-manifest.json').read_text(encoding='utf-8'))
    assert manifest['version']==config['version'] and manifest['updated']==config['updated'],'Rebuild DS before publishing'
    repository=hosting['repository'];name=repository.split('/')[-1]
    main_dir=ROOT/'tmp/github'/name;pages_dir=ROOT/'tmp/github'/(name+'-pages')
    if args.finalize_records:
        publisher.checkout(repository,'main',main_dir,hosting.get('previous_repositories',[]))
        copy_sources(main_dir,config)
        print(json.dumps(publisher.commit_push(main_dir,['期中复习','reader-source'],'Record DS v1.0.0 release evidence and v1.7.0 snapshot',args.publish),ensure_ascii=False,indent=2))
        return # The release record keeps the actual content-release commit; avoid self-referential hashes.
    for branch,destination in [('main',main_dir),('gh-pages',pages_dir)]:
        publisher.checkout(repository,branch,destination,hosting.get('previous_repositories',[]))
        shutil.copytree(ROOT/'site/ds',destination/'ds',dirs_exist_ok=True)
        for source in config['sources'].values():
            rel=Path('origin')/source['path'].removeprefix('origin/');target=destination/rel;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/'site'/rel,target)
        shutil.copy2(ROOT/'site/origin/ds-index.json',destination/'origin/ds-index.json')
    copy_sources(main_dir,config)
    shutil.copy2(ROOT/'知识整合/publish.py',main_dir/'知识整合/publish.py')
    readme=main_dir/'README.md';text=readme.read_text(encoding='utf-8');marker='<!-- ds-reader -->'
    entry=marker+'\nDS 期中知识复习：[在线入口]('+config['url']+') · [源文件与维护](期中复习/README.md) · 100 个知识条目与 15 个指定证明。\n<!-- /ds-reader -->\n\n'
    if marker in text:
        import re
        text=re.sub(r'<!-- ds-reader -->.*?<!-- /ds-reader -->\s*',lambda m:entry,text,flags=re.S)
    else:text=entry+text
    readme.write_text(text,encoding='utf-8')
    deploy=main_dir/'deploy.mjs';text=deploy.read_text(encoding='utf-8').replace("['reader', 'origin']","['reader', 'origin', 'ds']")
    deploy.write_text(text,encoding='utf-8')
    (pages_dir/'.nojekyll').write_text('',encoding='utf-8')
    message='Add knowledge-first DS reader v'+config['version']+' and official exam materials'
    result={'repository':repository,'version':config['version'],'release':config['repository_release'],'date':config['updated'],'published':args.publish,
      'main':publisher.commit_push(main_dir,['ds','origin','期中复习','reader-source','知识整合/publish.py','README.md','deploy.mjs'],message,args.publish),
      'gh_pages':publisher.commit_push(pages_dir,['ds','origin','.nojekyll'],message,args.publish),'url':config['url']}
    (BASE/'发布记录.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
