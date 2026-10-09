# 测量理论知识整合：维护说明

当前版本：**v1.6.0 · 2026-10-09**。阅读入口：[GitHub Pages 在线阅读](https://cuteyzm.github.io/theorie-mesure/reader/)。源文件与原 PDF：[GitHub 仓库](https://github.com/CuteYzm/theorie-mesure)。本地 [v1.5.1 单文件版](../测量理论_知识整合_按需加载.html)、[v1.5.0 完整备份](../测量理论_知识整合_v1.5.0_备份.html) 与 [旧入口](../测量理论_知识整合.html) 继续保留。

## 本版范围

沿用用户参考 HTML 的纸色背景、深蓝导航和分类色彩。现有 13 个主题、117 个条目、73 个中文证明区块，覆盖 W1–W3、W4 整份 157 页课程手册的核心知识与 25 页 CM04 幻灯片。支持一键中文、Français、中法对照，117 个条目全部关联原文，嵌入 271 个不重复的原 PDF 矢量摘录。法语侧保留原句、公式与编号，不进行翻译或 OCR 重录；重点加黑加粗。既有 ID、中文正文和证明保留。核心知识覆盖全部手册章节，并非逐页全文转写；TD 题目与题解不进入网页。

CM04 的当前课堂内容是多重积分；其余新主题以“W4 手册”标记，代表资料覆盖范围而非授课进度。第 07、08 主题采用新手册的 Lᵖ 空间、测度分解顺序。后续继续在相应主题中合并来源、补充或修订，无需另建重复周次页面。

本次将内容拆分为可缓存的在线资源。沿用 380 个中文排版片段、271 个法语原文片段及既有字形；正文、公式、编号和黑色粗体强调保留。入口只包含目录与条目元数据，章节正文与检索全文另存 JSON；每个 SVG 仅携带自身使用的字形，以图片加载。阅读时只挂载当前章节与所选语言，离开后移除；证明和补充原文展开时加载，宽/窄排版按窗口选择。

每个条目有来源 PDF 页码；依赖链接跳至前置知识。定义、性质、证明路线和阅读补充分别标明。该整合稿为学习辅助材料，不是教师官方讲义或官方 TD2 答案。

## 阅读与分享

- 跨设备访问同一在线网址即可阅读。入口约 62 KiB，初次打开只请求当前章节及所需矢量和字体，无运行时 TeX 或 MathJax 排版；全文索引首次搜索时加载。
- 顶部选择中文、Français 或对照。切换保留当前条目位置及展开状态；浏览器保存语言偏好。宽屏对照并排，窄屏上下排列。
- 中文模式检索整合稿，法语模式检索原文，对照模式检索两侧；法语重音不影响匹配。索引始终覆盖全部 117 个条目。搜索显示标题列表，点击后装入对应章节并定位条目。按 / 聚焦搜索，Esc 清除搜索或关闭手机目录。
- 点击“证明与依据”展开；点击“依赖”跳转；浏览器前进/后退可追踪章节。
- 中文正文及公式是 XeLaTeX 编译后的 SVG；法语沿用原 PDF 已编译的矢量字形。中文复制公式请展开“LaTeX 源文”，法语可点击页码查看原 PDF。正文搜索使用内置文本索引，浏览器原生选字体验与普通 HTML 文字不同。
- 原 PDF 链接直接使用同站点 origin/ 路径，保留实际 PDF 页序。资源目录读取 origin/index.json，列出发布的全部 17 份 PDF（16 份原资料及既有 TD2 学习答案）；TD 不进入知识正文。
- 章节、SVG、脚本、样式和字体使用内容哈希文件名；更新后刷新同一入口即可，未变化的资源继续复用缓存。在线版需要网络和 JavaScript，不应单独下载 index.html 后双击；完整离线阅读可使用保留的 v1.5.1 单文件版。
- “打印提纲”按当前语言临时装入全部章节，结束后回到当前章节和阅读位置。中文不打印展开证明；对照模式打印两侧；补充原文按已保存的折叠状态输出。

## 文件职责

| 文件 | 修改时机 |
| --- | --- |
| course.json | 版本、日期、周次、章节顺序、来源、学期计划及本版摘要 |
| content/01-exterior.tex | 外测度、可测性、Vitali 集 |
| content/02-tribus.tex | σ-代数、Borel 集、Cantor 集 |
| content/03-measures.tex | 测度、连续性、Dynkin 定理 |
| content/04-functions.tex | 可测函数、简单函数、像测度，以及 W3 的生成族原像、复合与扩展实数补充 |
| content/05-integral.tex | 积分构造、收敛定理、含参积分及 W4 广义控制收敛补充 |
| content/06-multiple.tex | 多重积分、CM04 使用方法、Jacobian 与坐标变换 |
| content/07-lp.tex / content/08-decomposition.tex | Lᵖ 空间、密度与测度分解 |
| content/09-probability.tex / content/10-vectors.tex | 随机变量、分布、独立性、随机向量与卷积 |
| content/11-conditional.tex | 条件期望、条件分布、投影与线性回归 |
| content/12-gaussian.tex / content/13-convergence.tex | 特征函数、高斯向量、收敛与极限定理 |
| content/05-td2.tex | 旧版习题导入元数据，当前未启用，不进入网页 |
| 排版配置.tex | 正文、公式和证明共用的字体与 LaTeX 宏 |
| assets/style.css / assets/lazy.css | 共用视觉和按需加载入口的附加样式 |
| assets/web.js / assets/web.css | 在线资源请求、独立 SVG、搜索延迟加载、重试、状态和打印 |
| assets/lazy.js | v1.5.1 单文件离线版交互，继续保留 |
| assets/app.js | 上一版完整加载逻辑，保留参考；新构建不使用 |
| render.py | HTML 模板、卡片结构、来源与依赖链接；按章节及片段生成惰性 JSON 数据 |
| build.py / web_export.py | 编译与资源拆分；默认写入 site/reader/、site/origin/，不覆盖本地旧 HTML |
| publish.py | 同步内容和原 PDF，以正常提交更新 GitHub main 与 gh-pages |
| ../site/reader/ | 小入口、章节 JSON、独立 SVG、字体、搜索索引与资源哈希清单 |
| ../site/origin/ | 发布所需 PDF 的原样副本与 index.json，不修改原始输入 |
| originals.py / french/originals.json | 原 PDF 内容流截取、重点强调及全部条目的原文映射 |
| french/README.md / french/原文构建记录.json | 法语维护流程、来源哈希、原文页码与截取范围 |
| 构建记录.json | 自动生成的数量、成品哈希和构建信息 |
| 网站构建记录.json / 网站检查.json / 发布记录.json | 在线版构建、实际必要检查与发布提交记录 |
| browser-check.js | 保留的浏览器交互与响应式复核脚本，本版未运行 |
| 校验记录.md | 实际执行的检查、结果与限制 |
| 按需加载检查.json / 语言切换性能调查.json | 本版必要功能/性能记录与上一版性能基线 |
| build/ | 可再生缓存，不进入版本清单 |

**不要直接编辑生成的 HTML 或 build/fragments.tex。** 下一次构建会重写它们。

W2 答案的唯一正文来源是 [既有 Markdown](../output/source/TD02_前五题/TD02_前五题_原题与逐步解答.md)。当前网页不导入 TD 答案；旧版导入配置保留但未启用。以后纠错应先修改该正文源文件，并按原答案目录的构建说明同步更新 PDF。

## 条目格式

在对应主题的 .tex 中追加以下结构，元数据必须在单独一行中使用合法 JSON：

~~~tex
% @card {"id":"stable-name","type":"theorem","title":"中文标题","fr":"Titre français","refs":[["cm2",41,42]],"requires":["measure-definition"]}
正文直接使用 LaTeX，行内公式写为 $A_n\uparrow A$。
\[
\mu(A)=\lim_{n\to\infty}\mu(A_n).
\]
% @proof
\textbf{第一步。}写明推理及所需条件。
\dep{测度定义；可数可加性；CM2 第 41–42 页。}
% @end
~~~

- id 全仓唯一，只使用小写英文字母、数字和连字符。已发布 ID 尽量不改，以免收藏链接失效。
- type 可取 definition、theorem、proposition、example、warning、exercise。
- refs 每项为“来源键、起始 PDF 页、终止 PDF 页”；页码为文件实际页序，不虚构定理编号。
- requires 必须指向已存在条目的 id。无前置依赖时用空数组。
- proof 部分可省略。正文和证明内均可使用 \dep 标明依据。新增命题要写明有限性、可测性、可数性及值域等条件。
- 来源不足时明确标为“补充推导”或“待核实”；不可把证明提纲标为完整证明。
- 公式同时编译为 340 pt 与 220 pt 两种行宽。长公式优先用 aligned / gathered 换行；构建发现溢出或缺字会停止。

## 加入下一周资料

1. 新 PDF 放入对应周次；保留原文件名与旧版资料。先阅读、记录实际覆盖范围。
2. 在 course.json 的 sources 添加来源键、相对根目录路径、准确页数和资料类别。
3. 将条目加入现有主题；新主题则新建 content 文件并加入 chapters。章节 id、编号、标题、文件路径、周次等必须齐全。
   同步在 french/originals.json 添加原文对应；新来源补齐 fr_label、fr_kind。中文补充或修正与原文不逐字对应时，添加双语对应说明。具体见 [法语维护说明](french/README.md)。
4. 将已开始整理的主题从 roadmap 中移除；更新 coverage、版本号、updated 日期和 release_notes。学期名称发生变化时更新 semester；整学期手册的资料覆盖说明使用 scope_note，避免把上传周次当作授课进度。
5. 按下面流程构建并核验，再更新根目录 CHANGELOG.md、README.md 和本目录校验记录。
6. 最后生成新的不可覆盖版本清单。新增内容升次版本；纠错与排版修订升修订号。

## 构建

所需现有工具：Python 3（pypdf、pdfplumber）、XeLaTeX、Pandoc、pdftocairo。命令应在 PATH 中可找到。中文使用 Latin Modern Roman、Latin Modern Math 和 Windows 宋体，正文与公式共用配置；法语保持原 PDF 字体。HTML 界面另加载 Latin Modern 正体/斜体，中文界面使用系统宋体。字体许可见 assets/GUST-FONT-LICENSE.TXT。

本机在仓库根目录执行：

~~~powershell
& 'C:\Users\22674\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 '.\知识整合\build.py'
~~~

仅修改 CSS、交互、标题或来源等、不改变 LaTeX 正文时，可复用缓存：

~~~powershell
& 'C:\Users\22674\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 '.\知识整合\build.py' --reuse
~~~

--reuse 会比较全部 LaTeX 片段的内容哈希；正文、宏或字体配置改变仍会重新编译。它不是逐条目的增量编译。缓存缺失时自动重建。

法语构建按原 PDF 的 SHA-256 与索引版本复用缓存，再按原文来源、页码、范围和强调算法版本生成独立片段。原始 PDF 从不被覆盖。法语文字提取仅用于检索；可见正文来自原内容流。

构建路径：内容 → XeLaTeX 多页 PDF → 逐片段 SVG → 按片段补齐字形 → 独立 SVG 与章节 JSON → 在线入口。法语沿用原 PDF 的已编译内容流。build/fragments.pdf 是排版中间文件，页面尺寸随片段高度变化，不是常规 A4 讲义。

当前默认输出 site/reader/ 与 site/origin/。在线入口不包含全部矢量或完整检索正文；当前章节缓存最多 4 章，关闭的展开内容不请求图片。语言选择在 measure-reading-mode-online 键保存，首次可继承旧版偏好；展开状态与章节位置在本次页面会话内保存。若明确需要重新生成单文件离线版，使用 --offline；此操作会覆盖根目录的 v1.5.1 按需加载文件，应先另存它。

本地预览必须通过 HTTP 服务，避免 file:// 的跨文件请求限制：

~~~powershell
python -m http.server 8000 --directory site
~~~

浏览器访问 http://127.0.0.1:8000/reader/。完成内容更新、构建和必要检查后发布：

~~~powershell
python 知识整合/build.py --reuse
python 知识整合/publish.py --publish
~~~

发布需要 git、已登录的 GitHub CLI 与该仓库写权限。发布器在 tmp/github/ 复用独立克隆，以普通提交更新 main 与 gh-pages，保留既有 VitePress 站点。main 保存 reader/、origin/、知识整合源文件和历史记录；gh-pages 保存可直接访问的静态资源。GitHub Pages 当前使用 gh-pages 根目录发布；旧站点 deploy.mjs 也会复制 reader/ 和 origin/，避免后续旧站点构建遗漏阅读器。构建不需要 GitHub 权限；省略 --publish 只准备本地提交。

更换电脑时可以通过 --font-root 指定含 lm 与 lm-math 子目录的字体目录；如果没有宋体，应在排版配置.tex 中明确改用已安装的中文字体，再完整编译。MiKTeX 首次调用可能需要其正常的缓存写入权限；本项目构建不需要 shell-escape，也不依赖 latexmk 或 Perl。

## 发布检查

依照用户当前约定，更新执行必要编译与发布记录；不自动重跑大规模浏览器或截图检查。交互/样式变化时只检查相关功能；截图仅在用户要求时执行。本版检查新增阅读模式，不重跑旧版完整检查脚本。

1. 构建成功：无 Overfull、Missing character 或 TeX 错误；数量、来源页数、ID 与依赖有效。
2. 交互改动时核验受影响功能，例如语言切换、相应正文检索、对照显示和展开状态。
3. 必要结构检查确保矢量引用有效及原文截取边界不切断字符；不默认生成截图或打印核验件。
4. 对照上一版本清单，确认原资料未意外变化。禁止覆盖历史清单。
5. 写好发布记录后，最后执行（替换版本号和实际日期）：

~~~powershell
python 维护记录/snapshot.py v1.6.0 --date YYYY-MM-DD --previous 维护记录/版本清单/v1.5.1.json
~~~

旧版截图与打印核验件保存在 output/playwright；本次未生成新截图，它们不代表当前版本的重新核验。版本清单排除此目录和编译缓存，只记录最终 HTML、源文件、维护记录及课程资料。
