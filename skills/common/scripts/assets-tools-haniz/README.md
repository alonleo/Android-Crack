# AssetsTools.NET 完整汉化工具

> 用 UABEA 的 **AssetsTools.NET** 库正确读写 Unity SerializedFile/Bundle，
> 实现 MonoBehaviour m_Text **变长**汉化（解决 UnityPy 变长替换崩溃根因）。

## 背景

HighwayBikeAttackRaceGame (Unity 6.0 il2cpp, 2026-08-09)：
- 游戏 UI 文本在 MonoBehaviour 的 m_Text 字段（静态序列化，不经 set_text）
- **变长替换崩溃根因**：bundle 中 MonoBehaviour 对象 DataSize 变化与 SerializedFile 元数据不符
- **UnityPy 变长崩溃**；**AssetsTools.NET `AssetsReplacerFromMemory` + `AssetsFile.Write` 正确更新 DataSize** → 变长安全

## 依赖

- `tools/crack-intergration-tools/source-projects/UABEA/Libs/AssetsTools.NET.dll`
- .NET 8

## 构建

```bash
cd skills/strategy/il2cpp-strategy-skill/scripts/common/assets-tools-haniz
dotnet build -c Release
```

## 运行

```bash
# <data.unity3d> <translations.json> <out>
dotnet run -c Release -- <data.unity3d> <translations.json> <out>
```

## 原理

1. `AssetsManager.LoadBundleFile` → 解压 bundle
2. 遍历各 `levelN`（SerializedFile）的 MonoBehaviour（TypeId=114）
3. 读原始数据 → 扫描 string 字段（int32 len + utf8）→ 匹配翻译表 → 变长重建
4. `AssetsReplacerFromMemory(af, info, newBuffer)` 替换（**正确更新对象大小**）
5. `BundleReplacerFromAssets` + `AssetBundleFile.Write` 写回 bundle

## 关键 API

- `AssetsReplacerFromMemory(AssetsFile, AssetFileInfo, byte[])` — 替换对象数据（变长安全）
- `BundleReplacerFromAssets(oldName, newName, AssetsFile, replacers)` — 组装回 bundle
- `AssetBundleFile.Write(writer, bundleReplacers)` — 写回
- `AssetFileInfo.GetAbsoluteByteStart(header)` + `af.Reader` — 读原始数据

## 验证

- 写回后 AssetStudio 可完整加载（结构无损坏）
- MB 数据中文正确（offset 144: "VR 模式" 等）
- 28 处文本跨 level0-3 汉化成功

## 与 AssetStudio 工具对比

- `assetstudio-haniz/`：解析 MonoBehaviour 字段布局（DummyDll TypeTree），只读验证
- **本工具**：AssetsTools.NET 正确写回（变长安全），是实际部署方案
