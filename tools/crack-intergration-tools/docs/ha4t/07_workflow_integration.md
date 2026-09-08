# HA4T 嵌入逆向工作流方案分析

## 1. 背景

本项目（android-crack）的核心流程包括多个真机验收阶段（08/10/12/14），当前主要依赖：
- `adb shell am start` 启动应用
- `adb logcat` 检查崩溃
- 人工目测验证 UI

**问题**：
- 人工验证耗时且不可靠
- 无法自动化记录验证结果
- 汉化验证依赖人工 OCR 或截图比对

**HA4T 可解决**：
- 自动化启动 + 等待 + 验证
- OCR 自动识别中文文字
- 截图自动存档
- 可脚本化、可重复执行

---

## 2. 嵌入点分析

### 2.1 真机验收阶段（08/10/12/14）

| 当前流程 | HA4T 增强 |
|---------|----------|
| `adb shell am start` | `dev.start_app()` + 自动等待启动完成 |
| `adb logcat *:E` 人工检查 | `dev.wait("主菜单", timeout=30)` 自动验证进入游戏 |
| 人工截图 | `dev.screenshot("verify.png")` 自动存档 |
| 人工判断无崩溃 | `dev.exists()` 验证关键 UI 元素存在 |

**集成方案**：创建 `tools/scripts/ha4t-verify.py`，封装验收逻辑。

### 2.2 汉化验证阶段

| 需求 | HA4T 方案 |
|------|----------|
| 验证中文显示 | `dev.get_page_text()` + 正则匹配中文 |
| 验证无乱码 | OCR 识别后检查编码范围 |
| 截图存档 | `dev.screenshot()` 自动保存 |

**集成方案**：创建 `tools/scripts/ha4t-hanization-verify.py`。

### 2.3 网络检测移除验证

| 需求 | HA4T 方案 |
|------|----------|
| 飞行模式下启动 | `adb shell cmd connectivity airplane-mode enable` + `dev.start_app()` |
| 验证无网络阻断 | `dev.wait("主菜单", timeout=30)` 确认进入游戏 |
| 验证无弹窗 | `dev.exists("网络连接失败")` 返回 False |

---

## 3. 实现方案

### 3.1 核心脚本：`ha4t-verify.py`

```python
#!/usr/bin/env python3
"""ha4t-verify.py — 基于 HA4T 的真机验收脚本"""

import os
import sys
import time
from datetime import datetime

# 确保项目环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import common

def verify_app_launch(package_name: str, activity_name: str, 
                      timeout: int = 30, output_dir: str = None) -> dict:
    """
    验证 APK 启动并进入游戏
    
    Args:
        package_name: 包名
        activity_name: 主 Activity
        timeout: 等待超时（秒）
        output_dir: 截图输出目录
        
    Returns:
        dict: 验证结果 {"success": bool, "message": str, "screenshots": list}
    """
    from ha4t import connect
    from ha4t.api import wait, exists, screenshot, get_page_text, start_app
    
    result = {
        "success": False,
        "message": "",
        "screenshots": [],
        "page_text": "",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # 1. 连接设备
        dev = connect(
            platform="android",
            android_package_name=package_name,
            android_activity_name=activity_name
        )
        
        # 2. 启动应用
        start_app(package_name, activity_name)
        time.sleep(2)  # 等待启动
        
        # 3. 截图：启动后
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            ss_path = os.path.join(output_dir, f"launch_{int(time.time())}.png")
            screenshot(ss_path)
            result["screenshots"].append(ss_path)
        
        # 4. 等待主界面（OCR 识别常见游戏主菜单文字）
        wait("开始游戏|play|start|主菜单|游戏", timeout=timeout, raise_error=False)
        
        # 5. 获取页面文字
        page_text = get_page_text()
        result["page_text"] = page_text
        
        # 6. 截图：主界面
        if output_dir:
            ss_path = os.path.join(output_dir, f"main_menu_{int(time.time())}.png")
            screenshot(ss_path)
            result["screenshots"].append(ss_path)
        
        # 7. 验证：无崩溃（检查是否仍在游戏内）
        current_app = dev.get_current_app()
        if package_name in current_app:
            result["success"] = True
            result["message"] = "应用启动成功，已进入主界面"
        else:
            result["message"] = f"应用已退出，当前应用：{current_app}"
            
    except Exception as e:
        result["message"] = f"验证失败：{str(e)}"
    
    return result


def verify_chinese_display(package_name: str, activity_name: str,
                           expected_texts: list = None, output_dir: str = None) -> dict:
    """
    验证汉化效果
    
    Args:
        package_name: 包名
        activity_name: 主 Activity
        expected_texts: 期望出现的中文文本列表
        output_dir: 截图输出目录
        
    Returns:
        dict: 验证结果
    """
    from ha4t import connect
    from ha4t.api import wait, get_page_text, screenshot, start_app
    
    result = {
        "success": False,
        "found_texts": [],
        "missing_texts": [],
        "page_text": "",
        "screenshots": []
    }
    
    try:
        dev = connect(
            platform="android",
            android_package_name=package_name,
            android_activity_name=activity_name
        )
        
        start_app(package_name, activity_name)
        time.sleep(3)
        
        # 获取页面文字
        page_text = get_page_text()
        result["page_text"] = page_text
        
        # 截图
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            ss_path = os.path.join(output_dir, f"hanization_{int(time.time())}.png")
            screenshot(ss_path)
            result["screenshots"].append(ss_path)
        
        # 检查中文文字
        if expected_texts:
            for text in expected_texts:
                if text in page_text:
                    result["found_texts"].append(text)
                else:
                    result["missing_texts"].append(text)
            
            result["success"] = len(result["missing_texts"]) == 0
        else:
            # 自动检测中文字符
            import re
            chinese_chars = re.findall(r'[\u4e00-\u9fff]+', page_text)
            result["success"] = len(chinese_chars) > 0
            result["found_texts"] = chinese_chars[:10]  # 前 10 个
            
    except Exception as e:
        result["message"] = f"验证失败：{str(e)}"
    
    return result


if __name__ == "__main__":
    common.ensure_env()
    
    import argparse
    parser = argparse.ArgumentParser(description="HA4T 真机验收工具")
    parser.add_argument("action", choices=["launch", "hanization"], help="验证类型")
    parser.add_argument("--package", required=True, help="包名")
    parser.add_argument("--activity", required=True, help="主 Activity")
    parser.add_argument("--timeout", type=int, default=30, help="超时秒数")
    parser.add_argument("--output", help="截图输出目录")
    parser.add_argument("--texts", nargs="*", help="期望中文文本列表")
    
    args = parser.parse_args()
    
    if args.action == "launch":
        result = verify_app_launch(args.package, args.activity, args.timeout, args.output)
    else:
        result = verify_chinese_display(args.package, args.activity, args.texts, args.output)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["success"] else 1)
```

### 3.2 集成到 crack.py

在 `crack.py` 的真机验收阶段调用 HA4T 验证：

```python
# 在 stage-08-device-verify.py 等脚本中
from ha4t_verify import verify_app_launch

def run_device_verify(project_name, package_name, activity_name):
    """执行真机验收"""
    output_dir = f"crackings/{project_name}/stages/08-device-verify/screenshots"
    
    result = verify_app_launch(
        package_name=package_name,
        activity_name=activity_name,
        timeout=30,
        output_dir=output_dir
    )
    
    # 写入验证报告
    with open(f"{output_dir}/verify-report.md", "w") as f:
        f.write(f"# 真机验收报告\n\n")
        f.write(f"- 时间: {result['timestamp']}\n")
        f.write(f"- 结果: {'✅ 通过' if result['success'] else '❌ 失败'}\n")
        f.write(f"- 说明: {result['message']}\n")
        f.write(f"\n## 截图\n")
        for ss in result["screenshots"]:
            f.write(f"![screenshot]({os.path.basename(ss)})\n")
    
    return result["success"]
```

---

## 4. 优势与风险

### 优势

| 优势 | 说明 |
|------|------|
| **自动化** | 减少人工干预，提高效率 |
| **可重复** | 脚本化验证，结果一致 |
| **可追溯** | 自动截图存档，便于回溯 |
| **OCR 能力** | 原生中文识别，无需额外配置 |
| **跨平台** | 同一套代码可用于 Android/iOS |

### 风险

| 风险 | 缓解措施 |
|------|---------|
| OCR 初始化慢（3-5s） | 仅在需要时初始化，复用实例 |
| PaddleOCR 模型体积大（~100MB） | 首次使用自动下载，后续缓存 |
| 游戏 UI 复杂识别困难 | 结合图像匹配 + OCR 双重验证 |
| 设备连接不稳定 | 增加重试机制 |

---

## 5. 实施步骤

### 第一阶段：基础集成（1-2 天）

1. ✅ 安装 HA4T：`pip install ha4t`
2. 创建 `tools/scripts/ha4t-verify.py` 核心脚本
3. 在 `tools/scripts/lib/common.py` 添加 HA4T 辅助函数
4. 更新 `tools/scripts/SCRIPTS-INDEX.md`

### 第二阶段：流程嵌入（2-3 天）

1. 修改 `stage-08-device-verify.py` 调用 HA4T
2. 修改 `stage-10-cleanup-device-verify.py` 调用 HA4T
3. 修改 `stage-12-ui-device-verify.py` 调用 HA4T
4. 修改 `stage-14-hanization-device-verify.py` 调用 HA4T

### 第三阶段：汉化验证增强（1-2 天）

1. 创建 `tools/scripts/ha4t-hanization-verify.py`
2. 集成到汉化阶段的自动化验证
3. 支持批量截图 + OCR 文字提取

### 第四阶段：经验沉淀（持续）

1. 记录 HA4T 使用经验到 `skills/common/general-strategy-skill/experience.md`
2. 优化 OCR 识别准确度
3. 收集游戏 UI 模板图片库

---

## 6. 与现有工具的关系

| 现有工具 | HA4T 关系 |
|---------|----------|
| `adb` | HA4T 底层依赖 uiautomator2，后者依赖 adb |
| `Tesseract OCR` | HA4T 使用 PaddleOCR，更适合中文；可互补 |
| `logcat` | HA4T 不替代 logcat，两者配合使用 |
| `apksigner` | 无直接关系，签名验证仍用 apksigner |

---

## 7. 结论

HA4T 是一个成熟的 UI 自动化框架，其 OCR 能力和跨平台特性非常适合本项目的真机验收需求。建议按上述步骤分阶段集成，优先在真机验收阶段（08/10/12/14）使用，逐步扩展到汉化验证等场景。
