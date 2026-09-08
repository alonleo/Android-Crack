# Native 库识别与保留边界

旧条目的 ESSENTIAL/REMOVABLE 是具体样本判断，不能迁移成按文件名删除的规则。首先分析各 ABI 的 `DT_NEEDED`、`dlopen`、`System.loadLibrary`、JNI/托管 DllImport、符号和资源加载链；实际操作通过已登记脚本及 type 路由完成。默认保留未知/共享依赖，关闭调用入口并验收之后才考虑删除。

## 引擎与核心桥接

| 库/模式 | 识别与保留原因 |
|---|---|
| `libeden.so` | EdenActivity 加载 `eden`，`assets/res_output` 可为引擎资源入口；属于 Eden 游戏运行库。 |
| `libMyGame.so`、`libcocos2d*.so` | Cocos2dxActivity 派生入口加载；可能包含 Lua/tolua，也可能为纯 C++。少量 Lua 符号不足以判断业务是否用 Lua。JNI 可调用 KKJ 等商业桥接，主库应保留。 |
| `libil2cpp.so`、`libunity.so`、`libmain.so` | Unity 游戏逻辑、Player 及入口；`global-metadata.dat` 支持 IL2CPP 识别，保留核心库及匹配 metadata。 |
| `libnative-lib.so` | 常见自定义 JNI 库名，先查调用；名称本身既不能证明是核心，也不能证明可删。 |
| `libmonodroid.so` 等 Mono/Xamarin 运行库 | 运行时及托管桥接，不能作为第三方统计库删除。 |
| `libflutter.so`、`libapp.so` | Flutter 运行时与 AOT 应用代码候选，应结合 assets/入口判定并保留。 |
| 重命名 Defold 主库 | 结合 `Java_com_defold_*`、`game.dmanifest/game.projectc` 和入口加载确认；仅出现 `libdmengine.so` 字符串不构成引擎归属证据。 |
| `libcorona.so` | Corona/Solar2D 核心与 Lua 集成，保留。 |
| `libgdx.so` | `com.badlogic.gdx`、AndroidApplication、EGL/GLES 与资源后端依赖，保留。 |
| `libyoyo.so` | GameMaker runner；`Java_com_yoyogames_runner_RunnerJNILib_*`、`YYObjectBase`、`RValue`、Rollback/CDS 符号线索。旧文从 Defold 字符串推断“复用其底层”没有充分证据，不沿用。 |

## 广告、分析与可选插件候选

| 库/模式 | 关联线索 | 删除前条件 |
|---|---|---|
| `libapplovin-native-crash-reporter.so` / `libapplovin*.so` | AppLovin native 崩溃上报或其他组件 | 核实每个库职责，停止 `com.applovin`/适配器的加载调用；不能按通配符全删。 |
| `libtt_ugen_layout.so` | Pangle 广告布局 | 检查 `com.bytedance.sdk.openadsdk` 及 JNI 加载路径。 |
| `libtobEmbedPagEncrypt.so` | 广告加密候选 | 证明只服务已停用广告，排除共享资源解码。 |
| `libapminsighta.so` / `libapminsightb.so` / `libapminsight*.so` | `com.apm.insight` 性能/崩溃监控 | 移除调用入口及检查其他消费者；不沿用未经证实的厂商归属。 |
| `libcrashlytics.so`、`libcrashlytics-common.so`、`libcrashlytics-handler.so`、`libcrashlytics-trampoline.so` 等 | Firebase native crash reporting | 不同版本库数不同；Provider 清理不保证业务侧不主动加载，检查 registrar 与 Java/C++ 初始化。 |
| `libads.so`、`libanalytics.so`、`libgameNetwork.so`、`liblicensing.so` | Corona 广告、分析、排行榜/网络、许可插件候选 | 分别追踪 LuaLoader/require、Java 注册和回调；仅名称相似不确认归属。删除可选网络插件须确保核心流程无等待；许可插件独立评估。 |
| `liblofelt_sdk.so` | Lofelt 触觉，`com.lofelt.haptics` / `Lofelt.NiceVibrations` | 接口桩化时仍可能需保留库，确认 JNI 注册/加载、反馈用途及调用方返回协议。 |

## PGL 与未知共享库

`libpglarmor.so`、`libbuffer_pgl.so`、`libfile_lock_pgl.so` 以及旧规则中的 `libbuffer_pg.so`、`libfile_lock_pg.so` 变体按实际文件与符号确认关系，不靠前缀判断厂商或删库。`Java_com_bytedance_sdk_component_pglcrypt_PglCryptUtils_bc` 与 `com.bytedance.sdk.component.pglcrypt` 是资源解码链的重要线索。

若 `assets/0[0-9A-F]{32}` 等 hash 资源经 PGL 解码后交给 `Pixmap`/纹理加载，保留库、辅助依赖和资源池。是否 Cocos2d-x、libGDX 或是否存在 `libMyGame.so` 都不能单独判定可删；以核心资源实际依赖为准。反调试与加密辅助库（含 `libEncryptorP.so`）同样逐库追踪。

`libnms.so` 曾被分别视为广告网络监控和游戏网络层；名称、大小、与 Pangle 同包都不足以定性。查加载者、导出符号及业务调用，未确认前保留。

`libbuffer.so`、`libfile_lock.so`、`libdatastore_shared_counter.so` 可能服务 AndroidX DataStore 或其他运行依赖。DataStore 共享计数器由 `androidx.datastore` 消费；不能因 Firebase/广告被停用而自动删除，也不能仅凭名称断言它们全是系统必需库。

## Firebase C++ 共享主库

`libFirebaseCppApp-*.so`、`libFirebaseCppCrashlytics.so`、`libFirebaseCppAnalytics.so`、`libFirebaseCppRemoteConfig.so` 是模块族；`Firebase_App_CSharp_*` SWIG 导出与托管绑定是依赖线索。Remote Config 若承担加载页 await，删除主库会触发 DllNotFoundException 或挂起。

历史案例中的 `Crashlytics::GetInstance → CrashlyticsInternal` 构造/JNI `GetObjectField(null)` 崩溃只能作为排查线索，不能据此对任意版本固定地址 patch。返回 null 需要所有调用者能接受，并且完成初始化失败/禁用的合法终态；优先沿已确认的组件边界停上报并保留业务模块。同步检查 Java FirebaseApp、资源配置及 registrar，参考 [SDK 目录](sdk-catalog.md#分析远程服务与共享初始化)。
