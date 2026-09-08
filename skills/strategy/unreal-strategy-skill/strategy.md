# Unreal Strategy — UE4/UE5 逆向策略

> 处理 **Unreal Engine 4/5** 项目的专用策略详述。
>
> 加载顺序：SKILL.md → **[strategy.md（本文件）]** → workflow.md → tools-index.md

---

## 1. 识别特征

| 项 | 期望 |
|----|------|
| `lib/<abi>/libUE4.so` | UE4 标准 native 库 |
| `libUnreal.so` | 旧 UE |
| `libUnrealEngine.so` | UE5 |
| `assets/<ProjectName>/Content/Paks/*.pak` | 资源包 |
| AndroidManifest | `<activity android:name="com.epicgames.unreal.GameActivity"`（UE4 标准入口） |

## 2. 阶段序列

```
00 → 00a → 01 → 02 → unreal-03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13
```

类型化分支：
- `unreal-03`：资源包（.pak）提取

## 3. 主要工具

| 用途 | 工具 | 路径 |
|------|------|------|
| 静态分析（资源） | **UE dumper** / **FModel** | `tools/crack-intergration-tools/` |
| so 分析 | **IDA** / **Ghidra** | 系统 / `tools/` |
| 动态分析 | Frida + And64InlineHook | 系统 / `source-projects/And64InlineHook/` |
| Java 层 | jadx | `source-projects/jadx/` |
| 重打包 | apktool | `execable/apktool.jar` |

## 4. 静态分析重点

| 切入点 | 找什么 |
|--------|-------|
| `.pak` 解包后 | `.uasset` / `.umap` / `.ubulk` |
| 寻找 Lua 脚本 | UE4 部分项目用 Lua 扩展 |
| IAP 在 C++ 层 | so 分析（libUE4.so） |

## 5. 动态分析重点

```bash
# Frida hook libUE4.so（基于 RVA）
frida -U -l hook-ue.js -f <pkg> --no-pause

# And64InlineHook 静态 hook（编译进 APK）
A64HookFunction(target, HookedIAP, &orig)
```

## 6. 常见坑位

| 坑位 | 现象 | 处理 |
|------|------|------|
| libUE4.so 体积极大 | 100-500 MB | 高性能机器 + 充足内存（32GB+） |
| .pak 加密 | 资源包解包失败 | UE dumper + 偏移解包 |
| 多 ABI 编译产物 | APK 体积极大（500MB+） | abiFilters 仅保留 arm64-v8a |
| C++ 反射类名混淆 | 类名变 a/b/c | IDA 符号恢复脚本；开启 bUseUnityBuild |

## 7. 阶段细节

详见 [workflow.md](./workflow.md)。

## 8. 已知 APK 示例

- 国内大型 UE4 手游（MMO、吃鸡）
- 海外 PUBG Mobile 原版（UE4）

## 9. 关联阅读

- [workflow.md](./workflow.md) — 阶段流程
- [tools-index.md](./tools-index.md) — 工具索引
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（unreal 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段主流程
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：unreal](../../common/third-party-removal-strategy-skill/references/engine-notes.md#unreal)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

