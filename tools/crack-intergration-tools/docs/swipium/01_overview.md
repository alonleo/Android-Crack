# Swipium 工具概述

## 基本信息

| 项 | 值 |
|---|---|
| 名称 | Swipium |
| 版本 | 1.5.0 |
| 类型 | MCP server（Model Context Protocol） |
| 语言 | TypeScript/Node.js |
| 仓库 | https://github.com/GeroPalombo/swipium |
| 许可证 | MIT |
| 安装 | `npm install swipium` |

## 定位

Swipium 是一个 **MCP server**，专为 AI 代理设计的移动 QA 测试工具。它让 AI 代理能够在 Android 模拟器或 iOS 模拟器中运行实际的移动应用 QA 测试。

**核心理念**：让 AI 代理像 QA 工程师一样测试应用——启动应用、检查屏幕、操作 UI、运行冒烟测试、收集证据、生成报告。

## 核心特性

### 1. Agent-Native 设计

Swipium 通过 MCP 协议暴露 60 个工具，AI 代理可以直接调用：

```python
# AI 代理调用示例
qa_test_this(projectRoot="/path/to/app", mode="execute", goal="smoke")
qa_screenshot(session="...")
qa_act(session="...", action="tap", target={"text": "开始游戏"})
qa_report(session="...", format="markdown")
```

### 2. Simulator-First 策略

专注于 Android Emulator 和 iOS Simulator 的可靠性：

- **Android**：通过 `adb` 直接驱动，无需额外代理
- **iOS**：通过 `simctl` + WebDriverAgent 驱动

### 3. Evidence-First 方法

所有测试结果都有证据支持：

- 截图
- 日志
- UI 树快照
- 测试报告
- 覆盖率数据

### 4. App Map（应用知识图谱）

构建应用的持久化知识图谱：

- 屏幕列表
- 功能映射
- 测试用例
- 流程定义
- 覆盖率上下文

## 工具分类

### 启动与配置

| 工具 | 说明 |
|------|------|
| `qa_doctor` | 检查工具链就绪状态 |
| `qa_capabilities` | 查询设备能力 |
| `qa_start_session` | 启动测试会话 |
| `qa_detect_context` | 检测项目上下文 |

### 设备控制

| 工具 | 说明 |
|------|------|
| `qa_device_info` | 获取设备信息 |
| `qa_orientation` | 控制屏幕方向 |
| `qa_geolocation` | 设置地理位置 |
| `qa_network` | 控制网络状态 |
| `qa_app_control` | 应用生命周期控制 |

### UI 交互

| 工具 | 说明 |
|------|------|
| `qa_snapshot` | 获取 UI 树快照 |
| `qa_inspect` | 检查 UI 元素 |
| `qa_act` | 执行操作（点击/滑动/输入） |
| `qa_screenshot` | 截图 |
| `qa_assert_visual` | 视觉断言 |

### 测试执行

| 工具 | 说明 |
|------|------|
| `qa_smoke` | 冒烟测试 |
| `qa_explore` | 探索性测试 |
| `qa_flow_run` | 运行预定义流程 |
| `qa_test_feature` | 测试特定功能 |
| `qa_first_run` | 首次运行测试 |

### 报告与资产

| 工具 | 说明 |
|------|------|
| `qa_report` | 生成测试报告 |
| `qa_generate` | 生成测试资产 |
| `qa_app_map_build` | 构建应用图谱 |
| `qa_suite_generate` | 生成测试套件 |

## 与传统测试框架对比

| 特性 | Swipium | Appium | uiautomator2 |
|------|---------|--------|--------------|
| AI 代理集成 | ✅ MCP 原生 | ❌ 需封装 | ❌ 需封装 |
| 应用图谱 | ✅ 内置 | ❌ | ❌ |
| 测试报告 | ✅ 自动生成 | ❌ 需配置 | ❌ 需配置 |
| 视觉断言 | ✅ 内置 | ❌ 需插件 | ❌ |
| 流程管理 | ✅ 内置 | ❌ | ❌ |
| 安装复杂度 | 简单 npm | 复杂 | 简单 |

## 适用场景

1. **AI 代理测试**：让 AI 代理自动测试移动应用
2. **冒烟测试**：快速验证应用基本功能
3. **探索性测试**：自动探索应用功能
4. **回归测试**：验证修改后的应用功能
5. **QA 自动化**：生成可复用的测试资产

## 限制

1. **需要模拟器**：依赖 Android Emulator 或 iOS Simulator
2. **Node.js 依赖**：需要 Node.js 20+
3. **iOS 需要 WDA**：iOS 完整交互需要 WebDriverAgent
4. **视觉断言精度**：依赖截图质量
