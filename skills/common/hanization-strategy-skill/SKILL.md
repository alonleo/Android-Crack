---
name: hanization-strategy-skill
description: Use when an Android game reverse-engineering task must assess Chinese localization of fonts, text, or image-based text across different engines.
---

# 汉化策略参考

本 skill 沉淀字体、文本与图片汉化的跨 type 分类、质量边界和经验；不定义可执行流程。实际处理、脚本选择、构建和 10–15 阶段验收均以已路由 type 的执行文档为准：统一为 `<type>-strategy-skill/workflow.md`。

## 使用边界

- 适用于字体兼容、静态或运行时文本、图片文字、语言选择与汉化质量判断。
- 不替代引擎私有资源格式、加密/解密、运行时注入、字符串表或重打包策略；这些由当前 type workflow 判断。
- 不记录具体 APK、项目过程、日期、路径、对象 ID 或翻译文本；汉化领域私有经验写 [experiences.md](./experiences.md)，通用逆向问题写根 `EXPERIENCES.md`。

## 加载顺序

1. [strategy.md](./strategy.md)：汉化对象分类、质量边界和风险判断。
2. [tools-index.md](./tools-index.md)：参考与实际执行入口的边界。
3. [experiences.md](./experiences.md)：跨 type 汉化问题经验。
