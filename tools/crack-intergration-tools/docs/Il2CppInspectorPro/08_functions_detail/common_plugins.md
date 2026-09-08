# 08 · `Il2CppInspector.Common` 插件系统

> 文件范围：
> - `Plugins/Internal/PluginManager.cs`
> - `Plugins/Internal/PluginHooks.cs`
> - `Plugins/Internal/ICorePlugin.cs`
> - `Plugins/API/V100/IPlugin.cs`
> - `Plugins/API/V100/ILoadPipeline.cs`
> - `Plugins/API/V100/IPluginOption.cs`
> - `Plugins/API/V100/PluginEventInfo.cs` + 全部 `*EventInfo`
> - `Plugins/API/V100/PluginServices.cs`
> - `Plugins/API/V100/ReentrantAttribute.cs`
> - `Plugins/API/V101/IPlugin.cs` + `Adapter.cs`

---

## `PluginManager.EnsureInit`

- **签名**: `static PluginManager EnsureInit()`
- **位置**: `Il2Inspector.Common/Plugins/Internal/PluginManager.cs:~60`
- **可见性**: public static
- **调用了**:
  - 第一次调用 → `Reload(...)`
- **调用**: CLI `App.Run`、`FrontendCore.UiContext` 构造、GUI `App.OnStartup`
- **简要说明**: 单例初始化

## `PluginManager.Reload`

- **签名**: `static void Reload(string pluginPath = null, bool reset = true, bool coreOnly = false)`
- **位置**: `PluginManager.cs:~110`
- **可见性**: public static
- **副作用**: 清空 `ManagedPlugins`；反射加载 `./plugins/*.dll`
- **调用了**:
  - `Directory.GetFiles(pluginPath, "*.dll", SearchOption.AllDirectories)`
  - `McMaster.NETCore.Plugins.PluginLoader.CreateFromAssemblyFile`
  - `Activator.CreateInstance(type)`
- **抛出**: `DirectoryNotFoundException` 当插件目录缺失
- **简要说明**: 重新加载所有插件

## `PluginManager.Reset(IPlugin)`

- **签名**: `static IPlugin Reset(IPlugin)`
- **位置**: `PluginManager.cs:~200`
- **可见性**: public static
- **简要说明**: 清空插件状态（缓存等）

## `PluginManager.OptionsChanged(IPlugin)`

- **签名**: `static PluginOptionsChangedEventInfo OptionsChanged(IPlugin)`
- **位置**: `PluginManager.cs:~225`
- **可见性**: public static
- **调用了**: `plugin.OptionsChanged(...)`
- **简要说明**: 转发选项变更

## `PluginManager.ValidateAllOptions`

- **签名**: `static PluginOptionsChangedEventInfo ValidateAllOptions()`
- **位置**: `PluginManager.cs:~250`
- **可见性**: public static
- **简要说明**: 全插件选项校验

## `PluginManager.Try<I, E>`

- **签名**: `internal static E Try<I, E>(Action<I, E> action, [CallerMemberName] string hookName = null) where E : PluginEventInfo, new()`
- **位置**: `PluginManager.cs:~290`
- **可见性**: internal static
- **副作用**: 栈追踪递归保护
- **调用**: 所有 `PluginHooks.*` 内部
- **简要说明**: hook fan-out + 递归守卫

---

## `PluginHooks.LoadPipelineStarting`

- **签名**: `static PluginLoadPipelineStartingEventInfo LoadPipelineStarting()`
- **位置**: `Il2Inspector.Common/Plugins/Internal/PluginHooks.cs:~15`
- **可见性**: public static
- **调用了**: `PluginManager.Try<ILoadPipeline, ...>(...)`

## `PluginHooks.PreProcessMetadata`

- **签名**: `static PluginPreProcessMetadataEventInfo PreProcessMetadata(BinaryObjectStream)`
- **位置**: `PluginHooks.cs:~20`
- **可见性**: public static
- **调用**: `Metadata.FromStream` 内部

## `PluginHooks.PostProcessMetadata`

- **签名**: `static PluginPostProcessMetadataEventInfo PostProcessMetadata(Metadata)`
- **位置**: `PluginHooks.cs:~25`
- **可见性**: public static
- **调用**: `Metadata.FromStream` 内部

## `PluginHooks.GetStrings` / `GetStringLiterals`

- **签名**: `static PluginGetStringsEventInfo GetStrings(Metadata)` / `static PluginGetStringLiteralsEventInfo GetStringLiterals(Metadata)`
- **位置**: `PluginHooks.cs:~28-32`
- **可见性**: public static
- **调用**: `Metadata.FromStream` 内部

## `PluginHooks.PreProcessImage` / `PostProcessImage<T>`

- **签名**: `static PluginPreProcessImageEventInfo PreProcessImage(BinaryObjectStream)` / `static PluginPostProcessImageEventInfo PostProcessImage<T>(FileFormatStream<T>)`
- **位置**: `PluginHooks.cs:~38-42`
- **可见性**: public static
- **调用**: `FileFormatStream.Load` + `Il2CppBinary.Load` 内部

## `PluginHooks.PreProcessBinary` / `PostProcessBinary`

- **签名**: `static PluginPreProcessBinaryEventInfo PreProcessBinary(Il2CppBinary)` / `static PluginPostProcessBinaryEventInfo PostProcessBinary(Il2CppBinary)`
- **位置**: `PluginHooks.cs:~48-52`
- **可见性**: public static
- **调用**: `Il2CppBinary.Load` / `PrepareMetadata`

## `PluginHooks.PostProcessPackage`

- **签名**: `static PluginPostProcessPackageEventInfo PostProcessPackage(Il2CppInspector)`
- **位置**: `PluginHooks.cs:~58`
- **可见性**: public static
- **调用**: `Il2CppInspector.LoadFromStream` 末尾

## `PluginHooks.LoadPipelineEnding`

- **签名**: `static PluginLoadPipelineEndingEventInfo LoadPipelineEnding(List<Il2CppInspector>)`
- **位置**: `PluginHooks.cs:~60`
- **可见性**: public static
- **调用**: CLI/GUI 流水线结束

## `PluginHooks.PostProcessTypeModel` / `PostProcessAppModel`

- **签名**:
  - `static PluginPostProcessTypeModelEventInfo PostProcessTypeModel(TypeModel)`
  - `static PluginPostProcessAppModelEventInfo PostProcessAppModel(AppModel)`
- **位置**: `PluginHooks.cs:~62-64`
- **可见性**: public static
- **调用**: 用户在 GUI/CLI 显式触发

---

## `IPlugin` (V100)

- **签名**: `interface IPlugin`
  - `string Id { get; }`
  - `string Name { get; }`
  - `string Author { get; }`
  - `string Description { get; }`
  - `string Version { get; }`
  - `List<IPluginOption> Options { get; }`
  - `void OptionsChanged(PluginOptionsChangedEventInfo)`
- **位置**: `Il2Inspector.Common/Plugins/API/V100/IPlugin.cs`
- **可见性**: public
- **调用**: `PluginManager.Reload` 反射加载

## `ILoadPipeline` (V100)

- **签名**: 13 hook 方法
  - `PluginLoadPipelineStartingEventInfo LoadPipelineStarting(PluginLoadPipelineStartingEventInfo)`
  - `PluginPreProcessMetadataEventInfo PreProcessMetadata(BinaryObjectStream, PluginPreProcessMetadataEventInfo)`
  - `PluginPostProcessMetadataEventInfo PostProcessMetadata(Metadata, PluginPostProcessMetadataEventInfo)`
  - `PluginGetStringsEventInfo GetStrings(Metadata, PluginGetStringsEventInfo)`
  - `PluginGetStringLiteralsEventInfo GetStringLiterals(Metadata, PluginGetStringLiteralsEventInfo)`
  - `PluginPreProcessImageEventInfo PreProcessImage(BinaryObjectStream, PluginPreProcessImageEventInfo)`
  - `PluginPostProcessImageEventInfo PostProcessImage(IFileFormatStream, PluginPostProcessImageEventInfo)`
  - `PluginPreProcessBinaryEventInfo PreProcessBinary(Il2CppBinary, PluginPreProcessBinaryEventInfo)`
  - `PluginPostProcessBinaryEventInfo PostProcessBinary(Il2CppBinary, PluginPostProcessBinaryEventInfo)`
  - `PluginPostProcessPackageEventInfo PostProcessPackage(Il2CppInspector, PluginPostProcessPackageEventInfo)`
  - `PluginLoadPipelineEndingEventInfo LoadPipelineEnding(List<Il2CppInspector>, PluginLoadPipelineEndingEventInfo)`
  - `PluginPostProcessTypeModelEventInfo PostProcessTypeModel(TypeModel, PluginPostProcessTypeModelEventInfo)`
  - `PluginPostProcessAppModelEventInfo PostProcessAppModel(AppModel, PluginPostProcessAppModelEventInfo)`
- **位置**: `Plugins/API/V100/ILoadPipeline.cs`
- **可见性**: public interface

## `IPluginOption`

- **签名**:
  - `string Name { get; }`
  - `string Description { get; }`
  - `bool Required { get; }`
  - `object Value { get; set; }`
  - `Func<bool> If { get; }`
  - `void SetFromString(string value)`
- **位置**: `Plugins/API/V100/IPluginOption.cs`
- **可见性**: public

## `ReentrantAttribute`

- **签名**: `[AttributeUsage(AttributeTargets.Method)] sealed class ReentrantAttribute : Attribute`
- **位置**: `Plugins/API/V100/ReentrantAttribute.cs`
- **可见性**: public
- **调用**: `PluginManager.Try` 内部检查

## `PluginServices`

- **签名**: `static class PluginServices`
- **位置**: `Plugins/API/V100/PluginServices.cs`
- **可见性**: public
- **简要说明**: 暴露给插件的服务（类型/log/event）

---

## `V101.IPlugin` (Adapter 占位)

- **位置**: `Plugins/API/V101/IPlugin.cs` + `Adapter.cs`
- **可见性**: public
- **简要说明**: 仓库注释标注为「未来版本契约」，**PluginManager 当前未激活 V101**（仅 V100）
- **跳过理由**：未启用