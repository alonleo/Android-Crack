# 08 — Functions Detail: Output

---

## `output/decompiler.rs`

### `pub struct Il2CppDecompiler`
- **位置**：`src-tauri/src/output/decompiler.rs:15`

### `pub fn decompile<L: FnMut(&str)>(executor, metadata, il2cpp, config, output_dir, log: L) -> Result<()>`
- **位置**：`src-tauri/src/output/decompiler.rs:18`
- **可见性**：pub
- **参数**：`&mut Il2CppExecutor`、`&mut Metadata`、`&mut Il2Cpp`、`&Config`、`&str`、`FnMut(&str)` 日志回调
- **副作用**：写 `dump.cs` 与 `DiffableCs/<Type>.cs`
- **调用**：被 `run_dump:1097` 调用
- **调用了**：`executor.get_type_name / get_type_def_name / get_modifiers / get_method_spec_name`、`metadata.get_string_from_index / get_string_literal_from_index`、`il2cpp.get_field_offset_from_index / get_method_pointer / get_rva`、`CustomAttributeDataReader.get_string_custom_attribute_data`

---

## `output/struct_generator.rs`

### `pub struct StructGenerator`
- **位置**：`src-tauri/src/output/struct_generator.rs:58`

### `pub fn write_all<L: FnMut(&str)>(executor, metadata, il2cpp, config, output_dir, catalog: Option<&StaticFieldCatalog>, log: L) -> Result<()>`
- **位置**：`src-tauri/src/output/struct_generator.rs:72`
- **可见性**：pub
- **副作用**：写 `script.json` / `stringliteral.json` / `il2cpp.h`
- **调用**：被 `run_dump:1133` 调用

### `pub fn resolve_generic_type_var_pub(...)` (pub, 给 cpp_scaffolding 用)
- **位置**：`src-tauri/src/output/struct_generator.rs:408`

### `pub fn build_struct_name_dic_pub(...)`
- **位置**：`src-tauri/src/output/struct_generator.rs:576`

### `pub fn build_type_def_image_names_pub(metadata: &mut Metadata) -> HashMap<usize, String>`
- **位置**：`src-tauri/src/output/struct_generator.rs:597`

---

## `output/dummy_assembly_generator.rs`

### `pub fn generate_dummy_dlls<L: FnMut(&str)>(executor, metadata, il2cpp, config, output_dir, log: L) -> Result<()>`
- **位置**：`src-tauri/src/output/dummy_assembly_generator.rs:142`
- **可见性**：pub
- **副作用**：用 vendored `dotnetdll` crate 生成 stub DLL
- **调用**：被 `run_dump:1144` 调用

---

## `output/generics.rs`

### `pub fn dump_generics<L: FnMut(&str)>(path: &str, metadata, il2cpp, executor, config, log: L) -> Result<()>`
- **位置**：`src-tauri/src/output/generics.rs:22`
- **可见性**：pub
- **副作用**：写 `generics_dump.txt`（7 段）
- **调用**：被 `run_dump:1158` 调用

---

## `output/cpp_scaffolding.rs`

### `pub struct CppScaffolding`
- **位置**：`src-tauri/src/output/cpp_scaffolding.rs:13`

### `pub fn build<L: FnMut(&str)>(metadata, il2cpp, executor, config, output_dir, log: L) -> Result<()>`
- **位置**：`src-tauri/src/output/cpp_scaffolding.rs:24`
- **可见性**：pub
- **副作用**：写 C++ headers + project files
- **调用**：被 `write_all` 或 `run_dump` 调用

### `pub fn write_project(output_dir: &Path) -> Result<()>`
- **位置**：`src-tauri/src/output/cpp_scaffolding.rs:440`
- **可见性**：pub

---

## `output/cpp_ast.rs`

### `pub struct CppField { ... }`
- **位置**：`src-tauri/src/output/cpp_ast.rs:33`

### `pub struct CppVTableEntry { ... }`
- **位置**：`src-tauri/src/output/cpp_ast.rs:41`

### `pub struct CppRGCTXEntry { ... }`
- **位置**：`src-tauri/src/output/cpp_ast.rs:46`

### `pub struct CppTypeDecl { ... }`
- **位置**：`src-tauri/src/output/cpp_ast.rs:54`

### `pub struct CppHeaderEmitter { ... }`
- **位置**：`src-tauri/src/output/cpp_ast.rs:64`

### `pub fn new(compiler_layout, is_32bit, is_pe) -> Self`
- **位置**：`src-tauri/src/output/cpp_ast.rs:73`
- **可见性**：pub

### `pub fn emit_all_with_groups(...)`
- **位置**：`src-tauri/src/output/cpp_ast.rs:156`
- **可见性**：pub

### `pub fn emit_all(&mut self, types: &[CppTypeDecl]) -> Result<String>`
- **位置**：`src-tauri/src/output/cpp_ast.rs:270`
- **可见性**：pub

---

## `output/cpp_type_model.rs`

### `pub enum CppTypeGroup { UnityApi, UnityTypes, UnityStructs, UnityEnums, GameClasses, ForwardDeclarations, InternalHelpers }`
- **位置**：`src-tauri/src/output/cpp_type_model.rs:4`

### `pub fn tag(self) -> &'static str`
- **位置**：`src-tauri/src/output/cpp_type_model.rs:13`

### `pub fn section_header(self) -> &'static str`
- **位置**：`src-tauri/src/output/cpp_type_model.rs:23`

### `pub enum ComplexValueKind { ... }`
- **位置**：`src-tauri/src/output/cpp_type_model.rs:35`

### `pub enum CppType { ... }`
- **位置**：`src-tauri/src/output/cpp_type_model.rs:43`

### 方法
| 方法 | 行 |
|------|----|
| `pub fn name(&self) -> String` | 83 |
| `pub fn size_bytes(&self) -> u32` | 96 |
| `pub fn alignment_bytes(&self) -> u32` | 109 |
| `pub fn is_enum(&self) -> bool` | 122 |
| `pub fn is_complex_struct(&self) -> bool` | 126 |
| `pub fn is_forward_declarable(&self) -> bool` | 133 |
| `pub fn as_pointer(&self, word_size_bytes: u32) -> CppType` | 143 |
| `pub fn as_array(&self, length: u32) -> CppType` | 150 |
| `pub fn as_alias(&self, name: &str) -> CppType` | 157 |
| `pub fn to_field_string(&self, field_name: &str) -> String` | 164 |

### `pub struct CppTypeGroupRegistry { ... }`
- **位置**：`src-tauri/src/output/cpp_type_model.rs:203`

### 方法
| 方法 | 行 |
|------|----|
| `pub fn new() -> Self` | 209 |
| `pub fn assign(&mut self, type_name, group)` | 213 |
| `pub fn group_of(&self, type_name) -> Option<CppTypeGroup>` | 227 |
| `pub fn members(&self, group) -> &[String]` | 231 |
| `pub fn promote(&mut self, type_name, new_group)` | 238 |
| `pub fn all_names(&self) -> impl Iterator<Item = &String>` | 253 |

---

## `output/cpp_type_dependency_graph.rs`

依赖图 + 拓扑排序。无公开 `pub fn`，主要数据结构 + 私有方法。详细函数列表见 `07_functions_index.md`。

---

## `output/name_mangler.rs`

### `pub struct MangledNameBuilder { buf: String }`
- **位置**：`src-tauri/src/output/name_mangler.rs:8`

### 方法
| 方法 | 行 | 说明 |
|------|----|------|
| `fn new()` | 15 | |
| `fn begin_name` / `begin_generics` / `write_end` | 23-25 | |
| `fn write_identifier` | 27 | |
| `fn skip_sub_index` | 33 | |
| `fn try_write_substitution` | 37 | |
| `fn register_substitution` | 61 | |
| `fn finish(self) -> String` | 66 | |
| `fn base_clean` (static) | 68 | |
| `fn type_def_key` (static) | 72 | |
| `fn write_type_name_from_td` | 79 | |
| `fn write_complex_type_from_td` | 133 | |
| `fn write_nested_system_type` | 156 | |
| `fn write_generic_inst` | 177 | |
| `fn write_type` | 197 | |
| `pub fn mangle_method` | 322 | |
| `pub fn mangle_method_info` | 335 | |
| `pub fn mangle_method_spec` | 348 | |
| `pub fn mangle_type_info` | 363 | |
| `pub fn mangle_type_ref` | 373 | |
| `fn mangle_data` | 383 | |
| `fn method_has_generic_params` (static) | 407 | |
| `fn mangle_method_inner` | 411 | |

---

## `output/header_manager.rs`

### `pub struct UnityResource { ... }`
- **位置**：`src-tauri/src/output/header_manager.rs:9`

### `pub fn get_text(&self) -> Option<String>`
- **位置**：`src-tauri/src/output/header_manager.rs:17`

### `pub struct UnityHeaders { ... }`
- **位置**：`src-tauri/src/output/header_manager.rs:26`

### `pub fn new(type_header, api_header) -> Self`
- **位置**：`src-tauri/src/output/header_manager.rs:34`

### `pub fn get_type_header_text(&self, is_32bit: bool) -> String`
- **位置**：`src-tauri/src/output/header_manager.rs:47`

### `pub fn get_api_header_text(&self) -> String`
- **位置**：`src-tauri/src/output/header_manager.rs:61`

### `pub fn get_all_type_headers() -> Vec<UnityResource>`
- **位置**：`src-tauri/src/output/header_manager.rs:65`

### `pub fn get_all_api_headers() -> Vec<UnityResource>`
- **位置**：`src-tauri/src/output/header_manager.rs:83`

### `pub fn guess_headers_for_binary(...) -> UnityHeaders`
- **位置**：`src-tauri/src/output/header_manager.rs:116`

---

## `output/header_constants.rs`

所有 `pub fn` 返回 `&'static str`：

| 函数 | 行 | 含义 |
|------|----|------|
| `generic_header()` | 1 | 共用前缀（Il2CppMethodPointer / VirtualInvokeData / Il2CppType / Il2CppObject / Il2CppRGCTXData） |
| `header_v29()` | 42 | v29/29.1/31 头 |
| `header_v27()` | 152 | v27/27.1/27.2 头 |
| `header_v242()` | 260 | v24.2~24.5 头 |
| `header_v241()` | 368 | v24.1 头 |
| `header_v240()` | 475 | v23/24.0 头 |
| `header_v22()` | 581 | v22 头 |
| `get_version_header(version: f64) -> Option<&'static str>` | 686 | dispatcher |

---

## `output/unity_version.rs`

### `pub enum BuildType { Release, Public, Beta, Alpha, Patch, Exp }`
- **位置**：`src-tauri/src/output/unity_version.rs:5`

### `pub fn from_str_safe(s: &str) -> Self`
- **位置**：`src-tauri/src/output/unity_version.rs:15`

### `pub struct UnityVersion { major, minor, patch, build_type, build_number }`
- **位置**：`src-tauri/src/output/unity_version.rs:29`

### `impl Default` / `PartialOrd` / `Ord` / `FromStr`
- **位置**：37 / 49 / 55 / 77

### 方法（UnityVersion）
- `pub fn new(...)`
- `pub fn parse(s: &str) -> Option<Self>`
- `pub fn gte(...)` / `gte_simple(...)` / `gte_major_minor(...)` / `gte_major(...)`
- `pub fn resolve_sub_version(raw_version: i32) -> f64`

### `pub struct UnityVersionRange { min, max }`
- **位置**：`src-tauri/src/output/unity_version.rs:131`

### 方法
- `pub fn new(min, max)` :137
- `pub fn contains(&self, version) -> bool` :141
- `pub fn intersect(&self, other) -> Option<UnityVersionRange>` :153
- `pub fn from_filename(header_filename: &str) -> Self` :174

---

## `output/static_field_exporter.rs`

- `StaticFieldCatalog::collect(...)` —— 收集所有 thread-static / FieldRVA 字段
- `StaticFieldExporter::write_document(...)` —— 写 `static_metadata.json`

详细函数列表见 `07_functions_index.md` 与 grep。

---

## `output/embedded_scripts.rs`

### `pub fn write_scripts(output_dir: &Path) -> Result<()>`
- **位置**：`src-tauri/src/output/embedded_scripts.rs:23`
- **可见性**：pub
- **副作用**：复制嵌入的 IDA / Ghidra / BinaryNinja 脚本到 output_dir
- **调用**：被 `run_dump:1137` 调用

---

## `output/script_json.rs`

POCO 数据类：

```rust
pub struct ScriptMethod { pub address, name, signature, type_signature, ... }
pub struct ScriptString { pub address, value }
pub struct ScriptMetadata { pub address, name, signature }
pub struct ScriptMetadataMethod { pub address, name, method_address }
pub struct ScriptTypeInfo { ... }
pub struct ScriptFieldInfo { ... }
pub struct ScriptJson { ... }
pub struct StringLiteralEntry { ... }

impl ScriptJson {
    pub fn new() -> Self
    pub fn to_json(&self) -> Result<String, serde_json::Error>
}
```