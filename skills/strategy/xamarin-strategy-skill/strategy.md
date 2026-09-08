# Xamarin Strategy — Mono Runtime 逆向策略

> 处理 **Xamarin (Mono runtime)** 项目的专用策略详述。
>
> 加载顺序：SKILL.md → **[strategy.md（本文件）]** → workflow.md → tools-index.md

---

## 1. 识别特征

| 项 | 期望 |
|----|------|
| `lib/<abi>/libmonodroid.so` | **必须存在** |
| `libmono-native.so` / `libxamarin-app.so` | 备选（不同版本） |
| AndroidManifest | 可能含 `<application android:name="mono.android.app.Application"` |
| `assemblies/*.dll` | 多个 .NET DLL 打包为 assemblies |

## 2. 阶段序列

```
00 → 00a → 01 → 02 → 03 → mono-03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13
```

类型化分支：`mono-03`（同 Unity Mono — ILSpy / dnSpy）

## 3. 主要工具

| 用途 | 工具 | 路径 |
|------|------|------|
| 静态反编译 | **ILSpy** / **dnSpy** | `source-projects/ILSpy/` + `source-projects/dnSpy/` |
| DLL 重编译 | dnSpy Edit Method | 内置 |
| 动态分析 | Frida hook managed code | 系统安装 |
| Java 层 | jadx | `source-projects/jadx/` |

## 4. 静态分析重点

| 切入点 | 找什么 |
|--------|-------|
| ILSpy 打开 `assemblies/<app>.dll` | 完整 C# 代码 |
| 寻找 IAP / 广告桥接类 | 业务逻辑 |

## 5. 动态分析重点

```bash
# Frida hook managed code
frida -U -l hook-managed.js -f <pkg> --no-pause

# dnSpy attach 进程
dnSpy → Debug → Attach to Process → <pkg>
```

## 6. 常见坑位

| 坑位 | 现象 | 处理 |
|------|------|------|
| DLL 包签名校验 | 重编译触发反作弊 | Frida hook 签名校验函数 |
| 混合调用栈 | C# ↔ Java ↔ Native 三层交错 | 分别 hook |
| Mono runtime 资源占用 | 比 ART 高 | 接受；或换 dnx / netcore |

## 7. 阶段细节

详见 [workflow.md](./workflow.md)。

## 8. 已知 APK 示例

- 老 Xamarin 商业应用（企业内部应用、跨平台 productivity 应用）
- 游戏较少使用 Xamarin（性能与生态问题）

## 9. 关联阅读

- [workflow.md](./workflow.md) — 阶段流程
- [tools-index.md](./tools-index.md) — 工具索引
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（xamarin 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段主流程
- 工具复用：[unity-mono-strategy-skill/tools-index.md](../unity-mono-strategy-skill/tools-index.md) — 同一套 ILSpy/dnSpy
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：xamarin](../../common/third-party-removal-strategy-skill/references/engine-notes.md#xamarin)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

