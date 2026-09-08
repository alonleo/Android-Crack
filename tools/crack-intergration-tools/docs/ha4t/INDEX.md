# HA4T 工具文档索引

> **HA4T (Hybrid App For Testing Tool)** — 跨平台 UI 自动化框架
> 版本：0.1.6 | 作者：caishilong | 许可证：MIT

---

## 快速导航

| 文档 | 说明 |
|------|------|
| [01_overview.md](./01_overview.md) | 工具概述、特性、安装 |
| [07_workflow_integration.md](./07_workflow_integration.md) | 嵌入逆向工作流方案分析 |

---

## 核心能力

| 能力 | 说明 | API |
|------|------|-----|
| **OCR 文字识别** | 基于 PaddleOCR，识别屏幕文字并定位 | `click("文字")` / `wait("文字")` / `get_page_text()` |
| **图像匹配** | 基于 aircv，模板匹配定位 UI 元素 | `click(image="template.png")` |
| **原生控件** | 基于 uiautomator2/wda，快速定位原生控件 | `click(text="按钮")` |
| **滑动操作** | 上下左右滑动，支持坐标和比例 | `swipe_up()` / `swipe((0.2,0.5),(0.8,0.5))` |
| **截图** | 截取当前屏幕 | `screenshot("file.png")` |
| **应用管理** | 启动/重启/清除应用 | `start_app()` / `restart_app()` / `clear_app()` |
| **文件操作** | 设备文件上传/下载/删除 | `pull_file()` / `upload_files()` / `delete_file()` |
| **WebView** | CDP 协议操作 WebView 内容 | `CDP` 类 |

---

## 依赖关系

```
ha4t
├── paddleocr (OCR 引擎)
├── paddlepaddle (深度学习框架)
├── uiautomator2 (Android 自动化)
├── facebook-wda (iOS 自动化)
├── hmdriver2 (HarmonyOS 自动化)
├── opencv-python (图像处理)
└── pillow (图像处理)
```

---

## 与本项目关联

| 项目需求 | HA4T 对应能力 |
|---------|--------------|
| 真机验收（08/10/12/14） | 自动化启动 APK、验证无崩溃 |
| 汉化验证 | OCR 识别中文文字、截图存档 |
| UI 功能验证 | 图像匹配、控件定位、自动化操作 |
| 网络检测移除验证 | 飞行模式下自动启动测试 |
