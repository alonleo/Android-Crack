# 08 — Functions Detail: 核心 (main / lib / config / error / il2cpp::base / il2cpp::metadata / il2cpp::enums / il2cpp::field_layout)

---

## `main.rs`

### `fn main()`
- **签名**：`fn main()`
- **位置**：`src-tauri/src/main.rs:4`
- **可见性**：private（被 runtime 调用）
- **副作用**：调用 `rodroid_il2cppdumper_lib::run()`
- **说明**：仅 6 行的 trampoline；release 模式禁用 console window。

---

## `lib.rs`

### 常量
| 名称 | 行 | 值 |
|------|----|----|
| `MAGIC_METADATA` | 34 | `0xFAB11BAF` |
| `MAGIC_ELF` | 35 | `0x464C457F` |
| `MAGIC_PE` | 36 | `0x5A4D` |
| `MAGIC_MACHO32` | 37 | `0xFEEDFACE` |
| `MAGIC_MACHO64` | 38 | `0xFEEDFACF` |
| `MAGIC_MACHOFAT` | 39 | `0xBEBAFECA` |
| `MAGIC_NSO` | 40 | `0x304F534E` |
| `MAGIC_WASM` | 41 | `0x6D736100` |

### 事件结构体

```rust
struct LogEvent { message: String }                  // :44
struct InputRequestEvent { prompt_type: String }    // :49
struct DumpCompleteEvent { success, output_path, error_message }  // :54
struct CrashEvent { crash_log: String }             // :61
struct BinaryInfo { format, unity_version }         // :66
struct AppState { input_sender: Mutex<Option<mpsc::Sender<String>>>, dump_running: Mutex<bool> }  // :71
```

### `fn emit_log(app: &AppHandle, message: &str)`
- **位置**：`src-tauri/src/lib.rs:76`
- **可见性**：private
- **副作用**：emit `dump-log` 事件
- **调用**：被 `run_dump` 与 6 个 `init_<format>` 大量调用

### `fn request_input(app: &AppHandle, state: &AppState, prompt_type: &str) -> String`
- **位置**：`src-tauri/src/lib.rs:85`
- **可见性**：private
- **副作用**：设置 `state.input_sender`；emit `dump-input-request`；阻塞 `rx.recv()`
- **调用**：`prompt_dump_address`、`prompt_manual_addresses`

### `fn parse_hex(s: &str) -> u64`
- **位置**：`src-tauri/src/lib.rs:102`
- **调用**：被 prompt_* 调用

### `fn prompt_dump_address(app: &AppHandle, state: &AppState) -> Option<u64>`
- **位置**：`src-tauri/src/lib.rs:107`
- **调用**：被 6 个 `init_<format>` 调用

### `fn prompt_manual_addresses(app: &AppHandle, state: &AppState) -> Option<(u64, u64)>`
- **位置**：`src-tauri/src/lib.rs:113`

### `fn read_magic_u32(data: &[u8]) -> u32`
- **位置**：`src-tauri/src/lib.rs:126`

### `fn read_magic_u16(data: &[u8]) -> u16`
- **位置**：`src-tauri/src/lib.rs:133`

### `fn is_valid_metadata_version(data: &[u8]) -> bool`
- **位置**：`src-tauri/src/lib.rs:140`
- **说明**：检查 version 字段在 `0..200` 范围

### `fn try_decrypt_metadata(data: &mut Vec<u8>) -> Option<String>`
- **位置**：`src-tauri/src/lib.rs:148`
- **可见性**：private
- **返回值**：Some(scheme description) 成功；None 失败
- **副作用**：原位解密 `data`
- **调用**：被 `run_dump:1043` 调用

### `fn detect_unity_version(data: &[u8]) -> Option<String>`
- **位置**：`src-tauri/src/lib.rs:279`
- **可见性**：private
- **说明**：扫描 2xxx.x / 6xxx.x 模式，要求 `dot_count == 2` 且包含后缀（f/b/a/p/rc）
- **调用**：被 `run_dump:1033`

### `fn detect_format(data: &[u8]) -> &'static str`
- **位置**：`src-tauri/src/lib.rs:324`
- **可见性**：private
- **返回值**："ELF" / "PE" / "Mach-O" / "Fat Mach-O" / "NSO" / "WASM" / "Unknown"
- **调用**：被 `run_dump:1064`、`detect_binary:1183` 调用

### `fn resolve_codm(config: &Config, metadata: &Metadata) -> bool`
- **位置**：`src-tauri/src/lib.rs:338`
- **可见性**：private
- **说明**：`config.codm || metadata.variant == MetadataVariant::Codm`
- **调用**：被 6 个 `init_<format>` 调用

### `fn init_elf(data, metadata, config, app, state) -> Result<Il2Cpp>`
- **位置**：`src-tauri/src/lib.rs:342`
- **可见性**：private
- **副作用**：emit log + dump-input-request（可选）
- **调用**：被 `run_dump:1068` 调用
- **调用了**：`Elf::new` / `Elf::new_with_codm_diag`、`set_properties`、`check_dump`、`load`、`get_section_helper`、`find_code_registration`、`find_metadata_registration(_codm)`、`auto_plus_init`、`symbol_search`、`search_arm32`、`list_exported_symbols`、`Il2Cpp::from_elf`

### `fn init_pe(data, metadata, config, app, state) -> Result<Il2Cpp>`
- **位置**：`src-tauri/src/lib.rs:476`
- **调用了**：`Pe::new`、`set_properties`、`symbol_search`、`get_section_helper`、`find_code_registration`、`find_metadata_registration`、`list_exported_symbols`、`Il2Cpp::new`、`Il2Cpp::init`、`Il2Cpp::data_sections = pe.data_search_sections()`

### `fn init_macho_fat(data, metadata, config, app, state) -> Result<Il2Cpp>`
- **位置**：`src-tauri/src/lib.rs:611`
- **调用了**：`parse_fat`、`extract_fat_slice`、`init_macho`

### `fn init_macho(data, metadata, config, app, state) -> Result<Il2Cpp>`
- **位置**：`src-tauri/src/lib.rs:644`
- **调用了**：`MachO::new` / `MachO::new_with_codm_fixups`、`symbol_search`、`search_mod_init_func`、`get_section_helper`、`find_code_registration`、`find_metadata_registration(_codm)`、`Il2Cpp::new`、`Il2Cpp::init`、`list_exported_symbols`

### `fn init_nso(data, metadata, config, app, state) -> Result<Il2Cpp>`
- **位置**：`src-tauri/src/lib.rs:828`

### `fn init_wasm(data, metadata, config, app, state) -> Result<Il2Cpp>`
- **位置**：`src-tauri/src/lib.rs:928`

### `fn run_dump(app, state, binary_path, metadata_path, output_dir, config) -> Result<String, String>`
- **位置**：`src-tauri/src/lib.rs:1009`
- **可见性**：private
- **副作用**：创建 `Dump<N>/` 子目录；读 binary + metadata；emit 多个 dump-log；调用 5 个输出生成器；最终 emit `dump-complete`
- **抛出**：String（错误消息）

### `#[tauri::command] fn detect_binary(path: String) -> Result<BinaryInfo, String>`
- **位置**：`src-tauri/src/lib.rs:1181`
- **可见性**：Tauri command
- **副作用**：读文件；emit 不发生
- **调用**：前端 `dumpRunner.ts` / IdleScreen

### `#[tauri::command] fn start_dump(...) -> Result<(), String>`
- **位置**：`src-tauri/src/lib.rs:1192`
- **可见性**：Tauri command
- **副作用**：`std::thread::spawn(run_dump)` + `catch_unwind` + DumpGuard
- **调用**：前端 `dumpRunner.beginDump`

### `impl Drop for DumpGuard`
- **位置**：`src-tauri/src/lib.rs:1211`
- **副作用**：把 `state.dump_running` 置回 false

### `#[tauri::command] fn submit_input(state, response)`
- **位置**：`src-tauri/src/lib.rs:1284`
- **副作用**：把 response 喂给 `state.input_sender`

### `#[tauri::command] fn get_default_config() -> String`
- **位置**：`src-tauri/src/lib.rs:1292`
- **返回值**：`serde_json::to_string_pretty(&Config::default())`

### `pub fn run()`
- **位置**：`src-tauri/src/lib.rs:1297`
- **可见性**：pub
- **副作用**：构造 `AppState`；注册 fs/os/opener/dialog plugin；注册 4 个 invoke handler；运行 tauri context

---

## `config.rs`

### `pub struct Config` (40+ 字段，camelCase serde)
- **位置**：`src-tauri/src/config.rs:5`

### `impl Default for Config::default()` (private fn)
- **位置**：`src-tauri/src/config.rs:51`

### `pub fn load_from_file(path: &str) -> Result<Self, Box<dyn Error>>`
- **位置**：`src-tauri/src/config.rs:100`

### `pub fn save_to_file(&self, path: &str) -> Result<(), Box<dyn Error>>`
- **位置**：`src-tauri/src/config.rs:106`

---

## `error.rs`

```rust
#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Invalid metadata file: {0}")]
    InvalidMetadata(String),

    #[error("Unsupported metadata version: {0}")]
    UnsupportedVersion(i32),

    #[error("Address 0x{0:x} not in any segment")]
    AddressNotMapped(u64),

    #[error("Invalid binary format: {0}")]
    InvalidFormat(String),

    #[error("Read out of bounds: offset 0x{offset:x}, size {size}")]
    OutOfBounds { offset: u64, size: usize },

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Cyclic value-type dependency: {0}")]
    CyclicDependency(String),

    #[error("{0}")]
    Other(String),
}

pub type Result<T> = std::result::Result<T, Error>;
```

无方法。

---

## `il2cpp/base.rs`

### `pub struct VaSegment { vaddr, memsz, offset }`
- **位置**：`src-tauri/src/il2cpp/base.rs:9`

### `pub struct Il2Cpp { ... 30+ 字段 }`
- **位置**：`src-tauri/src/il2cpp/base.rs:15`

### `pub fn new(stream, version, is_32bit) -> Self`
- **位置**：`src-tauri/src/il2cpp/base.rs:62`
- **可见性**：pub
- **调用**：被 `init_pe:580`、`init_macho:763`、`init_nso:897`、`init_wasm:997` 调用

### `pub fn from_elf(elf: &Elf) -> Self`
- **位置**：`src-tauri/src/il2cpp/base.rs:104`
- **可见性**：pub
- **副作用**：从 Elf 实例克隆所有表 + 设置 arch（`Architecture::from_elf_machine`）
- **调用**：被 `init_elf:456` 调用

### `pub fn init(&mut self, code_registration, metadata_registration, map_vatr: &dyn Fn(u64) -> Result<u64>) -> Result<()>`
- **位置**：`src-tauri/src/il2cpp/base.rs:162`
- **可见性**：pub
- **副作用**：填充所有 Il2Cpp 表（types / method_pointers / field_offsets / code_gen_modules / rgctxs_dictionary / generic_insts / method_specs）
- **CODM 容错**：若 `codm && is_dumped`，跳过坏指针的 type（记录 `skipped` 数）
- **调用**：被 6 个 `init_<format>` 调用

### `fn build_method_spec_lookup(&mut self)` (private)
- **位置**：`src-tauri/src/il2cpp/base.rs:433`

### `fn load_code_gen_modules(&mut self, map_vatr)` (private)
- **位置**：`src-tauri/src/il2cpp/base.rs:457`

### `pub fn get_method_pointer(&self, image_name, method_def) -> u64`
- **位置**：`src-tauri/src/il2cpp/base.rs:492`
- **可见性**：pub
- **调用**：被 `StructGenerator`、`Decompiler` 等大量调用

### `pub fn get_raw_field_offset(...)` (pub, 但被 `get_field_offset_from_index` 调用)
- **位置**：`src-tauri/src/il2cpp/base.rs:511`

### `pub fn get_field_offset_from_index(type_index, field_index_in_type, field_index, is_value_type, is_static) -> i32`
- **位置**：`src-tauri/src/il2cpp/base.rs:547`
- **可见性**：pub
- **调用**：被 `Decompiler`、`StructGenerator` 调用

### `pub fn get_rva(&self, pointer: u64) -> u64`
- **位置**：`src-tauri/src/il2cpp/base.rs:570`

### `pub fn get_il2cpp_type(&self, pointer) -> Option<&Il2CppType>`
- **位置**：`src-tauri/src/il2cpp/base.rs:578`

### `pub fn map_vatr(&self, addr) -> Result<u64>`
- **位置**：`src-tauri/src/il2cpp/base.rs:582`
- **说明**：扫 `va_segments` 线性查找

### `pub fn map_rtva(&self, offset) -> u64`
- **位置**：`src-tauri/src/il2cpp/base.rs:591`

### `pub fn read_generic_class(&mut self, addr) -> Result<Il2CppGenericClass>`
- **位置**：`src-tauri/src/il2cpp/base.rs:600`

### `pub fn read_generic_inst(&mut self, addr) -> Result<Il2CppGenericInst>`
- **位置**：`src-tauri/src/il2cpp/base.rs:606`

### `pub fn read_ptr_array(&mut self, addr, count) -> Result<Vec<u64>>`
- **位置**：`src-tauri/src/il2cpp/base.rs:612`

### `pub fn detect_architecture(&self) -> Architecture`
- **位置**：`src-tauri/src/il2cpp/base.rs:622`
- **说明**：根据 `is_pe + is_32bit` 决定 `X86 / X64 / ARM / ARM64`

### `pub fn build_sorted_method_addresses(&self) -> Vec<u64>`
- **位置**：`src-tauri/src/il2cpp/base.rs:629`
- **说明**：合并所有 method-pointer 数组并排序去重，给 disassembler 用

### `pub fn get_method_body_size(&self, rva, sorted_addrs) -> usize`
- **位置**：`src-tauri/src/il2cpp/base.rs:661`
- **说明**：基于下一个 method 估算当前 method 大小

### `pub fn read_bytes_at_rva(&self, rva, size) -> Option<Vec<u8>>`
- **位置**：`src-tauri/src/il2cpp/base.rs:679`

---

## `il2cpp/metadata.rs`

### `pub enum MetadataVariant { Standard, Codm }`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:9`

### `fn detect_codm_variant(stream, file_size) -> bool` (private)
- **位置**：`src-tauri/src/il2cpp/metadata.rs:14`
- **说明**：根据 header 字段大小判断是否 CODM

### `pub struct Metadata { ... 30+ 字段 }`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:66`

### `pub fn new(data: Vec<u8>) -> Result<Self>`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:113`
- **可见性**：pub
- **说明**：默认 Standard 变种；自动检测 unity_version

### `pub fn new_with_unity_version(data, unity_version_str) -> Result<Self>`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:117`

### `pub fn new_with_options(data, unity_version_str, codm) -> Result<Self>`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:121`
- **可见性**：pub
- **调用**：被 `run_dump:1056` 调用

### `fn detect_subversion(&mut self) -> Result<()>` (private)
- **位置**：`src-tauri/src/il2cpp/metadata.rs:237`

### `fn load_metadata(&mut self) -> Result<()>` (private)
- **位置**：`src-tauri/src/il2cpp/metadata.rs:262`
- **说明**：Standard 路径加载所有 Defs

### `fn load_metadata_codm(&mut self) -> Result<()>` (private)
- **位置**：`src-tauri/src/il2cpp/metadata.rs:418`
- **说明**：CODM 路径加载

### `fn read_metadata_array_codm<T: CodmReadable>(...)` (private)
- **位置**：`src-tauri/src/il2cpp/metadata.rs:524`

### `fn read_metadata_array<T: MetadataReadable>(...)` (private)
- **位置**：`src-tauri/src/il2cpp/metadata.rs:541`

### `fn read_metadata_array_with_offsets<T>(...)` (private)
- **位置**：`src-tauri/src/il2cpp/metadata.rs:578`

### `fn process_metadata_usage(...)` (private)
- **位置**：`src-tauri/src/il2cpp/metadata.rs:624`

### `fn calculate_metadata_usages_count(&self) -> usize` (private)
- **位置**：`src-tauri/src/il2cpp/metadata.rs:656`

### `fn build_attribute_lookup(&mut self)` (private)
- **位置**：`src-tauri/src/il2cpp/metadata.rs:672`

### `pub fn get_string_from_index(&mut self, index: i32) -> Result<String>`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:693`

### `pub fn get_string_literal_from_index(&mut self, index: usize) -> Result<String>`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:703`

### `pub fn get_field_default_value(&self, field_index: i32) -> Option<&Il2CppFieldDefaultValue>`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:725`

### `pub fn get_parameter_default_value(&self, param_index: i32) -> Option<&Il2CppParameterDefaultValue>`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:729`

### `pub fn get_default_value_offset(&self, index: i32) -> u64`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:733`

### `pub fn get_custom_attribute_index(image_def, custom_attribute_index, token) -> i32`
- **位置**：`src-tauri/src/il2cpp/metadata.rs:737`
- **可见性**：pub

### trait `MetadataReadable`（line 757）
```rust
trait MetadataReadable: Sized {
    fn read(stream: &mut BinaryStream, version: f64) -> Result<Self>;
    fn byte_size(version: f64) -> usize;
    fn read_codm(_stream: &mut BinaryStream) -> Result<Self> { ... }
    fn codm_byte_size() -> usize { ... }
}
```

### trait `CodmReadable`（line 827）
```rust
trait CodmReadable: Sized {
    fn read_codm_dispatch(stream: &mut BinaryStream) -> Result<Self>;
    fn codm_size_dispatch() -> usize;
}
```

---

## `il2cpp/enums.rs`

### `pub enum Il2CppTypeEnum { ... 30+ 变体 }`
- **位置**：`src-tauri/src/il2cpp/enums.rs:3`

### `pub fn from_u8(value: u8) -> Option<Self>`
- **位置**：`src-tauri/src/il2cpp/enums.rs:44`

### `pub fn type_name(&self) -> Option<&'static str>`
- **位置**：`src-tauri/src/il2cpp/enums.rs:87`

### `pub fn is_il2cpp_primitive(&self) -> bool`
- **位置**：`src-tauri/src/il2cpp/enums.rs:111`

### `pub fn is_numeric(&self) -> bool`
- **位置**：`src-tauri/src/il2cpp/enums.rs:123`

### `pub fn is_reference_type(&self) -> bool`
- **位置**：`src-tauri/src/il2cpp/enums.rs:134`

### `pub enum Il2CppRGCTXDataType { Invalid, Type, Class, Method, Array, Constrained }`
- **位置**：`src-tauri/src/il2cpp/enums.rs:144`

### `pub fn from_u32(value: u32) -> Option<Self>`
- **位置**：`src-tauri/src/il2cpp/enums.rs:154`

### `pub enum Il2CppMetadataUsage { Invalid, TypeInfo, Il2CppType, MethodDef, FieldInfo, StringLiteral, MethodRef }`
- **位置**：`src-tauri/src/il2cpp/enums.rs:169`

### `pub fn from_u32(value: u32) -> Option<Self>`
- **位置**：`src-tauri/src/il2cpp/enums.rs:180`

### `pub fn encoded_index_shift(version: f64) -> u32`
- **位置**：`src-tauri/src/il2cpp/enums.rs:193`
- **说明**：v>=27 shift = 1，mask = 0x1FFFFFFE；否则 shift = 0，mask = 0x1FFFFFFF

### `pub fn encoded_index_mask(version: f64) -> u32`
- **位置**：`src-tauri/src/il2cpp/enums.rs:197`

---

## `il2cpp/field_layout.rs`

### `pub enum StaticFieldKind { None, RuntimeData, FieldRva, ThreadStatic }`
- **位置**：`src-tauri/src/il2cpp/field_layout.rs:12`

### `pub struct DecodedFieldOffset { offset: i32, size: i32 }`
- **位置**：`src-tauri/src/il2cpp/field_layout.rs:21`

### `pub struct FieldLayoutInfo { ... }`
- **位置**：`src-tauri/src/il2cpp/field_layout.rs:28`

### `pub fn is_static_storage(&self) -> bool`
- **位置**：`src-tauri/src/il2cpp/field_layout.rs:45`

### `pub fn decode_field_offset(raw: i32) -> DecodedFieldOffset`
- **位置**：`src-tauri/src/il2cpp/field_layout.rs:55`
- **说明**：按 valueType + size 决定 offset 修正

### `pub fn estimate_field_rva_size(metadata, type_def, field_def) -> Option<usize>`
- **位置**：`src-tauri/src/il2cpp/field_layout.rs:72`

### `pub fn read_metadata_bytes(metadata, offset, size) -> Option<Vec<u8>>`
- **位置**：`src-tauri/src/il2cpp/field_layout.rs:101`

### `pub fn read_binary_bytes(il2cpp, va, size) -> Option<Vec<u8>>`
- **位置**：`src-tauri/src/il2cpp/field_layout.rs:120`

### `pub fn analyze_field_layout(il2cpp, metadata, type_def, field_def, config) -> FieldLayoutInfo`
- **位置**：`src-tauri/src/il2cpp/field_layout.rs:127`
- **可见性**：pub
- **调用**：被 `StaticFieldCatalog::collect` 调用

---

## `il2cpp/structures.rs`

POD 与 version-aware 结构体（2222 行）。关键 entry：

```rust
pub struct UnityVersion { ... }                              // :8
pub enum UnityBuildType { Release, Public, Beta, Alpha, Patch, Exp }  // :17
impl UnityVersion { new / parse / gte / gte_simple / gte_major_minor / gte_major / resolve_sub_version }  // :24-135

pub enum Il2CppPackingSizeEnum { ... }                       // :165
impl Il2CppPackingSizeEnum { from_u32 }                       // :178

// POD
pub struct Il2CppGlobalMetadataHeader { ... }
pub struct Il2CppImageDefinition { ... }
pub struct Il2CppAssemblyDefinition { ... }
pub struct Il2CppTypeDefinition { ... }  // bitfield, IsValueType, IsEnum
pub struct Il2CppMethodDefinition { ... }
pub struct Il2CppParameterDefinition { ... }
pub struct Il2CppFieldDefinition { ... }
pub struct Il2CppFieldDefaultValue { ... }
pub struct Il2CppParameterDefaultValue { ... }
pub struct Il2CppPropertyDefinition { ... }
pub struct Il2CppEventDefinition { ... }
pub struct Il2CppGenericContainer { ... }
pub struct Il2CppGenericParameter { ... }
pub struct Il2CppFieldRef { ... }
pub struct Il2CppStringLiteral { ... }
pub struct Il2CppCustomAttributeTypeRange { ... }
pub struct Il2CppCustomAttributeDataRange { ... }
pub struct Il2CppMetadataUsageList / Pair { ... }
pub struct Il2CppType { ... datapoint, bits, attrs, type, ... }  // 含 Init
pub struct Il2CppGenericClass { ... }
pub struct Il2CppGenericContext { ... }
pub struct Il2CppGenericInst { ... }
pub struct Il2CppArrayType { ... }
pub struct Il2CppGenericMethodFunctionsDefinitions { ... }
pub struct Il2CppGenericMethodIndices { ... }
pub struct Il2CppMethodSpec { ... }
pub struct Il2CppCodeGenModule { ... }
pub struct Il2CppRange { ... }
pub struct Il2CppTokenRangePair { ... }
pub struct Il2CppCodeRegistration { ... }
pub struct Il2CppMetadataRegistration { ... }
pub struct Il2CppRGCTXDefinition { ... }
pub struct Il2CppRGCTXDefinitionData { ... }
pub struct Il2CppTypeDefinitionSizes { ... }
```

所有 struct 都有 `MetadataReadable + CodmReadable` 实现（由 macro 展开）。