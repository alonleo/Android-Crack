# Unity 资源提取：UnityPy vs AssetStudio vs UABEANext

> 来源: TinkerIslandSurvivalStory (Unity 6, data.unity3d 67MB) | 2026-07-30
> 作者: Agent

## 工具对比

| 工具 | 平台 | CLI | 成熟度 | 维护状态 |
|------|------|-----|-------|---------|
| **UnityPy** (Python) | Linux/Mac/Win | ✅ | 高 | 活跃 (1.25.2) |
| **AssetStudio** (.NET) | Win only | ❌ (GUI) | 高 | Razmoth/Perfare |
| **AssetStudio CLI** (.NET) | Win only | ✅ | 中 | Razmoth 1.36 |
| **UABEANext** (Avalonia) | Linux/Mac/Win | ❌ (GUI) | 高 | nesrak1 |
| **AssetRipper** | Win/Mac/Linux | ✅ | 高 | nesrak1/AssetRipper |

## 结论：Linux 下用 UnityPy

本工作区主推 **UnityPy**（Python 跨平台库），原因：
1. ✅ 纯 Python，Linux 友好（不依赖 Windows Forms）
2. ✅ 已在本会话验证：TinkerIslandSurvivalStory 成功提取 3907 张 Texture2D
3. ✅ 同时输出 MonoScript 类名（1478 唯一 C# 类）
4. ✅ 自动跳过损坏纹理，不中断流程

**AssetStudio CLI 限制**: `.csproj` 只 target `net8.0-windows`/`net10.0-windows`，Linux 无法 build。

## UnityPy 关键 API

```python
from UnityPy import Environment  # 不是 AssetsManager!
from PIL import Image

env = Environment('/path/to/data.unity3d')
for obj in env.objects:
    tname = obj.type.name
    if tname == "Texture2D":
        raw = obj.read()
        img = raw.image  # PIL.Image
        img.save("out.png")
    elif tname == "TextAsset":
        raw = obj.read()
        data = bytes(raw.m_Script)
```

**坑**: 用 `AssetsManager` 类时，路径会被误解析为目录。**必须用 `Environment` 类**。

## sharedassets*.resource 是什么？

**常见误解**: sharedassets0/1/2.resource 包含游戏场景的所有纹理。
**真实情况**: 在很多 Unity 项目中，它们是 **FMOD 音频包 (FSB5)**，不是纹理。

```bash
xxd -l 16 sharedassets0.resource
# 00000000: 4653 4235 0100 0000 ...  ← "FSB5" magic
```

FSB5 = FMOD Sound Bank v5（音频格式），UnityPy **不支持解析**。

**如何确认**:
```bash
# 看 magic bytes
for f in sharedassets*.resource; do
    echo "$f: $(head -c 4 "$f" | xxd -p)"
done
# FSB5...  ← 是音频
# UnityRaw  ← 是纹理
```

**正确的纹理来源**:
- `data.unity3d` — 主资源包（含所有场景 + 纹理 + MonoBehaviour）
- `resources.resource` — Resources/ 目录内容（仅在 use "Unity Raw" 时是纹理）
- `sharedassets*.assets` — 旧版 Unity 场景包（v5 之前）

## 提取产物结构

```
06-images/unity_extracted/
├── data__chinese_font_Atlas_1967.png      # Texture2D
├── data__map_2491.png
├── data__tinker_island_iphonex_xxx.png
├── data__CardPackView_xxx.bin             # TextAsset (if any)
└── _manifest.json                          # 完整清单
```

`_manifest.json` 字段：

```json
{
  "bundles": [
    {
      "file": "data.unity3d",
      "size": 67663847,
      "objects": 24763,
      "textures_extracted": 3907,
      "textures_failed": 2,
      "text_assets_extracted": 0,
      "sprites_seen": 3864,
      "fonts_seen": 0
    }
  ],
  "textures": [{"bundle":"data.unity3d","name":"chinese_font Atlas","width":4096,"height":4096,"format":"DXT5"}],
  "sprite_names": [...],
  "fonts": [...]
}
```

## 已知 Unity 项目的纹理提取经验

| APK | Texture2D | MonoScript | 备注 |
|-----|-----------|------------|------|
| TinkerIslandSurvivalStory | 3,907 | 1,478 | Unity 6, 67MB data.unity3d |
| RealmDefenseHeroLegendsTD | (TBD) | (TBD) | Unity 2022 |
| WonkasWorldOfCandyMatch3 | (TBD) | (TBD) | Unity 2022 |

## 安装

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --break-system-packages UnityPy Pillow
```

或（推荐，不污染系统）：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --user UnityPy Pillow
```

## 相关脚本

- `skills/common/general-strategy-skill/scripts/workflow/sub-stage-extract-unity-textures.py` — UnityPy 提取脚本（已固化）
- `skills/common/general-strategy-skill/scripts/workflow/sub-stage-ocr.py` — Android res 图片识别
- `skills/common/general-strategy-skill/scripts/workflow/stage-06d-images-manifest.py` — AS 工程图片清单生成