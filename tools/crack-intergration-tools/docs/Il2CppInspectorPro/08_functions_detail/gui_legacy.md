# 08 · `Il2CppInspector.GUI`（旧版 WPF）

> 文件：
> - `Il2CppInspector.GUI/App.xaml` + `App.xaml.cs`
> - `Il2CppInspector.GUI/MainWindow.xaml` + `MainWindow.xaml.cs`
> - `Il2CppInspector.GUI/LoadOptionsDialog.xaml` + `.xaml.cs`
> - `Il2CppInspector.GUI/PluginConfigurationDialog.xaml` + `.xaml.cs`
> - `Il2CppInspector.GUI/PluginManagerDialog.xaml` + `.xaml.cs`
> - `Il2CppInspector.GUI/EqualityConverter.cs` / `HexStringValueConverter.cs`
> - `Il2CppInspector.GUI/User.Designer.cs`（自动生成，跳过）+ `User.settings`

---

## `App.OnStartup`

- **签名**: `void OnStartup(StartupEventArgs e)`
- **位置**: `Il2Inspector.GUI/App.xaml.cs:~50`
- **可见性**: protected override
- **调用了**: `MainWindow` 实例化
- **简要说明**: 启动入口

## `App.LoadPackageAsync`

- **签名**: `Task LoadPackageAsync(...)`
- **位置**: `App.xaml.cs:~120`
- **可见性**: internal
- **调用了**: `PluginManager.EnsureInit`、`Il2Inspector.LoadFromPackage`
- **简要说明**: APK/AAB 包异步加载

## `App.LoadMetadataAsync`

- **签名**: `Task LoadMetadataAsync(...)`
- **位置**: `App.xaml.cs:~170`
- **可见性**: internal
- **调用了**: `Metadata.FromStream`
- **简要说明**: 单 metadata 文件

## `App.LoadBinaryAsync`

- **签名**: `Task LoadBinaryAsync(...)`
- **位置**: `App.xaml.cs:~210`
- **可见性**: internal
- **调用了**: `FileFormatStream.Load`
- **简要说明**: 单 binary 文件

---

## `MainWindow.ctor`

- **签名**: `MainWindow()`
- **位置**: `Il2Inspector.GUI/MainWindow.xaml.cs:~50`
- **可见性**: public
- **调用了**: `InitializeComponent`
- **简要说明**: WPF 构造

## `MainWindow.OnLoaded`

- **签名**: `void OnLoaded(object sender, RoutedEventArgs e)`
- **位置**: `MainWindow.xaml.cs:~90`
- **可见性**: private
- **简要说明**: 加载完成回调

## `MainWindow.SelectBinary_Click`

- **签名**: `void SelectBinary_Click(object sender, RoutedEventArgs e)`
- **位置**: `MainWindow.xaml.cs:~150`
- **可见性**: private
- **调用了**: `Ookii.Dialogs.Wpf.VistaOpenFileDialog`
- **简要说明**: 选 binary 文件

## `MainWindow.SelectMetadata_Click`

- **签名**: `void SelectMetadata_Click(object sender, RoutedEventArgs e)`
- **位置**: `MainWindow.xaml.cs:~200`
- **可见性**: private
- **简要说明**: 选 metadata 文件

## `MainWindow.Analyze_Click`

- **签名**: `void Analyze_Click(object sender, RoutedEventArgs e)`
- **位置**: `MainWindow.xaml.cs:~280`
- **可见性**: private
- **调用了**: `RunAnalysis`
- **简要说明**: 触发分析

## `MainWindow.RunAnalysis`

- **签名**: `void RunAnalysis()` (private)
- **位置**: `MainWindow.xaml.cs:~340`
- **可见性**: private
- **副作用**: UI 状态切换
- **调用了**:
  - `Il2Inspector.LoadFromFile(...)`
  - `new TypeModel(...)`
  - `new AppModel(model, false)`
  - `AppModel.Build(...)`
- **简要说明**: GUI 主分析流（与 CLI 同构但带 UI 反馈）

## `MainWindow.GenerateCSharp_Click` / `GenerateCpp_Click` / `GenerateJSON_Click` / `GeneratePython_Click` / `GenerateDll_Click`

- **签名**: 5 个 `void Generate*_Click(object sender, RoutedEventArgs e)`
- **位置**: `MainWindow.xaml.cs:~400-600`
- **可见性**: private
- **调用了**:
  - `new CSharpCodeStubs(model).WriteSingleFile(...)`
  - `new CppScaffolding(am).Write(...)`
  - `new JSONMetadata(am).Write(...)`
  - `new PythonScript(am).WriteScriptToFile(...)`
  - `new AssemblyShims(model).Write(...)`
- **简要说明**: 5 个生成按钮各自走对应 emitter

---

## `LoadOptionsDialog.ctor`

- **签名**: `LoadOptionsDialog()`
- **位置**: `Il2Inspector.GUI/LoadOptionsDialog.xaml.cs:~15`
- **可见性**: public
- **简要说明**: 模态对话框设置 `ImageBase`

---

## `PluginConfigurationDialog.ctor`

- **签名**: `PluginConfigurationDialog()`
- **位置**: `Il2Inspector.GUI/PluginConfigurationDialog.xaml.cs:~30`
- **可见性**: public
- **简要说明**: 启用/选项配置

## `PluginConfigurationDialog.Ok_Click`

- **签名**: `void Ok_Click(object sender, RoutedEventArgs e)`
- **位置**: `PluginConfigurationDialog.xaml.cs:~250`
- **可见性**: private
- **调用了**: `PluginManager.ValidateAllOptions`、`PluginManager.Reload`
- **简要说明**: 保存选项 + 重载

---

## `PluginManagerDialog.ctor`

- **签名**: `PluginManagerDialog()`
- **位置**: `Il2Inspector.GUI/PluginManagerDialog.xaml.cs:~30`
- **可见性**: public
- **简要说明**: 插件列表（启用/顺序/刷新）

## `PluginManagerDialog.Refresh_Click`

- **签名**: `void Refresh_Click(object sender, RoutedEventArgs e)`
- **位置**: `PluginManagerDialog.xaml.cs:~110`
- **可见性**: private
- **调用了**: `PluginManager.Reload(...)`
- **简要说明**: 刷新磁盘

---

## `EqualityConverter.Convert` / `ConvertBack`

- **签名**: `object Convert(object value, Type targetType, object parameter, CultureInfo culture)` / `object ConvertBack(...)`
- **位置**: `Il2Inspector.GUI/EqualityConverter.cs:10-25`
- **可见性**: public
- **简要说明**: XAML 值比较

## `HexStringValueConverter.Convert` / `ConvertBack`

- **签名**: `object Convert(object value, ...)` / `object ConvertBack(...)`
- **位置**: `Il2Inspector.GUI/HexStringValueConverter.cs:15-40`
- **可见性**: public
- **简要说明**: 数字 ↔ 16 进制字符串