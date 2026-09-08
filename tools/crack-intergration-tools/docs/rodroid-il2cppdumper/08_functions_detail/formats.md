# 08 — Functions Detail: 格式解析 (ELF / PE / Mach-O / NSO / WASM)

---

## `formats/elf.rs`

### POD

```rust
pub struct ElfHeader { ... }   // :67
pub struct ElfPhdr { ... }     // :85
pub struct ElfDyn { ... }      // :97
pub struct ElfSym { ... }      // :103
pub struct ElfShdr { ... }     // :113
```

### `pub struct Elf { ... }`
- **位置**：`src-tauri/src/formats/elf.rs:126`
- **字段**：stream / version / is_32bit / header / segments / dynamic_section / symbols / method_definition_method_specs / method_spec_generic_method_pointers / generic_insts / method_specs / rgctxs_dictionary / type_definition_sizes / codm_diag / is_dumped ...

### `pub fn new(data: Vec<u8>, is_32bit: bool) -> Result<Self>`
- **位置**：`src-tauri/src/formats/elf.rs:163`
- **可见性**：pub
- **调用**：被 `init_elf:358` 调用
- **副作用**：parse header + program headers + dynamic section + symbol table + relocations

### `pub fn new_with_codm_diag(data, is_32bit, codm_diag) -> Result<Self>`
- **位置**：`src-tauri/src/formats/elf.rs:204`
- **可见性**：pub
- **调用**：被 `init_elf:356` 调用（CODM 模式）

### `pub fn load(&mut self) -> Result<()>`
- **位置**：`src-tauri/src/formats/elf.rs:251`
- **可见性**：pub
- **副作用**：re-load segments + relocations（dump 模式用）
- **调用**：被 `init_elf:374` 调用

### `pub fn map_vatr(&self, addr) -> Result<u64>`
- **位置**：`src-tauri/src/formats/elf.rs:756`

### `pub fn map_rtva(&self, offset) -> u64`
- **位置**：`src-tauri/src/formats/elf.rs:765`

### `pub fn map_vatr_array(&mut self, addr, count) -> Result<Vec<u64>>`
- **位置**：`src-tauri/src/formats/elf.rs:774`
- **副作用**：写入数据（dump 模式 relocate）

### `pub fn map_vatr_u32_array(&mut self, addr, count) -> Result<Vec<u32>>`
- **位置**：`src-tauri/src/formats/elf.rs:782`

### `pub fn list_exported_symbols(&mut self) -> Result<Vec<(String, u64)>>`
- **位置**：`src-tauri/src/formats/elf.rs:790`
- **可见性**：pub
- **调用**：被 `init_elf:455` 调用

### `pub fn symbol_search(&mut self) -> Result<Option<(u64, u64)>>`
- **位置**：`src-tauri/src/formats/elf.rs:859`
- **可见性**：pub
- **调用**：被 `init_elf:422` 调用

### `pub fn get_section_helper(&self, method_count, type_definitions_count, image_count) -> SectionHelper<'_>`
- **位置**：`src-tauri/src/formats/elf.rs:885`
- **可见性**：pub
- **调用**：被 `init_elf:404` 调用

### `pub fn check_dump(&mut self) -> bool`
- **位置**：`src-tauri/src/formats/elf.rs:927`
- **可见性**：pub
- **调用**：被 `init_elf:368` 调用

### `pub fn check_protection(&mut self) -> bool`
- **位置**：`src-tauri/src/formats/elf.rs:977`
- **可见性**：pub

### `pub fn get_rva(&self, pointer: u64) -> u64`
- **位置**：`src-tauri/src/formats/elf.rs:1004`

### `pub fn set_properties(&mut self, version, metadata_usages_count)`
- **位置**：`src-tauri/src/formats/elf.rs:1012`
- **可见性**：pub
- **调用**：被 `init_elf:365` 调用

### `pub fn init(&mut self, code_registration_addr, metadata_registration_addr) -> Result<()>`
- **位置**：`src-tauri/src/formats/elf.rs:1017`
- **可见性**：pub
- **说明**：从 CodeRegistration + MetadataRegistration 提取所有 method_pointer / generic_inst / methodSpec / codeGenModule
- **调用**：被 `init_elf:393, 426, 437` 调用

### `pub fn get_field_offset_from_index(...)`
- **位置**：`src-tauri/src/formats/elf.rs:1406`
- **可见性**：pub

### `pub fn get_method_pointer(&self, image_name, method_token, method_index) -> u64`
- **位置**：`src-tauri/src/formats/elf.rs:1437`
- **可见性**：pub

### `pub fn auto_plus_init(&mut self, code_reg: Option<u64>, metadata_reg: Option<u64>) -> Result<bool>`
- **位置**：`src-tauri/src/formats/elf.rs:1455`
- **可见性**：pub
- **说明**：与 C# 版 `AutoPlusInit` 对应；带 v24.2+ 版本细分
- **调用**：被 `init_elf:419` 调用

### `pub fn search_arm32(&mut self, version: f64) -> Option<(u64, u64)>`
- **位置**：`src-tauri/src/formats/elf.rs:1497`
- **可见性**：pub
- **说明**：ARM32 字节模式扫描（v<24.2）
- **调用**：被 `init_elf:433` 调用

---

## `formats/pe.rs`

### POD

```rust
pub struct PeSectionHeader { ... }   // :15
pub struct DataDirectory { ... }      // :29
```

### `pub struct Pe { ... }`
- **位置**：`src-tauri/src/formats/pe.rs:34`
- **字段**：stream / sections / is_32bit / image_base / ...

### `pub fn new(data: Vec<u8>) -> Result<Self>`
- **位置**：`src-tauri/src/formats/pe.rs:43`
- **可见性**：pub
- **调用**：被 `init_pe:483` 调用

### `pub fn map_vatr(&self, addr) -> Result<u64>`
- **位置**：`src-tauri/src/formats/pe.rs:143`

### `pub fn map_rtva(&self, addr) -> u64`
- **位置**：`src-tauri/src/formats/pe.rs:157`

### `pub fn list_exported_symbols(&mut self) -> Result<Vec<(String, u64)>>`
- **位置**：`src-tauri/src/formats/pe.rs:168`
- **可见性**：pub
- **调用**：被 `init_pe:592` 调用

### `pub fn symbol_search(&mut self) -> Result<Option<(u64, u64)>>`
- **位置**：`src-tauri/src/formats/pe.rs:213`
- **可见性**：pub
- **调用**：被 `init_pe:535` 调用

### `pub fn data_search_sections(&self) -> Vec<SearchSection>`
- **位置**：`src-tauri/src/formats/pe.rs:272`
- **可见性**：pub
- **调用**：被 `init_pe:591` 调用

### `pub fn get_section_helper(&self, method_count, type_definitions_count, metadata_usages_count, image_count, version) -> SectionHelper<'_>`
- **位置**：`src-tauri/src/formats/pe.rs:294`
- **可见性**：pub
- **调用**：被 `init_pe:545` 调用

### `pub fn check_dump(&self) -> bool`
- **位置**：`src-tauri/src/formats/pe.rs:345`
- **可见性**：pub
- **调用**：被 `init_pe:501` 调用

### `pub fn load_from_memory(&mut self, addr: u64)`
- **位置**：`src-tauri/src/formats/pe.rs:353`

### `pub fn get_rva(&self, pointer: u64) -> u64`
- **位置**：`src-tauri/src/formats/pe.rs:362`

### `pub fn image_base(&self) -> u64`
- **位置**：`src-tauri/src/formats/pe.rs:366`

---

## `formats/macho.rs`

### POD

```rust
pub struct FatArch { ... }     // :23
pub struct Segment { ... }     // :33
```

### `pub fn parse_fat(data: &[u8]) -> Result<Vec<FatArch>>`
- **位置**：`src-tauri/src/formats/macho.rs:68`
- **可见性**：pub
- **调用**：被 `init_macho_fat:619` 调用

### `pub fn extract_fat_slice(data: &[u8], arch: &FatArch) -> Result<Vec<u8>>`
- **位置**：`src-tauri/src/formats/macho.rs:116`
- **可见性**：pub
- **调用**：被 `init_macho_fat:640` 调用

### `pub struct MachO { ... }`
- **位置**：`src-tauri/src/formats/macho.rs:137`
- **字段**：stream / sections / segments / is_32bit / vmaddr / codm_fixups / ...

### `pub fn new(data: Vec<u8>, is_32bit: bool) -> Result<Self>`
- **位置**：`src-tauri/src/formats/macho.rs:152`
- **可见性**：pub
- **调用**：被 `init_macho:664` 调用

### `pub fn new_with_codm_fixups(data, is_32bit, apply_fixups) -> Result<Self>`
- **位置**：`src-tauri/src/formats/macho.rs:156`
- **可见性**：pub
- **调用**：被 `init_macho:662` 调用（CODM 模式）

### `pub fn map_vatr(&self, addr) -> Result<u64>`
- **位置**：`src-tauri/src/formats/macho.rs:383`

### `pub fn map_rtva(&self, offset) -> u64`
- **位置**：`src-tauri/src/formats/macho.rs:413`

### `pub fn read_uint_ptr(&mut self) -> Result<u64>`
- **位置**：`src-tauri/src/formats/macho.rs:430`

### `pub fn symbol_search(&self) -> Option<(u64, u64)>`
- **位置**：`src-tauri/src/formats/macho.rs:451`
- **可见性**：pub
- **调用**：被 `init_macho:705` 调用

### `pub fn list_exported_symbols(&self) -> Vec<(String, u64)>`
- **位置**：`src-tauri/src/formats/macho.rs:471`
- **可见性**：pub
- **调用**：被 `init_macho:808` 调用

### `pub fn search_mod_init_func(&mut self, version: f64) -> Option<(u64, u64)>`
- **位置**：`src-tauri/src/formats/macho.rs:483`
- **可见性**：pub
- **调用**：被 `init_macho:715` 调用

### `pub fn data_search_sections(&self) -> Vec<SearchSection>`
- **位置**：`src-tauri/src/formats/macho.rs:664`
- **可见性**：pub
- **调用**：被 `init_macho:793` 调用

### `pub fn get_section_helper(&self, method_count, type_definitions_count, metadata_usages_count, image_count, version) -> SectionHelper<'_>`
- **位置**：`src-tauri/src/formats/macho.rs:687`
- **可见性**：pub
- **调用**：被 `init_macho:726` 调用

### `pub fn check_dump(&self) -> bool`
- **位置**：`src-tauri/src/formats/macho.rs:949`
- **可见性**：pub
- **调用**：被 `init_macho:674` 调用

### `pub fn get_rva(&self, pointer: u64) -> u64`
- **位置**：`src-tauri/src/formats/macho.rs:960`

---

## `formats/nso.rs`

### `pub struct Nso { ... }`
- **位置**：`src-tauri/src/formats/nso.rs:19`

### `pub fn new(data: Vec<u8>) -> Result<Self>`
- **位置**：`src-tauri/src/formats/nso.rs:29`
- **可见性**：pub
- **调用**：被 `init_nso:836` 调用

### `pub fn map_vatr(&self, addr) -> Result<u64>`
- **位置**：`src-tauri/src/formats/nso.rs:336`

### `pub fn map_rtva(&self, offset) -> u64`
- **位置**：`src-tauri/src/formats/nso.rs:345`

### `pub fn data_search_sections(&self) -> Vec<SearchSection>`
- **位置**：`src-tauri/src/formats/nso.rs:354`
- **可见性**：pub
- **调用**：被 `init_nso:905` 调用

### `pub fn get_section_helper(&self, method_count, type_definitions_count, metadata_usages_count, image_count, version) -> SectionHelper<'_>`
- **位置**：`src-tauri/src/formats/nso.rs:375`
- **可见性**：pub
- **调用**：被 `init_nso:868` 调用

### `pub fn check_dump(&self) -> bool`
- **位置**：`src-tauri/src/formats/nso.rs:420`
- **可见性**：pub
- **调用**：被 `init_nso:844` 调用

### `pub fn list_exported_symbols(&mut self) -> Result<Vec<(String, u64)>>`
- **位置**：`src-tauri/src/formats/nso.rs:424`
- **可见性**：pub
- **调用**：被 `init_nso:907` 调用

### `pub fn get_rva(&self, pointer: u64) -> u64`
- **位置**：`src-tauri/src/formats/nso.rs:447`

---

## `formats/wasm.rs`

### `pub enum WasmSectionId { ... }`
- **位置**：`src-tauri/src/formats/wasm.rs:10`
- **实现 `From<u8>`** ：`wasm.rs:27`

### `pub struct Wasm { ... }`
- **位置**：`src-tauri/src/formats/wasm.rs:62`

### `pub fn new(data: Vec<u8>) -> Result<Self>`
- **位置**：`src-tauri/src/formats/wasm.rs:70`
- **可见性**：pub
- **调用**：被 `init_wasm:936` 调用

### `pub fn map_vatr(&self, addr) -> Result<u64>`
- **位置**：`src-tauri/src/formats/wasm.rs:195`

### `pub fn map_rtva(&self, offset) -> u64`
- **位置**：`src-tauri/src/formats/wasm.rs:205`

### `pub fn data_search_sections(&self) -> Vec<SearchSection>`
- **位置**：`src-tauri/src/formats/wasm.rs:214`
- **可见性**：pub
- **调用**：被 `init_wasm:1005` 调用

### `pub fn get_section_helper(&self, method_count, type_definitions_count, metadata_usages_count, image_count, version) -> SectionHelper<'_>`
- **位置**：`src-tauri/src/formats/wasm.rs:228`
- **可见性**：pub
- **调用**：被 `init_wasm:968` 调用

### `pub fn check_dump(&self) -> bool`
- **位置**：`src-tauri/src/formats/wasm.rs:267`
- **可见性**：pub
- **调用**：被 `init_wasm:944` 调用

### `pub fn get_rva(&self, pointer: u64) -> u64`
- **位置**：`src-tauri/src/formats/wasm.rs:271`