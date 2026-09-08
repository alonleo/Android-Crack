# Android_Inline_Hook_ARM64 深度文档

> Source: [`/home/leo/文档/android-crack/tools/source-projects/Android_Inline_Hook_ARM64`](../../Android_Inline_Hook_ARM64/)
> Author: **GToad** (gtoad1994@aliyun.com)
> Date: 2018 (首发), ARM64 版完成于 2018/09/20
> License: 未在仓库明确标注（推测 MIT，参考姊妹仓库 Android_Inline_Hook）
> Language: C + ARM64 汇编
> Volume: 6 文件 ~1300 行

## 文档导航

| 文件 | 内容 |
|------|------|
| [01_overview.md](01_overview.md) | 项目定位、设计理念、与 Rprop 库的关系 |
| [02_directory_tree.md](02_directory_tree.md) | 完整目录树 + 各文件角色 |
| [03_architecture.md](03_architecture.md) | 整体架构 + 6 张 mermaid |
| [04_data_flow.md](04_data_flow.md) | `INLINE_HOOK_INFO` 数据结构生命周期 |
| [05_operation_chains.md](05_operation_chains.md) | 7 条主要操作链（每条配 mermaid） |
| [06_build_and_run.md](06_build_and_run.md) | 编译、链接、NDK 集成、API 用法 |
| [07_functions_index.md](07_functions_index.md) | 函数索引总表 |
| [08_functions_detail/](08_functions_detail/) | 按子模块拆分的函数详细说明 |
| [09_callstacks.md](09_callstacks.md) | 关键调用栈汇总 |
| [10_glossary.md](10_glossary.md) | 术语表 |

## 08 函数详细文档

| 文件 | 覆盖范围 |
|------|---------|
| [ihook.md](08_functions_detail/ihook.md) | `Ihook.h` + `Ihook.c`（库核心编排） |
| [fixPCOpcode.md](08_functions_detail/fixPCOpcode.md) | `fixPCOpcode.h` + `fixPCOpcode.c`（指令修复） |
| [ihookstub_asm.md](08_functions_detail/ihookstub_asm.md) | `ihookstub.s`（汇编 stub 模板） |
| [interface.md](08_functions_detail/interface.md) | `Interface/InlineHook.cpp`（用户接口） |

## 一句话总结

Android_Inline_Hook_ARM64 是一个**带汇编 stub + 完整寄存器上下文切换 + unhook 支持**的 ARM64 inline hook 库。它通过 ARM64 汇编 stub 保存全部 GPR + NZCV、调用户回调（`onCallBack(user_pt_regs *regs)`）、再跳回原函数；同时构造"修复后的原函数入口"（PC-relative 修复），最后在 hook 点写入 24 字节长跳转。

## 项目目录

```
Android_Inline_Hook_ARM64/
├── README.md
├── arm64hook.{png,pdf,vsdx,xlsx}    # ARM64 设计图
├── arm64hook4.png
├── stack.{png,pdf,vsdx,xlsx}         # 栈帧设计图
├── STACK{1,2}.{png,pdf}
├── jni/
│   ├── Android.mk                    # 顶层构建入口
│   ├── Application.mk                # APP_ABI := arm64-v8a
│   ├── InlineHook/                   # 库实现层
│   │   ├── Ihook.h                   # 数据结构 + 函数声明
│   │   ├── Ihook.c                   # Hook 编排（435 行）
│   │   ├── fixPCOpcode.h             # 修复函数声明
│   │   ├── fixPCOpcode.c             # 修复函数实现（594 行）
│   │   ├── ihookstub.s               # 汇编 stub 模板（82 行）
│   │   └── Android.mk
│   └── Interface/                    # 用户接口层
│       ├── InlineHook.cpp            # InlineHook / UnInlineHook
│       └── Android.mk
├── libs/arm64-v8a/                   # 编译产物 .so
└── obj/local/                        # NDK 中间产物
```