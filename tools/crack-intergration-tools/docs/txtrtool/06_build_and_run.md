# txtrtool — 构建与运行

## 环境要求

- cmake ≥ 3.28
- ninja
- gcc/g++（clang 可选）
- git（克隆子模块）

## 构建

### 方式一：项目内构建脚本（推荐）

```bash
source tools/environments/env.sh
python3 tools/crack-intergration-tools/execable/txtrtool/build-txtrtool.py
```

脚本流程：
1. 复制源码到 /tmp 临时目录
2. 按行移除 `extern/gxtexture_base/tga/include/tga.h` 中宏体内的 `_Pragma(...)` 行（GCC 14 修复）
3. 移除 `cmake/txtrtool_gcc.cmake` 中的 `-pedantic-errors` flag
4. cmake configure（Release + Ninja）+ build
5. 拷贝 `txtrtool` 可执行到 `execable/txtrtool/`

### 方式二：手动构建（需打补丁）

```bash
cd /tmp && git clone --recursive https://github.com/xchellx/txtrtool.git
cd txtrtool
# 补丁 1：移除 tga.h 宏内 _Pragma（否则 GCC14 报错）
sed -i '/^\s*_Pragma(/d' extern/gxtexture_base/tga/include/tga.h
# 补丁 2：禁用 -pedantic-errors
sed -i 's/SHELL:"-pedantic-errors"//' cmake/txtrtool_gcc.cmake cmake/txtrtool_clang.cmake
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -G Ninja
cmake --build build
./build/txtrtool version
```

## 验证

```bash
tools/crack-intergration-tools/execable/txtrtool/txtrtool version
# 输出: txtrtool <hash>-CLEAN based on v1.0.2
```

## 使用示例

```bash
# 打印 TXTR 信息
txtrtool print example.txtr

# 解码 TXTR → TGA
txtrtool decode example.txtr output.tga

# 编码 TGA → TXTR
txtrtool encode input.tga output.txtr
```

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `expected ';' before '#pragma'` | GCC14 拒绝宏内 `_Pragma` | 构建脚本自动移除 `_Pragma` 行 |
| `-pedantic-errors` 编译失败 | GCC14 常量表达式限制 | 构建脚本自动移除该 flag |
| cmake 找不到 GetGitRevisionDescription | 子模块未初始化 | `git submodule update --init --recursive` |