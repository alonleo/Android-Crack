# 第三方 SDK 移除：各 type 实现要点

本页提炼各 type 的 strategy、workflow 与 SDK 参考资料。被收敛的旧章节保存在 `docs/migrations/sdk-type-references/`；其中项目事实、旧编号和命令不作为当前执行规则。只有分析方法、没有专属移除实证的 type 明确标注为“分析要求”。

统一遵循 [A/B/C 策略](../strategy.md)和 [03/04 共用要求](stage-contract.md)。包前缀、SDK 名或引擎类型命中只形成候选清单，不能证明文件可删。

## android

- 从 `Application.onCreate`、入口 Activity、Provider 自动初始化和多 dex 引用定位 SDK。Manifest 清理不能解除业务代码中的硬调用。
- 有 Java/反射/JNI 调用时保留类及签名，桩化初始化、生命周期和回调；确认无依赖才删除 smali，保留工程编译所需类。
- 网络门槛可能在 Java/Smali；删除后卡加载须检查调用方是否仍等待异步结果，区分联网检测与核心数据加载。
- 来源：[strategy](../../../strategy/android-strategy-skill/strategy.md)、[workflow](../../../strategy/android-strategy-skill/workflow.md)。

## il2cpp

- Java/Smali 多为 SDK 桥接，C# 业务在 `libil2cpp.so`；结合 dump.cs、metadata、native 调用方和 Java 引用判断，不能只扫描 smali。
- 保留 `libil2cpp.so`、`libunity.so` 及实际引擎依赖。AppLovin mediation 可能反射读取 BuildConfig，需相应 stubs 和编译类路径。
- 04 声明 type 专用 worker，涉及 registry、BuildConfig、hook-plan、网络检测、smali→jar 和合并报告；具体顺序读 step-register，不照旧文档“15 步”硬编码。
- GDPR/consent、广告 WebView 问题追踪 SDK 控制器初始化及 delegate 回调。签名、RVA、生命周期逐 APK 确认，不能复制案例地址。04 保留 06/07 本地替代状态机所需接口。
- 来源：[workflow](../../../strategy/il2cpp-strategy-skill/workflow.md)、[GDPR/WebView 参考](../../../strategy/il2cpp-strategy-skill/references/gdpr-delegate-webview-crash.md)。

## unity-mono

- 分析要求：通过 ILSpy/dnSpy 检查 Managed DLL 的 AdMob/AdColony、UnityIAP/PurchasingManager 桥接，再追踪 C# ↔ Java ↔ native 混合调用。
- 保留 Mono/Unity 运行库和游戏 DLL；Java 层清理后仍可能有托管调用。DLL 替换后核对类型引用、签名与运行时加载。
- 原资料没有完整的 Mono 专属 SDK 删除配方，具体处理点需项目分析证据。
- 来源：[strategy](../../../strategy/unity-mono-strategy-skill/strategy.md)、[workflow](../../../strategy/unity-mono-strategy-skill/workflow.md)。

## cocos2dx

- SDK 可跨 Java 插件、C++ 和 Lua；`libcocos2d*.so`、`libMyGame.so` 等实际引擎库加入项目白名单。
- 联网门槛可能在 C++ `network*`/`checkServer*` 或 Lua 侧；Java 清理后继续追踪 native/脚本回调。多 dex 项目保留 MultiDex 所需类。
- 旧 workflow 将 ANE 与 Cocos 插件并列；ANE 的 application.xml 处理仅适用于确实存在 AIR Native Extension 的依赖，不能套用于普通 Cocos 插件。
- 来源：[strategy](../../../strategy/cocos2dx-strategy-skill/strategy.md)、[workflow](../../../strategy/cocos2dx-strategy-skill/workflow.md)。

## cocos-creator

- 分析要求：结合 JS/TS 恢复结果、JSB/native 桥接和 Java SDK 初始化判断。2.x browserify 与 3.x SystemJS/bundle 组织不同，不能只清理单个脚本文件。
- 加密 JSC 先通过 type 分析流程恢复；保留引擎库、核心 bundle 和运行时，沿实际 SDK 调用路径处理。原资料没有专属 SDK 桩化配方。
- 来源：[strategy](../../../strategy/cocos-creator-strategy-skill/strategy.md)、[workflow](../../../strategy/cocos-creator-strategy-skill/workflow.md)。

## unreal

- 分析要求：SDK 依赖可能连接 GameActivity、native C++ 和 `.pak` 资源。保留实际引擎库（如 `libUE4.so`、`libUnreal.so`）及核心资源；库名不能单独证明版本或可删除性。
- Java 组件清理后检查 C++ 调用和异步回调。原资料只有 native 分析方法，没有独立验证的 SDK 移除配方。
- 来源：[strategy](../../../strategy/unreal-strategy-skill/strategy.md)、[workflow](../../../strategy/unreal-strategy-skill/workflow.md)。

## flutter

- 分析要求：结合 `libapp.so` Dart AOT 与 Java ↔ Dart/FlutterJNI 桥接识别广告调用。保留 `libflutter.so`、`libapp.so` 和核心 flutter_assets。
- 调用方等待结果时保留相容返回及完成路径，避免缺失方法和永久等待。原资料没有专属 SDK 移除实证，偏移和签名逐 APK 确认。
- 来源：[strategy](../../../strategy/flutter-strategy-skill/strategy.md)、[workflow](../../../strategy/flutter-strategy-skill/workflow.md)。

## xamarin

- 分析要求：从 `assemblies/*.dll` 广告/IAP 桥接追踪 C# ↔ Java ↔ native；Java 清理不能替代托管依赖判断。
- 保留 `libmonodroid.so` 和当前包实际使用的 Mono/Xamarin 运行库、assemblies、必要绑定。SDK DLL/native 库只有引用解除后才能删除。
- 原资料没有专属 SDK 桩化配方；DLL 修改后的加载与回调须真机复核。
- 来源：[strategy](../../../strategy/xamarin-strategy-skill/strategy.md)、[workflow](../../../strategy/xamarin-strategy-skill/workflow.md)。

## air

- SDK 常嵌入 ANE（Adobe Native Extension）。移除扩展同步修改 AIR `application.xml` 的 `extensions` 列表，并检查 ActionScript/SWF 的 ExtensionContext 调用方。
- Manifest 仅覆盖容器层；URLRequest、URLLoader、navigateToURL 等网络路径及完成/失败事件继续在 ActionScript 层检查。
- 保留 AIR 容器、主 SWF 和核心模块，不对所有 URL 加载或事件分发全局空返回。
- 来源：[strategy](../../../strategy/air-strategy-skill/strategy.md)、[workflow](../../../strategy/air-strategy-skill/workflow.md)。

## defold

- `lib<game>.so` 可由 dmengine 重命名；`com.defold.*JNI` glue 仍引用 SDK 实现类。先清理自动初始化组件、保留 smali/JNI 接口，再按证据停用副作用；删库也须核对动态加载。
- 原资料的命令队列 hook 候选：Admob/Firebase/Analytics/GPGS 的 `*AddToQueue`；Push 按用途判断，`IapJNI_onPurchaseResult` 等本地替代回调保留。
- dlsym 在引擎库加载后解析；注入保留原 Application 初始化链，可通过加载时机探测安装 hook。And64InlineHook 限匹配的 arm64 场景；检查 C++ runtime 链接，避免缺失 `libc++_shared.so`，需要时通过现有构建脚本静态链接。
- UNAVAILABLE、未初始化告警只有在失败分支完成、玩法继续时才可接受；吞回调可能卡死。native 队列 hook 不证明 Provider/Java/后台线程停止联网，不能将案例“仅 hook 成功”推广为替代初始化清理。
- 来源：[strategy](../../../strategy/defold-strategy-skill/strategy.md)、[JNI 经验](../../../strategy/defold-strategy-skill/experiences.md)、[工具](../../../strategy/defold-strategy-skill/tools-index.md)。

## gamemaker

- `libyoyo.so` 与 RunnerJNILib 连接游戏和 Java SDK；glue 有引用时保留 smali，先清理 Manifest 自动组件，再针对 SDK 扩展停用调用。
- EXTN chunk、ext_opt 和 `Java_com_yoyogames_*` 导出用于定位候选；**不能全部 hook**，其中包含 Startup、Process、RenderSplash、TouchEvent、dsMap/dsList 等核心入口。
- HttpResult、CloudResult、LoginResult、InputResult 逐调用方确认；核心下载、本地状态机、购买替代或输入路径可能仍依赖这些回调。
- native 方案在 `libyoyo.so` 加载后解析具体符号，保留 RunnerActivity/Application 启动链；ABI、C++ runtime 与注入检查同 Defold。原工具索引的 GameMaker hook 构建工具尚为 TODO，不能当现成入口调用。
- 来源：[strategy](../../../strategy/gamemaker-strategy-skill/strategy.md)、[workflow](../../../strategy/gamemaker-strategy-skill/workflow.md)、[工具](../../../strategy/gamemaker-strategy-skill/tools-index.md)。

## libgdx

- 保留 `libgdx.so`、AndroidApplication 启动链和核心 assets。PGL 的 `libpglarmor.so` 等库可能解密游戏资源；hash、高熵文件或 Bytedance 前缀都不是删除依据，先追踪 Gdx.files/Pixmap/资源加载引用。
- `assets/template/`、adimages、ad-viewer、audience_network 是广告候选目录，后者可能含动态 dex；逐项证实无核心依赖后处理，保留 MultiDex 加载链。
- 发行方 fork 可能硬调 Facebook/Firebase；删 Provider/meta-data 后出现 Facebook app id/context 错误、`Default FirebaseApp is not initialized`、统计单例 NPE。
- 桩化保持初始化不变量：Facebook 下游仍读 context 时保留该字段，仍校验 app id 时保持 fb 前缀格式。只停用日志/上报副作用，不能将整个初始化方法 return。
- Firebase Messaging token/订阅与 ThinkingData uuid 上报连同调用方检查；只移除上报段，保留模块单例初始化和 uuid 读写。getInstance 返回 null 仅在所有使用点已处理时成立。
- 旧资料 GameActivity.P()、p226y4.b.q() 等混淆名是案例线索，新 APK 按行为定位；已有 libGDX cleanup 脚本匹配同样须复核。
- 来源：[strategy](../../../strategy/libgdx-strategy-skill/strategy.md)、[工具](../../../strategy/libgdx-strategy-skill/tools-index.md)、[workflow](../../../strategy/libgdx-strategy-skill/workflow.md)。
