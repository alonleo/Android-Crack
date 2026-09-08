# Android Strategy Skill — Workflow Scripts

> Android（普通 Java/Kotlin）类型使用通用子阶段骨架 01–21（仿 il2cpp 模型），
> **无专用流程脚本**。所有阶段由 general-strategy-skill 的通用脚本驱动：

| 阶段 | 脚本 | 路径 |
|------|------|------|
| 00 | sub-stage-sniff.py | `skills/common/general-strategy-skill/scripts/workflow/` |
| 00a | sub-stage-assess.py | 同左 |
| 01 | sub-stage-record.py | 同左 |
| 02 | sub-stage-preprocess.py | 同左 |
| 03 | sub-stage-static-analyze.py | 同左 |
| 04 | sub-stage-entry-points.py | 同左 |
| 05 | sub-stage-extract-all-strings.py | 同左 |
| 06 | sub-stage-ocr.py | 同左 |
| 07 | sub-stage-redraw.py | 同左 |
| 08 | sub-stage-image-device-verify.py | 同左 |
| 09 | sub-stage-fonts.py | 同左 |
| 10 | sub-stage-font-device-verify.py | 同左 |
| 11 | sub-stage-remove-sdks.py | `skills/common/third-party-removal-strategy-skill/scripts/workflow/` |
| 12 | sub-stage-sdk-device-verify.py | `skills/common/general-strategy-skill/scripts/workflow/` |
| 13 | sub-stage-feature-removal.py | 同左 |
| 14 | sub-stage-feature-device-verify.py | 同左 |
| 15 | sub-stage-hanization.py | 同左 |
| 16 | sub-stage-hanization-device-verify.py | 同左 |
| 17 | sub-stage-repack-sign.py | 同左 |
| 18 | sub-stage-runtime-verify.py | 同左 |
| 19 | sub-stage-as-build.py | 同左 |
| 20 | sub-stage-final-check.py | 同左 |
| 21 | sub-stage-cleanup.py | 同左 |

## 同步规则

Android 类型的标准阶段脚本是所有 type 共享的，**不**复制到本 skill 目录；canonical 副本在 `skills/common/general-strategy-skill/scripts/workflow/`。
