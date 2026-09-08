# AssetStudio 汉化辅助工具

> 用 AssetStudio 库（`tools/crack-intergration-tools/source-projects/assetstudio`）正确解析
> Unity 6 MonoBehaviour 的脚本类型（UnityPy 缺失的 DummyDll TypeTree 能力）。
>
> 背景: HighwayBikeAttackRaceGame (Unity 6.0 il2cpp, 2026-08-09)。
> UnityEngine.UI.Text 组件的 m_Text 字段布局 + 变长替换崩溃根因已确认（见 [EXPERIENCES.md](../../../../EXPERIENCES.md) §il2cpp）。

## 用途

1. **提取 Text 组件**：用游戏 DummyDll 正确识别所有 UnityEngine.UI.Text / TMPro 组件
2. **导出 m_Text 数据**：JSON 输出 Text 组件的原始数据（可解析 m_Text 内容 → 生成翻译表）
3. **布局验证**：确认 Text 组件 m_Text 位置（offset 144: len + UTF-8）与后续字段

## 构建（Linux）

```bash
# 1. 构建 AssetStudio 核心库（net10.0 跨平台）
cd tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio
dotnet build -f net10.0 -c Release

# 2. 构建 AssetStudio.Utility
cd ../AssetStudio.Utility && dotnet build -c Release

# 3. 构建本工具
cd skills/strategy/il2cpp-strategy-skill/scripts/common/assetstudio-haniz
dotnet build -c Release
```

依赖（NuGet）：Mono.Cecil 0.11.5, ZstdSharp.Port 0.7.2, MessagePack 2.6.100-alpha, Newtonsoft.Json 13.0.3

## 运行

```bash
# <data.unity3d> <DummyDll目录> <输出json>
dotnet run -c Release -- <data.unity3d> <dump/DummyDll> <out.json>
# 输出: JSON 含每个 Text/TMP 组件的 file/pathID/name/script/rawLen/hex(原始字节)
```

DummyDll 由 Il2CppDumper 生成（`crackings/<type>/<Name>/stages/05-il2cpp-dump/dump/DummyDll/`）。

## 关键结论（详见 [EXPERIENCES.md](../../../../EXPERIENCES.md) §il2cpp）

- **m_Text 布局**：offset 144 = int32 长度 + offset 148 = UTF-8 文本；m_Text 是 Text 组件**最后一个字段**（后 1 字节对齐填充）
- **变长替换崩溃根因**：MonoBehaviour 对象 DataSize 变化与 bundle SerializedFile 元数据不符 → 运行时 Loading.Preload SIGTRAP
- **等长替换安全**：不改变对象大小，可稳定汉化
- **AssetStudio 无写回**：完整汉化需扩展 SerializedFile 写回或重新打包资源
