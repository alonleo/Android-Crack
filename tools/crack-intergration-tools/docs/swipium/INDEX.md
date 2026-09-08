# Swipium 工具文档索引

> **Swipium** — MCP server for simulator-based mobile QA agents
> 版本：1.5.0 | 许可证：MIT | 仓库：https://github.com/GeroPalombo/swipium

---

## 快速导航

| 文档 | 说明 |
|------|------|
| [01_overview.md](./01_overview.md) | 工具概述、特性、安装 |
| [07_workflow_integration.md](./07_workflow_integration.md) | 嵌入逆向工作流方案分析 |

---

## 核心能力（60 个 MCP 工具）

| 分组 | 工具 | 说明 |
|------|------|------|
| **启动** | `qa_test_this` | 一键测试入口 |
| | `qa_doctor` | 检查工具链就绪状态 |
| | `qa_capabilities` | 查询设备能力 |
| **设备** | `qa_device_info` | 设备信息 |
| | `qa_orientation` | 屏幕方向 |
| | `qa_network` | 网络状态 |
| **驱动** | `qa_snapshot` | 获取 UI 树快照 |
| | `qa_screenshot` | 截图 |
| | `qa_act` | 执行操作（点击/滑动/输入） |
| | `qa_inspect` | 检查 UI 元素 |
| **运行** | `qa_smoke` | 冒烟测试 |
| | `qa_explore` | 探索性测试 |
| | `qa_report` | 生成报告 |
| **流程** | `qa_flow_run` | 运行预定义流程 |
| | `qa_flow_check` | 检查流程状态 |
| **生成** | `qa_generate` | 生成测试资产 |
| **应用图谱** | `qa_app_map_build` | 构建应用知识图谱 |
| | `qa_app_map_read` | 读取应用图谱 |

---

## 与本项目关联

| 项目需求 | Swipium 对应能力 |
|---------|-----------------|
| 真机验收（08/10/12/14） | `qa_smoke` 自动化冒烟测试 |
| 汉化验证 | `qa_screenshot` + `qa_assert_visual` 视觉断言 |
| UI 功能验证 | `qa_explore` 探索性测试 + `qa_act` 操作 |
| 测试报告 | `qa_report` 自动生成带证据的报告 |
| 应用知识图谱 | `qa_app_map_build` 构建应用结构图 |

---

## 安装

```bash
# 本地安装（推荐）
mkdir -p ~/tools/swipium && cd ~/tools/swipium
npm init -y && npm install swipium

# 验证安装
npx swipium verify
```

---

## 与 HA4T 的关系

| 维度 | HA4T | Swipium |
|------|------|---------|
| 类型 | Python UI 自动化框架 | MCP server（Node.js） |
| 定位 | 底层 UI 操作 | AI 代理 QA 测试 |
| OCR | ✅ PaddleOCR | ❌ 视觉断言 |
| 图像匹配 | ✅ aircv | ✅ 视觉断言 |
| 测试报告 | ❌ 需自建 | ✅ 自动生成 |
| 应用图谱 | ❌ | ✅ 知识图谱 |
| MCP 集成 | ❌ | ✅ 原生 |

**建议**：HA4T 用于底层 UI 操作和 OCR，Swipium 用于高层 QA 流程和报告生成。
