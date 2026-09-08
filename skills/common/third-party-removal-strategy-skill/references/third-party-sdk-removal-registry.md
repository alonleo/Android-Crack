# 第三方 SDK 执行清单

> 自动生成自 [third-party-sdk-removal-registry.yaml](third-party-sdk-removal-registry.yaml)。请通过 manage-sdk-registry.py 增删改查，勿手工编辑本文件。

此表是 YAML 规则的阅读视图；关键词命中不证明可删除。Agent 仍须核对策略、引擎依赖与项目证据。

## manifest_drop_exact

条目数：3

| 匹配项 / 保留项 | 属性 |
|---|---|
| FirebaseInitProvider | {&quot;why&quot;: &quot;onCreate 调 FirebaseApp.initializeApp → Ktor 静态初始化失败 → 自杀&quot;} |
| MobileAdsInitProvider | {&quot;why&quot;: &quot;GMS ads init 触发 AppLovin mediation 列所有广告 SDK → 缺类 NoClassDefFoundError → 自杀&quot;} |
| com.squareup.picasso | {&quot;why&quot;: &quot;Squareup Picasso ContentProvider 类缺失导致 ClassNotFoundException&quot;} |

## manifest_drop_keyword_contains

条目数：24

| 匹配项 / 保留项 | 属性 |
|---|---|
| vungle | {&quot;why&quot;: &quot;广告 SDK，不影响主玩法&quot;} |
| applovin | {&quot;why&quot;: &quot;广告 SDK，不影响主玩法&quot;} |
| facebook | {&quot;why&quot;: &quot;广告 SDK（Facebook Audience Network）&quot;} |
| google.android.gms.ads | {&quot;why&quot;: &quot;GMS ads 测量&quot;} |
| ironsource | {&quot;why&quot;: &quot;广告 SDK&quot;} |
| yandex.mobile.ads | {&quot;why&quot;: &quot;广告 SDK&quot;} |
| bigo | {&quot;why&quot;: &quot;广告 SDK&quot;} |
| bidmachine | {&quot;why&quot;: &quot;广告 SDK&quot;} |
| my.target | {&quot;why&quot;: &quot;广告 SDK&quot;} |
| appmetrica | {&quot;why&quot;: &quot;广告 SDK&quot;} |
| picasso | {&quot;why&quot;: &quot;Squareup Picasso（注意：被 exact &#x27;com.squareup.picasso&#x27; 优先匹配）&quot;} |
| squareup | {&quot;why&quot;: &quot;Squareup 系列（被 picasso 覆盖）&quot;} |
| adjoe | {&quot;why&quot;: &quot;广告 SDK&quot;} |
| moloco | {&quot;why&quot;: &quot;广告 SDK&quot;} |
| androidx.startup | {&quot;why&quot;: &quot;AndroidX Startup（早期 SDK 启动框架）&quot;} |
| com.adjust | {&quot;why&quot;: &quot;Adjust 归因 SDK&quot;} |
| mbridge | {&quot;why&quot;: &quot;Mintegral 广告 SDK&quot;} |
| adn | {&quot;why&quot;: &quot;auto-added by stage-04 step2 [FLOWFIX 2026-08-18]: step1 scan detected&quot;} |
| bytedance | {&quot;why&quot;: &quot;auto-added by stage-04 step2 [FLOWFIX 2026-08-18]: step1 scan detected&quot;} |
| digitalturbine | {&quot;why&quot;: &quot;auto-added by stage-04 step2 [FLOWFIX 2026-08-18]: step1 scan detected&quot;} |
| firebase | {&quot;why&quot;: &quot;auto-added by stage-04 step2 [FLOWFIX 2026-08-18]: step1 scan detected&quot;} |
| pubnative | {&quot;why&quot;: &quot;auto-added by stage-04 step2 [FLOWFIX 2026-08-18]: step1 scan detected&quot;} |
| yandex | {&quot;why&quot;: &quot;auto-added by stage-04 step2 [FLOWFIX 2026-08-18]: step1 scan detected&quot;} |
| custom_notification_android_activity | {&quot;why&quot;: &quot;Firebase MessagingUnityPlayerActivity meta-data；Firebase .so 已强制移除，无需此 meta&quot;} |

## so_early_kill

条目数：6

| 匹配项 / 保留项 | 属性 |
|---|---|
| libcrashlytics.so | {&quot;why&quot;: &quot;Firebase Crashlytics native crash handler，会调 killProcess&quot;} |
| libcrashlytics-common.so | {&quot;why&quot;: &quot;Crashlytics 通用库&quot;} |
| libcrashlytics-handler.so | {&quot;why&quot;: &quot;Crashlytics exception handler&quot;} |
| libcrashlytics-trampoline.so | {&quot;why&quot;: &quot;Crashlytics 信号桥接 trampoline&quot;} |
| libFirebaseCppCrashlytics.so | {&quot;why&quot;: &quot;Firebase C++ Crashlytics 桥接&quot;} |
| libapplovin-native-crash-reporter.so | {&quot;why&quot;: &quot;AppLovin native crash reporter&quot;} |

## so_keyword_contains

条目数：19

| 匹配项 / 保留项 | 属性 |
|---|---|
| applovin | — |
| mbridge | — |
| vungle | — |
| facebook | — |
| chartboost | — |
| inmobi | — |
| pangle | — |
| ironsource | — |
| appsflyer | — |
| adjust | — |
| tapjoy | — |
| bugly | — |
| safedk | — |
| adn | — |
| bytedance | — |
| digitalturbine | — |
| firebase | — |
| pubnative | — |
| yandex | — |

## raw_apk_drop_entries

条目数：8

| 匹配项 / 保留项 | 属性 |
|---|---|
| lib/arm64-v8a/libcrashlytics-common.so | — |
| lib/arm64-v8a/libcrashlytics-handler.so | — |
| lib/arm64-v8a/libcrashlytics-trampoline.so | — |
| lib/arm64-v8a/libcrashlytics.so | — |
| lib/arm64-v8a/libFirebaseCppCrashlytics.so | — |
| lib/arm64-v8a/libapplovin-native-crash-reporter.so | — |
| assets/crashlytics-build.properties | — |
| res/raw/firebase_crashlytics_keep.xml | — |

## build_config_stubs

条目数：6

| 匹配项 / 保留项 | 属性 |
|---|---|
| com/facebook/ads/BuildConfig.java | {&quot;package&quot;: &quot;com.facebook.ads&quot;} |
| com/mbridge/BuildConfig.java | {&quot;package&quot;: &quot;com.mbridge&quot;} |
| com/moloco/sdk/BuildConfig.java | {&quot;package&quot;: &quot;com.moloco.sdk&quot;} |
| com/vungle/ads/BuildConfig.java | {&quot;package&quot;: &quot;com.vungle.ads&quot;} |
| net/pubnative/lite/sdk/BuildConfig.java | {&quot;package&quot;: &quot;net.pubnative.lite.sdk&quot;} |
| io/adn/sdk/BuildConfig.java | {&quot;package&quot;: &quot;io.adn.sdk&quot;} |

## smali_exclude_prefixes

条目数：23

| 匹配项 / 保留项 | 属性 |
|---|---|
| androidx/compose | — |
| androidx/work | — |
| androidx/browser | — |
| com/google/firebase/crashlytics | — |
| com/unity3d/ads | — |
| com/unity3d/services | — |
| com/unity3d/ads/mediation | — |
| com/ironsource | — |
| com/applovin | — |
| com/applovin/shadow | — |
| com/iab | — |
| com/google/android/gms | — |
| com/google/android/play | — |
| com/google/protobuf | — |
| com/google/common | — |
| com/google/firebase | — |
| com/amazon/device/ads | — |
| com/yandex | — |
| gatewayprotocol | — |
| io/bidmachine | — |
| net/pubnative | — |
| org/chromium | — |
| org/intellij | — |

## meta_data_force_value

条目数：1

| 匹配项 / 保留项 | 属性 |
|---|---|
| firebase_crashlytics_collection_enabled | {&quot;value&quot;: &quot;false&quot;, &quot;why&quot;: &quot;即使删了 libcrashlytics，Java 侧 Crashlytics 静态初始化仍可能调 native signal&quot;} |

## engine_so_keep

条目数：4

| 匹配项 / 保留项 | 属性 |
|---|---|
| libil2cpp.so | — |
| libunity.so | — |
| libmain.so | — |
| libGameAssembly.so | — |

