# FM 框架（Green Mushroom / rivergame）Mono .mdl 提取与反编译

> 来源: TopHeroes | 2026-08-02
> 用途: 遇到 `assets/Assemblies/*.mdl` + `libfm_mono_glue.so` 的 Unity 游戏时使用

## 识别特征

| 特征 | 说明 |
|---|---|
| `assets/Assemblies/*.mdl` | 自定义封装的 Mono 程序集（非标准 .dll） |
| `libfm_mono_glue.so` | FM Mono 桥接库（解密 .mdl → Mono 运行时加载） |
| 启动器 | `com.rivergame.*`（BaseActivity → FMMonoBaseActivity → UnityPlayerActivity） |
| 混合架构 | libil2cpp.so（玩法）+ Mono（启动/网络/登录）双运行时 |

## .mdl 格式

- 自定义头（每文件不同，如 `CT...` / `^I...`），内部嵌 `MZ`（PE/Mono DLL）
- 运行时由 libfm_mono_glue.so 解密 → Mono 加载
- 静态直接修改不可行（异或/随机密钥）→ 需运行时 dump

## 提取流程（frida）

### 1. 前置
- 设备 root + frida-server（版本与本地 frida 一致）
- `adb forward tcp:27042 tcp:27042`

### 2. hook LoadAssemblyWithImageBinary
```js
// libfm_mono_glue.so 导出: LoadAssemblyWithImageBinary
// 签名: (assemblyName:string, dllBytes:MZ*, len:int, flag:int, ...)
var glue = Process.findModuleByName("libfm_mono_glue.so");
var addr = null;
glue.enumerateExports().forEach(e => { if (e.name === "LoadAssemblyWithImageBinary") addr = e.address; });
Interceptor.attach(addr, {
  onEnter(args) {
    this.name = args[0].readCString();
    this.dll = null; this.len = 0;
    try { if (args[1].readU16() === 0x5a4d) { this.dll = args[1]; this.len = args[2].toInt32(); } } catch(e){}
  },
  onLeave(ret) {
    if (this.dll && this.len > 0) {
      // 分块 send 到 python 客户端（frida 写文件受 SELinux 限制）
      var chunk = 0x100000;
      for (var o = 0; o < this.len; o += chunk) {
        var sz = Math.min(chunk, this.len - o);
        send({type:"chunk", name:this.name, offset:o, size:sz, total:this.len}, this.dll.add(o).readByteArray(sz));
      }
    }
  }
});
```
- spawn 模式运行（`frida -f <pkg>`），用 setInterval 轮询等 glue 加载
- python 客户端用 `device.get_device_manager().add_remote_device("127.0.0.1:27042")` + `device.spawn()` 接收

### 3. 反编译
```
dotnet tool install -g ilspycmd
ilspycmd -l c ScriptProj.dll | grep Class
ilspycmd -t "ClassName" ScriptProj.dll   # 反编译单个类
```

## 产物示例（TopHeroes）
- ScriptProj.dll (37MB) — 游戏主逻辑（状态机/网络/登录）
- ScriptInterface.dll (4.5MB) — 接口层
- FMCommon / FM_MonoLib / ScriptThirdParty — FM 框架

## 坑位
- `Module.findExportByName` 可能 "not a function" → 用 `enumerateExports()` 遍历
- frida File API 写 /data/local/tmp 被 SELinux 拒 → 用 send() 传客户端保存
- 分块 send 大文件（37MB）需调大客户端等待时间
- spawn 模式脚本要在 interval 里等 libfm_mono_glue.so 加载（~50ms 轮询）
