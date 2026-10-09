# 全学期资料阅读器

在线入口：https://n1cola5f.github.io/theorie-mesure/reader/

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
