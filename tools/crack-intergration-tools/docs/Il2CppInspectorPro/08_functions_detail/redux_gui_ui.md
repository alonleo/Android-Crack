# 08 · `Il2CppInspector.Redux.GUI.UI`（Tauri + Svelte 前端）

> 该子项目 **不是 C#**，是独立运行时（Tauri Rust + Svelte/TS）。
> 文件清单：
> - `src-tauri/Cargo.toml`, `Cargo.lock`, `build.rs`, `tauri.conf.json`, `capabilities/default.json`
> - `src-tauri/src/main.rs`, `lib.rs`
> - `src/app.html`, `app.css`
> - `src/lib/{tauri.ts, export.svelte.ts, settings.ts, utils.ts}`
> - `src/lib/signalr/{server-api.ts, client-api.ts, api.svelte.ts}`
> - `src/lib/components/{Footer,Header,loading}.svelte`
> - `src/lib/components/settings/{combobox,option,path-selector}.svelte`
> - `src/lib/components/ui/*`（shadcn-svelte 原语）
> - `src/routes/+layout.svelte`, `+layout.ts`, `+page.svelte`, `advanced/+page.svelte`, `export/+page.svelte`, `export/[formatId]/+page.svelte`, `options/+page.svelte`
> - `package.json`, `vite.config.js`, `svelte.config.js`, `tailwind.config.ts`, `tsconfig.json`, `postcss.config.js`

---

## `tauri::Builder` (`src-tauri/src/main.rs`)

- **签名**: `fn main()`
- **位置**: `Il2Inspector.Redux.GUI.UI/src-tauri/src/main.rs:~5`
- **可见性**: –
- **调用了**:
  - `il2cpp_inspector_redux_lib::run()`
- **简要说明**: Tauri exe 入口

## `il2cpp_inspector_redux_lib::run` (`src-tauri/src/lib.rs`)

- **签名**: `#[cfg_attr(mobile, tauri::mobile_entry_point)] pub fn run()`
- **位置**: `Il2Inspector.Redux.GUI.UI/src-tauri/src/lib.rs:~10`
- **可见性**: public
- **调用了**:
  - `tauri::Builder::default().setup(|app| { ... })`
  - `app.handle().plugin(...)`
  - `Ok(())`
- **简要说明**: 最小 Tauri 壳子

## `src-tauri/build.rs`

- **位置**: `build.rs`
- **可见性**: –
- **调用了**: `tauri_build::build()`
- **简要说明**: Tauri 构建脚本

---

## Svelte 路由

### `src/routes/+layout.svelte`

- **签名**: `<script lang="ts"> ... </script>`
- **可见性**: –
- **调用了**: `Header`、`Footer`、`loading.svelte`
- **简要说明**: 全局布局

### `src/routes/+page.svelte`

- **位置**: `src/routes/+page.svelte`
- **可见性**: –
- **调用了**: `onMount(() => api.getInspectorVersion())`
- **简要说明**: 主页（显示版本、加载入口）

### `src/routes/advanced/+page.svelte`

- **位置**: `src/routes/advanced/+page.svelte`
- **可见性**: –
- **调用了**: `api.getPotentialUnityVersions()` 等
- **简要说明**: 高级选项（Unity 版本、image base、名称映射）

### `src/routes/export/+page.svelte`

- **位置**: `src/routes/export/+page.svelte`
- **可见性**: –
- **调用了**: `api` + 设置 store
- **简要说明**: 导出选项首页

### `src/routes/export/[formatId]/+page.svelte`

- **位置**: `src/routes/export/[formatId]/+page.svelte`
- **可见性**: –
- **调用了**: 按 `formatId` 渲染对应输出表单
- **简要说明**: 单格式导出表单

### `src/routes/options/+page.svelte`

- **位置**: `src/routes/options/+page.svelte`
- **可见性**: –
- **简要说明**: 全局选项

---

## SignalR 客户端

### `client-api.ts`

- **签名**: 导出 `submitInputFiles`, `queueExport`, `startExport`, `getPotentialUnityVersions`, `getInspectorVersion`, `setSettings`, `onUiLaunched`
- **位置**: `src/lib/signalr/client-api.ts`
- **可见性**: public
- **调用**: Svelte 各路由
- **简要说明**: SignalR RPC 客户端封装

### `server-api.ts`

- **签名**: 服务端推送回调注册（`onLogMessage`, `onImportCompleted`, `onLoadingStart/Finish`）
- **位置**: `src/lib/signalr/server-api.ts`
- **可见性**: public

### `api.svelte.ts`

- **签名**: 导出 reactive state（`status`, `unityVersions`, `loading` 等）
- **位置**: `src/lib/signalr/api.svelte.ts`
- **可见性**: public
- **简要说明**: Svelte 5 runes 状态

---

## 状态/工具

### `export.svelte.ts`

- **签名**: reactive export options
- **位置**: `src/lib/export.svelte.ts`
- **可见性**: public

### `settings.ts`

- **签名**: settings store
- **位置**: `src/lib/settings.ts`
- **可见性**: public

### `utils.ts`

- **签名**: 杂项 helper
- **位置**: `src/lib/utils.ts`
- **可见性**: public

---

## UI 组件（shadcn-svelte 原语）

> 路径：`src/lib/components/ui/{button,card,checkbox,command,dialog,label,popover,select,separator,sonner,tooltip}/`

每个组件：
- `index.ts` 导出组件
- `*.svelte` 模板（基于 `bits-ui` + `tailwind-variants`）

> 简要说明：这些是 headless UI 原语，前端代码本身是声明性的；不在本仓库的「函数」语义范畴内，仅作目录参考。

---

## `tauri.conf.json`

- **位置**: `Il2Inspector.Redux.GUI.UI/src-tauri/tauri.conf.json`
- **简要说明**: Tauri 应用配置（identifier、window、安全策略）
- **副作用**: 决定 Capabilities

## `capabilities/default.json`

- **位置**: `Il2Inspector.Redux.GUI.UI/src-tauri/capabilities/default.json`
- **简要说明**: Tauri 权限（窗口/fs 等）