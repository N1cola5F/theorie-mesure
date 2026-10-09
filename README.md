<!-- semester-reader -->
本学期 W1–W4（13 个主题、117 个条目）：[在线原文对照阅读器](https://cuteyzm.github.io/theorie-mesure/reader/) · [维护说明](reader-source/README.md)

# 测度论 · Théorie de la mesure — 交互式双语文档站

把原先的单文件 `mindmap_proba.html` 重构为基于 [VitePress](https://vitepress.dev/) 的交互式双语（法语 / 中文）测度论知识站：保留并升级数学公式与关系图，新增可缩放/可点击的概念地图、悬停定义，以及 5 个可调参数的数学动态演示，内置侧边栏导航与本地全文搜索。

## 功能特性

- **三章完整内容**（双语内联）：测度论基础 / 可测函数与积分 / 随机变量
- **数学公式**：MathJax（`markdown-it-mathjax3`）
- **关系图**：Mermaid（`vitepress-plugin-mermaid`）
- **语义容器**：`def / prop / theo / coro / attn / exer / loi` 七类彩色卡片
- **低饱和学术风主题**，自动适配明 / 暗模式
- **本地全文搜索**（MiniSearch，零配置、纯本地）
- **5 个交互演示组件**（见下）

## 环境要求

- Node.js ≥ 18（开发时使用 v24）

## 常用命令

```bash
npm install        # 安装依赖
npm run dev        # 本地开发服务器（热更新）
npm run build      # 生产构建 → docs/.vitepress/dist
npm run preview    # 预览构建产物
npm test           # 运行 Vitest 单元测试（组件纯逻辑）
```

构建产物位于 `docs/.vitepress/dist/`，为纯静态文件，可直接用任意静态服务器托管。

## 部署 Déploiement

已部署到 GitHub Pages：**https://cuteyzm.github.io/theorie-mesure/**

更新内容后，重新部署只需：

```bash
npm run deploy     # 用正确 base 构建并推送到 gh-pages 分支
```

`deploy.mjs` 会自动从 `origin` 推断仓库名设置 `base`，再把构建产物推到 `gh-pages` 分支（Pages 源指向该分支）。源码托管在 `main` 分支。

> 若想改为「推送即自动部署」的 CI 流程：先 `gh auth refresh -s workflow` 授予 workflow 权限，再加入 `.github/workflows/deploy.yml`（VitePress 官方 Pages 工作流）。


## 目录结构

```
docs/
  .vitepress/
    config.ts                 # 站点配置：nav/sidebar、math、mermaid、本地搜索、语义容器
    theme/
      index.ts                # 扩展默认主题 + 全局注册交互组件
      custom.css              # 低饱和明/暗配色与容器样式
      components/*.vue         # 5 个交互演示组件
      lib/*.ts                 # 组件纯逻辑（被 Vitest 覆盖）
  index.md                    # 首页
  ch1.md  ch2.md  ch3.md       # 三章正文
  dictionary.md               # 概率↔测度论词典
tests/*.test.ts               # 单元测试
```

## 交互演示组件

| 组件 | 位置 | 说明 |
| :-- | :-- | :-- |
| `ConceptMap` | 第一章顶部 | 全局概念地图：缩放/平移、点击节点跳转、悬停看定义 |
| `LimsupLiminf` | §1.2 | 滑动 n，观察 limsup / liminf 的元素 |
| `MeasureContinuity` | §1.4 | 测度连续性动画 + 反例 $B_n=[n,+\infty)$ |
| `PreimageDemo` | §2.1 | 逆像与集合运算的交换性 |
| `StepApprox` | §2.2 | 阶梯函数逐点单增逼近目标函数 |

每个组件的纯计算逻辑抽离到 `theme/lib/*.ts`，并由 `tests/` 下的 Vitest 用例覆盖。

## 内容来源

正文迁移自原 `mindmap_proba.html` 与 `测度论.md`，并参照三个法语讲义 PDF
（`Cours1/2/3`）补全。原始文件保留在仓库根目录，未作改动。
