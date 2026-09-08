# 01 项目概览

## 项目定位

Rodroid-Il2CppDumper 是 Perfare/Il2CppDumper 的现代 Rust 重写版，配套 Svelte 5 + Tauri 2 GUI。覆盖：

1. **与原版对等的能力**：
   - 解析 ELF / PE / Mach-O / Fat Mach-O / NSO / WASM 六种可执行格式
   - 解析 `global-metadata.dat`（含 v16~v39 + v104/v106 CODM 变种）
   - 写出 `dump.cs` / `il2cpp.h` / `script.json` / `stringliteral.json` / `DummyDll/`
2. **新增能力**：
   - **Auto-XOR metadata 解密**：7 种常见 XOR 加密方案自动尝试（单字节、4 字节、8 字节、16/32/64/128/256 字节 rolling、position-dependent、masked-position、header-only）
   - **CODM 兼容**：自动检测 v104/v106 内部变种并使用 CODM 专属路径
   - **V5 disassembler**：内嵌 ARM32/ARM64 (`yaxpeax-arm`) + x86/x64 (`iced-x86`)，支持字符串字面量 / 方法名 / boxing / unboxing / static field / switch table 注解
   - **C++ header scaffolding**：topological sort + GCC/MSVC 布局 + name mangling
   - **Static-field metadata**：`static_metadata.json` 包含 thread-static + FieldRVA
   - **Generics dump**：`generics_dump.txt` 7 个子开关
   - **DiffableCs split**：`split_dump_per_type` 把 dump.cs 拆为 `DiffableCs/<TypeName>.cs`
   - **Tauri 事件流**：跨桌面 / 移动端异步交互
   - **Panic capture**：`catch_unwind` 包裹 + `dump-crash` 事件 + 时间戳格式化报告

## 版本信息

| 项 | 值 |
|---|---|
| 版本（推断） | v6.1.0（基于 `Cargo.toml`） |
| 适用 il2cpp | v16 ~ v39 + v104/v106 |
| 桌面平台 | Windows / macOS / Linux |
| 移动平台 | Android / iOS |

## 技术栈

| 维度 | 选择 |
|------|------|
| 后端语言 | Rust（edition 2021） |
| 后端框架 | Tauri 2 |
| 前端框架 | SvelteKit 2 + Svelte 5（runes API） |
| 前端组件库 | noph-ui（Material 3）+ Tailwind CSS 4 |
| 构建 | Cargo + pnpm + Vite 6 |
| LTO | release profile: `opt-level=3`, `lto=true`, `codegen-units=1`, `strip="symbols"`, `panic="abort"` |
| 主要 Rust crates | `tauri 2`, `serde`, `byteorder`, `lz4_flex`, `rayon`, `thiserror`, `yaxpeax-arm`, `yaxpeax-arch`, `iced-x86`, `include_dir`, `dotnetdll`（vendored submodule） |
| 主要 JS libs | `@tauri-apps/api ^2`, `@tauri-apps/plugin-{dialog,fs,opener,os}`, `lottie-web ^5.13`, `noph-ui ^0.33.4` |
| 前端 dev deps | `@sveltejs/adapter-static`, `@sveltejs/kit ^2`, `svelte 5`, `svelte-check`, `tailwindcss`, `typescript`, `vite 6`, `@tauri-apps/cli` |

## 入口

- 后端：`src-tauri/src/main.rs:6` → `rodroid_il2cppdumper_lib::run()` → `src-tauri/src/lib.rs:1297`
- 前端：`src/routes/+page.svelte` — 屏幕路由 + 各组件

## Tauri 命令

| 命令 | 行 | 用途 |
|------|----|------|
| `detect_binary(path)` | `lib.rs:1181` | 仅探测格式与 Unity 版本 |
| `start_dump(binaryPath, metadataPath, outputDir, configJson)` | `lib.rs:1192` | 启动后台 dump 线程 |
| `submit_input(response)` | `lib.rs:1284` | 前端把 input dialog 响应回传 |
| `get_default_config()` | `lib.rs:1292` | 返回默认 Config JSON |

## Tauri 事件

| 事件 | Payload | 触发时机 |
|------|---------|---------|
| `dump-log` | `{ message }` | 每条日志（init / search / dump / 等） |
| `dump-input-request` | `{ prompt_type }` | 需要用户输入（如 dump address / manual addresses） |
| `dump-complete` | `{ success, output_path, error_message }` | 正常结束 |
| `dump-crash` | `{ crash_log }` | panic 捕获 |