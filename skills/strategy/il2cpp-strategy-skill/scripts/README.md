# il2cpp scripts/ — Skill 脚本库（01–29 重排后）

> 本目录是 il2cpp skill 的脚本库，分三类：
> - `workflow/` — 流程脚本（每阶段专用，命名 `stage-<NN>-*.py`，重排为 04–29，共 26 个）
> - `common/` — 通用脚本（跨阶段工具，命名 `<verb>-<scope>.py`）
> - `lib/stage_common.py` — 阶段公共工具（ADB/Gradle/路径/进度/日志）
>
> **声明式调度**：阶段脚本由 `skills/common/scripts/strategy/strategy-config.yaml`（`il2cpp.scripts`）
> 注册，`crack.py` 按注册路径加载执行。修改 workflow 脚本后**无需**复制到 `skills/common/scripts/`。
>
> 01–02（sniff + assess）来自 general-strategy-skill，03（通用静态分析）来自 general-strategy-skill。
> 本目录从 04 开始（il2cpp 专用）。

## workflow/（流程脚本，04–29）

| 脚本 | 阶段 | 角色 | 旧映射 |
|------|------|------|-------|
| `sub-stage-preprocess-build.py` | **04** | 预处理构建检测（apktool + FakerAndroid + toolchain + 编译测试） | 合并 01 + 02 + 03 |
| `sub-stage-sdk-network-removal.py` | **04** | 去SDK + 去网络检测（manifest + smali + .so + apktool b） | 拆自原 04+06 |
| `sub-stage-sdk-network-device-verify.py` | **05** | 真机验收（普通模式 + 飞行模式 2 段）⚠️成功→强制固化 | 合并原 05+07 |
| `sub-stage-ui-hide.py` | **10** | 去功能点（UI 隐藏） | 旧 11 改名 |
| `sub-stage-ui-hide-device-verify.py` | 08 | 去功能点真机验收 ⚠️成功→强制固化 | 旧 12 改名 |
| `sub-stage-template-integration.py` | **12** | 集成模板文件（MainActivity + App + JniBridge + native-lib scaffolding） | 拆自 04 |
| `sub-stage-template-device-verify.py` | 13 | 模板集成真机验收 ⚠️成功→强制固化 | 新增 |
| `sub-stage-sdk-utils-integration.py` | **14** | 集成 SDKUtils（com.android.common.SDKUtils 三阶段模拟） | 拆自 04 |
| `sub-stage-sdk-utils-device-verify.py` | 15 | SDKUtils 真机验收 ⚠️成功→强制固化 | 新增 |
| `sub-stage-reward-video-forwarding.py` | **16** | 激励视频转发（showVideo callJava） | 拆自 07 |
| `sub-stage-reward-video-device-verify.py` | 17 | 激励视频真机验收 ⚠️成功→强制固化 | 拆自 08 |
| `sub-stage-iap-premium-forwarding.py` | **18** | IAP（Premium）转发（processPurchase callJava） | 拆自 07 |
| `sub-stage-iap-device-verify.py` | 19 | IAP 真机验收 ⚠️成功→强制固化 | 拆自 08 |
| `sub-stage-font-replace.py` | **20** | 字体替换（中文字体注入 res/font/） | 拆自 13 |
| `sub-stage-font-device-verify.py` | 10 | 字体真机验收 ⚠️成功→强制固化 | 拆自 14 |
| `sub-stage-text-hanization.py` | **22** | 文本汉化操作（strings.xml + hanization_map.h） | 拆自 13 |
| `sub-stage-text-device-verify.py` | 12 | 文本汉化真机验收（OCR）⚠️成功→强制固化 | 拆自 14 |
| `sub-stage-image-hanization.py` | **24** | 图片汉化操作（PNG 重绘） | 拆自 13 |
| `sub-stage-image-device-verify.py` | 14 | 图片汉化真机验收（OCR）⚠️成功→强制固化 | 拆自 14 |
| `sub-stage-as-build.py` | **26** | AS 工程化（gradle assembleRelease + apksigner v1+v2+v3） | 旧 19 改名 |
| `sub-stage-record-project-files.py` | 15 | 记录工程文件（dir-index.yaml + manifest.yaml） | 新增 |
| `sub-stage-final-check.py` | **28** | 最终验收（6 条硬指标） | 旧 20 改名 |
| `sub-stage-cleanup.py` | **29** | 清理临时空间 | 旧 21 改名 |

## common/（通用脚本）

| 脚本 | 角色 |
|------|------|
| `dump-cs-generator.py` | dump.cs → Frida JS 片段 + C++ 桩（按 hook-discovery-rules.json） |
| `analyze-hook-points.py` | 启发式 hook 点分析（dump.cs 不可用时，用 MonoScript 类名 + metadata 字符串替代） |
| `extract-fm-mono-dll.py` | FM 框架 .mdl → 解密 DLL 提取（hook LoadAssemblyWithImageBinary + frida send） |
| `inject-smali-dex.py` | smali_classesN → classesN.dex 汇编 + 注入 APK（`--force` 重注入；FakerAndroid 无插件/超大 APK 时用） |
| `convert-smali-to-jars.py` | smali → dex → jar(.class) 转换（问题 7：输出项目无 smali，jar 进 app/libs/ 引用） |
| `rename-dollar-res.py` | `$` 前缀资源重命名 + XML/public.xml 引用修复（AAPT2 拒绝 `$` 资源名） |
| `patch-so-return-null.py` | 二进制 patch ELF .so 函数返回 null（Firebase C++ Crashlytics SIGABRT 绕过；aarch64） |
| `fix-dex-jar-frames.py` | ASM 重算 StackMapTable（修复 dex2jar 输出被 D8 "Expected stack map table" 拒收） |
| `generate-stable-ids.py` | apktool public.xml → stable_ids.txt（资源 ID 保真，`aaptOptions --stable-ids`） |
| `inject-native-hook-loader.py` | 注入 native-lib 加载 + installNativeHooks 到真实 Application（解决 native hook 从未生效） |
| `generate-ui-hide-hooks.py` | 生成 UIElements 按钮隐藏 hook 代码（Update / 触发方法两种模式 + 调用链切断） |
| `generate-ui-hide-region-hooks.py` | 生成 UIElements 区域容器隐藏 hook（树遍历 + 保留标记区域；字段引用≠显示元素场景） |
| `frida-dump-uielements-tree.py` | Frida 从 rootElement 递归 dump UXML 树（定位 UI 元素/区域 name） |
| `hide-menu-pages.py` | 静态隐藏 Unity NGUI UI：MenuPage tab（--hide, showOnPlatform=0）+ GameObject 按钮（--hide-go, m_IsActive）+ 语言按钮（--hide-langs, 裁剪 GuiLanguageSelect.buttonList）；data.unity3d 重打包 |
| `hide-unity-gameobject.py` | 静态隐藏 Unity 场景 GameObject（BundleFile 子文件 scene + m_Name → m_IsActive=False）；移除游戏 Logo/游戏名标题 + 主菜单按钮（LeaderBoard/MoreGames/VR Help/VR Mode）；多场景/多名称批量 + --pid 精确隐藏；--list / --list-objects |
| `remove-logo-texture.py` | 静态替换 Unity Texture2D 为全透明（移除 Logo 纹理；仅当标题经该纹理渲染时生效） |
| `verify-il2cpp-rva.py` | 生成 Frida 脚本验证 libil2cpp RVA 是否函数入口（防 hook 极短内联函数 SIGSEGV） |
| `collect-localization-strings.py` | Frida 收集 Unity Localization 字符串（hook GetEntry/GetLocalizedString） |
| `generate-hanization-map.py` | translations.json → hanization_map.h（native hook 汉化表） |
| `replace-game-font.py` | 静态替换 Unity 内嵌字体（⚠️ 实测崩溃，仅记录失败路径；Unity 6 汉化无需字体注入） |
| `hanize-unity-texts-safe.py` | 场景 MB m_Text 安全汉化（m_Text 末尾检测 + 严格等长判断；字节级替换；变长会崩溃——bundle 对象大小不匹配） |
| `hanize-unity-texts.py` | 场景 MB m_Text 变长汉化（⚠️ 实测崩溃，仅记录失败路径） |
| `assetstudio-haniz/` | AssetStudio 汉化辅助（C#）：用游戏 DummyDll 正确解析 MonoBehaviour 脚本类型 + 导出 Text/TMP m_Text 布局（UnityPy 缺失能力） |
| `metadata-patcher.py` | **方案A核心**：global-metadata.dat 字符串字面量提取/回写（il2cpp-stringliteral-patcher 算法自实现，MIT）。extract/patch/show 三子命令 |
| `assets-tools-haniz/` | **完整汉化部署工具**（C#，AssetsTools.NET）：MonoBehaviour m_Text 变长汉化 + 正确写回 bundle（AssetsReplacerFromMemory 更新 DataSize） |

## 同步规则

| 操作 | `skills/common/scripts/` | `skills/.../scripts/workflow/` |
|------|------------------|--------------------------------|
| 修改 workflow 脚本 | 不需要（声明式注册，按 strategy-config.yaml 路径加载） | canonical |
| 新增 skill-only 脚本 | 不创建 | 仅在本目录创建 |
| 修改 common 脚本（skill 内部工具） | 不存在 | 仅在本目录修改 |
| 旧编号脚本 | 不保留 | 重命名/重写为 `sub-stage-*.py` 后删除旧版 |

## 去功能点清单

`../stages/ui-hide/default-action/step-load-feature-checklist.py`：阶段首步委托统一 YAML 加载器；清单维护使用 common/feature-removal-strategy-skill 的 manage-feature-checklist.py。
