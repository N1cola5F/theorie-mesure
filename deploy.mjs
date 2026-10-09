// 一键部署到 GitHub Pages（gh-pages 分支）
// 用法：npm run deploy
import { execSync } from 'node:child_process'
import { writeFileSync, rmSync, cpSync, existsSync } from 'node:fs'

const DIST = 'docs/.vitepress/dist'
const run = (cmd, opts = {}) => execSync(cmd, { stdio: 'inherit', ...opts })

// 从 origin 远程推断仓库名 → base 路径，兼容仓库改名
const remote = execSync('git remote get-url origin').toString().trim()
const repo = remote.replace(/\.git$/, '').split('/').pop()

process.env.DOCS_BASE = `/${repo}/`
run('vitepress build docs')

// Keep the semester reader and source PDFs when the original site is rebuilt.
for (const directory of ['reader', 'origin']) {
  if (existsSync(directory)) cpSync(directory, `${DIST}/${directory}`, { recursive: true })
}

writeFileSync(`${DIST}/.nojekyll`, '')
rmSync(`${DIST}/.git`, { recursive: true, force: true })
const git = (c) => run(`git -C "${DIST}" ${c}`)
git('init -b gh-pages')
git('config user.name "Mesure Site"')
git('config user.email "mesure-site@example.com"')
git('add -A')
git('commit -m deploy')
git(`push -f "${remote}" gh-pages`)
rmSync(`${DIST}/.git`, { recursive: true, force: true })

console.log(`\n✓ 已部署。几十秒后访问：https://${remote.split('/')[3].toLowerCase()}.github.io/${repo}/`)
