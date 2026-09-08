# 逆向共享脚本与运行支持

本目录仅放逆向项目共享脚本、工具链与策略支持。创建前须声明类别：改名、目录迁移、文档/索引整理等仓库维护脚本独立存放，不进入本目录、统一逆向索引或本子索引，具体规则见根 `AGENTS.md` §1.3。

> 本目录**不存放阶段脚本**。所有阶段脚本已迁出到各 skill：
> - 跨 type 共享的通用阶段脚本 → `skills/common/general-strategy-skill/scripts/workflow/`
> - 类型专用阶段脚本 → `skills/strategy/<type>-strategy-skill/scripts/workflow/`
>
> 修改脚本时以实际调用路径为准，删除前检查代码与注册表引用。

## 目录

```
skills/common/scripts/
├── crack.py / run-*.py   ← 历史兼容与辅助入口
├── strategy/              ← 策略引擎（strategy-config.yaml + strategy-config.py）
├── lib/                   ← 公共函数库（common.py + routing.py）
├── template-files/        ← 模板文件（MainActivity.template.java / SDKUtils.java / my.keystore.jks 等）
├── README.md              ← 本文件
└── (其他辅助工具)
```

## 当前执行模式

Agent 负责 M1 sniff、M2 assess、M3 final-check、M4 cleanup 的判断、记录和验收。M2 子阶段由当前 type 的 `stages/sub_stage-dispatcher.py` 调度，读取 `sub-stage-register.yaml` → `action-register.yaml` → `step-register.yaml` 并执行步骤。

`crack.py`、`run-pipeline.py`、`run-major-*.py`、`run-sub-stage.py` 是保留的历史或辅助入口。部分仍包含旧阶段编号、直调 worker 和批量流程，不能替代当前 type 注册表，不作为新任务默认入口。保留这些文件及兼容路由数据是为了避免破坏现有引用。

## 阶段脚本位置速查

| 脚本类型 | 位置 |
|---------|------|
| 嗅探/评估/解包/打包/签名/OCR/汉化/清理（跨 type 共享） | `skills/common/general-strategy-skill/scripts/workflow/` |
| il2cpp 专用（FakerAndroid/Il2CppDumper/Hook） | `skills/strategy/il2cpp-strategy-skill/scripts/workflow/` |
| Adobe AIR 专用（SWF/ffdec） | `skills/strategy/air-strategy-skill/scripts/workflow/` |
| Cocos2d-x 专用（Lua/so） | `skills/strategy/cocos2dx-strategy-skill/scripts/workflow/` |
| Flutter 专用 | `skills/strategy/flutter-strategy-skill/scripts/workflow/` |
| Unity Mono 专用 | `skills/strategy/unity-mono-strategy-skill/scripts/workflow/` |
| Unreal 专用 | `skills/strategy/unreal-strategy-skill/scripts/workflow/` |
| SDK 移除（第三方） | `skills/common/third-party-removal-strategy-skill/scripts/workflow/` |

> **逆向项目脚本索引**：脚本路径与角色见 **[SCRIPTS-INDEX.md](./SCRIPTS-INDEX.md)**。
> 查找逆向项目脚本时先读该表（AGENTS.md §1.9）；仓库维护脚本不属于本表范围。

## 清理规则

- 不保留旧阶段迁移生成器、硬编码项目路径或 RVA 的一次性探针、编号递增的试验副本。
- 删除前检查代码、注册表和维护中说明的引用；仍被调用的运行库、模板、C# 工具与兼容数据必须先处理调用者。
- 移除脚本时同步索引和子索引；历史经验与项目证据不因目录整理而改写。
- 目录清理校验不等于 APK 构建或真机验收通过，复用保留脚本前仍需核对参数、环境和实际输入。
