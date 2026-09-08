# IL2CPP Unity 项目汉化方案总览

> 面向「Unity + IL2CPP」手游（含联网单机）的文本汉化。整理自网络公开资料 + 本工作区既有管线。
> 核心前提：**IL2CPP 把 C# 写死的字符串字面量从托管代码里拿出来，存进 `global-metadata.dat`**。
> 这与 Mono（可直接改 `Assembly-CSharp.dll`，难度低很多）完全不同，是 IL2CPP 汉化所有坑的根源。

---

## 0. 先判断文本存在哪（决定用哪套方案）

Unity IL2CPP 游戏的文字可能分散在 4 处，**必须逐一确认**，再选对应工具：

| 文本存放位置 | 形态 | 典型体积 | 工具 |
|---|---|---|---|
| **global-metadata.dat** | 代码里硬编码的 C# 字符串字面量（最核心） | 大（单作可达 5 万+ 条） | Il2CppDumper + stringliteral-patcher |
| **data.unity3d / .assets** | 场景里 MonoBehaviour 的 `m_Text` / TextMeshPro 组件 | 中 | UnityPy / UABE(AssetStudio) |
| **res/values/strings.xml** | Android 资源字符串 | 小 | 直接改 XML（工作区 frida-policy 常用） |
| **AssetBundle / Addressables** | 外部化的对白/剧情文案 | 视游戏而定 | AssetStudio / UABE 解析后单独处理 |
| **内嵌字形的图片（png/astc）** | 文字烧录在贴图里的 UI / 无字体文本 | 视游戏而定 | OCR + 图片重绘（image-hanization） |

> 经验：**先解包原 APK，抓一张主菜单截图 + logcat，看哪些文字是「写死的 UI / 代码字符串」而非外部资源**，再决定主攻 metadata 还是 assets。参考工作区 `hanize-unity-texts.py` / `collect-ui-texts.py` 的提取流程。

---

## 1. 方案 A：global-metadata.dat 字符串字面量静态替换（主流）

这是 IL2CPP 汉化的**标准答案**。思路：提取 metadata 里所有字符串 → 翻译 → 依据原索引写回 -> 重打包。

### 工具链
1. **Il2CppDumper**（Perfare，★9.3k）——读 `libil2cpp.so` + `global-metadata.dat`，导出：
   - `dump.cs`（类/方法签名，供 hook 用）
   - `il2cpp.h` / `script.json`
   - **`stringliteral.json`（所有字符串字面量，按 index 组织）** ← 汉化主入口
   - `DummyDll/`（可反编译的伪托管程序集）
2. **il2cpp-stringliteral-patcher**（jozsefsallai，★60，MIT）——真正写回的工具：
   ```
   python3 extract.py -i global-metadata.dat -o strings.json     # 导出
   python3 patch.py  -i original-global-metadata.dat -p strings.json -o patched.dat  # 回写
   ```
   - JSON 格式 `{ "index": 12345, "value": "译文" }`；**`index` 永远不改**，`value` 换成中文。
   - `patch.py` 会**重建** metadata，因此**中英文长度不同也能行**（放宽了「同长度替换」限制）。
   - 只能替换却未命中的条目会原样保留（patch.py 自动跳过非译文条目）。
3. **meta-string-edit**（MiddleRed，Go CLI + `pip install metastringedit` / Python 绑定）——单条/批量/正则搜索替换：
   ```
   metastringedit <file> -d -o strings.json        # dump 全部
   metastringedit <file> -e "12345=译文" -o out.dat # 改第 N 条
   metastringedit <file> -r 'PATTERN'              # 正则搜
   ```
4. **il2cpp-string-loc-toolkit**（Show-o4210）——把上面这套**包装成一条汉化流水线**（面向日文→简体中文，但可改源语种）：
   - `extract → filter(分 P0/P1/skip) → 机翻(deep-translator, 在线 Google) → merge → validate → apply(基于 backup 写回) → verify`
   - 内置 `glossary/terms.md` 保护专名 / `<color>` / `{0}` 占位符
   - 8 步：`self-check / all-pretranslate / batch / auto-translate / post-fix / merge / validate / apply / verify`

### 关键护栏（否则闪退）
- **永远基于原始 backup 打补丁**，禁止在已改的 metadata 上反复改（偏移变化会毁指针）→ il2cpp-string-loc-toolkit 明确要求 `backup/global-metadata.dat.original`。
- **index 不可改**；占位符 `%s / %d / {0} / <color>` 必须保留。
- **只翻游戏文本，别碰引擎 /.NET 内部字符串**（Unity、System.* 等），否则运行期行为异常——用 skip 清单排除。
- **metadata 可能加密**：若解包后文件头不是标准 media 头、或 extract 报 "Invalid global-metadata file"，说明被加壳/魔改。此时**静态改不了**，需用 **Zygisk-Il2CppDumper**（运行时 Dump 解密后的内存 metadata）或真机/模拟器运行时 dump，再回写。
- 老 Unity（5.x）或前沿版本可能不被 patcher 识别，需更换组件。

---

## 2. 方案 B：data.unity3d / .assets 资产文本替换（免 hook）

针对**场景里 Text/TextMeshPro 组件的 `m_Text`**。工作区已落地：`hanize-unity-texts.py`（UnityPy，字节级补丁，**变长重写** `set_raw_data`）。

```
python3 hanize-unity-texts.py <data.unity3d> <translations.json> [-o out] [--dry-run]
```
- 扫描 BundleFile 各场景 MonoBehaviour → 匹配 `m_Text` 字符串（int32 len + UTF-8）→ 命中翻译表则用 `set_raw_data` 重写该 MB。
- **优点**：纯静态、不依赖 hook、ARM32/ARM64 通用、可变长。
- **缺点**：只覆盖场景挂载的 Text 组件；**改 data.unity3d 有风险**（经验：改坏了 UI 全丢），务必备份 + dry-run 预览 + 真机验证。
- 主流 GUI 替代：**UABE / AssetStudio**（注意：UABEA 是 .NET 工具，无 Python 绑定；要 Python 用 UnityPy）。

---

## 3. 方案 C：运行时 native hook 替换文本（A64HookFunction）

工作区 text-hanization 的做法：把译文编进 `hanization_map.h`（`HANIZATION_MAP`），在 native-lib.cpp 用 **A64HookFunction** 拦截字符串返回/构造，运行时换成中文。与方案 A（静态改 metadata）互补。

- **适用**：metadata 加密改不动 / 不想动 assets / 需要按 Game 逻辑动态换文案。
- **产物**：`crackings/<type>/<Name>/project/app/app/src/main/cpp/hanization_map.h` + `res/values-zh-rCN/strings.xml`（system 层字符串）。
- **约束**（见 `il2cpp-android-frida-policy`）：A64HookFunction 必须挂 **Injected** 函数体而非单指令 thunk（thunk 一挂即 SIGSEGV）；Frida 只用于查询/侦察，**禁止 Frida 做持久化汉化**。

---

## 4. 方案 D：图片烧字文本处理（image-hanization）

文字若是烧录在贴图里的（中文公告图、按钮美式字、无字体 UI），需：
1. **OCR** 识别原内容（工作区 `sub-stage-image-device-verify.py` 反向验收用 OCR）
2. **重绘**：背景抹除 + 用中文字体重排 + 贴回（注意 **9-patch 边界保留**、不变形不拉伸）
3. 产物：`res/drawable*/<translated>.png` + `images-manifest.yaml`
4. 硬指标：主流程 20+ 张含文字图片替换 + 无黑边/变形。

---

## 5. 方案 E：字体（CJK 字形）处理 ⚠️

替换文案后中文能否显示，取决于**字体是否含中文字形**。

- **Unity 6 / TextCore 动态字体**：会**自动 fallback 到 Android 系统 NotoSansCJK**，中文正常显示 → **不需要注入字体**。先 OCR/截图确认是不是真豆腐块，别盲目注入。
- **老 Unity（无 TextCore fallback）**：静态替换 `m_FontData` 会 **SIGTRAP / libunity.so 断言** 崩溃 —— 正确的 re-bake（同时重生成 `m_CharacterRects` + `m_Texture`）本工作区脚本做不到，仅记录失败路径（`replace-game-font.py`）。
- 工作区 font-replace 阶段标准做法：把中文字体落 `res/font/notosanssc.ttf`，`Typeface.createFromAsset` 加载无异常即通过。

---

## 6. 方案选型速查表

| 文本来源 | 首选方案 | 说明 |
|---|---|---|
| 代码硬编码字符串（最常见） | **A：metadata 静态替换** | Il2CppDumper + stringliteral-patcher |
| 场景 Text/TMP 组件 | **B：UnityPy 改 assets** | 免 hook，但破坏 UI 风险高 |
| metadata 加密 | **C 或 Zygisk dump** | 先运行时 dump 解密，或改走 native hook |
| Android 层/系统 UI 字符串 | **res/values-zh-rCN** | 直接改 strings.xml |
| 贴图烧字 | **D：OCR + 重绘** | 注意 9-patch 边界 |
| 中文显示豆腐块 | **E：确认是否需要字体** | Unity 6 自动 fallback，通常不用动 |

**推荐组合（工作区 il2cpp 标准流程）**：
```
03-fn-analyze (Il2CppDumper 导出 stringliteral.json)
→ 09 font-replace (确认/注入中文字体)
→ 11 text-hanization (hanization_map.h 钩子 + strings.xml)
→ 13 image-hanization (OCR 重绘)
→ 11/13/15 真机验收 (OCR 抓屏见中文 + 无崩溃)
```

---

## 7. 通用避坑清单

1. **Metadata 加密** → 静态改不动，用 Zygisk-Il2CppDumper / 运行时 dump。
2. **metadata vs assets 混淆** → 先解包确认文字实际存放位置，别一上来就改 assets。
3. **改 assets 破坏 UI 加载** → 必带 `--dry-run` + 真机截图对比。
4. **中英长度** → 现代 patcher 支持变长重建，但**必须基于 backup**。
5. **占位符 / 格式化串** → `%s %d {0} <color>` 必须保留。
6. **引擎串误翻** → 用 skip 清单排除 Unity/System.* 内部字符串。
7. **Hook 挂 thunk 崩溃** → A64HookFunction 挂 Injected 函数体。
8. **Frida 持久化** → 禁止；只准侦察，持久化必须写回 native-lib.cpp。
9. **豆腐块** → 先确认 Unity 版本，Unity 6 通常自动 fallback，别盲目注入字体。
10. **真机验收** → 编译通过/安装成功 ≠ 汉化完成；必须 OCR 命中中文 + 无 FATAL。真机无法验证时暂停并记录，禁止跳过。

---

## 8. 工具索引

| 工具 | 用途 | 链接 |
|---|---|---|
| Il2CppDumper (Perfare) | 读 libil2cpp.so + metadata，导出 dump.cs / stringliteral.json | github.com/Perfare/Il2CppDumper |
| Zygisk-Il2CppDumper | 运行时 dump 加密 metadata | github.com/Perfare/Zygisk-Il2CppDumper |
| Il2CppInspector (djkaty) | 逆向源码 + C++ scaffold（配 hook） | github.com/djkaty/Il2CppInspector |
| il2cpp-stringliteral-patcher | extract + patch metadata 字符串 | github.com/jozsefsallai/il2cpp-stringliteral-patcher |
| meta-string-edit | Go CLI / Python 绑定，搜改 metadata 字符串 | pip install metastringedit |
| il2cpp-string-loc-toolkit | 日→中全流程汉化流水线（可改源语种） | github.com/Show-o4210/il2cpp-string-loc-toolkit |
| UnityPy | Python 解析 data.unity3d / assets | pip install UnityPy |
| UABE / AssetStudio | GUI 改资产（无 Python 绑定，.NET） | github.com/AssetStudio |
| 工作区 hanize-unity-texts.py | 场景 Text 组件静态汉化（免 hook） | skills/strategy/il2cpp-strategy-skill/scripts/common/ |
| 工作区 replace-game-font.py | 记录静态字体替换失败路径（勿用于正式） | 同上 |

---

## 9. 中文社区实操帖（52pojie / CSDN / 看雪）

> 已通过 HTTP 200 可达性校验，均为真实页面。52pojie 部分帖子正文可能「回复可见」，需登录观看。
> **注意平台区分**：标「PC/BepInEx」的是桌面版 Unity 的 XUnity.AutoTranslator 插件流，**不适用于 Android ITL2CPP**；
> Android 场景看「手机逆向/Il2CppDumper/资源提取」类。

### 52pojie（吾爱破解）
| 标题 | 链接 | 说明 / 平台 |
|---|---|---|
| 一次Unity引擎gal游戏TextMesh Pro字库汉化记录 | https://www.52pojie.cn/thread-1588559-1-1.html | TextMeshPro 字库汉化，GalGame，接近 Text 组件改字 |
| unity逆向手机游戏资源提取+游戏汉化 | https://www.52pojie.cn/thread-1689096-1-1.html | **Android 场景**：资源提取 + 汉化 |
| Galgame汉化中的逆向(五)：Switch平台Unity后端il2cpp分析 | https://www.52pojie.cn/forum.php?mod=viewthread&tid=1236497 | **il2cpp 后端逆向 + 汉化**，价值最高 |
| Unity游戏改头换面之-汉化以及替换图片 | https://www.52pojie.cn/thread-1024343-1-1.html | 改文本 + 替换图片（含烧字图处理） |
| Unity游戏汉化解包求助TextAsset乱码 | https://www.52pojie.cn/thread-1589716-1-1.html | TextAsset 乱码调试（对应方案 B 坑 3） |
| UnityDebug-打印出Unity游戏场景以及UI信息 | https://www.52pojie.cn/thread-1023568-1-1.html | 侦察场景/UI，定位文本来源的辅助帖 |

### CSDN
| 标题 | 链接 | 说明 / 平台 |
|---|---|---|
| Unity Il2cpp汉化资源位置总结 | https://blog.csdn.net/MarketAndTechnology/article/details/107843171 | **最贴主题**：il2cpp 汉化资源位置（对应方案 A/B） |
| 教你使用IL2CppDumper从Unity il2cpp二进制导出 | https://linxinfa.blog.csdn.net/article/details/116572369 | Il2CppDumper 实操导出流程 |
| Unity构架解析：Unity IL2CPP脚本后端概述 | https://blog.csdn.net/gitblog_00891/article/details/161952560 | 原理铺垫 |
| IL2CPP游戏汉化实战：BepInEx+XUnity.AutoTranslator 5.4.0 | https://blog.csdn.net/weixin_28025327/article/details/162715018 | **PC/BepInEx**，勿用于 Android |
| Unity游戏自动汉化实战：BepInEx与XUnity.AutoTranslator全解析 | https://blog.csdn.net/weixin_29002595/article/details/162803407 | **PC/BepInEx** |
| XUnity.AutoTranslator IL2CPP翻译失效修复完全指南 | https://blog.csdn.net/gitblog_00495/article/details/159485362 | **PC/BepInEx** |
| 5分钟实战Unity游戏汉化：XUnity.AutoTranslator完全使用指南 | https://blog.csdn.net/gitblog_00048/article/details/162506504 | **PC/BepInEx** |

### 看雪（补充）
| 标题 | 链接 | 说明 |
|---|---|---|
| 《原创》什么？IL2CPP APP分析这一篇就够啦！ | https://bbs.kanxue.com/thread-282821-1.htm | IL2CPP 逆向分析全景（手机反调试/结构） |

> 检索说明：中文站对「global-metadata 字符串替换」类实操帖索引偏弱，主流公开教程集中在
> ① Il2CppDumper 提取；② XUnity.AutoTranslator（但那是 PC/BepInEx）；③ 手机端多靠社区讨论帖。
> 真正的 Android 端推荐按本文档 §1 方案 A（Il2CppDumper + stringliteral-patcher）执行，CSDN/52pojie 帖仅作交叉参考。
