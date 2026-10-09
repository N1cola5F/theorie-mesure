"""Publish the split reader without replacing the pre-existing GitHub Pages site."""
from pathlib import Path
import argparse,json,shutil,subprocess

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'知识整合'

def run(*args,cwd=None):
    result=subprocess.run(list(args),cwd=cwd,text=True,encoding='utf-8',errors='replace',capture_output=True)
    if result.returncode:raise RuntimeError(' '.join(args)+'\n'+result.stderr[-3000:]+result.stdout[-1000:])
    return result.stdout.strip()

def checkout(repository,branch,folder):
    if not(folder/'.git').exists():
        folder.parent.mkdir(parents=True,exist_ok=True)
        run('git','clone','--quiet','--branch',branch,'https://github.com/'+repository+'.git',str(folder))
    remote=run('git','remote','get-url','origin',cwd=folder)
    assert remote.rstrip('/').removesuffix('.git')=='https://github.com/'+repository,'Unexpected remote'
    assert run('git','branch','--show-current',cwd=folder)==branch,'Unexpected checkout branch'
    if run('git','status','--porcelain',cwd=folder):raise RuntimeError('Publish checkout has uncommitted changes: '+str(folder))
    run('git','fetch','--quiet','origin',branch,cwd=folder)
    run('git','merge','--ff-only','origin/'+branch,cwd=folder)
    profile=json.loads(run('gh','api','user'))
    run('git','config','user.name',profile.get('name') or profile['login'],cwd=folder)
    run('git','config','user.email',str(profile['id'])+'+'+profile['login']+'@users.noreply.github.com',cwd=folder)

def source_copy(destination):
    def ignored(path,names):return {name for name in names if name in {'build','__pycache__'}}
    shutil.copytree(BASE,destination/'知识整合',dirs_exist_ok=True,ignore=ignored)
    config=json.loads((BASE/'course.json').read_text(encoding='utf-8'))
    for source in config['sources'].values():
        if not source['path'].startswith('origin/'):source['path']='origin/'+source['path']
    (destination/'知识整合/course.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    records=destination/'reader-source';records.mkdir(exist_ok=True)
    for name in ['README.md','CHANGELOG.md']:shutil.copyfile(ROOT/name,records/name)
    shutil.copytree(ROOT/'维护记录',records/'历史记录',dirs_exist_ok=True,ignore=ignored)
    (records/'README.md').write_text('''# 全学期资料阅读器

在线入口：https://cuteyzm.github.io/theorie-mesure/reader/

- reader/：已编译的静态站点，章节 JSON、完整搜索索引与 SVG 分开保存。
- origin/：教师原 PDF 与资源页所需资料，index.json 记录原路径和 SHA-256。
- 知识整合/：内容、原文映射、构建程序和界面脚本。
- reader-source/历史记录：不可覆盖的版本清单。

本地 50 MiB 左右的旧 HTML 备份不进入在线仓库。在线阅读只请求当前章节与可见片段。

维护者在本地课程目录运行：

    python 知识整合/build.py --reuse
    python 知识整合/publish.py --publish

发布器以正常提交更新 main 和 gh-pages，仅更新 reader 与 origin，不使用强制推送。
gh-pages 更新后由 GitHub Pages 自动发布。同一网址刷新即可阅读新版。
现有 npm run deploy 也会保留 reader/ 和 origin/。
''',encoding='utf-8')
    readme=destination/'README.md';text=readme.read_text(encoding='utf-8')
    marker='<!-- semester-reader -->'
    if marker not in text:
        text=marker+'\n本学期 W1–W4（13 个主题、117 个条目）：[在线原文对照阅读器](https://cuteyzm.github.io/theorie-mesure/reader/) · [维护说明](reader-source/README.md)\n\n'+text
        readme.write_text(text,encoding='utf-8')
    deploy=destination/'deploy.mjs';text=deploy.read_text(encoding='utf-8')
    if 'cpSync' not in text:
        text=text.replace('writeFileSync, rmSync','writeFileSync, rmSync, cpSync, existsSync')
        text=text.replace("writeFileSync(`${DIST}/.nojekyll`, '')","// Keep the semester reader and source PDFs when the original site is rebuilt.\nfor (const directory of ['reader', 'origin']) {\n  if (existsSync(directory)) cpSync(directory, `${DIST}/${directory}`, { recursive: true })\n}\n\nwriteFileSync(`${DIST}/.nojekyll`, '')")
        deploy.write_text(text,encoding='utf-8')

def commit_push(folder,paths,message,publish):
    run('git','add','--',*paths,cwd=folder)
    changes=run('git','diff','--cached','--stat',cwd=folder)
    if changes:run('git','commit','-m',message,cwd=folder)
    branch=run('git','branch','--show-current',cwd=folder)
    ahead=int(run('git','rev-list','--count','origin/'+branch+'..HEAD',cwd=folder))
    if publish and ahead:
        run('git','-c','credential.helper=','-c','credential.helper=!gh auth git-credential','push','origin',branch,cwd=folder)
    return {'commit':run('git','rev-parse','HEAD',cwd=folder),'changed':bool(changes),'prepared':not publish,
            'pending_commits_before_push':ahead,'summary':changes.splitlines()[-1] if changes else 'No content changes'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');parser.add_argument('--repo',default='CuteYzm/theorie-mesure');args=parser.parse_args()
    assert (ROOT/'site/reader/index.html').exists(),'Build the web reader first'
    config=json.loads((BASE/'course.json').read_text(encoding='utf-8'))
    assert json.loads((ROOT/'site/reader/resource-manifest.json').read_text(encoding='utf-8'))['version']==config['version'],'Stale site build'
    main_dir=ROOT/'tmp/github'/args.repo.split('/')[-1]
    pages_dir=ROOT/'tmp/github'/(args.repo.split('/')[-1]+'-pages')
    checkout(args.repo,'main',main_dir);checkout(args.repo,'gh-pages',pages_dir)
    for destination in [main_dir,pages_dir]:
        for directory in ['reader','origin']:shutil.copytree(ROOT/'site'/directory,destination/directory,dirs_exist_ok=True)
    source_copy(main_dir)
    (pages_dir/'.nojekyll').write_text('',encoding='utf-8')
    message='Publish semester reader v'+config['version']+' with on-demand resources'
    result={'repository':args.repo,'version':config['version'],'date':config['updated'],'published':args.publish,
            'main':commit_push(main_dir,['reader','origin','知识整合','reader-source','README.md','deploy.mjs'],message,args.publish),
            'gh_pages':commit_push(pages_dir,['reader','origin','.nojekyll'],message,args.publish),
            'url':'https://'+args.repo.split('/')[0].lower()+'.github.io/'+args.repo.split('/')[1]+'/reader/'}
    (BASE/'发布记录.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
