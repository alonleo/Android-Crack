# il2cpp 黑屏 / 卡加载修复

> 来源: Unity il2cpp 项目实测（Unity 6000.3.12f1, arm64）
> 关联: EXPERIENCES.md「黑屏/卡加载全链路修复」条目
> 适用: 所有 FakerAndroid fake 模式产出的 il2cpp 项目（patched.apk 启动崩溃/黑屏/卡加载）

## 1. 症状 → 根因速查表

| 症状 | 根因 | 修复 |
|------|------|------|
| 启动 SIGSEGV（libil2cpp.so 偏移崩溃） | FakerAndroid fakeCpp 模式 RVA 偏移错误 | 覆盖为 A64HookFunction 模板 |
| 安装 INSTALL_FAILED_MISSING_SPLIT | manifest 残留 requiredSplitTypes | 清除 split 属性 |
| Activity class does not exist | manifest 缺 MainActivity 注册 | _ensure_main_activity_declared |
| SafeDKApplication ClassNotFoundException | application 指向被过滤类 | 替换为 com.android.boot.App |
| VungleProvider ClassNotFoundException | 广告 provider 类被 dex 过滤 | manifest 移除广告 provider |
| **纯黑屏（1 帧）** | MainActivity extends Activity 不加载 Unity | extends UnityPlayerActivity |
| VerifyError: Unresolved UnityPlayer | inject SMALI_DIRS 只到 10 | 扩展到 15 |
| LoadedApk CoreComponentFactory 缺失 | androidx/core 被过滤 | EXCLUDE 只留 compose |
| **卡 Loading（Unity 已渲染）** | appsflyer/applovin/firebase 类被过滤 | 保留游戏 JNI 依赖类 |
| 卡 Loading 等网络 | Firebase Remote Config 无网络 | hook RemoteConfigFirebaseInit |

## 2. 关键决策点

### 2.1 MainActivity 必须 extends UnityPlayerActivity
- FakerAndroid 壳 Activity 必须继承 `com.unity3d.player.UnityPlayerActivity`，否则 Unity 引擎不启动。
- UnityPlayerActivity 在 smali_classes5（注入 dex 提供运行时类），libs jar 提供编译期 classpath。
- 编译报错「找不到符号 UnityPlayerActivity」时，先确认 libs jar 是否含该类 + 是否注入 dex，
  不要降级为 extends Activity（会导致黑屏）。

### 2.2 smali 过滤白名单（inject-filtered-original-dex.py EXCLUDE）
```
必须保留：com/appsflyer, com/applovin, com/google(含 firebase), com/unity3d/player,
          androidx/*, kotlin, kotlinx, com/yandex, io/bidmachine
可过滤：com/facebook(不含 ads 桥接), com/adjust, com/vungle, com/ironsource,
        com/chartboost, com/unity3d/ads, com/unity3d/services, com/amazon/device/ads
```
⚠️ EXCLUDE_PARTS 不要用宽泛词（ads/services/google），会误伤游戏 JNI 依赖。

### 2.3 网络等待绕过（无网络环境）
游戏常等待 Firebase Remote Config / 广告初始化。用 A64HookFunction hook 对应方法直接 return：
- `RocketRemoteConfig.RemoteConfigFirebaseInit`（public static void）
- `GameService.InitializeFirebase` 等
hook 必须在 libil2cpp.so 加载后安装（installNativeHooks 后台线程 /proc/self/maps 基址）。

## 3. raw vs patched 像素级对比法（验证画面一致）
```python
from PIL import Image
img = Image.open('screenshot.png').convert('RGB')
w, h = img.size
sub = img.crop((w//3, 2*h//3, 2*w//3, h))   # 中下区域（UI 文字/按钮）
px = list(sub.getdata())
white = sum(1 for r,g,b in px if r>200 and g>200 and b>200)
print(f"中下白像素={white}")  # raw 与 patched 一致 → 画面相同
```
黑屏判定：`dumpsys gfxinfo <pkg>` Total frames rendered < 5 = 引擎没渲染。

## 4. 涉及脚本（均已修复，见代码内 [FLOWFIX] 注释）
- sub-stage-template-integration.py（内联实现 + MainActivity extends UnityPlayerActivity + App.installNativeHooks）
- sub-stage-as-build.py（manifest split/MainActivity/广告 provider/application 清理 + CMakeLists GLOB 修复）
- sub-stage-extract-filtered-smali-jars.py（EXCLUDE 只过滤 compose + jar 同步编译入口）
- sub-stage-inject-filtered-original-dex.py（保留游戏 JNI 依赖类）
- convert-smali-to-jars.py / inject-smali-dex.py（SMALI_DIRS 扩展到 15）
- skills/common/scripts/template-files/il2cpp/native-lib.template.cpp（A64HookFunction + installNativeHooks 标准模板）
