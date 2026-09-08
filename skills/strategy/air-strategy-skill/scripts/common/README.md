# AIR Strategy Skill — Common Scripts 索引

> 本目录是 air-strategy-skill 的**通用脚本**（跨阶段工具，继承自原 air-localization script 库）。

---

## 目录结构

```
scripts/common/
├── swf-text-import.sh         # SWF 文本批量导入
├── swf-resource-extract.py    # SWF 资源提取（图片/字体/音频）
├── extract-swf-text.py        # SWF 文本提取（ffdec 封装）
├── filter-swf-strings.py      # SWF 字符串过滤
├── inject-as-text.py          # AS3 注入（运行时 TextField 覆盖静态文本）
├── install-ffdec.py           # ffdec 安装脚本
├── install-swfmill.py         # swfmill 安装脚本
├── patch-swf-translations.py  # SWF 翻译回灌
├── swf-gui-edit.py            # ffdec GUI 编辑入口
├── swf-xml-edit.py            # swfmill XML 编辑
└── verify-swf-text.py         # SWF 文本验证
```

## 脚本说明

| 脚本 | 角色 |
|------|------|
| `swf-text-import.sh` | SWF 文本批量导入 |
| `swf-resource-extract.py` | SWF 资源提取（图片/字体/音频） |
| `extract-swf-text.py` | SWF 文本提取（ffdec 封装） |
| `filter-swf-strings.py` | SWF 字符串过滤 |
| `inject-as-text.py` | AS3 注入（运行时 TextField 覆盖静态文本） |
| `install-ffdec.py` | ffdec 安装脚本 |
| `install-swfmill.py` | swfmill 安装脚本 |
| `patch-swf-translations.py` | SWF 翻译回灌 |
| `swf-gui-edit.py` | ffdec GUI 编辑入口 |
| `swf-xml-edit.py` | swfmill XML 编辑 |
| `verify-swf-text.py` | SWF 文本验证 |

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具索引
- [../../workflow/README.md](../../workflow/README.md) — 流程脚本索引