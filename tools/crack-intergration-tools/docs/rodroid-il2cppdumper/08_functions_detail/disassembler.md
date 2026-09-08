# 08 — Functions Detail: Disassembler + Utils

---

## `disassembler/mod.rs`

### `pub enum Architecture { X86, X64, ARM32, ARM64 }`
- **位置**：`src-tauri/src/disassembler/mod.rs:10`

### `impl Display for Architecture`
- **位置**：`src-tauri/src/disassembler/mod.rs:17`

### `impl Architecture`
| 方法 | 行 | 说明 |
|------|----|------|
| `pub fn from_elf_machine(e_machine: u16) -> Option<Self>` | 29 | |
| `pub fn from_pe_machine(machine: u16) -> Option<Self>` | 39 | |
| `pub fn from_macho_cputype(cputype: u32) -> Option<Self>` | 49 | |
| `pub fn from_bitness(is_32bit: bool, is_pe: bool) -> Self` | 59 | 兜底：x86 / x64 |

### POD

```rust
pub struct RegRegAccess { ... }              // :69
pub struct LoadInfo { ... }                  // :76
pub enum ConstantOp { ... }                  // :83
pub struct DisassembledInstruction { ... }    // :94
impl fmt::Display for DisassembledInstruction   // :114
```

### `pub struct DisassemblyContext { ... }`
- **位置**：`src-tauri/src/disassembler/mod.rs:124`

### `impl DisassemblyContext`

| 方法 | 行 |
|------|----|
| `pub fn new() -> Self` | 135 |
| `pub fn resolve_register(&self, reg: &str) -> String` | 147 |
| `pub fn resolve_operands(&self, operands: &str) -> String` | 155 |

### `pub enum MetadataAnnotationKind { ... }`
- **位置**：`src-tauri/src/disassembler/mod.rs:177`

### `pub struct MetadataAnnotation { ... }`
- **位置**：`src-tauri/src/disassembler/mod.rs:185`

### `pub struct Disassembler { arch, annotations, method_names, type_names, static_fields, ... }`
- **位置**：`src-tauri/src/disassembler/mod.rs:190`

### `impl Disassembler`

| 方法 | 行 | 说明 |
|------|----|------|
| `pub fn new(arch) -> Self` | 204 | |
| `pub fn add_string_new_wrapper_rva(rva)` | 219 | |
| `pub fn add_box_helper_rva(rva)` | 223 | |
| `pub fn add_object_new_helper_rva(rva)` | 227 | |
| `pub fn add_unbox_helper_rva(rva)` | 231 | |
| `pub fn add_static_field(rva, type_name, offset, field_name)` | 235 | |
| `pub fn lookup_static_field(rva, offset) -> Option<(&str, &str)>` | 245 | |
| `pub fn type_name_at_va(va) -> Option<&str>` | 252 | |
| `pub fn set_string_literal_table(table)` | 262 | |
| `pub fn arch() -> Architecture` | 266 | |
| `pub fn set_method_names(map)` | 269 | |
| `pub fn has_method_name(rva) -> bool` | 273 | |
| `pub fn annotation_count() -> usize` | 277 | |
| `pub fn add_string_literal(rva, value)` | 281 | |
| `pub fn add_type_info(rva, name)` | 303 | |
| `pub fn add_method_ref(rva, name)` | 310 | |
| `pub fn add_field_ref(rva, name)` | 317 | |
| `pub fn disassemble(bytes, base, max) -> Vec<DisassembledInstruction>` | 324 | |
| `pub fn format_method_body(...) -> String` | 333 | 主输出函数 |

### 其他
- `impl CfgAnalysis` (private) :747
- `pub struct PropagationResults` :1226
- `pub fn analyze_propagation(...)` :1234
- `pub enum SwitchAnnotation { ... }` :1419

---

## `disassembler/arm.rs`

### `pub fn disassemble_arm64(bytes, base, max) -> Vec<DisassembledInstruction>`
- **位置**：`src-tauri/src/disassembler/arm.rs:6`
- **可见性**：pub
- **后端**：yaxpeax-arm
- **调用**：被 `Disassembler::disassemble` 根据 arch 决定调用

### `pub fn disassemble_arm32(bytes, base, max) -> Vec<DisassembledInstruction>`
- **位置**：`src-tauri/src/disassembler/arm.rs:111`
- **可见性**：pub

---

## `disassembler/x86.rs`

### `pub fn disassemble_x86(bytes, base, max, is_64bit) -> Vec<DisassembledInstruction>`
- **位置**：`src-tauri/src/disassembler/x86.rs:6`
- **可见性**：pub
- **后端**：iced-x86

### `pub fn normalize_x86_reg(reg: iced_x86::Register) -> u16`
- **位置**：`src-tauri/src/disassembler/x86.rs:289`

---

## `utils/pattern_search.rs`

### `pub fn find_bytes(data: &[u8], pattern: &[u8]) -> Option<usize>`
- **位置**：`src-tauri/src/utils/pattern_search.rs:1`
- **可见性**：pub
- **说明**：朴素字节搜索（pattern 中允许 `0x00` wildcards）

### `mod tests` (private, line 36+)
- `fn test_find_bytes()`

---

## `utils/string_utils.rs`

### `pub struct NameSanitizerOptions { ... }`
- **位置**：`src-tauri/src/utils/string_utils.rs:21`

### `pub fn sanitize_path_component(name: &str) -> String`
- **位置**：`src-tauri/src/utils/string_utils.rs:26`

### `pub fn sanitize_cpp_identifier(name: &str, opts: NameSanitizerOptions) -> String`
- **位置**：`src-tauri/src/utils/string_utils.rs:39`

### `pub fn sanitize_mangled_identifier_chars(id: &str) -> String`
- **位置**：`src-tauri/src/utils/string_utils.rs:71`

### `pub fn escape_string(s: &str) -> String`
- **位置**：`src-tauri/src/utils/string_utils.rs:83`

### `pub fn escape_string_preview(s: &str, max_len: usize) -> String`
- **位置**：`src-tauri/src/utils/string_utils.rs:102`

### `mod tests` (private, line 121)
- `fn test_escape_string()`