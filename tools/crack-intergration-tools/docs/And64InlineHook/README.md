# And64InlineHook 深度文档

> Source: [`/home/leo/文档/android-crack/tools/source-projects/And64InlineHook`](../../And64InlineHook/)
> Author: **Rprop** (r_prop@outlook.com)
> Date: 2018/04/18
> License: MIT (`LICENSE`)
> Language: C++ (单文件实现)
> Volume: `And64InlineHook.cpp` (596 行) + `And64InlineHook.hpp` (41 行) + `LICENSE` + `README.md`

## 文档导航

| 文件 | 内容 |
|------|------|
| [01_overview.md](01_overview.md) | 项目定位、设计理念、与 GToad 库的关系 |
| [02_module_layout.md](02_module_layout.md) | 按代码段分组的模块布局（单文件项目） |
| [03_architecture.md](03_architecture.md) | 整体架构 + 6 张 mermaid |
| [04_data_flow.md](04_data_flow.md) | `context` 数据结构生命周期 + trampoline 数据流 |
| [05_operation_chains.md](05_operation_chains.md) | 7 条主要操作链（每条配 mermaid） |
| [06_build_and_run.md](06_build_and_run.md) | 编译、链接、NDK 集成、API 用法 |
| [07_functions_index.md](07_functions_index.md) | 函数索引总表 |
| [08_functions_detail.md](08_functions_detail.md) | 函数详细说明（含全部修复路由） |
| [09_callstacks.md](09_callstacks.md) | 关键调用栈汇总 |
| [10_glossary.md](10_glossary.md) | 术语表（ARMv8、PC-relative、trampoline 等） |

## 一句话总结

And64InlineHook 是一个**单文件、轻量、零依赖**的 ARM64 inline hook 库。它通过把原函数开头的 4–5 条指令搬运到一张**静态预分配的 RWX trampoline 池**，然后在 hook 点写入 4 字节（B）或 20 字节（LDR+BR+addr）的跳转实现劫持。整个库只有两个公开 API、修复函数表驱动、无 unhook、无并发保护、设计目标是**单线程一次性 hook**。

## 项目目录

```
And64InlineHook/
├── And64InlineHook.cpp    # 596 行全部实现
├── And64InlineHook.hpp    # 41 行公开 API 声明
├── LICENSE                # MIT
└── README.md              # 简要说明 + 参考链接
```

无 `Android.mk` / `CMakeLists.txt` —— 编译时直接 `.cpp` 纳入构建系统即可。