# Defold 引擎工具与脚本索引

## 工具

| 工具 | 用途 | 路径 |
|------|------|------|
| apktool 2.11.1 | 解包/重打包 | `$APKTOOL` / `tools/crack-intergration-tools/execable/apktool.jar` |
| jadx | Java 反编译 | `$JADX` |
| adb | 真机验证 | `$ADB_BIN` |
| apksigner / zipalign | 签名/对齐 | `$APKSIGNER` / `$ZIPALIGN` |
| strings / readelf | .so 引擎判定 | 系统 binutils |

## 脚本

### workflow/

| 脚本 | 角色 |
|------|------|
| `sub-stage-defold-manifest-clean.py` | Defold 引擎 manifest SDK 清理（保留 smali，防 JNI NoClassDefFoundError） |

> 注意：`sub-stage-defold-manifest-clean.py` 规范存放于 `skills/common/third-party-removal-strategy-skill/scripts/workflow/`（跨 Defold/Cocos 等引擎通用），本 skill 通过 SCRIPTS-INDEX 引用。

### common/

| 脚本 | 角色 |
|------|------|
| `build-defold-hook-native-lib.py` | 编译 Defold SDK hook native-lib.so（And64InlineHook，`-static-libstdc++`） |
| `inject-defold-hook.py` | 注入 hook：拷贝 libnative-lib.so 到 lib/<abi>/ + DefoldActivity.onCreate 注入 `loadLibrary("native-lib")` |

### assets/

| 文件 | 角色 |
|------|------|
| `native-lib.sdk-hook.template.cpp` | Defold SDK hook 模板（dlsym 定位导出符号 + dlopen(RTLD_NOLOAD) 探测时机） |
| `CMakeLists.txt` | hook 编译 CMake 模板（含 And64InlineHook 子目录） |

## 阶段脚本复用

Defold 采用 android 型阶段序列，直接复用 general-strategy-skill 的跨 type 脚本：
`sub-stage-sniff.py` / `sub-stage-assess.py` / `sub-stage-preprocess.py` / `sub-stage-static-analyze.py` / `sub-stage-entry-points.py` / `sub-stage-repack-sign.py` / `sub-stage-runtime-verify.py` / `sub-stage-as-build.py` / `sub-stage-final-check.py`。

## 通用去功能点清单

| 文档 | 角色 |
|------|------|
| `../../common/feature-removal-strategy-skill/SKILL.md` | 去功能点统一参考（必须去除的按钮 + 实现方案 + 真机验收项） |

