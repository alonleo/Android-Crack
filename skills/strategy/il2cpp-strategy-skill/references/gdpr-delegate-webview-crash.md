# Unity il2cpp 卡加载页全链路修复 + Frida 探针方法论

> 来源：Unity il2cpp 项目实测（Unity 6000.3.12f1，arm64）
> 关联：EXPERIENCES.md「卡加载全链路」条目；探针脚本在 `scripts/common/probe-*.js`

## 1. 症状 → 根因速查表

| 症状 | 根因 | 修复 |
|------|------|------|
| 卡加载页、进度条冻结 | UMP GDPR 无网络请求失败 → `InitDone` 永不触发 → `WaitRunLoadingBar` 协程不启动 | hook `OnConsentInfoUpdated`(0x01351660) 直接 invoke InitDone 委托 |
| 加载页画面不消失 | Fade 协程 WaitUntil 条件 `_Fade_b__15_0`(0x013F8388) 返回 false 永远等待 | hook 返回 **true**（Unity WaitUntil 语义：true=停止等待） |
| 进主菜单后反复崩溃重启（看似滑动无效） | Gadsme 广告 SDK 用 Vuplex WebView 渲染 → WebView 沙盒被杀 → SIGABRT | hook `GadsmeSDKController.Awake/Start`(0x0135B354/0x0135B454) 直接 return |
| 广告/IAP hook 注入后游戏异常 | hook-plan.yaml RVA 未验证（12 字节函数被 A64HookFunction 溢出改写） | 先 Frida attach 验证 RVA 是函数入口，再注入 |

## 2. 关键机制

### 2.1 Il2CppDelegate 调用约定（血泪坑）

`System.Action` 委托（il2cpp）内存布局：
```
+0x00: Il2CppObject 基类
+0x10: method_ptr   ← 实际函数地址
+0x20: target       ← 委托绑定的 this 对象
```
**调用必须 `method_ptr(target)`**：
```cpp
void* init_done = *(void**)((char*)this_ptr + 0x20);  // InitDone 字段
void* method_ptr = *(void**)((char*)init_done + 0x10);
void* target = *(void**)((char*)init_done + 0x20);
((void(*)(void*))method_ptr)(target);
```
直接 `fn()` 调用 → 协程 this=null → il2cpp abort。**target 在 +0x20 不是 +0x18**（+0x18 是 invoke_impl）。

### 2.2 Unity WaitUntil 语义

`WaitUntil(predicate)` 的 predicate：**返回 true = 停止等待继续执行**，返回 false = 继续等待。
hook keepWaiting 委托时**返回 true** 才能让协程推进。

### 2.3 崩溃诊断

- tombstone 位置：`/storage/emulated/0/Android/data/<pkg>/files/tombstone_00`
- `#01 pc ... libmonochrome.so` = WebView 渲染库（Android WebView 相关崩溃）
- logcat 关键行：`Killing ... webview:sandboxed_process0 ... isolated not needed`（沙盒被系统回收）

## 3. Frida 探针模式（可复用）

| 探针 | 目的 |
|------|------|
| `probe-scrollsnap-base.js` | hook ScrollSnap 拖拽链 |

### 3.1 StandaloneInputModule 正确地址

Unity 6 (6000.3.x) uGUI：
- `StandaloneInputModule.ProcessTouchEvents` = **0x27EA558**
- `StandaloneInputModule.ProcessTouchPress` = **0x27EAB3C**
- **不要** hook `TouchInputModule`（0x27EBD54/0x27EBE98）——那是旧模块，游戏不工作。

查法：metadata.json 里搜 `StandaloneInputModule`。

### 3.2 adb input swipe 的触摸 phase 坑

`adb input swipe/tap` 注入的触摸 phase 无效（Input.GetTouch 读到垃圾 fingerId/phase），
**不能用于验证 UI 交互**。验证 UI 交互必须：
1. 用户真手测试，或
2. Frida 直接调用游戏方法（`NativeFunction` + 实例指针）

### 3.3 直接调用游戏方法（区分「逻辑坏」vs「UI 事件坏」）

```js
// 捕获实例：hook 该 MonoBehaviour 的 Update 拿 this
Interceptor.attach(libBase.add(0x01371DE0), {  // UiMainLobby.Update
    onEnter: function (a) { instance = a[0]; }
});
// 直接调用
var fn = new NativeFunction(libBase.add(0x01372164), 'void', ['pointer']);  // OnClickBtnPlay
fn(instance);
```
若直接调用 → 游戏正常开始（LoadLevel 链工作），则问题在 UI 输入层，不在游戏逻辑。

## 4. 遗留问题（未解）

主菜单 TAP TO PLAY 区域 UI 事件不触发：`StandaloneInputModule.ProcessTouchPress`
从不被调用（即使真手操作），设置按钮有效但 PLAY 区域无效。疑似：
- 场景序列化 onClick 绑定失效（UnityEvent 按类名解析，目标类被过滤？）
- 或输入模块状态异常
- 或 PLAY 按钮被透明层遮挡
待后续项目验证。
