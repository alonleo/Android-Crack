# SDK 检索候选模式

本表用于静态盘点，不是自动删除/全量桩化配置。阶段由当前 type 注册表决定，不沿用旧 stage-03/09 编号；操作通过登记脚本执行，Manifest 用结构化 XML 处理，资源删除前检查引用。

| 类别 | 包前缀/特征 | 检查重点 |
|---|---|---|
| 统计与崩溃 | `com.umeng`、`com.tencent.bugly`、`com.google.firebase.analytics`、`com.google.firebase.crashlytics`、`com.sensorsdata`、`cn.thinkingdata`、`com.tapdb` | 拆分自动初始化、网络行为与业务依赖。 |
| 广告 | `com.google.android.gms.ads`、`com.bytedance.sdk.openadsdk`、`com.qq.e.ads`、`com.kwad.sdk`、`com.mintegral`、`com.mbridge`、`com.unity3d.ads`、`com.applovin` | 广告网络、聚合适配器、共享组件与引擎桥接分别核查。 |
| AIR 插件 | `com.adobe.air.mopub`、`com.ironsource.adobeair.googlebase`、`com.ironsource.adobeair.admob`、`com.ironsource.adobeair.unityads` | 同步查 ANE、FREContext、ActionScript 调用及初始化回调。 |
| 推送与远程配置 | `cn.jpush`、`com.igetui`、`com.mobpush`、`com.huawei.hms.push`、`com.xiaomi.push`、`com.google.firebase.remoteconfig` | 本地默认值、存档/账号、订阅与等待任务不可遗漏。 |
| 自定义聚合入口 | `com.facebook.appevents.a.AdUtils`、`AdSourceUtils`、`setActivity`、`init` | 历史入口可能串起 MAX/Pangle/AdMob/Yandex；包名不能证明归属，确认实际调用链后处理。 |
| 自定义购买桥 | `com.red.iap`、`IAPJniHelper`、`purchase`、`restorePurchases`、`nativeOnProductPurchaseSuccess`、`nativeOnRestorePurchasesFinished` | 仅作为业务边界检索，广告清理不包含改写购买结果；具体项目实施仅存档。 |

## Manifest 候选

- Umeng provider authority 与 receiver 类名、JPush receiver 与 `JPUSH` meta-data。
- `com.google.android.gms.permission.AD_ID` 与包含 `umeng` 的自定义权限。
- 查明权限/组件是否仍有消费者，完整解析名称和 namespace；不要用匹配单行的正则/sed 删除 XML。

## 资源候选

旧模式 `umeng_*`、`bugly_*`、`jpush_*`、`*_umeng*`、`UM*` 仅可生成待审查清单。`UM*` 尤其宽泛；需有 SDK 归属和引用证据，不得自动 `find -delete`。同厂商加密资源和共享布局先保留。

具体 SDK 的组件和接口见 [SDK 目录](sdk-catalog.md)，native 保留边界见 [native 目录](native-catalog.md)。
