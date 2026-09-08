# Cocos Creator Strategy — JS/TS 逆向策略

> 处理 **Cocos Creator（JS/TS）** 项目的专用策略详述。
>
> 加载顺序：SKILL.md → **[strategy.md（本文件）]** → workflow.md → tools-index.md

---

## 1. 识别特征

| 项 | 期望 |
|----|------|
| `lib/<abi>/libcocos2djs.so` | **必须存在**（JS 引擎 native 库） |
| `assets/src/settings.js` / `assets/src/settings.json` | 项目元信息 |
| `assets/main/config.json` / `assets/internal/config.json` | bundle 配置文件 |
| `assets/src/chunks/*.js` | 3.x SystemJS 模块分块 |
| `assets/cc.common.js` 或 `assets/cc.common.min.js` | 引擎 bundle |
| `assets/resources/` | 原始资源目录 |

## 2. 阶段序列

```
00 → 00a → 01 → 02 → cocos-03 → 04 → cocos-05 → 06 → 09 → 10 → 11 → 12 → 13
```

类型化分支：
- `cocos-03`：so + JS 资源分析
- `cocos-05`：JS 提取与解密（XXTEA / .jsc）

## 3. 主要工具链（6 个工具）

| 工具 | 角色 | 路径 |
|------|------|------|
| **cc-reverse**（首选） | ⭐ 功能最完整：自动检测 2.x/3.x、解密 XXTEA、提取场景/预制体/Spine/DB 资源、还原为可读 TS/JS | `source-projects/cc-reverse/` + `execable/cc-reverse` |
| **reverse** | Cocos ARM64 静态分析，定位并提取 XXTEA 加密密钥（从 `libcocos2djs.so`） | `source-projects/reverse-tool/` + `execable/reverse` |
| **cocos2d-dec** | Python 批处理解密，用 XXTEA 密钥批量解密 .jsc / .lua 文件 | `source-projects/cocos2d-dec/` |
| **JSC-PyDecrypt-Tool** | 命令行 JSC 解密（xxtea+base64 两种加密方式） | `source-projects/JSC-PyDecrypt-Tool/` |
| **frida-cocosjs** | Frida 动态插桩，运行时 Hook Cocos JS 引擎钓出内存密钥 | `source-projects/frida-cocosjs/` |
| **il2Fusion** | Android 侧 Unity/Cocos2d-x Lua 运行时代理（LSPosed + JNI Hook） | `source-projects/il2Fusion/` |

## 4. 静态分析重点

| 步骤 | 操作 |
|------|------|
| **第一步（必需）** | `cc-reverse --path <APK解包目录> --verbose` 自动检测版本、解密 .jsc、重建项目 |
| **第二步** | 若 .jsc 解密失败，用 `reverse libcocos2djs.so` 从 ARM64 原生库提取 XXTEA 密钥 |
| **第三步** | 拿到密钥后，用 `cocos2d-dec` 或 `JSC-PyDecrypt-Tool` 批处理解密所有 .jsc 脚本 |
| **第四步** | 分析还原出的 TS/JS，定位 IAP、广告、网络检测等目标逻辑点 |
| CCON 二进制解码 | `cc-reverse` 自动解析 `.cconb` / `.ccon`（v1 JSON / v2 notepack） |

## 5. 动态分析重点

```bash
# Frida hook libcocos2djs.so 内 JS 执行函数
frida -U -l frida-cocosjs/hook-cocos.js -f <pkg> --no-pause

# frida-cocosjs 提供现成脚本 Hook Cocos JS 引擎、运行时提取 XXTEA 密钥
# il2Fusion 适用于 Lua 版 Cocos2d-x 的运行时文本捕获与替换
```

## 6. 常见坑位

| 坑位 | 现象 | 处理 |
|------|------|------|
| JSC 加密是关键区分点 | 未加密直接提取；加密项目必须先解密钥 | cc-reverse 自动 + 失败回退 |
| cc-reverse 自动提取密钥失败 | application.js / src/settings.json 不可读 | 用 `--key` 参数手动指定 |
| version-hint | 自动检测失败 | `--version-hint 2.3.x\|2.4.x\|3.x` 强制指定 |
| bundle 感知 | 3.x 项目按 `config.json` 中的 bundle 组分别处理 | main / internal / resources / 自定义 |
| 脚本恢复差异 | 2.x 用 browserify；3.x 用 SystemJS | cc-reverse 自动处理 |
| Spine/DragonBones 骨骼动画 | 骨骼数据 + Atlas + 纹理 | cc-reverse 支持直接提取 |

## 7. 阶段细节

详见 [workflow.md](./workflow.md)。

## 8. 已知 APK 示例

- Cocos Creator 2.x 游戏（`libcocos2djs.so` + `src/settings.js` + `src/project.js`）
- Cocos Creator 3.x 游戏（`application.js` + `src/settings.json` + 多 bundle）
- 合成大西瓜等经典 Cocos Creator 开源项目

## 9. 关联阅读

- [workflow.md](./workflow.md) — 阶段流程
- [tools-index.md](./tools-index.md) — 工具索引
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（cocos-creator 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段主流程
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：cocos-creator](../../common/third-party-removal-strategy-skill/references/engine-notes.md#cocos-creator)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

