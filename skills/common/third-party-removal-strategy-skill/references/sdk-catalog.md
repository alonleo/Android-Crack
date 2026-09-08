# SDK 识别与依赖目录

本目录合并旧参考库的可复用知识。包名、类名、组件和方法是检索线索，不是删除白名单；混淆名仅为历史版本定位线索，必须重新确认签名与调用链。具体 APK、版本、文件数量、资源 ID、地址和成功结论仅保留在迁移存档。

## 共同处理条件

先定位 Java/托管代码、JNI、反射、Lua require、动态 dex 和 Manifest 自动初始化入口，再按当前 type 路由选择停用、兼容桩或删除。只有所有存活引用已处理且冷启动、核心玩法及失败回调通过验收，才可物理删除。反射调用可能抛出未捕获异常；ART 延迟验证不保证删类安全。广告不可用时必须完成上层等待的失败/不可用回调，不得靠空 return 让加载页无限等待。

## 广告与聚合

| SDK | 识别线索 | 依赖与处理边界 |
|---|---|---|
| InMobi | `com.inmobi.ads`、`com.inmobi.media`、`InMobiAdActivity`、`InMobiBanner`、`InMobiInterstitial` | 检查 Picasso 是否共享；聚合链还包括 `InMobiMediationAdapter`、`com.iab.omid.library.inmobi`、SafeDK `SpecialsBridge.inmobiOnInterstitialAdDisplayed`、`InMobiCreativeInfo`。适配器注册表（历史混淆名 `a4`）的字符串引用须确认异常处理，不能直接视为安全。 |
| Vungle | `com.vungle.ads`、`com.vungle.mediation`、`VungleActivity`、`VungleProvider` | 同步处理广告适配器和 Provider；Defold JNI 桥接仍引用时保留兼容类。 |
| IronSource / Unity LevelPlay / AdQuality | `com.ironsource`、`mediationsdk`、`adqualitysdk`、`ControllerActivity`、`IronsourceLifecycleProvider`、`LevelPlayActivityLifecycleProvider`、`CrashProvider`、`Unity.LevelPlay.dll` | 聚合适配器、生命周期和托管 DLL 联动；Unity Services Core、Authentication、Remote Config、Purchasing 不是整个广告包的附属删除目标。 |
| Google AdMob | `com.google.android.gms.ads`、`AdView`、`InterstitialAd`、`RewardedAd`、`NativeAd`、`AdActivity`、`AdService`、`MobileAdsInitProvider`、`com.google.android.gms.ads.APPLICATION_ID` | 限定 ads 模块；GMS 的登录、存档和工具模块可能共享。处理业务广告桥与初始化，而非删除所有 GMS。 |
| AppLovin MAX | `com.applovin`、`AppLovinInitProvider`、`AppLovinFullscreenActivity`、`MaxDebugger*`、`GoogleMediationAdapter`、`ByteDanceMediationAdapter`、`libapplovin-native-crash-reporter.so` | 部分混淆集成可见 `ads_mobile_sdk`；仅凭该名称不能认定厂商。Defold `com.defold.admob.AdmobJNI` 或 IL2CPP C# 硬引用时保留桥接；详见同意管理。 |
| Unity Ads | `com.unity3d.ads`、`com.unity3d.services`、`ironsourceads`、`mediation`、`scar`、`AdUnitActivity`、`AdUnitTransparentActivity`、`AdUnitSoftwareActivity` | 区分广告 services 与 Unity Player/Services Core，不能删除整个 `com.unity3d`。 |
| Facebook / Meta Audience Network | `com.facebook.ads`、`AudienceNetworkContentProvider`、`assets/audience_network/classes*.dex` | 追踪动态 dex 及解包派生物；`com.facebook.internal` 与 Core/login 可能共用，保留业务依赖。 |
| Moloco | `com.moloco.sdk.acm`、`internal`、`publisher`、`xenoss` | 检查聚合适配器与组件引用。 |
| Yandex Ads | `com.yandex.mobile.ads`、`YandexAdsInitializeProvider` | 清理已停用广告初始化入口。 |
| MyTarget | `com.my.target.common`、`MyTargetActivity`、`MyTargetContentProvider` | 组件与代码引用成套检查。 |
| BidMachine | `io.bidmachine`、`BidMachineInitProvider`、authority 后缀 `bidmachineinitprovider` | Provider 可在 Application 前调用 `preInitialize`（历史混淆类 `k2`）；同时检查 AndroidX Startup，按实际调用链判断，不能仅凭异常归因 Startup。 |
| Mintegral / MBridge | `com.mintegral.msdk`、`com.mbridge.msdk`、`MBComponentLifecycleProvider`、`MBRewardVideoActivity`、`NetWorkChangeReceiver` | MAX 适配器或 JNI 存活时保留兼容实现，清理入口须包含生命周期组件。 |
| Smaato | `com.smaato.sdk.core`、`interstitial`、`SmaatoSdkBrowserActivity`、`SmaatoSplashActivity` | 检查浏览器、开屏与 Provider 入口。 |
| Amazon Device Ads | `com.amazon.device.ads`、`DTBAdUtil`、`ResponseReceiver` | 停广告 receiver；不将所有 Amazon 模块视为广告。 |
| AdColony | `com.adcolony.sdk`、`AdColonyActivity` | 处理调用方及 Activity。 |
| Pangle / ByteDance | `com.bytedance.sdk.openadsdk`、`com.bykv.vk.openvk`、`libtt_ugen_layout.so`、`libtobEmbedPagEncrypt.so` | PGL、加密及资源加载可能被核心游戏复用，见 native 目录；不得按厂商全删。 |
| Chartboost | `com.chartboost.sdk`、`CBImpressionActivity`、`EmbeddedBrowserActivity` | 检查广告展示及内嵌浏览器入口。 |
| Yodo1 MAS | `com.yodo1.mas`、`Yodo1VPActivity`、`debugger`、`Yodo1MasAppOpenContainerActivity` | 托管侧搜索 `ShowRewardedAd`、`ShowInterstitialAd`、`IsRewardedAdLoaded`、`LoadRewardAdV2`；清理 Manifest 不代表 C# 路径停用。 |

## 分析、远程服务与共享初始化

| SDK | 识别线索 | 依赖与处理边界 |
|---|---|---|
| Firebase Analytics / Messaging | `com.google.firebase.analytics`、`messaging`、`installations`、`components`、`FirebaseInitProvider`、`AppMeasurementService`、`FirebaseMessagingService` | `datatransport`、GMS `measurement`、`cloudmessaging` 是关联候选，只有无其他消费者才删；不可全删 Firebase。 |
| Firebase Remote Config | `com.google.firebase.remoteconfig`、`ComponentDiscoveryService` 的 registrar meta-data | 查加载页 await、默认参数、本地配置与失败回调；仅在本地配置能完成初始化时停用远端。 |
| Firebase C++ / Unity Firebase | `libFirebaseCppApp-*.so`、`libFirebaseCppAnalytics.so`、`libFirebaseCppCrashlytics.so`、`libFirebaseCppRemoteConfig.so`、`Firebase_App_CSharp_*` | C++ 仍可主动调用 Java `FirebaseApp.initializeApp`。按保留功能保留配置资源及必要 registrar；资源缺失可触发 `Resources$NotFoundException`。Provider 保留/停用及 `onCreate` 返回值必须结合初始化协议，不采用“全保留然后 return false”通用模板。 |
| Firebase Crashlytics | `com.google.firebase.crashlytics`、`CrashlyticsNdkRegistrar`、`libcrashlytics*.so` | 区分崩溃上报与 Remote Config 等业务依赖；见 native 目录的 C++ 空返回风险。 |
| Braze / Appboy | `com.braze`、`BrazeWebViewActivity`、`NotificationTrampolineActivity` | 推送/分析/互动组件须与业务回调解耦。 |
| Facebook Core | `com.facebook`、`FacebookSdk`、`AppEventsLogger`、`FacebookActivity`、`FacebookInitProvider`、`CustomTabActivity` | Core/share/login/app events 是不同功能；检查账户及存档依赖，不能依据广告移除授权全删。 |
| Google Play Games | `com.google.android.gms.games`、`com.google.games`、`PlayGamesInitProvider`、`PlayGamesPlatform`、`Google.Play.Games.dll`、`Google.Android.Libraries.Play.Games.InputMapping.dll` | 查云存档与本地存档边界及失败路径；没有普遍的“为 Firebase 保留 PlayGamesInitProvider”要求。 |
| Google Play Billing | `com.android.billingclient.api`、`BillingClientImpl`、`ProxyBillingActivity`、`ProxyBillingActivityV2`、`com.android.vending.BILLING`、`InAppBillingService.BIND` | Unity Purchasing 的 `IStoreListener.OnInitialized`、`ProcessPurchase` 可能为业务契约；移除广告不自动包含购买模拟或改发货结果。 |
| AppsFlyer | `com.appsflyer`、`AppsFlyerSDK`、安装归因 receiver、`queries` | 检索具体实现的 `start` 重载和 `logEvent`（历史混淆实现 `AFa1ySDK`）；保留 C# 可见类型并使监听器获得合法终态。 |
| APM Insight | `com.apm.insight`、`libapminsighta.so`、`libapminsightb.so` | 以模块依赖识别监控功能；旧文“阿里监控”厂商归属未经验证，不作为判断依据。 |
| AndroidX Startup | `androidx.startup.InitializationProvider`，值为 `androidx.startup` 的 initializer meta-data | 只移除已停用 SDK 的 initializer 与依赖节点，保留仍需使用的 WorkManager/生命周期等初始化。不得清空全部 meta-data 来掩盖 `StartupException`。 |

## 同意管理

OneTrust：`com.onetrust`、`OneTrustLaunchActivity`。Google UMP：`com.google.android.ump`。二者需检查广告启动顺序及同意回调，不能仅删 UI 后留住等待。

AppLovin MAX 可通过 `Terms and Privcay Policy Flow` 日志、`applovin_pp_and_tos_title`、`applovin_privacy_policy_text`、`applovin_terms_of_service_text` 定位。公共 API `AppLovinPrivacySettings.isUserConsentSet/hasUserConsent`（含 Context 重载）可能不同于内部状态；`CmpServiceImpl.showCmp/showCmpForExistingUser` 也未必覆盖 TOS/PP 对话框。沿 `AlertDialog` 创建与显示调用链查实际入口；历史混淆链 `h6.run → a1.a(Activity, …)` 与其重载只作定位示例。

停用广告和相关数据收集后，按实际版本切断同意 UI 初始化，并给上层明确的停用/取消终态。不要以强制 `hasUserConsent=true` 伪造用户同意，也不要把桩化某个混淆类写成“100% 阻止”保证。独立的托管 GDPR 模块（如可检索的 `Noodle.Gdpr.Initialize`、`[GDPR] Cached IsApplicable` 日志）可能不属于 AppLovin，删除 MAX 后仍应追踪其自己的初始化和回调。

## 引擎与框架适配

| 桥接 | 保留边界与处理 |
|---|---|
| King ABM | `com.king.abm.adprovider` 与 `internal` 是桥接/接口候选；`applovin/facebook/google/ironsource/moloco/unity/vungle` 是网络适配器候选。`AbmAdProviderRewardAdGoogleRV/RI` 等调用方应确认捕获异常及回调终态，不能把历史 try-catch 推广到所有版本。 |
| King uSDK | `ada/adinfo/cloudstorage/filesystem/kdid/lifecycle/localnotification/logger/nativesharing/popupguard/popupwebview/urllauncher/privacyagecompliance` 默认作为业务依赖候选保留；`braze/facebook/identitygpgs/notificationtokenprovider/otconsent` 逐项检查可选功能。`com.king.firebaseanalytics` 也独立评估。 |
| KAKAROD KKJ | `kakarodJavaLibs.data.KKJ*`、`KKJPaymentGoogle`、`KKJGameServiceGoogle`、`KKJAdsAppLovin/Admob/Unity`、`KKJAdsPolicy`；`KKJGameServiceActivity` 可能为 Cocos2dxActivity 派生父类，`KKJUtils` 供主流程使用。native 可按类名查找桥接，日志曾容错不代表可删。 |
| Corona / Solar2D | `plugin.admob.LuaLoader` 实现 Lua 广告桥；Lua `require` 失败也可能中止业务，必须确认加载与回调协议。`CoronaProvider.licensing.google` 的 JavaFunction、LVL `LicenseChecker`、`MyLicenseCheckerCallback.allow/dontAllow/applicationError` 是许可独立链，不能随广告清理将拒绝伪作允许。 |
| Defold | `com.defold.admob.AdmobJNI`、Lua 队列与广告网络适配器可能共同引用 Java SDK。选择 Manifest 停用、兼容桩或删除前需验证 JNI 符号、队列消费与 UNAVAILABLE 处理；不能把“保留 smali + 删 so”当所有项目通用方案。 |
| GameMaker | `GoogleMobileAdsGM extends ExtensionBase`、`assets/admob.ext`；`YYFirebaseCrashlytics`、`YYFirebaseSetup`、`assets/firebasecrashlytics.ext`；`RunnerJNILib` JNI 桥。停用对应组件和 collection 配置需保留仍被扩展装载的接口；`InvocationTargetException` 不是可忽略的验收证据。 |

## 加固与功能工具

PairIP LicenseCheck：`com.pairip.licensecheck`、`LicenseClient`、`LicenseActivity`、`LicenseContentProvider`、`com.android.vending.CHECK_LICENSE`、`ILicensingService`、`licensePubKey`。入口可能是 Provider，也可能是 `com.pairip.application.Application.attachBaseContext → LicenseClient.checkLicense → connectToLicensingService`；重签名或服务/权限异常可能显示错误并退出。许可模块必须独立确认范围与业务依赖，既不能认定必须全删，也不能删类留 Application 硬调用。

PGL Armor：`com.pgl`、`libpglarmor.so` 与辅助库可能承担反调试、资源解密或运行依赖，详见 [native 目录](native-catalog.md)。

Lofelt：`com.lofelt.haptics`、`Lofelt.NiceVibrations`、`liblofelt_sdk.so`；`LofeltHaptics.load/loop/play/seek/stop/setAmplitudeMultiplication` 是触觉入口候选。停触觉不等于可删 JNI 库，确认返回类型、加载关系与无障碍/反馈用途。

非 SDK 的语言包替换、具体购买成功回调改写和项目地址不进入本目录；其原文仅作为历史存档，不能充当通用 SDK 清理步骤。
