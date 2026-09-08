# il2cpp Strategy Skill — Workflow Scripts

> 本目录是 **canonical 副本**，`skills/common/scripts/strategy/strategy-config.yaml` 中 `il2cpp.scripts`
> 为声明式阶段注册的单一事实来源，`crack.py` 通过 `load_stage_registry` + `resolve_stage_script`
> 按注册路径调度。修改脚本后**不需要**双向同步到 `skills/common/scripts/`（已改为声明式注册，无副本）。

---

| 脚本 | 阶段 | 角色 | 强制 |
|------|------|------|------|
| `sub-stage-fake-android.py` | **01** | ASBuilder.jar fake → AS 工程骨架 | ✓ |
| `sub-stage-toolchain-normalize.py` | 02 | AGP/Gradle/SDK/JDK/ProGuard 规范化 | |
| `sub-stage-baseline-device.py` | **03** | 基线编译 + 真机安装 + 启动门禁 | ✓ |
| `sub-stage-wire-templates.py` | **04** | 模板架构接线（MainActivity/SDKUtils/JniBridge/native-lib.cpp） | ✓ |
| `sub-stage-il2cpp-dump.py` | **05** | Il2CppDumper 导出 dump.cs + il2cpp.h | ✓ |
| `sub-stage-hook-plan.py` | 03 (helper) | dump.cs 自动匹配 hook 候选点，输出 hook-plan.yaml | |
| `sub-stage-reward-forwarding.py` | **07** | 激励/IAP 转发（callJava 不硬编码 RVA） | ✓ |
| `sub-stage-reward-device-verify.py` | 08 | 阶段 07 真机验收：30s 无 FATAL | |
| `sub-stage-third-party-cleanup.py` | **09** | 第三方 SDK / 资源 / 网络依赖清理 | ✓ |
| `sub-stage-cleanup-device-verify.py` | 10 | 阶段 09 飞行模式回归 | |
| `sub-stage-ui-hide.py` | **11** | 去功能点（无用功能/按钮/UI 隐藏） | ✓ |
| `sub-stage-ui-device-verify.py` | **12** | 阶段 11 功能点去除真机验收 | ✓ |
| `sub-stage-hanization.py` | **13** | 文本/字体/图片汉化（hanization_map.h 占位） | ✓ |
| `sub-stage-hanization-device-verify.py` | 14 | 汉化真机验收（OCR） | |
| `sub-stage-finalize.py` | **15** | 统一签名 + 交付验收（patched.apk 与 release APK 哈希一致） | ✓ |

## 与 strategy-config.yaml 的关系

- 阶段注册 / 强制标志 / 产物契约见 [skills/common/scripts/strategy/strategy-config.yaml](../../../../skills/common/scripts/strategy/strategy-config.yaml)。
- 旧编号（02b/03b/04b/04c/05a/05b/08b/12b）通过 `legacy_stage_map` 自动迁移到 01–15，无需双份脚本。
