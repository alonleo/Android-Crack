# il2cpp 加密 Unity 项目逆向 — 模板与配置

本目录包含 `stage-01`（FakerAndroid fake）与 `stage-06/07/11`（hook 分析 / 转发 / 清理）引用的所有模板与配置。

---

## 目录结构

```
assets/
├── README.md                          ← 本文件
├── frida-hook-template.js             ← Frida 主脚本模板（hook-main.js 基础）
├── and64-inline-hook-template.cpp     ← And64InlineHook C++ 模板（il2cpp_hook_main.cpp 基础）
├── hook-discovery-rules.json          ← 从 dump.cs 自动匹配 hook 目标的正则规则
├── dump.cs-parsing.awk                ← awk 解析 dump.cs 的辅助脚本
└── known-il2cpp-games.tsv             ← 已知 il2cpp 加密游戏列表（启发式参考）
```

---

## 模板说明

### 1. `frida-hook-template.js`

动态 hook 主脚本模板。功能：

- Java 层网络检测 hook（`NetworkInfo.isConnected`）
- 第三方 SDK hook（Umeng / Bugly / Firebase）
- libil2cpp.so 入口点 hook（il2cpp_string_new）
- 自动从 dump.cs 生成的 ENCRYPTION_TARGETS / AUTH_TARGETS 数组

**使用方式**：

```bash
# 1. 启动目标应用
adb shell am start -n <pkg>/<MainActivity>

# 2. attach frida
frida -U -f <pkg> -l app/src/main/cpp/hooks/frida-scripts/hook-main.js --no-pause

# 3. 观察 logcat（hook 命中会打印 [frida-hook] ...）
adb logcat -s frida-hook:V
```

### 2. `and64-inline-hook-template.cpp`

And64InlineHook C++ 模板。结构：

```cpp
// 1. Hook 目标函数桩（每个自动生成的 Hooked*）
void* HookedCls_Mth(void* __this, void* args) { /* TODO */ }

// 2. 注册所有 hook（在 JNI_OnLoad 中调用）
static void registerIl2CppHooks(JNIEnv* env) {
    // - 找 libil2cpp.so 基址（遍历 /proc/self/maps）
    // - 对每个目标调用 A64HookFunction(target, replacement, &original)
}

// 3. JNI_OnLoad 入口
extern "C" JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void* reserved) {
    registerIl2CppHooks(env);
    return JNI_VERSION_1_6;
}
```

**集成到 AS 工程**：

```cmake
# CMakeLists.txt（追加）
add_library(il2cpp-hook SHARED
    hooks/il2cpp_hook_main.cpp
    hooks/And64InlineHook/And64InlineHook.cpp
)
target_link_libraries(il2cpp-hook ${log-lib})
```

### 3. `hook-discovery-rules.json`

从 dump.cs 自动匹配 hook 目标的正则规则集。结构：

```json
{
  "categories": [
    {
      "name": "encryption",
      "patterns": ["Decrypt", "Encrypt", "AesDecrypt", "AesEncrypt", "XorEncrypt", ...],
      "weight": 10
    },
    {
      "name": "auth",
      "patterns": ["CheckLicense", "VerifySignature", "IsAuthed", ...],
      "weight": 8
    },
    {
      "name": "network",
      "patterns": ["SendRequest", "HttpGet", "HttpPost", "ConnectServer", ...],
      "weight": 5
    }
  ]
}
```

可手动添加新规则（如 `AntiCheatCheck`、`RootDetection` 等）。

### 4. `dump.cs-parsing.awk`

awk 辅助脚本，从 dump.cs 抽取方法签名 + offset。`stage-06` 内部使用。

### 5. `known-il2cpp-games.tsv`

已知 il2cpp 加密 Unity 游戏列表（每行：包名 / 加密类型 / 难度 / 备注）。

---

## 自定义扩展

要添加新的 hook 类别：

1. 在 `hook-discovery-rules.json` 增加新 category
2. 在 `frida-hook-template.js` 增加对应的 hook 代码段
3. 在 `and64-inline-hook-template.cpp` 增加对应的 Hooked* 模板
4. 重新跑 `sub-stage-hook-fn-analyze.py`（或 `sub-stage-reward-video-forwarding.py` 重新注入）
   > **注**：`sub-stage-hook-plan.py` 已被 [REFACTOR-2026-08-11-il2cpp-deadcode-cleanup.md](../../../../docs/REFACTOR-2026-08-11-il2cpp-deadcode-cleanup.md) 删除；其 hook-plan.json 生成逻辑需合并到 `sub-stage-hook-fn-analyze.py`（**待跟进**）。