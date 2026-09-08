# 公共脚本索引

本目录包含新 type 生成入口、公共阶段入口及其依赖库。创建规范见 [SKILL.md](../SKILL.md)，流程见 [workflow.md](../workflow.md)。

## 目录职责

- 根目录：`create-type-skill.py` 提供新 type 草稿生成入口。
- `workflow/`：公共阶段及 XAPK 辅助入口；通过注册的路由调用。
- `lib/`：公共阶段依赖库，不作为独立阶段执行。
- `common/`：当前仅保留包占位；旧配置与旧 handler 调用方仍引用此目录，没有可用 handler 实现。
- `__init__.py` 为包标识，不属于阶段脚本；`__pycache__/` 是本地生成缓存，不登记。

## 现有脚本

| 文件 | 职责 |
|---|---|
| [create-type-skill.py](create-type-skill.py) | 创建新 type skill 草稿；默认预览，--apply 生成，--verify 静态校验 |
| [workflow/sub-stage-sniff.py](workflow/sub-stage-sniff.py) | M1：读取集中策略配置并识别 APK/XAPK 引擎 |
| [workflow/sub-stage-assess.py](workflow/sub-stage-assess.py) | M2：评估项目难度并输出评估记录 |
| [workflow/sub-stage-final-check.py](workflow/sub-stage-final-check.py) | M3：检查交付产物 |
| [workflow/sub-stage-cleanup.py](workflow/sub-stage-cleanup.py) | M4：按项目规则清理产物 |
| [workflow/sub-stage-static-analyze.py](workflow/sub-stage-static-analyze.py) | 01：公共静态分析 |
| [workflow/sub-stage-preprocess-build.py](workflow/sub-stage-preprocess-build.py) | 02：预处理与工程构建 |
| [workflow/sub-stage-sdk-network-device-verify.py](workflow/sub-stage-sdk-network-device-verify.py) | 04：SDK/网络修改后的设备验证（既有实现） |
| [workflow/sub-stage-xapk-merge.py](workflow/sub-stage-xapk-merge.py) | M1 helper：合并 XAPK |
| [lib/device_verify_common.py](lib/device_verify_common.py) | 设备验证依赖库：ADB 调用、安装、启动及结果采集 |
| [lib/stage_runtime.py](lib/stage_runtime.py) | 公共运行库：项目路径、环境、release 构建/签名、证据和失败记录 |
| [lib/modification_plans.py](lib/modification_plans.py) | 显式源码/Manifest 修改方案：哈希校验、预检与幂等写入 |
| [lib/localization.py](lib/localization.py) | 文本、字体和图片预检及替换（可编辑工程资源） |
| [lib/stage_device_verify.py](lib/stage_device_verify.py) | 显式页面断言与参考图设备验证，绑定 release APK |
| [workflow/sub-stage-sdk-network-removal.py](workflow/sub-stage-sdk-network-removal.py) | 03：执行 SDK/网络源码与 Manifest 修改方案并构建 |
| [workflow/sub-stage-revenue-forwarding.py](workflow/sub-stage-revenue-forwarding.py) | 05：执行收益路径源码修改方案并构建 |
| [workflow/sub-stage-revenue-device-verify.py](workflow/sub-stage-revenue-device-verify.py) | 06：验证收益目标页面/本地状态断言 |
| [workflow/sub-stage-ui-hide.py](workflow/sub-stage-ui-hide.py) | 07：执行功能入口源码/布局修改方案并构建 |
| [workflow/sub-stage-ui-hide-device-verify.py](workflow/sub-stage-ui-hide-device-verify.py) | 08：验证目标入口消失及保留页面 |
| [workflow/sub-stage-font-replace.py](workflow/sub-stage-font-replace.py) | 09：校验字体格式/目标字形，替换字体并构建 |
| [workflow/sub-stage-font-device-verify.py](workflow/sub-stage-font-device-verify.py) | 10：按参考图验证字体渲染 |
| [workflow/sub-stage-text-hanization.py](workflow/sub-stage-text-hanization.py) | 11：校验占位符/标签并替换文本、构建 |
| [workflow/sub-stage-text-device-verify.py](workflow/sub-stage-text-device-verify.py) | 12：验证目标文本或页面参考图 |
| [workflow/sub-stage-image-hanization.py](workflow/sub-stage-image-hanization.py) | 13：校验图片尺寸/格式/色彩，替换图片并构建 |
| [workflow/sub-stage-image-device-verify.py](workflow/sub-stage-image-device-verify.py) | 14：按参考图验证目标图片页面 |
| [workflow/sub-stage-record-project-files.py](workflow/sub-stage-record-project-files.py) | 15：校验 release 一致性与签名，生成工程文件哈希清单和目录索引 |

此表确认文件存在，不代表已完成 APK、构建或真机验收。逆向阶段运行前仍须按 AGENTS.md 加载项目环境并检查工具、输入及设备。

## 公共实现与执行范围

当前注册的公共阶段均有脚本入口；这不代表所有 type 的打包资源均可使用公共方案。

新增入口的参数、JSON 方案和产物约束见 [stage-plans.md](stage-plans.md)。源码修改支持标准 Android 工程默认输入，本地化支持已解码资源；不支持的引擎输入须使用 type 专属实现。缺少方案、工具或设备时明确失败。

[公共注册表](../stages/sub-stage-register.yaml) 保留全部阶段编号。当前没有缺失公共入口。

路由优先查询各 type 的 register；未命中且公共实现缺失时返回 None，由调用方报错并暂停。缺失不表示阶段可跳过，也不把空实现注册为成功。补实现时须验证后填写 `script`，移除缺失标记，并同步此表及统一索引。

旧 handler 路径仅存在于历史配置/调用方，不列为可用能力。后续迁移应核对其消费者，不能仅凭当前目录为空就删除兼容占位。

## 索引维护

新增、移动或删除逆向脚本时，同步本文件、[统一脚本索引](../../scripts/SCRIPTS-INDEX.md) 和公共注册表。仓库维护脚本存放于 `tools/maintenance/scripts/`，不登记在逆向索引中。
