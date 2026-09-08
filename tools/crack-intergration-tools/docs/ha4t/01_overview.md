# HA4T 工具概述

## 基本信息

| 项 | 值 |
|---|---|
| 名称 | HA4T (Hybrid App For Testing Tool) |
| 版本 | 0.1.6 |
| 作者 | caishilong |
| 仓库 | https://github.com/exuils/HA4T |
| 许可证 | MIT |
| 安装 | `pip install ha4t` |

## 定位

HA4T 是一个跨平台的 UI 自动化框架，专为混合型 App 设计，支持：

- **Android** — 基于 uiautomator2
- **iOS** — 基于 facebook-wda
- **HarmonyOS NEXT** — 基于 hmdriver2
- **Web** — 基于 CDP 协议

## 核心特性

### 1. 多种定位方式

```python
from ha4t import connect
from ha4t.aircv.cv import Template

# 连接设备
dev = connect(platform="android", device_serial="emulator-5554",
              android_package_name="com.example.app",
              android_activity_name="com.example.app.MainActivity")

# 方式1: OCR 文字识别（适合混合 App、游戏）
dev.click("开始游戏")
dev.wait("加载完成", timeout=30)

# 方式2: 图像匹配（适合自定义 UI、游戏按钮）
dev.click(image="start_button.png")
dev.click(Template("start_button.png", threshold=0.8))

# 方式3: 原生控件（适合原生 App，速度快）
dev.click(text="开始游戏")
dev.click(resourceId="com.example.app:id/start_btn")
```

### 2. 页面文字获取

```python
# 获取当前页面所有文字（OCR）
page_text = dev.get_page_text()
print(page_text)  # "开始游戏 设置 退出 ..."
```

### 3. 等待与断言

```python
# 等待文字出现
dev.wait("主菜单", timeout=30)

# 等待文字消失（反向等待）
dev.wait("加载中", reverse=True, timeout=60)

# 判断元素是否存在
if dev.exists("设置"):
    dev.click("设置")
```

### 4. 滑动操作

```python
dev.swipe_up()     # 上滑
dev.swipe_down()   # 下滑
dev.swipe_left()   # 左滑
dev.swipe_right()  # 右滑

# 自定义滑动（坐标比例）
dev.swipe((0.5, 0.8), (0.5, 0.3), duration=0.5)
```

### 5. 截图

```python
# 截图并保存
img = dev.screenshot("screenshot.png")

# 截图不保存
img = dev.screenshot()
```

### 6. 应用管理

```python
dev.start_app()                    # 启动应用
dev.restart_app()                  # 重启应用
dev.clear_app("com.example.app")   # 清除数据
current = dev.get_current_app()    # 获取当前应用
```

## 与竞品对比

| 特性 | HA4T | Airtest | uiautomator2 |
|------|------|---------|--------------|
| OCR 支持 | ✅ PaddleOCR | ✅ | ❌ |
| 图像匹配 | ✅ | ✅ | ❌ |
| 原生控件 | ✅ | ✅ | ✅ |
| 跨平台 | ✅ Android/iOS/HarmonyOS/Web | ✅ Android/iOS | ❌ Android |
| WebView | ✅ CDP | ❌ | ❌ |
| 安装复杂度 | 简单 pip | 需要 Poco | 简单 pip |

## 限制

1. **OCR 初始化慢**：首次使用需加载 PaddleOCR 模型（约 3-5 秒）
2. **图像匹配依赖截图质量**：分辨率、缩放可能影响匹配准确度
3. **部分 API 文档不完善**：需查看源码了解详细用法
