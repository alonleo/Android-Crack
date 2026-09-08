# 公共阶段输入与执行契约

这些入口用于已生成的 Android Studio 工程。由当前 type 的注册调度链调用，参数也可通过 `NAME`、`TYPE` 环境变量传入。没有通用方式从任意游戏自动推断购买、奖励、UI 或本地化逻辑，方案必须来自项目分析；公共脚本负责严格执行、验证和记录方案。

## 入口与公共输入

新增入口都接受 `--name <项目名>`、`--type <引擎类型>`、`--plan <方案路径>`。未指定方案路径时读取 `crackings/<type>/<Name>/plans/<阶段英文名>.json`。`record-project-files` 不需要方案。

- 项目目录固定为 `crackings/<type>/<Name>/project/`。
- 方案内工程路径相对 `project/`；外部替换素材和参考截图路径相对该项目的 `crackings/<type>/<Name>/`。
- 拒绝越界路径、缺失文件、错误输入类型和不支持的资源格式。
- 运行前加载 `tools/environments/env.sh`。构建需要该环境的 `JAVA_HOME`、`APKSIGNER`，设备验证需要 `ADB_BIN`、`AAPT2`。不使用系统同名工具兜底。
- 修改阶段执行工程 wrapper 的 `:app:clean :app:assembleRelease`，要求唯一 release APK、v1/v2/v3 签名以及与 `project/patched.apk` 完全一致的 SHA-256。失败不发布新 patched.apk；源码修改保留供诊断和重跑。
- 设备阶段验证的 APK 必须与工程唯一 release 输出一致；断言绑定实际 APK 包名和明确在线设备。
- 依赖：Python 3、PyYAML；字体、图片与设备截图验证额外需要含 FreeType 的 Pillow。维护测试不需要 Android 工具或设备，不代表已完成真实构建/真机验收。

输出目录按当前 type/common register 的编号动态生成：`stages/<ID>-<stage>/`。`execution-report.json` 记录执行结果和证据，`accepted` 始终为 false，须由 Agent 检查后按 AGENTS.md 更新阶段验收状态。失败写入 `status.yaml` 的 `current_stage`、`failed_stages` 和原因，不删除无关状态；缺设备也必须停在该阶段。

## SDK/网络、收益和 UI 修改

入口：`sub-stage-sdk-network-removal.py`、`sub-stage-revenue-forwarding.py`、`sub-stage-ui-hide.py`。

方案是 JSON 对象，`schema_version` 必须为 1，`edits` 为明确的源码替换列表。每项必须包含：

| 字段 | 含义 |
|---|---|
| `path` | 工程相对文件路径 |
| `before` / `after` | 精确旧文本与新文本；必须不同 |
| `count` | 旧文本的预期出现次数，正整数 |
| `before_sha256` | 修改前完整文件字节的 SHA-256，小写十六进制 |
| `after_sha256` | 修改后完整文件字节的 SHA-256，小写十六进制 |

一个文件只允许一项；多处修改可在同一项中指定完整文件前后内容。先校验整批文件，再写入。重跑时完整文件匹配 after 哈希才能认定已应用，仍会执行构建。

只接受标准默认构建输入：`app/src/main/AndroidManifest.xml`、`java/` 和 `kotlin/` 下源码、`res/` 下 XML，以及 `assets/` 下明确的文本运行资源。不接受松散 smali、C#、native 源码或封装引擎文件；这些需要 type 专属转换和构建链。

SDK 阶段还接受 `manifest` 对象，可与 `edits` 合用：

- `path` 必须为 `app/src/main/AndroidManifest.xml`。
- `remove` 是 `{tag, name}` 列表，按 Android 命名空间的 `android:name` 精确匹配。支持 activity、activity-alias、service、receiver、provider、meta-data、uses-permission、uses-permission-sdk-23。
- 同样要求完整文件的 `before_sha256`、`after_sha256`。首次运行必须找到待移除条目；重跑须匹配 after 哈希且条目确已不存在。
- Manifest 通过保留注释的 ElementTree 解析，并按 UTF-8、含 XML declaration 序列化。生成 after 哈希时必须以这个结果为准；序列化可能调整命名空间前缀与空白。

脚本不会凭 SDK 名称批量删除代码，也不会凭函数名称自动改写收益结果。方案必须涵盖依赖和调用路径，后续设备断言负责验证目标行为。

## 文本汉化

入口：`sub-stage-text-hanization.py`。方案示例：

```json
{
  "files": [{
    "path": "app/src/main/res/values/strings.xml",
    "format": "android-xml",
    "replacements": [{"source": "Play", "target": "开始游戏", "count": 1}]
  }]
}
```

`android-xml` 精确匹配 string、string-array/item、plurals/item 的完整内部 XML；保留原文件注释、属性与空白，不修改 `translatable="false"` 条目。`text` 格式用于已解码的 UTF-8 文本片段；JSON 输入和输出均须可解析，XML 必须使用 `android-xml`。两种格式都保护格式占位符、转义和标签顺序。拒绝含 NUL 的二进制输入、歧义匹配及相互重叠的规则。

## 字体与图片替换

字体入口 `sub-stage-font-replace.py` 的方案示例：

```json
{
  "replacements": [{
    "source": "inputs/fonts/chinese.ttf",
    "target": "app/src/main/assets/fonts/game.ttf",
    "required_characters": "开始游戏设置退出"
  }]
}
```

必须保留 standalone TTF/OTF 格式；通过 FreeType 加载及 Unicode cmap 验证 `required_characters` 的字形存在。传入全部目标文本所需字形；字体存在不等于设备排版已正确，须执行后续参考图验证。

图片入口 `sub-stage-image-hanization.py` 同样使用 `replacements` 列表，每项只有 `source` 和 `target`。源文件是已翻译图片。校验 PNG/JPEG/WEBP 的格式、尺寸、像素模式、透明表示和色彩配置一致。字体和图片目标仅支持 `app/src/main/assets/` 或 `res/` 下已有资源。动画、九宫格、字体集合与打包引擎纹理需专属处理。

## 五个设备验证入口

适用于 revenue、ui-hide、font、text、image 的 `*-device-verify.py`。通用方案示例：

```json
{
  "apk": "patched.apk",
  "package": "com.example.game",
  "activity": ".MainActivity",
  "settle_seconds": 3,
  "checkpoints": [{
    "name": "main-menu",
    "purpose": "main menu text",
    "actions": [],
    "assertions": [{"kind": "ui", "attribute": "text", "value": "开始游戏", "present": true}]
  }]
}
```

可指定 `serial`，否则用 `ANDROID_SERIAL`，再否则要求恰好一台在线设备。操作只允许数值 tap、swipe、keyevent、wait；不会执行方案传入的任意 shell 命令。每个 checkpoint 必须有唯一安全名称、目的和非空断言。

| 操作或断言 | 字段 |
|---|---|
| tap | `kind: "tap"`、`x`、`y` |
| swipe | `kind: "swipe"`、`x1`、`y1`、`x2`、`y2`、`duration_ms` |
| keyevent | `kind: "keyevent"`、`code`（数值） |
| wait | `kind: "wait"`、`seconds`（0–60） |
| UI | `kind: "ui"`、`attribute` 为 text/resource-id/content-desc、`value`、`present` |
| 截图 | `kind: "screenshot"`、`reference`（项目内独立审核的 PNG）、`max_mean_error`（0–0.1）、`region: [x, y, width, height]`（字体/图片必填） |

必须有正向页面断言或参考截图。UI 隐藏还要求负向目标断言；收益验证的 purpose 为 reward/purchase/local-state，并按实际交互设计状态断言；文本验证要求预期文字或参考图；字体、图片要求参考截图和具体目标区域。参考图尺寸必须匹配设备，区域必须在图内，阈值应按目标区域差异设定，不能用刚采集的结果冒充预期图。

验证记录安装/启动响应、稳定的目标进程 PID、启动时间后的目标 PID 日志、PNG、UI XML、断言结果、APK/截图/参考图哈希，以及待 Agent 固化的 `experience-sync-task.json`。没有断言、离线设备、安装失败、崩溃、进程重启或目标不匹配均失败。不卸载已有应用，不改变设备网络设置。此模块只覆盖当前方案中的页面和行为，不能据此声明整个游戏已验收。

## 工程文件记录

`sub-stage-record-project-files.py` 不需要修改方案。检查 AS 必要文件、签名密钥和 APK；要求 patched.apk 与唯一 release 哈希一致并通过三种签名验证。生成：

- `output-project-manifest.yaml`：源文件路径、大小、SHA-256，以及 release 路径/哈希/签名证据。
- `dir-index.yaml`：项目目录清单。
- 通用 `execution-report.json`：本阶段的执行证据。

源码清单不收录 `.git`、`.gradle`、build、Python 缓存；密钥仅记录文件哈希，不输出密钥内容。记录阶段不替代前序设备验收，也不将项目状态自动改为全部完成。
