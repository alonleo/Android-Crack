# Unity Mono Strategy — .NET DLL 逆向策略

> 处理 **Unity Mono / .NET DLL** 项目的专用策略。
>
> 加载顺序：SKILL.md → **[strategy.md（本文件）]** → workflow.md → tools-index.md

---

## 1. 识别特征

| 项 | 期望 |
|----|------|
| `lib/<abi>/GameAssembly.dll` | **必须存在**（Unity Mono runtime） |
| `assets/bin/Data/Managed/.../*.dll` | 多个 .NET DLL（游戏代码） |
| AndroidManifest | `<activity android:name="com.unity3d.player.UnityPlayerActivity"` |

## 2. 阶段序列

```
00 → 00a → 01 → 02 → 03 → mono-03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13
```

类型化分支：
- `mono-03`：.NET DLL 反编译（ILSpy / dnSpy）

## 3. 主要工具

| 用途 | 工具 | 路径 |
|------|------|------|
| 静态反编译 | **ILSpy**（跨平台 Avalonia） | `source-projects/ILSpy/` |
| 静态反编译 + 调试 | **dnSpy**（WPF） | `source-projects/dnSpy/` |
| DLL 重编译 | dnSpy Edit Method → 编译为新 DLL → 替换 | 内置 |
| 动态分析 | Frida hook C# 函数 | 系统安装 |
| Java 层 | jadx | `source-projects/jadx/` |

## 4. 静态分析重点

| 切入点 | 找什么 |
|--------|-------|
| ILSpy 直接打开 `*.dll` | 看到完整 C# 代码 |
| dnSpy 设置断点 + 调用栈 | 运行时行为跟踪 |
| `UnityEngine.MonoBehaviour` 子类 | 关键业务逻辑 |
| `UnityIAP` / `PurchasingManager` | IAP 桥接类 |
| `AdColony` / `AdMob` 桥接类 | 广告桥接 |

## 5. 动态分析重点

```bash
# Frida hook C# 函数
frida -U -l hook-cs.js -f <pkg> --no-pause
hook UnityEngine.MonoBehaviour 子类方法

# dnSpy attach 进程做实时调试
dnSpy → Debug → Attach to Process → <pkg>
```

## 6. 常见坑位

| 坑位 | 现象 | 处理 |
|------|------|------|
| DLL 包签名校验 | 重编译 DLL 后触发反作弊 | Frida hook 签名校验函数返回原签名 |
| 混合调用栈 | C# ↔ Java ↔ Native 三层交错 | 分别 hook |
| dnSpy 兼容 | 老项目 dnSpy 崩溃 | 换 ILSpy；或用 dotPeek |
| Mono runtime 资源占用 | 比 ART 高 | 无解；接受 |

## 7. 阶段细节

详见 [workflow.md](./workflow.md)。

## 8. 已知 APK 示例

- 老版本 Unity 项目（2017 年前后 Unity 默认 Mono，已少见）
- 部分老 King 系游戏

## 9. 关联阅读

- [workflow.md](./workflow.md) — 阶段流程
- [tools-index.md](./tools-index.md) — 工具索引
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（unity-mono 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段主流程
- [../../OBJECTIVES.md §1.3](../../OBJECTIVES.md) — SDK 移除验收
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：unity-mono](../../common/third-party-removal-strategy-skill/references/engine-notes.md#unity-mono)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

