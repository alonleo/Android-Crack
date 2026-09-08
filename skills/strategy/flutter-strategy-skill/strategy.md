# Flutter Strategy — Dart AOT 逆向策略

> 处理 **Flutter (Dart AOT 编译)** 项目的专用策略详述。
>
> 加载顺序：SKILL.md → **[strategy.md（本文件）]** → workflow.md → tools-index.md

---

## 1. 识别特征

| 项 | 期望 |
|----|------|
| `lib/<abi>/libflutter.so` | Flutter 引擎 |
| `lib/<abi>/libapp.so` | Dart AOT 编译产物（10-50 MB） |
| AndroidManifest | `<activity android:name="io.flutter.embedding.android.FlutterActivity"` |
| 入口 Dart 类 | `assets/flutter_assets/kernel_blob.bin` 或 `libapp.so` 中 |

## 2. 阶段序列

```
00 → 00a → 01 → 02 → flutter-03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13
```

类型化分支：`flutter-03`（Dart AOT dump）

## 3. 主要工具

| 用途 | 工具 | 路径 |
|------|------|------|
| 静态分析 | **blutter** / **reFlutter** | `tools/crack-intergration-tools/` |
| so 分析 | **Dart SDK** (`dart-disassemble`) + IDA / Ghidra | `tools/` |
| 动态分析 | Frida + And64InlineHook | 系统 / `source-projects/And64InlineHook/` |
| Java 层 | jadx | `source-projects/jadx/` |

## 4. 静态分析重点

| 切入点 | 找什么 |
|--------|-------|
| `libapp.so` 反汇编 | Dart AOT 指令 |
| `blutter` 输出 | 函数签名 + 类层次 |
| Hook 候选点 | Dart IAP / 广告 SDK 桥接 |

## 5. 动态分析重点

```bash
# Frida hook Dart 函数（基于偏移）
frida -U -l hook-dart.js -f <pkg> --no-pause

# Hook Java ↔ Dart 桥接
hook io.flutter.embedding.engine.FlutterJNI
```

## 6. 常见坑位

| 坑位 | 现象 | 处理 |
|------|------|------|
| Dart AOT 反编译不成熟 | blutter / reFlutter 输出质量参差 | IDA + Ghidra 辅助 |
| Flutter 引擎版本升级快 | v1.x → v2.x → v3.x | Hook 点位置每次升级都变 |
| Dart 函数签名混淆 | debug vs release 差异大 | blutter --release-mode |

## 7. 阶段细节

详见 [workflow.md](./workflow.md)。

## 8. 已知 APK 示例

- Google 内部应用（Google Pay）
- Flutter 写的小型独立游戏

## 9. 关联阅读

- [workflow.md](./workflow.md) — 阶段流程
- [tools-index.md](./tools-index.md) — 工具索引
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（flutter 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段主流程
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：flutter](../../common/third-party-removal-strategy-skill/references/engine-notes.md#flutter)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

