# Android Tools Index — 工具与脚本索引

> 本文件是 android-strategy-skill 的"工具索引"——所有本 skill 用到的工具和脚本。
>
> 加载顺序：strategy.md → workflow.md → **[tools-index.md（本文件）]**

---

## 1. 外部工具（来自 `tools/crack-intergration-tools/`）

| 工具 | 路径 | 用途 | 阶段 |
|------|------|------|------|
| **jadx** | `source-projects/jadx/` | Dex → Java 反编译 | 03 |
| **apktool** | `execable/apktool.jar` | APK 解包 / 打包 | 02 / 17 |
| **apksigner** | `tools/environments/android-sdk/build-tools/34.0.0/apksigner` | APK 签名 | 17 |
| **zipalign** | `tools/environments/android-sdk/build-tools/34.0.0/zipalign` | APK 对齐 | 17 |
| **aapt2** | `tools/environments/android-sdk/build-tools/34.0.0/aapt2` | 资源解码 | 03 / 09 / 12 |
| **Frida** | 系统安装 | 动态 hook（仅当需要） | 18 |

### 1.1 工具版本

| 工具 | 推荐版本 |
|------|---------|
| jadx | 1.5.x+ |
| apktool | 2.11.1 |
| Frida | 16.x+（可选） |

## 2. 模板文件（来自 `skills/common/scripts/template-files/`）

> 普通 Android 类型**不强制使用模板**——直接走 apktool + smali 路线即可。
> 仅当某些高级玩法（如自定义 MainActivity 注入）时才使用模板。

| 模板 | 路径 | 用途 | 何时使用 |
|------|------|------|---------|
| `my.keystore.jks` | `skills/common/scripts/template-files/my.keystore.jks` | 统一签名密钥 | 阶段 17 |
| `LXGWWenKai-Regular.ttf` | `skills/common/scripts/template-files/LXGWWenKai-Regular.ttf` | 中文字体 | 阶段 09/15 |

## 3. Skill 内部脚本

### 3.1 scripts/workflow/（流程脚本）

> Android（普通 Java/Kotlin）类型**无专用流程脚本**。所有阶段由 general-strategy-skill 的通用脚本驱动（01–21 骨架）：
>
> | 调用方式 | 实际脚本 |
> |---------|---------|
> | `crack.py <apk> stage-01` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-record.py` |
> | `crack.py <apk> stage-02` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess.py` |
> | `crack.py <apk> stage-03` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-static-analyze.py` |
> | `crack.py <apk> stage-04` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-entry-points.py` |
> | `crack.py <apk> stage-05` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-extract-all-strings.py` |
> | `crack.py <apk> stage-06` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-ocr.py` |
> | `crack.py <apk> stage-07` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-redraw.py` |
> | `crack.py <apk> stage-08` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-device-verify.py` |
> | `crack.py <apk> stage-09` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-fonts.py` |
> | `crack.py <apk> stage-10` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-device-verify.py` |
> | `crack.py <apk> stage-11` | `skills/common/third-party-removal-strategy-skill/scripts/workflow/sub-stage-remove-sdks.py` |
> | `crack.py <apk> stage-12` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-sdk-device-verify.py` |
> | `crack.py <apk> stage-13` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-feature-removal.py` |
> | `crack.py <apk> stage-14` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-feature-device-verify.py` |
> | `crack.py <apk> stage-15` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-hanization.py` |
> | `crack.py <apk> stage-16` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-hanization-device-verify.py` |
> | `crack.py <apk> stage-17` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-repack-sign.py` |
> | `crack.py <apk> stage-18` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-runtime-verify.py` |
> | `crack.py <apk> stage-19` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-as-build.py` |
> | `crack.py <apk> stage-20` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-final-check.py` |
> | `crack.py <apk> stage-21` | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py` |
>
> 这些脚本的 canonical 副本在 `skills/common/general-strategy-skill/scripts/workflow/`（所有 type 共享），**不**另复制到本 skill。

### 3.2 scripts/common/（通用脚本）

| 脚本 | 角色 |
|------|------|
| `grep-dex-smali.py` | smali 目录中 grep 任意模式（按 SDK 名 / 类名） |
| `filter-dex-jar.sh` | 过滤 dex-jar 中的 R 类冲突 |
| `apksigner-verify.py` | 统一 apksigner verify 输出格式 |

## 4. Skill assets/ 资源

```
assets/
├── README.md                          # 资源索引
├── known-android-games.tsv            # 已知普通 Android 游戏列表
├── proguard-deobfuscation-rules.md    # ProGuard 反混淆规则汇总
└── multi-dex-handling.md              # MultiDex 处理样例
```

| 资源 | 使用时机 | 备注 |
|------|---------|------|
| `known-android-games.tsv` | 启发式预判 | 只追加不删改 |
| `proguard-deobfuscation-rules.md` | 阶段 03 反编译失败时 | 启发式正则 |
| `multi-dex-handling.md` | dex > 5 时 | Frida / jadx 参数参考 |

### 4.1 扩展规则

- 新增资源前必须评估：是项目级（→ `crackings/<type>/<Name>/raw/`）还是 skill 级（→ `assets/`）
- skill 级资源须被 2 个以上项目复用
- 命名 `<scope>-<format>`（如 `multi-dex-handling.md`）

## 5. 工具调用示例

### 5.1 阶段 02（apktool 解包）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-02

# 手动执行（apktool 本身）
java -jar tools/crack-intergration-tools/execable/apktool.jar d \
     -o crackings/<type>/<Name>/raw/01-apktool \
     -f apks/<file>.apk
```

### 5.2 阶段 03（jadx 反编译）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-03

# 手动执行
jadx -d crackings/<type>/<Name>/raw/02-jadx/sources \
     -ds crackings/<type>/<Name>/raw/02-jadx/sources \
     apks/<file>.apk
```

### 5.3 阶段 09（SDK 移除）

```bash
# 策略 A/B：桩化
./skills/common/scripts/crack.py <apk> stage-09

# 策略 C：物理删除
./skills/common/scripts/crack.py <apk> sub-stage-remove
```

### 5.4 阶段 10（重打包 + 签名）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-10

# 手动执行（强制顺序）
java -jar tools/crack-intergration-tools/execable/apktool.jar b \
     crackings/<type>/<Name>/raw/01-apktool \
     -o crackings/<type>/<Name>/project/app-as-generated.apk

zip -d crackings/<type>/<Name>/project/app-as-generated.apk 'META-INF/*.RSA'

zipalign -p -f 4 crackings/<type>/<Name>/project/app-as-generated.apk \
                   crackings/<type>/<Name>/project/aligned.apk

apksigner sign --ks skills/common/scripts/template-files/my.keystore.jks \
                --ks-pass pass:Ab123145 \
                --ks-key-alias jy \
                --key-pass pass:Ab123145 \
                --v1-signing-enabled true \
                --v2-signing-enabled true \
                --v3-signing-enabled true \
                --out crackings/<type>/<Name>/project/patched.apk \
                crackings/<type>/<Name>/project/aligned.apk
```

## 6. 工具下载与更新

> 下载新工具后必须按 AGENTS.md §6 在主仓库工具路径速查表中追加一行。

| 工具 | 仓库 | 备注 |
|------|------|------|
| jadx | https://github.com/skylot/jadx | release jar |
| apktool | https://github.com/iBotPeaches/Apktool | release jar |
| Frida | https://frida.re | pip / npm 安装 |

### 6.1 SHA-256 校验

下载后必须校验 SHA-256 并记录在 `tools/crack-intergration-tools/source-projects/<tool>/CHECKSUM`。

## 7. 关联阅读

- [strategy.md](./strategy.md) — 类型策略
- [workflow.md](./workflow.md) — 阶段流程
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [../../AGENTS.md §6](../../AGENTS.md) — 主仓库工具路径速查表
- [../../OBJECTIVES.md §2](../../OBJECTIVES.md) — 工具版本约束

## 通用去功能点清单

| 文档 | 角色 |
|------|------|
| `../../common/feature-removal-strategy-skill/SKILL.md` | 去功能点统一参考（必须去除的按钮 + 实现方案 + 真机验收项） |

