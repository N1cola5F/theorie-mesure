import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import type MarkdownIt from 'markdown-it'
import container from 'markdown-it-container'

const CONTAINERS: Record<string, string> = {
  def: 'Définition 定义',
  prop: 'Proposition 命题',
  theo: 'Théorème 定理',
  coro: 'Corollaire 推论',
  attn: 'Attention 注意',
  exer: 'Exemple / Exercice 例',
  loi: 'Loi usuelle 常用分布'
}

function registerContainers(md: MarkdownIt) {
  for (const [name, defaultTitle] of Object.entries(CONTAINERS)) {
    md.use(container, name, {
      render(tokens: any[], idx: number) {
        const token = tokens[idx]
        if (token.nesting === 1) {
          const info = token.info.trim().slice(name.length).trim()
          const title = md.renderInline(info || defaultTitle)
          return `<div class="mblock mblock-${name}"><p class="mblock-title">${title}</p>\n`
        }
        return `</div>\n`
      }
    })
  }
}

// https://vitepress.dev/reference/site-config
export default withMermaid(defineConfig({
  title: 'Théorie de la mesure · 测度论',
  description: '测度论交互式双语笔记 — Théorie de la mesure, fonctions mesurables, variables aléatoires',
  lang: 'zh-CN',
  base: process.env.DOCS_BASE || '/',
  cleanUrls: true,
  markdown: {
    math: true,
    config: (md) => registerContainers(md)
  },
  themeConfig: {
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索 Rechercher', buttonAriaLabel: '搜索' },
          modal: {
            displayDetails: '显示详情',
            resetButtonTitle: '清除',
            backButtonTitle: '返回',
            noResultsText: '无结果 Aucun résultat',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' }
          }
        }
      }
    },
    nav: [
      { text: '首页 Accueil', link: '/' },
      { text: '第一章 Mesure', link: '/ch1' },
      { text: '第二章 Fonctions', link: '/ch2' },
      { text: '第三章 V.A.', link: '/ch3' },
      { text: '词典 Lexique', link: '/dictionary' }
    ],
    sidebar: [
      { text: '首页 Accueil', link: '/' },
      {
        text: '第一章 — Éléments de théorie de la mesure',
        link: '/ch1',
        items: [
          { text: '1.1 Rappels théorie des ensembles', link: '/ch1#sec-1-1' },
          { text: '1.2 Limite sup / inf', link: '/ch1#sec-1-2' },
          { text: '1.3 Tribus', link: '/ch1#sec-1-3' },
          { text: '1.4 Mesure', link: '/ch1#sec-1-4' }
        ]
      },
      {
        text: '第二章 — Fonctions mesurables et intégration',
        link: '/ch2',
        items: [
          { text: '2.1 Image réciproque', link: '/ch2#sec-2-1' },
          { text: '2.2 Fonctions mesurables', link: '/ch2#sec-2-2' },
          { text: '2.3 Intégration de Lebesgue', link: '/ch2#sec-2-3' },
          { text: "2.3' Trois théorèmes de convergence", link: '/ch2#sec-2-3p' }
        ]
      },
      {
        text: '第三章 — Variables aléatoires réelles',
        link: '/ch3',
        items: [
          { text: '3.1 Fubini-Tonelli & changement de variable', link: '/ch3#sec-3-1' },
          { text: '3.2 Variables aléatoires', link: '/ch3#sec-3-2' }
        ]
      },
      { text: '概率↔测度论词典 Lexique', link: '/dictionary' }
    ],
    docFooter: { prev: '上一页', next: '下一页' },
    darkModeSwitchLabel: '外观',
    returnToTopLabel: '返回顶部',
    sidebarMenuLabel: '菜单',
    outline: { label: '本页目录', level: [2, 3] }
  }
}), {
  // mermaid-js 初始化选项
})
