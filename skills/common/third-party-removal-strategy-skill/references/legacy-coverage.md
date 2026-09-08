# 旧参考库覆盖映射

序号按旧 `references/sdks.md` 的三级标题出现顺序计算；native 序号按旧 `references/native-libs.md` 的实际库三级标题计算，不含格式示例 `<文件名>`。重复标题合并，项目名标题泛化。原文由迁移存档保存，此表不将样本结论变为通用规则。

## SDK 标题

共 66 个：64 个 SDK/框架标题已合并，1 个空分类标题并入同意管理，1 个语言包标题仅留历史存档（非 SDK）。

| 旧序号 | 泛化名称 | 合并位置 |
|---|---|---|
| 1、28、50 | InMobi | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 2、10、29、59 | Vungle | [广告与聚合](sdk-catalog.md#广告与聚合)、[引擎桥接](sdk-catalog.md#引擎与框架适配) |
| 3、8、21、34、53 | IronSource / LevelPlay / AdQuality | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 4 | AdMob | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 5、35、57 | AppLovin MAX | [广告与聚合](sdk-catalog.md#广告与聚合)、[引擎桥接](sdk-catalog.md#引擎与框架适配) |
| 6 | MAX 同意弹窗 | [同意管理](sdk-catalog.md#同意管理) |
| 7、37、60 | Audience Network | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 9、36 | Unity Ads | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 11 | Moloco | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 12 | Firebase Analytics | [共享初始化](sdk-catalog.md#分析远程服务与共享初始化) |
| 13 | Braze / Appboy | [共享初始化](sdk-catalog.md#分析远程服务与共享初始化) |
| 14、56 | Google Play Games | [共享初始化](sdk-catalog.md#分析远程服务与共享初始化) |
| 15 | Facebook Core | [共享初始化](sdk-catalog.md#分析远程服务与共享初始化) |
| 16 | 空分类标题 | [同意管理](sdk-catalog.md#同意管理) |
| 17、18 | OneTrust / UMP | [同意管理](sdk-catalog.md#同意管理) |
| 19、20 | King ABM / uSDK | [引擎桥接](sdk-catalog.md#引擎与框架适配) |
| 22 | Yandex | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 23 | MyTarget | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 24、62 | BidMachine | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 25、33、58 | Mintegral / MBridge | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 26 | Smaato | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 27 | Amazon Device Ads | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 30 | AdColony | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 31 | Pangle / ByteDance | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 32 | Chartboost | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 38 | Remote Config | [共享初始化](sdk-catalog.md#分析远程服务与共享初始化) |
| 39 | APM Insight | [共享初始化](sdk-catalog.md#分析远程服务与共享初始化) |
| 40、44 | PGL Armor | [加固与功能工具](sdk-catalog.md#加固与功能工具)、[PGL 依赖](native-catalog.md#pgl-与未知共享库) |
| 41、47、52 | PairIP | [加固与功能工具](sdk-catalog.md#加固与功能工具) |
| 42、43 | Corona Licensing / Ads | [引擎桥接](sdk-catalog.md#引擎与框架适配) |
| 45、49 | Lofelt | [加固与功能工具](sdk-catalog.md#加固与功能工具) |
| 46 | Firebase C++ | [共享初始化](sdk-catalog.md#分析远程服务与共享初始化)、[C++ 库](native-catalog.md#firebase-c-共享主库) |
| 48 | AppsFlyer | [共享初始化](sdk-catalog.md#分析远程服务与共享初始化) |
| 51 | KKJ | [引擎桥接](sdk-catalog.md#引擎与框架适配) |
| 54 | 内嵌托管 GDPR | [同意管理](sdk-catalog.md#同意管理) |
| 55 | Play Billing | [共享初始化](sdk-catalog.md#分析远程服务与共享初始化) |
| 61 | Defold 语言包 | 非 SDK，仅保留原文存档；不复制项目名及资源路径。 |
| 63 | Yodo1 MAS | [广告与聚合](sdk-catalog.md#广告与聚合) |
| 64 | AndroidX Startup | [共享初始化](sdk-catalog.md#分析远程服务与共享初始化) |
| 65、66 | GameMaker Ads / Crashlytics 扩展 | [引擎桥接](sdk-catalog.md#引擎与框架适配) |

## Native 库条目

共 35 个实际库标题，全部合并；另 1 个模板标题由现有 native 条目格式承接。

| 旧序号 | 泛化名称 | 合并位置 |
|---|---|---|
| 1 | Eden | [引擎与核心桥接](native-catalog.md#引擎与核心桥接) |
| 2、8、24、28 | AppLovin crash reporter | [可选库](native-catalog.md#广告分析与可选插件候选) |
| 3、12、29 | DataStore / Buffer / FileLock | [共享库](native-catalog.md#pgl-与未知共享库) |
| 4、23 | Cocos2d-x 主库 | [引擎与核心桥接](native-catalog.md#引擎与核心桥接) |
| 5、18、19、30 | PGL 及辅助库 | [共享库](native-catalog.md#pgl-与未知共享库) |
| 6、7 | Pangle 布局/加密 | [可选库](native-catalog.md#广告分析与可选插件候选) |
| 9 | APM Insight | [可选库](native-catalog.md#广告分析与可选插件候选) |
| 10、27 | Crashlytics 库组 | [可选库](native-catalog.md#广告分析与可选插件候选) |
| 11、32 | NMS | [共享库](native-catalog.md#pgl-与未知共享库) |
| 13、14、15、16 | Corona 四类插件 | [可选库](native-catalog.md#广告分析与可选插件候选) |
| 17 | Corona 核心 | [引擎与核心桥接](native-catalog.md#引擎与核心桥接) |
| 20 | Lofelt | [可选库](native-catalog.md#广告分析与可选插件候选) |
| 21、22 | Firebase C++ 主库/Crashlytics | [共享主库](native-catalog.md#firebase-c-共享主库) |
| 25、34、35 | Unity / IL2CPP / Player | [引擎与核心桥接](native-catalog.md#引擎与核心桥接) |
| 26 | 重命名 Defold 主库 | [引擎与核心桥接](native-catalog.md#引擎与核心桥接) |
| 31 | libGDX | [引擎与核心桥接](native-catalog.md#引擎与核心桥接) |
| 33 | GameMaker runner | [引擎与核心桥接](native-catalog.md#引擎与核心桥接) |

旧“通用 .so 移除规则”的其他库名纳入 native 目录；手工 find/grep 操作改为登记脚本约束。旧 `sdk-patterns.md` 的 2 条自定义桥接、9 条统计、9 条广告、6 条推送/远程配置、6 条 Manifest、5 条资源候选均在 [候选模式](sdk-patterns.md) 覆盖；具体来源字段和购买成功改写步骤仅存档。
