# 08 — Functions Detail: Frontend (Svelte 5 + TypeScript)

覆盖 `src/routes/+page.svelte`、`src/lib/*.ts`、`src/lib/components/*.svelte` 的关键导出。

---

## `src/routes/+page.svelte`

### 路由组件 (默认 export)
- **位置**：`src/routes/+page.svelte:1`（160 行）
- **可见性**：default export
- **状态**：`currentOs` (`$state`)、`draftConfig` (`$state<DumperConfig>`)
- **副作用**：`onMount` 内调 `@tauri-apps/plugin-os.type()` + 路径探测 + `setupDumpEvents()` + 应用主题 + 监听系统色彩
- **调用了**：`applyTheme`、`setupDumpEvents`、`handleSplashFinished`、`handleCrashRestart`、`confirmConfigDialog`、`cancelConfigDialog`

### `function confirmConfigDialog()`
- **位置**：`+page.svelte:34`
- **副作用**：把 `draftConfig` 写回 `config` store，关闭对话框

### `function cancelConfigDialog()`
- **位置**：`+page.svelte:39`

### `function handleSplashFinished()`
- **位置**：`+page.svelte:78`
- **副作用**：`currentScreen.set("idle")`

### `function handleCrashRestart()`
- **位置**：`+page.svelte:82`
- **副作用**：清空 `crashLog`、`resetAll()`

---

## `src/lib/types.ts`

### `interface DumperConfig { ... }`
- **位置**：`src/lib/types.ts:1`
- **可见性**：export
- **字段**：40+（camelCase，镜像 Rust `Config`）

### `interface BinaryInfo { format, unity_version }`
- **位置**：`src/lib/types.ts:45`

### `interface DumpCompleteEvent { success, output_path, error_message }`
- **位置**：`src/lib/types.ts:50`

### `interface InputRequestEvent { prompt_type }`
- **位置**：`src/lib/types.ts:55`

### `type AppState = "idle" | "dumping" | "result" | "error"`
- **位置**：`src/lib/types.ts:60`

### `const DEFAULT_CONFIG: DumperConfig`
- **位置**：`src/lib/types.ts:62`
- **可见性**：export

---

## `src/lib/stores.ts`

### `type ScreenState = "idle" | "settings" | "about" | "dumping" | "result" | "error" | "crash" | "splash"`
- **位置**：`src/lib/stores.ts:7`

### `interface PersistedPrefs { themeMode, language, config, outputDir }`
- **位置**：`src/lib/stores.ts:11`
- **可见性**：private

### `function loadPrefs() -> PersistedPrefs`
- **位置**：`src/lib/stores.ts:18`
- **副作用**：从 `localStorage` 读

### `function defaultPrefs() -> PersistedPrefs`
- **位置**：`src/lib/stores.ts:34`

### `function savePrefs(prefs: Partial<PersistedPrefs>)`
- **位置**：`src/lib/stores.ts:43`

### Stores

| Store | 行 | 类型 |
|------|----|------|
| `themeMode` | 52 | `Writable<ThemeMode>` |
| `language` | 53 | `Writable<AppLanguage>` |
| `config` | 54 | `Writable<DumperConfig>` |
| `configDialogOpen` | 55 | `Writable<boolean>` |
| `outputDir` | 56 | `Writable<string>` |
| `t` (derived) | 63 | `Readable<Translations>` |
| `defaultOutputDir` | 65 | `Writable<string>` |
| `currentScreen` | 66 | `Writable<ScreenState>` |
| `crashLog` | 67 | `Writable<string>` |
| `appState` | 68 | `Writable<AppState>` |
| `logs` | 69 | `Writable<string[]>` |
| `binaryPath` | 70 | `Writable<string>` |
| `metadataPath` | 71 | `Writable<string>` |
| `binaryInfo` | 72 | `Writable<BinaryInfo \| null>` |
| `outputPath` | 73 | `Writable<string>` |
| `errorMessage` | 74 | `Writable<string>` |
| `inputRequest` | 75 | `Writable<string \| null>` |
| `elapsedSeconds` | 76 | `Writable<number>` |

### `function resetAll()`
- **位置**：`src/lib/stores.ts:78`
- **可见性**：export
- **副作用**：清空所有 dump 相关 store

### `function resetForNewDump()`
- **位置**：`src/lib/stores.ts:93`
- **可见性**：export

### `function applyTheme(mode: ThemeMode)`
- **位置**：`src/lib/stores.ts:104`
- **可见性**：export
- **副作用**：设置 `<html data-theme>` 与 `colorScheme`

---

## `src/lib/dumpRunner.ts`

### `async function beginDump(): Promise<void>`
- **位置**：`src/lib/dumpRunner.ts:18`
- **可见性**：export
- **副作用**：检查 `isDumpInProgress`、`setupDumpEvents`、`setDumpInProgress(true)`、reset logs/timer、切到 `dumping` 屏；调用 `invoke("start_dump", {...})`
- **调用**：`IdleScreen` 的 Start 按钮

---

## `src/lib/dumpEvents.ts`

### `let unlisteners: UnlistenFn[] = []`
- **位置**：`src/lib/dumpEvents.ts:14`
- **可见性**：module-private

### `async function registerDumpEvents(): Promise<void>`
- **位置**：`src/lib/dumpEvents.ts:17`
- **可见性**：private
- **副作用**：注册 `dump-log` / `dump-complete` / `dump-input-request` / `dump-crash` 四个监听

### `function setupDumpEvents(): Promise<void>`
- **位置**：`src/lib/dumpEvents.ts:49`
- **可见性**：export
- **说明**：幂等 + 单例；多次调用只注册一次

### `function teardownDumpEvents(): void`
- **位置**：`src/lib/dumpEvents.ts:59`
- **可见性**：export

---

## `src/lib/dumpLogs.ts` (推断)

无 read 文件，但 exports `appendDumpLog(message: string)`。被 `dumpEvents.ts:22` 调用。

---

## `src/lib/dumpState.ts` (推断)

exports `setDumpInProgress(bool)` 与 `isDumpInProgress(): boolean`。

---

## `src/lib/utils.ts` (推断)

通用 helper（`formatBytes`、`formatDuration` 等）。完整内容未读取，但作为通用工具被广泛使用。

---

## `src/lib/i18n.ts` (370 行)

### `export type AppLanguage = "en" | "sq" | "ar" | "es" | "hi" | "id" | "jv"`
- 推断

### `export type ThemeMode = "system" | "light" | "dark"`
- 推断

### `function getTranslations(lang: AppLanguage) -> Translations`
- **可见性**：export

支持 7 语言：英语 / 阿尔巴尼亚语 / 阿拉伯语 / 西班牙语 / 印地语 / 印尼语 / 爪哇语。

---

## `src/lib/components/*.svelte` (13 个)

> 行号与具体函数签名以仓库当前状态为准。下面列出每个组件的"对外 props"与"关键导出事件"。

### `IdleScreen.svelte`
- **位置**：`src/lib/components/IdleScreen.svelte`
- **功能**：展示路径选择、设置按钮、开始按钮
- **调用了**：`beginDump` (dumpRunner)、`detect_binary` (invoke)
- **关键 props**：无

### `DumpingScreen.svelte`
- **功能**：进度日志显示 + 计时器
- **订阅**：`logs`、`elapsedSeconds`、`inputRequest`

### `ResultScreen.svelte`
- **功能**：成功总结 + 打开文件夹按钮
- **订阅**：`outputPath`、`binaryInfo`

### `ErrorScreen.svelte`
- **功能**：错误消息 + 重试
- **订阅**：`errorMessage`

### `SettingsScreen.svelte`
- **功能**：Config 编辑
- **调用了**：`config` store、`outputDir`

### `AboutScreen.svelte`
- **功能**：关于页

### `SplashScreen.svelte`
- **功能**：启动屏（Lottie 动画）
- **Props**：`onfinished: () => void`

### `CrashScreen.svelte`
- **功能**：崩溃报告
- **Props**：`crashLog: string`、`onrestart: () => void`

### `InputDialog.svelte`
- **功能**：响应 `dump-input-request`，调 `submit_input`
- **订阅**：`inputRequest`

### `ConfigDialog.svelte`
- **功能**：Config 弹窗（大量 ConfigSwitch + PathInput）
- **Props**：`config: DumperConfig`、`onconfirm`、`oncancel`

### `ConfigSwitch.svelte`
- **功能**：单个开关项
- **Props**：`label`、`checked`、`onchange`

### `PathInput.svelte`
- **功能**：路径选择输入框（用 @tauri-apps/plugin-dialog）
- **Props**：`value: string`、`onchange`、`placeholder`

### `AnimatedExpand.svelte`
- **功能**：Svelte 过渡动画

---

## Svelte 5 Runes

项目使用 Svelte 5 runes API：

- `$state<T>(...)` — 局部响应式状态（`+page.svelte:25,26`）
- `$derived(...)` — 派生值
- `$effect(() => { ... })` — 副作用（`+page.svelte:28-32, 72-73`）
- `bind:config`、`onclick={...}` — 模板语法（Svelte 5 风格）