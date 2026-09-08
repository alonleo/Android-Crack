# 自动化汉化测试方案

## 1. 背景

传统的汉化流程需要人工识别游戏中的非中文内容，效率低且容易遗漏。本方案通过自动化手段实现：

1. **自动收集**：自动识别游戏中的所有非中文文本
2. **位置记录**：记录每个文本的位置信息
3. **汉化映射**：生成可翻译的映射表
4. **自动验证**：汉化后自动验证效果

## 2. 技术原理

### 2.1 双重文本收集机制

```
┌─────────────────────────────────────────────────────────┐
│                    游戏界面                              │
├─────────────────────────────────────────────────────────┤
│  原生 UI 部分                    游戏渲染部分            │
│  (按钮、菜单、对话框)            (Unity/Cocos/il2cpp)    │
│         │                              │                │
│         ▼                              ▼                │
│  ┌─────────────┐              ┌─────────────┐          │
│  │  无障碍服务  │              │    OCR      │          │
│  │ (uiautomator2)│            │ (PaddleOCR) │          │
│  └─────────────┘              └─────────────┘          │
│         │                              │                │
│         └──────────┬───────────────────┘                │
│                    ▼                                    │
│            ┌─────────────┐                              │
│            │  合并去重    │                              │
│            └─────────────┘                              │
│                    │                                    │
│                    ▼                                    │
│            ┌─────────────┐                              │
│            │ 过滤非中文  │                              │
│            └─────────────┘                              │
│                    │                                    │
│                    ▼                                    │
│            ┌─────────────┐                              │
│            │ 汉化映射表  │                              │
│            └─────────────┘                              │
└─────────────────────────────────────────────────────────┘
```

### 2.2 两种文本来源对比

| 来源 | 工具 | 适用场景 | 优点 | 缺点 |
|------|------|---------|------|------|
| **无障碍服务** | uiautomator2 | 原生 UI（按钮、菜单、对话框） | 精确、快速、无需 OCR | 无法获取游戏渲染文本 |
| **OCR** | PaddleOCR (HA4T) | 游戏渲染文本（Unity/Cocos） | 识别游戏内文字 | 速度较慢、可能有误识别 |

### 2.3 游戏引擎与文本获取方式

| 游戏引擎 | 原生 UI 文本 | 游戏渲染文本 | 推荐方案 |
|---------|-------------|-------------|---------|
| **原生 Android** | ✅ 无障碍服务 | ❌ 无 | 无障碍服务 |
| **Unity (il2cpp)** | ✅ 无障碍服务 | ✅ OCR | 双重收集 |
| **Cocos2d-x** | ✅ 无障碍服务 | ✅ OCR | 双重收集 |
| **Cocos Creator** | ✅ 无障碍服务 | ✅ OCR | 双重收集 |
| **Unreal** | ✅ 无障碍服务 | ✅ OCR | 双重收集 |

## 3. 实现方案

### 3.1 核心脚本

| 脚本 | 功能 | 用法 |
|------|------|------|
| `collect-non-chinese.py` | 收集非中文内容 | `./collect-non-chinese.py collect --package ...` |
| `auto-hanization-test.py` | 完整测试流程 | `./auto-hanization-test.py full --package ...` |

### 3.2 使用流程

#### 步骤 1：收集非中文内容

```bash
# 完整测试流程（推荐）
./tools/scripts/auto-hanization-test.py full \
  --package com.example.game \
  --activity .MainActivity \
  --screens 10 \
  --output crackings/ExampleGame/hanization

# 或仅收集
./tools/scripts/collect-non-chinese.py collect \
  --package com.example.game \
  --activity .MainActivity \
  --output hanization_map.json \
  --report report.md
```

#### 步骤 2：人工翻译

编辑 `hanization_map.json`，为每个 `translation` 字段填写中文翻译：

```json
{
  "translations": [
    {
      "original": "Start Game",
      "translation": "开始游戏",
      ...
    },
    {
      "original": "Settings",
      "translation": "设置",
      ...
    }
  ]
}
```

#### 步骤 3：汉化替换

根据映射表进行汉化替换（需要根据游戏引擎选择不同方式）：

- **原生 UI**：修改 `strings.xml` 或 smali
- **游戏渲染**：修改资源文件或代码

#### 步骤 4：验证汉化效果

```bash
./tools/scripts/auto-hanization-test.py verify-only \
  --package com.example.game \
  --activity .MainActivity \
  --mapping crackings/ExampleGame/hanization/hanization_map.json
```

### 3.3 输出文件

```
crackings/<Name>/hanization/
├── hanization_map.json          # 汉化映射表（需人工翻译）
├── hanization_report.md         # 收集报告
└── screenshots/                 # 截图存档
    ├── screenshot_1.png
    ├── screenshot_2.png
    └── ...
```

## 4. 与现有流程集成

### 4.1 集成到 WORKFLOW.md

| 阶段 | 当前流程 | 自动化增强 |
|------|---------|----------|
| 13-hanization | 人工识别非中文 | `auto-hanization-test.py collect-only` |
| 14-hanization-verify | 人工验证 | `auto-hanization-test.py verify-only` |

### 4.2 集成到 crack.py

```python
# 在 stage-13-hanization.py 中
from auto_hanization_test import AutoHanizationTester

def run_hanization_collect(project_name, package_name, activity_name):
    """收集非中文内容"""
    tester = AutoHanizationTester(
        package_name=package_name,
        activity_name=activity_name,
        output_dir=f"crackings/{project_name}/hanization"
    )
    
    result = tester.run_full_test(max_screens=10)
    return result["success"]
```

## 5. 优势与风险

### 优势

| 优势 | 说明 |
|------|------|
| **自动化** | 减少人工识别工作量 |
| **全面性** | 双重机制确保不遗漏 |
| **可追溯** | 截图和位置信息便于回溯 |
| **可验证** | 自动验证汉化效果 |
| **可复用** | 映射表可跨版本复用 |

### 风险

| 风险 | 缓解措施 |
|------|---------|
| OCR 误识别 | 人工审核映射表 |
| 游戏内动态文本 | 多次收集、不同场景 |
| 特殊字符处理 | 过滤规则优化 |
| 性能影响 | 限制探索屏幕数 |

## 6. 示例

### 6.1 收集示例

```bash
$ ./tools/scripts/auto-hanization-test.py full \
    --package com.example.game \
    --activity .MainActivity \
    --screens 5

============================================================
🎮 自动化汉化测试 - 完整流程
============================================================

📱 步骤 1: 探索应用并收集文本
🔍 开始探索应用 (最多 5 个屏幕)

📱 屏幕 1/5
  ✅ 无障碍服务: 15 个文本
  ✅ OCR: 23 个文本
  📊 新增 38 个文本 (总计 38)

📱 屏幕 2/5
  ✅ 无障碍服务: 12 个文本
  ✅ OCR: 20 个文本
  📊 新增 15 个文本 (总计 53)

...

✅ 探索完成，共收集 120 个唯一文本

🔤 步骤 2: 过滤非中文文本
🔤 过滤后: 45 个非中文文本

💾 步骤 3: 生成汉化映射表
💾 汉化映射表已保存: crackings/ExampleGame/hanization/hanization_map.json

📄 步骤 4: 生成测试报告
📄 报告已生成: crackings/ExampleGame/hanization/hanization_report.md

============================================================
✅ 测试完成!
📊 总计: 120 个文本, 45 个非中文
💾 映射表: crackings/ExampleGame/hanization/hanization_map.json
📄 报告: crackings/ExampleGame/hanization/hanization_report.md
============================================================
```

### 6.2 映射表示例

```json
{
  "generated_at": "2026-08-07T21:30:00",
  "package_name": "com.example.game",
  "total_items": 45,
  "translations": [
    {
      "original": "Start Game",
      "source": "ocr",
      "bounds": [100, 200, 300, 250],
      "confidence": 0.95,
      "screen_index": 0,
      "translation": "开始游戏",
      "context": "主菜单"
    },
    {
      "original": "Settings",
      "source": "accessibility",
      "bounds": [100, 300, 300, 350],
      "confidence": 1.0,
      "screen_index": 0,
      "translation": "设置",
      "context": "主菜单"
    }
  ]
}
```

## 7. 总结

本方案通过无障碍服务 + OCR 双重机制，实现游戏非中文内容的自动收集和验证，大幅提高汉化效率。结合 HA4T 和 uiautomator2，可以覆盖原生 UI 和游戏渲染两种场景，确保汉化的全面性和准确性。
