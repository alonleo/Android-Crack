# Adobe AIR Strategy — AIR 项目逆向策略

> 处理 **Adobe AIR** 项目（Flash/AIR 移植到 Android）的专用策略。
>
> 加载顺序：SKILL.md → **[strategy.md（本文件）]** → workflow.md → tools-index.md

---

## 1. 识别特征

| 项 | 期望 |
|----|------|
| `assets/META-INF/AIR/application.xml` 或 `META-INF/AIR/application.xml` | **必须存在** |
| `assets/META-INF/AIR/sig` | AIR 应用签名 |
| `assets/*.swf` | ActionScript 字节码（核心游戏代码） |
| AndroidManifest | `<application android:name="air.my.application.AppEntry"` |
| 容器层 Java | air.* 包（AIR 运行时） |

## 2. 阶段序列

```
00 → 00a → 01 → 02 → air-03 → 04 → 05 → 06 → 07 → air-09 → 09 → 10 → 11 → 12 → 13
```

类型化分支：
- `air-03`：SWF 反编译
- `air-09`：AIR 字体嵌入到 SWF

## 3. 主要工具

| 用途 | 工具 | 路径 |
|------|------|------|
| SWF 反编译 | **ffdec**（Java SWF 反编译） | `tools/crack-intergration-tools/source-projects/` |
| Java 层反编译 | jadx | `source-projects/jadx/` |
| AIR SDK | 构建/解包 AIR 包 | `tools/crack-intergration-tools/` |
| 动态分析 | Frida | 系统安装 |
| 重打包 | apktool + smali patch | `execable/apktool.jar` |

## 4. 静态分析重点

| 切入点 | 找什么 |
|--------|-------|
| `ffdec` 导出 SWF ActionScript → `.as` 文件 | 游戏核心逻辑（多数业务代码在 SWF 层） |
| `flash.net.URLRequest` / `URLLoader` / `navigateToURL` | 网络调用（需桩化） |
| IAP / 广告相关 ActionScript | 内购和广告回调 |
| AIR application.xml | 应用元信息 + 启动 SWF |
| Stage3D / OpenGL 调用 | GPU 加速层（难直接 hook） |

## 5. 动态分析重点

```bash
# Frida hook Java 容器层
frida -U -l script.js -f <pkg> --no-pause

# Hook AIR runtime 关键点
hook flash.net.URLLoader              # URLLoader.load()
hook flash.events.EventDispatcher     # 事件分发
```

## 6. 常见坑位

| 坑位 | 现象 | 处理 |
|------|------|------|
| SWF 加密（Alchemy / 字符串混淆） | ffdec 反编译后代码不可读 | ffdec deobfuscator；手动解密常量 |
| 多 SWF 文件 | 主 SWF + 多个 module SWF | 按 application.xml 中 `<contents>` 列表逐一处理 |
| Stage3D GPU 渲染 | GPU 层无法直接 hook | 仅 Java / AS 层 hook；接受 GPU 不可见 |
| AIR 签名校验 | 重打包后启动崩溃 | Frida hook AIR 签名校验函数返回原签名 |
| SWF 字体嵌入 | 中文字体在 SWF 中（而非 assets/） | 阶段 08 用 ffdec 直接替换嵌入字体 |

## 7. 阶段细节

详见 [workflow.md](./workflow.md)。

## 8. 启用条件与回退

| 条件 | 处理 |
|------|------|
| 默认 | type=air 自动触发；嗅探命中 `META-INF/AIR/application.xml` |
| SWF 加密 | 先 ffdec deobfuscator + 字符串解密 |
| Stage3D GPU 限制 | 仅 Java 层 hook，接受限制 |

## 9. 关联阅读

- [workflow.md](./workflow.md) — 阶段流程
- [tools-index.md](./tools-index.md) — 工具索引
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（air 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段主流程
- [../../OBJECTIVES.md §1.5](../../OBJECTIVES.md) — 网络检测去除验收
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：air](../../common/third-party-removal-strategy-skill/references/engine-notes.md#air)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

