# 08 · PluginPreviewer / MeshPlugin / NativeLibs

## 1. PluginPreviewer/

```
PluginPreviewer/
├── PluginPreviewer.csproj
├── App.axaml(.cs)
├── ViewModels/
│   ├── MainViewModel.cs
│   └── ViewModelBase.cs
└── Views/
    ├── MainView.axaml(.cs)
    └── MainWindow.axaml(.cs)
```

### ViewModels/MainViewModel.cs

`class MainViewModel : ViewModelBase`

#### 字段
- `[ObservableProperty] Bitmap? _previewImage`
- `[ObservableProperty] TextDocument? _previewText`
- `[ObservableProperty] MeshObj? _previewMesh`

#### 命令
- `[RelayCommand] OpenFileCommand` —— 接收 IPC 来的指令
- `[RelayCommand] RenderMeshCommand`

#### 方法
- `Task SetPreviewImage(Bitmap image)` —— 来自 `IUavPluginPreviewerFunctions`
- `Task SetPreviewText(TextDocument doc)`
- `Task SetPreviewMesh(MeshObj mesh)`

### Views/MainView.axaml(.cs)

Avalonia 主视图，含：
- 顶部菜单（File / View）
- 中部 OpenGL 渲染区（`MeshPreviewerControl`）
- 底部状态栏

### Views/MainWindow.axaml(.cs)

Avalonia Window 壳。

---

## 2. PluginPreviewer.Desktop/

```
PluginPreviewer.Desktop/
├── PluginPreviewer.Desktop.csproj
├── Program.cs
├── App.axaml(.cs)
├── Window.axaml(.cs)
└── app.manifest
```

### Program.cs

`Main(string[] args)`：
- 装崩溃钩
- `BuildAvaloniaApp().StartWithClassicDesktopLifetime`

### App.axaml.cs / Window.axaml.cs

启动一个独立 Avalonia 应用，承载 `PluginPreviewer` 库的 UI。

### IPC（推测）

主进程 `UABEANext4.Desktop.exe` 与 `PluginPreviewer.Desktop.exe` 之间通过：
- 启动时 stdin/stdout JSON 协议
- 或命名管道

主进程调用 `MeshPreviewer.OnPreview` → `funcs.SetPreviewMesh(meshObj)` → IPC → PluginPreviewer 进程接收 → 渲染。

---

## 3. MeshPlugin/

```
MeshPlugin/
├── MeshPlugin.csproj
└── MeshPreviewer.cs (121 LoC)
```

### `class MeshPreviewer : IUavPluginPreviewer`

#### 字段
- `private Workspace? _workspace`
- `private IUavPluginPreviewerFunctions? _funcs`

#### `string Name => "Mesh Previewer"`
#### `string Description => "Live 3D mesh preview"`

#### `UavPluginPreviewerType SupportsPreview(Workspace workspace, AssetInst asset)`
- **签名**：`public UavPluginPreviewerType SupportsPreview(Workspace workspace, AssetInst asset)`
- **位置**：`MeshPreviewer.cs`
- **可见性**：public
- **算法**：
  1. 若是 GameObject（classId == 1）：
     - 读取 m_Components
     - 找 MeshFilter component
     - 解析其 m_Mesh 引用
  2. 若是 Mesh asset（classId == 43）：返回 Mesh
  3. 否则返回 None

#### `bool Initialize(Workspace workspace, IUavPluginPreviewerFunctions funcs)`
- **签名**：`public bool Initialize(Workspace workspace, IUavPluginPreviewerFunctions funcs)`
- **位置**：`MeshPreviewer.cs`
- **可见性**：public
- **副作用**：缓存 workspace + funcs

#### `Task OnPreview(AssetInst asset, UavPluginPreviewerFunctions funcs)`
- **签名**：`public Task OnPreview(AssetInst asset, UavPluginPreviewerFunctions funcs)`
- **位置**：`MeshPreviewer.cs`
- **可见性**：public
- **算法**：
  1. `workspace.GetBaseField(asset)`
  2. 若 GameObject → 找 MeshFilter → 加载 Mesh asset → 构造 MeshObj
  3. 若 Mesh → 构造 MeshObj
  4. `funcs.SetPreviewMesh(meshObj)`

### Mesh 构造

`MeshObj.BuildFromBaseField`：
- 读 `m_Vertices` (ByteArray)
- 读 `m_Indices` (UInt32 array)
- 读 `m_Channels` → `List<Channel>`
- 读 `m_Topology`
- 读 `m_LocalAABB` → `Bounds`

---

## 4. Controls/MeshPreviewer/ (in UABEANext4 main project)

### MeshPreviewerControl.cs
- `class MeshPreviewerControl : UserControl`
- 内部封装 Silk.NET.OpenGL
- `void SetMesh(MeshObj mesh)` —— 设置要渲染的网格
- `OnOpenGlInit / OnOpenGlRender` —— 回调

### MeshPreviewerShaders.cs
- `static class MeshPreviewerShaders`
- 静态字符串属性：
  - `VertexShaderSource`
  - `FragmentShaderSource`

---

## 5. NativeLibs/

### win-x64/

| DLL | 来源 | 用途 |
|---|---|---|
| `textureencoder.dll` | nesrak1/TextureEncoder | BC1-BC7 / ETC2 / ASTC 编码（推测基于 ISPC Texture Compressor） |
| `cuttlefish.dll` | GitHub: Cadair/cuttlefish 或类似 | Crunch 压缩库（解/编 DXT/ETC2） |
| `PVRTexLib.dll` | PowerVR | PVRTC 编解码（iOS） |

### linux-x64/

| SO | 用途 |
|---|---|
| `libtextureencoder.so` | 同上 Linux 版 |
| `libcuttlefish.so.2.10` | Crunch |
| `libPVRTexLib.so` | PVRTex |

### 加载机制

通过 MSBuild target `BuildNativeAndSetConfig`：
1. 编译时复制 `<NativeLibs>/<rid>/*` 到 `<output>/runtimes/<rid>/native/`
2. 运行时 .NET 8 RID-specific 加载
3. PluginLoadContext.LoadUnmanagedDll 通过 AssemblyDependencyResolver 解析

### 在插件中的使用

```csharp
// TexturePlugin/Helpers/TextureLoader.cs
[DllImport("textureencoder")]
static extern uint EncodeByCrunchUnity(...);

[DllImport("cuttlefish")]
static extern uint DecodeByCrunch(...);

[DllImport("PVRTexLib")]
static extern uint DecodeByPVRTexLib(...);
```

具体函数签名需要查 TextureLoader.cs。

---

## 关键调用栈

```
[Mesh Previewer 注册]
  → Workspace ctor → PluginLoader.LoadPluginsInDirectory
    → foreach MeshPlugin.dll:
      PluginLoadContext.LoadFromAssemblyPath
      → asm.GetExportedTypes
      → typeof(IUavPluginPreviewer).IsAssignableFrom(MeshPreviewer)
      → Activator.CreateInstance(MeshPreviewer)
      → _pluginPreviewers.Add
```

```
[Previewer 命中]
  → User select asset
  → InspectorToolViewModel.OnSelectedAssetChanged
    → workspace.Plugins.GetPreviewersThatSupport(workspace, asset)
    → for each (previewer, type):
      previewer.Initialize(workspace, funcs)
      previewer.OnPreview(asset, funcs)
        → MeshPreviewer: new MeshObj → funcs.SetPreviewMesh
        → TexturePreviewer: TextureLoader.LoadTexture → funcs.SetPreviewImage
        → TextAssetPreviewer: read m_Script → funcs.SetPreviewText
```

```
[IPC to PluginPreviewer]
  [main process] UavPluginPreviewerFunctions.SetPreviewMesh(mesh)
    → serialize mesh → write to stdin/pipe
  [previewer process] MainViewModel.OnMessageReceived
    → deserialize → PreviewMesh property changed
    → MeshPreviewerControl.SetMesh
      → recreate VBO/VAO
      → InvalidateVisual → 触发 OnOpenGlRender
        → glClear, glDrawArrays/Triangles
```