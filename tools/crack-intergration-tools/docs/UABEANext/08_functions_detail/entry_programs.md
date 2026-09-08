# 08 · 入口与 App

涉及文件：
- `UABEANext4.Desktop/Program.cs`
- `UABEANext4.Desktop/App.axaml.cs`
- `UABEANext4.Desktop/Window.axaml.cs`
- `UABEANext4/App.axaml.cs` (67 LoC)

---

## Program.cs (UABEANext4.Desktop)

### `Main(string[] args)`
- **签名**：`public static void Main(string[] args)`
- **位置**：`UABEANext4.Desktop/Program.cs`
- **可见性**：public static
- **作用**：启动 Avalonia 桌面运行时
- **调用了**：`BuildAvaloniaApp`, `StartWithClassicDesktopLifetime`

### `UABEANExceptionHandler(object, UnhandledExceptionEventArgs)`
- **签名**：`public static void UABEANExceptionHandler(object sender, UnhandledExceptionEventArgs args)`
- **位置**：`UABEANext4.Desktop/Program.cs`
- **可见性**：public static
- **副作用**：写 `uabeacrash.log`（不再使用 mshta 弹窗）

### `BuildAvaloniaApp()`
- **签名**：`public static AppBuilder BuildAvaloniaApp()`
- **位置**：`UABEANext4.Desktop/Program.cs`
- **可见性**：public static
- **返回值**：`AppBuilder`
- **配置**：`.UsePlatformDetect().LogToTrace().StartWithClassicDesktopLifetime(args)`

---

## App.axaml.cs (UABEANext4)

### `App : Application`
- **位置**：`UABEANext4/App.axaml.cs:8`
- **可见性**：public

### `Initialize()`
- **签名**：`public override void Initialize()`
- **位置**：`UABEANext4/App.axaml.cs:10`
- **可见性**：public override

### `OnFrameworkInitializationCompleted()`
- **签名**：`public override void OnFrameworkInitializationCompleted()`
- **位置**：`UABEANext4/App.axaml.cs:16`
- **可见性**：public override
- **算法**：
  1. 若 `ApplicationLifetime is IClassicDesktopStyleApplicationLifetime`：
     - 从 DI 取 `MainViewModel`
     - `MainWindow.DataContext = mainViewModel`
     - `MainWindow.MainViewModel = mainViewModel`
  2. base.OnFrameworkInitializationCompleted
- **调用了**：`Ioc.Default.GetService<MainViewModel>`

---

## Window.axaml.cs (UABEANext4.Desktop)

### `class Window : Avalonia.Controls.Window`
- **位置**：`UABEANext4.Desktop/Window.axaml.cs`
- **可见性**：public
- **DataContext**：MainViewModel
- **Content**：MainView（嵌入主内容）

---

## 关键启动序列

```
[Program.Main]
  → AppDomain.UnhandledException += UABEANExceptionHandler
  → BuildAvaloniaApp().StartWithClassicDesktopLifetime
    → Avalonia 加载 App.axaml.cs
      → OnFrameworkInitializationCompleted
        → Ioc.Default.GetService<MainViewModel>()
        → MainWindow.DataContext = vm
    → MainWindow.Show()
```