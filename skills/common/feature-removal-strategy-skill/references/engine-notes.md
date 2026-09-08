# 去功能点：各 type 实现要点

按已识别的 type 阅读对应章节；功能分类、核心玩法保留边界见 [strategy.md](../strategy.md)，执行与验收接口见 [stage-contract.md](stage-contract.md)。这里集中维护实现知识，脚本仍由 type 注册表路由。脚本名称仅用于查阅统一 SCRIPTS-INDEX，不是绕过阶段 driver 的调用指令。

## android

- Activity/Fragment 入口：在核对生命周期和返回结果后终止目标页面；不能不分方法地替换为 `return-void`。
- XML View 使用 `gone` 或删除节点，同时处理父容器占位；菜单项检查 `res/menu/*.xml`。
- Java/smali 弹窗从 `AlertDialog`、`showDialog`、`Dialog.show` 调用链定位。保留仍被引用的类，按方法返回类型和回调契约桩化。

## il2cpp

### NGUI 与动态菜单

| 目标 | 实现 | 原因 |
|---|---|---|
| MenuPage tab | `showOnPlatform = 0` | `GetComponentsInChildren(true)` 仍收集 inactive 节点 |
| UITable/UIGrid 普通按钮 | `m_IsActive = False`，检查自动重排 | 布局通常跳过 inactive 子项 |
| GenerateButtons 生成的语言按钮 | 裁剪 `GuiLanguageSelect.buttonList` | 隐藏模板会被重新生成覆盖 |

`hide-menu-pages.py` 的 `--hide`、`--hide-go`、`--hide-langs` 对应三种目标。同一源 `data.unity3d` 的关联修改应合并应用，避免后一次写回覆盖前一次。语言索引须从当前资源核实，不能套用其他 APK 的索引。

UnityPy 重打包需核实输出：旧经验中 `env.save()` 未正确保存 Bundle，使用 `fitem.save(packer="lz4")`；自定义 MonoBehaviour 通过 `m_Script` 关联 MonoScript 类名。旧布局中的偏移 0x14/0 只可作定位线索，须验证当前版本与结构。

### 多场景标题与品牌

`hide-unity-gameobject.py` 按 Bundle 子文件、场景、名称定位；同名对象用 `--pid` 精确区分。检查加载页和主菜单的独立实例，以及同一入口的 UGUI/3D 对象。隐藏父节点会同时影响子标签、勾选框和按钮，先确认用途。仅改 Texture2D 不一定覆盖实际标题渲染路径；引擎闪屏与游戏 Logo 分开核实，`unity.splash-enable` 配置须在当前 Unity 版本验证。

### UIElements

`UnityEngine.UIElements.Button` 不是 MonoBehaviour，不能套用 Behaviour 显隐 hook。`set_visible(false)` 可能留下布局空隙；`RemoveFromHierarchy()` 可移除节点，`IStyle.set_display(None)` 也可释放布局，但涉及 StyleEnum 包装。

从当前 dump/metadata 定位宿主字段偏移、宿主更新方法和 `VisualElement.RemoveFromHierarchy`，在节点实际生成后处理，并切断仍可达的 click handler。`generate-ui-hide-hooks.py` 是相关生成器；不得复用其他项目 RVA。加载与基址机制见 [native hook 引擎设置](../../../strategy/il2cpp-strategy-skill/references/native-hook-engine-setup.md)。

### 工程与 hook 边界

目标工程位于 `crackings/<type>/<Name>/project/`，不可硬编码旧 `output-projects/`。先识别当前工程使用 A64HookFunction 还是 ASBuilder/libtool 的 `baseImageAddr`/`fakeCpp`，后者的链接、加载等待和页权限要求以 type workflow 的收入转发阶段说明为准。排行榜等非核心跳转可以桩化，但 UI、布局和调用链均须验收。新增隐藏判断须同步声明、实现与安全默认分支。

## unity-mono

NGUI/UGUI 资源与动态数组处理参考上面的 Unity 规则；托管逻辑在 .NET DLL 中，用 ILSpy/dnSpy 定位后由当前阶段脚本修改。弹窗核查 `Dialog.show`/`ShowDialog` 与场景 GameObject 两条路径；修改 DLL 后必须验证重编译与运行时依赖。

## cocos2dx

优先处理解密后的 Lua 按钮回调、弹窗回调与节点创建逻辑，定位词包括 `Dialog`、`showPop`、`popup`。场景检查 `.plist`/`.scene`；C++ 实现需要在对应 `.so` 中定位。仅置空回调不能消除可见按钮与占位。广告调用可能跨 Lua、C++ 和 Android 容器层。

## cocos-creator

解密后的 JS/JSC 中核查按钮、弹窗函数及生成逻辑；场景 `.fire`/`.scene` 和 `.prefab` 中核查节点。JS 回调置空、节点移除、父布局重排需要形成闭环；Android SDK 弹窗仍须核对原生调用链。

## unreal

UMG widget 与 Blueprint 可能位于 `.uasset`/`.pak` 中，先确认版本和可用编辑链；FModel 用于检查/导出，不等同于具备任意资源回写能力。Blueprint 修改需要匹配的 UE 工具链。原生 SDK 弹窗需要识别实际 Java/JNI/native 调用方，不能把所有弹窗都假定在 `libUE4.so`。

## flutter

区分有源码的 widget 树修改与仅有 Dart AOT 的 `libapp.so` 分析。blutter/reFlutter 是定位线索，不能将分析输出当作可直接重编译的原工程。弹窗定位 `showDialog`；Platform/MethodChannel 桩化必须保持 Dart Future/result 回调完成，避免页面一直等待。广告插件可能同时涉及 Dart 与 Java。

## xamarin

C# 按钮与弹窗逻辑在 `assemblies/*.dll`，XAML 可能是 DLL 内嵌资源，也可能转为 Android 布局。使用 ILSpy/dnSpy 定位 `ShowDialog`/`AlertDialog` 后检查托管与原生两侧；替换 DLL 需要验证资源、引用和返回契约。

## air

SWF DisplayList 按钮与弹窗由 ActionScript 控制，可用 ffdec 定位 `showDialog`/`Alert`，同时处理节点和回调。Android 容器层仍可能有独立 Java/XML UI；ANE 广告/同意入口保留被引用的扩展类，按实际签名桩化，不要把 ActionScript 方法当作 smali。

## defold

内置按钮由 `game.arcd` 中编译的 Lua/GUI 逻辑控制，需核实解包与回写能力。native 引擎经 `com.defold.*JNI` 引用 SDK 类，不能因隐藏入口而物理删除仍被引用的 smali。JNI `addToQueue` 等回调拦截须保持队列和状态推进；manifest 清理只处理已确认可移除组件，`.so` 必须先检查依赖。详见 [Defold native SDK 策略](../../../strategy/defold-strategy-skill/strategy.md#7-sdk-移除进阶and64inlinehook-native-hook策略规则)。

## gamemaker

`game.droid` 内的 ROOM 对象与 CODE 中的动态创建逻辑需要分别处理，不能因为不支持直接 smali patch 就跳过去功能点阶段。

用 UndertaleModTool/UndertaleModCli 对应的正式脚本处理 ROOM：移除一个房间实例时，核查 `layer.InstancesData.Instances`、`room.GameObjects`、`room.InstanceCreationOrderIDs.InstanceIDs` 三处。只清图层列表时，VM 仍可能从扁平 GameObjects 列表创建对象。

`instance_create_depth` 等动态生成对象需另行定位 GML CODE；工具和格式支持时重编译对应代码。`inspect-gamemaker-rooms.py` 用于定位，`remove-gamemaker-buttons.py` 的 `--objects`/`--replace` 处理实例和代码替换。实际工具能力不足时记录阻塞，不把 JNI 桩化当作 UI 移除验收。

## libgdx

Scene2D 的 Stage/Actor 通常由 dex 游戏逻辑创建；高度混淆时按行为和资源加载定位，不依赖类名。`setVisible` 只处理可见性，移除 Actor 后仍须核对 Table/Cell 占位和布局。AssetManager 加载观测可区分核心 hash 资源与广告资源；hash 资源池及参与解密的 PGL `.so` 不能按广告资源误删。弹窗可能是 Java 原生，也可能是引擎 Actor。
