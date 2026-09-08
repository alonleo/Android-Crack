# Android Strategy Skill — Assets 资源索引

> 本目录包含 android-strategy-skill 专用的资源文件（heuristic 规则、已知 APK 列表等）。
>
> 加载顺序：tools-index.md → **[assets/README.md（本文件）]**

---

## 目录结构

```
assets/
├── README.md                          # 本文件
├── known-android-games.tsv            # 已知普通 Android 游戏列表
├── proguard-deobfuscation-rules.md    # ProGuard 反混淆规则汇总
└── multi-dex-handling.md              # MultiDex 处理样例
```

## 资源使用规则

| 资源 | 使用时机 | 备注 |
|------|---------|------|
| `known-android-games.tsv` | 启发式预判（嗅探新 APK 时对照） | 只追加不删改 |
| `proguard-deobfuscation-rules.md` | 阶段 03 反编译失败时 | 启发式正则 |
| `multi-dex-handling.md` | dex > 5 时 | Frida / jadx 参数参考 |

## 扩展规则

- 新增资源前必须评估：是项目级（→ `crackings/<type>/<Name>/raw/`）还是 skill 级（→ `assets/`）
- skill 级资源须被 2 个以上项目复用
- 命名 `<scope>-<format>`（如 `multi-dex-handling.md`）

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具与脚本索引
- [../strategy.md](../strategy.md) — 类型策略
- [../workflow.md](../workflow.md) — 阶段流程