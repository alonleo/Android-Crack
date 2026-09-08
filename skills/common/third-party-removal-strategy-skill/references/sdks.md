# 第三方 SDK 特征库

> 仅记录可跨项目识别的 SDK 特征；不得记录来源 APK、项目名、日期或项目级决定。

旧目录的 SDK 明细已按依赖边界合并到 [SDK 识别与依赖目录](sdk-catalog.md)；包名、AIR 插件及 Manifest/资源检索规则见 [候选模式](sdk-patterns.md)。下方保留各 type 提炼的共用摘要。

## 条目格式

```md
### <SDK 名称>

- **类别**：
- **识别特征**：manifest 组件、包前缀、资源、assets 或字符串特征
- **native 特征**：可选；仅列通用库名或符号模式
- **默认判断**：保留 / 停用 / 桩化 / 物理删除前需分析
- **依赖风险**：
- **相关文档**：
```

## 条目

<!-- 在此追加 SDK 特征。 -->

### Facebook / Audience Network

- **类别**：社交、分析与广告，按实际模块区分。
- **识别特征**：com.facebook、FacebookSdk、AppEventsLogger、assets/audience_network/ 动态 dex。
- **默认判断**：先停用入口，硬引用保留并桩化；不要仅删 Provider。
- **依赖风险**：下游可能读取 applicationContext、app id 或校验初始化；空 return 可能导致 NPE。
- **相关文档**：[libGDX 初始化链](engine-notes.md#libgdx)。

### Firebase / Crashlytics / Messaging

- **类别**：分析、崩溃上报、推送等；不将全部 Firebase 功能视为同一删除目标。
- **识别特征**：FirebaseInitProvider、FirebaseApp、FirebaseMessaging、FirebaseCrashlytics。
- **native 特征**：libcrashlytics*.so、libFirebaseCppCrashlytics.so，仅为候选。
- **默认判断**：停止自动初始化及业务副作用，保留必要桥接。
- **依赖风险**：删 Provider 后业务可能仍调用 getInstance/getToken/subscribeToTopic；返回 null 需同时处理调用方。
- **相关文档**：[libGDX](engine-notes.md#libgdx)、[il2cpp](engine-notes.md#il2cpp)。

### 广告聚合与归因候选

- **类别**：广告/聚合/归因，按 SDK 模块判定。
- **识别特征**：applovin、mbridge、bytedance/Pangle、inmobi、unity3d.ads、vungle、fyber、digitalturbine、ironsource、adjust、appsflyer。
- **默认判断**：逐个检查 Manifest、适配器、动态 dex、native 与 assets；名单命中不等于可删。
- **依赖风险**：聚合适配器可能反射访问 BuildConfig；加固/资源解码可能复用同厂商库。
- **相关文档**：[il2cpp](engine-notes.md#il2cpp)、[native 库](native-libs.md)。
