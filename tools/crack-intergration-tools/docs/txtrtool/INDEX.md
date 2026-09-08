# txtrtool — 工具文档索引

> Metroid Prime TXTR 纹理格式解码/编码工具（C++/CMake）

## 基本信息

- **来源**: https://github.com/xchellx/txtrtool（克隆于 2026-08-09）
- **源码**: `tools/crack-intergration-tools/source-projects/txtrtool/`（READONLY）
- **可执行**: `tools/crack-intergration-tools/execable/txtrtool/txtrtool`
- **构建脚本**: `tools/crack-intergration-tools/execable/txtrtool/build-txtrtool.py`
- **版本**: 1.0.2（基于 commit 75ef86d）
- **语言**: C++ / C
- **构建系统**: CMake + Ninja
- **用途**: 解码/编码 Metroid Prime 1/2/3 的 TXTR（CTexture）纹理格式，支持所有 GX 图像格式

## ⚠️ 重要说明

> **此工具针对 Metroid Prime 的 TXTR 格式，不是 GameMaker 的 TXTR chunk。**
> 两者格式完全不同：
> - Metroid Prime TXTR：CTexture 格式（调色板头 + GX 编码图像数据 + mipmap）
> - GameMaker TXTR：`.droid` 归档中的纹理页数据
>
> 本工具对 GameMaker 逆向无直接用途，但可作为「二进制纹理格式编解码」的参考实现。

## 命令

```
txtrtool help <command>     # 子命令帮助
txtrtool version            # 版本信息
txtrtool decode <in> <out>  # TXTR → TGA（支持多 mipmap）
txtrtool encode <in> <out>  # TGA → TXTR
txtrtool print <in>         # 打印 TXTR 信息（格式/尺寸等）
```

## 构建方法

```bash
python3 tools/crack-intergration-tools/execable/txtrtool/build-txtrtool.py
```

> 构建脚本把源码复制到 /tmp 临时目录，在副本上打补丁（移除 `tga.h` 宏内 `_Pragma` + 禁用 `-pedantic-errors`），
> 编译后拷贝可执行到 `execable/txtrtool/`。不触碰 READONLY 源目录。

## 目录结构

```
tools/crack-intergration-tools/
├── source-projects/txtrtool/        ← 上游源码（READONLY）
│   ├── src/txtrtool.c
│   ├── include/txtrtool.h
│   ├── extern/gxtexture_base/       ← 纹理编解码核心
│   └── cmake/                       ← GCC/Clang 编译配置
└── execable/txtrtool/
    ├── txtrtool                     ← 编译后的可执行
    └── build-txtrtool.py            ← 构建脚本（副本打补丁）
```

## 已知坑位

1. **GCC 14 编译失败**: `tga.h` 宏内 `_Pragma` 被 GCC 14 拒绝（`expected ';' before '#pragma'`）→ 构建脚本按行移除 `_Pragma(...)` 行
2. **-pedantic-errors**: `cmake/txtrtool_gcc.cmake` 强制 `-pedantic-errors` → 构建脚本移除该 flag
3. **构建依赖**: 需要 `cmake` + `ninja` + `gcc/g++`（clang 可选）