# 08 — Functions Detail: Search / Executor

---

## `search/section_helper.rs`

### `pub struct SearchSection { offset, offset_end, address, address_end }`
- **位置**：`src-tauri/src/search/section_helper.rs:4`

### `pub fn new(offset: u64, offset_end: u64, address: u64, address_end: u64) -> Self`
- **位置**：`src-tauri/src/search/section_helper.rs:12`

### `pub struct SectionHelper<'a> { ... }`
- **位置**：`src-tauri/src/search/section_helper.rs:17`
- **字段**：il2cpp / metadata / exec / data / bss / version / method_count / type_definitions_count / metadata_usages_count / image_count / pointer_in_exec

### `pub fn new(il2cpp, method_count, type_definitions_count, metadata_usages_count, image_count) -> Self`
- **位置**：`src-tauri/src/search/section_helper.rs:34`
- **可见性**：pub

### `pub fn find_code_registration(&mut self) -> Option<u64>`
- **位置**：`src-tauri/src/search/section_helper.rs:69`
- **可见性**：pub
- **副作用**：可能修改 `pointer_in_exec`
- **调用**：被各 `init_<format>` 调用

### `pub fn find_metadata_registration(&self) -> Option<u64>`
- **位置**：`src-tauri/src/search/section_helper.rs:94`
- **可见性**：pub
- **调用**：被各 `init_<format>` 调用

### `pub fn find_metadata_registration_codm(&self) -> Option<u64>`
- **位置**：`src-tauri/src/search/section_helper.rs:492`
- **可见性**：pub
- **说明**：CODM 专用启发式
- **调用**：被 `init_elf:407`、`init_macho:728` 调用

### 私有方法（line 491 后）

- `find_code_registration_exec` / `find_code_registration_data` / `find_code_registration_2019` 等价于 C# 版的 `SectionHelper.FindCodeRegistration*`
- `find_metadata_registration_old` / `find_metadata_registration_v21` 等价于 C# 版
- `find_refs_fast` (`section_helper.rs` 内部)
- `find_metadata_registration_codm` 是 codm 专用路径

---

## `executor/il2cpp_executor.rs`

### `pub enum DefaultValue { None, Bool(bool), I8(i8), U8(u8), ... Str(String), Type(...) }`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:10`
- **实现 `Display`** ：`il2cpp_executor.rs:27`

### `pub struct Il2CppExecutor { metadata, il2cpp, caches }`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:61`
- **字段**：metadata / il2cpp / type_name_cache / type_def_name_cache / generic_class_cache / generic_inst_cache / generic_container_params_cache / modifier_cache / custom_attribute_generators

### `pub fn new(metadata: &Metadata, il2cpp: &mut Il2Cpp) -> Result<Self>`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:73`
- **可见性**：pub
- **副作用**：缓存 custom_attribute_generators（v27~v28）
- **调用**：被 `run_dump:1094` 调用

### `pub fn get_type_name(&mut self, type, add_namespace, is_nested) -> String`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:97`
- **可见性**：pub
- **调用**：被 `Decompiler`、`StructGenerator`、`DummyGenerator` 调用

### `pub fn get_type_def_name(&mut self, type_def, add_namespace, generic_parameter) -> String`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:270`
- **可见性**：pub

### `pub fn get_generic_inst_params(&mut self, generic_inst) -> String`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:320`
- **可见性**：pub

### `pub fn get_generic_container_params(&mut self, generic_container) -> String`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:359`
- **可见性**：pub

### `pub fn get_method_spec_name(&mut self, method_spec, add_namespace) -> (String, String)`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:384`
- **可见性**：pub

### `pub fn try_get_default_value(&mut self, type_index, data_index) -> Option<DefaultValue>`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:434`
- **可见性**：pub

### `pub fn get_modifiers(&mut self, flags: u32) -> &str`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:516`
- **可见性**：pub
- **副作用**：缓存到 `modifier_cache`

### `pub fn get_generic_class_type_definition(&mut self, generic_class) -> Option<&Il2CppTypeDefinition>`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:544`
- **可见性**：pub

### `pub fn get_generic_parameter_from_type(&mut self, il2cpp_type) -> Option<&Il2CppGenericParameter>`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:602`
- **可见性**：pub

### `pub fn get_rgctx_definition_for_type(&self, image_name, type_def) -> Option<&[Il2CppRGCTXDefinition]>`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:631`
- **可见性**：pub

### `pub fn get_rgctx_definition_for_method(&self, image_name, method_def) -> Option<&[Il2CppRGCTXDefinition]>`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:655`
- **可见性**：pub

### `pub fn get_method_spec_generic_context(&self, method_spec) -> Il2CppGenericContext`
- **位置**：`src-tauri/src/executor/il2cpp_executor.rs:679`
- **可见性**：pub

---

## `executor/custom_attribute_reader.rs`

### `pub struct CustomAttributeDataReader { ... }`
- **位置**：`src-tauri/src/executor/custom_attribute_reader.rs:9`

### `pub fn new(data: Vec<u8>) -> Result<Self>`
- **位置**：`src-tauri/src/executor/custom_attribute_reader.rs:18`
- **可见性**：pub

### `pub fn get_string_custom_attribute_data(&mut self, metadata: &mut Metadata) -> Result<String>`
- **位置**：`src-tauri/src/executor/custom_attribute_reader.rs:48`
- **可见性**：pub
- **说明**：返回 `[Foo(arg1, fieldName=value)]` 字符串
- **调用**：被 `Decompiler` 调用

### `pub fn get_ctor_type_name(&mut self, metadata: &mut Metadata) -> Result<String>`
- **位置**：`src-tauri/src/executor/custom_attribute_reader.rs:127`
- **可见性**：pub

### `pub fn format_custom_attribute_data(...)`
- **位置**：`src-tauri/src/executor/custom_attribute_reader.rs:299`
- **可见性**：pub
- **说明**：自由函数；从 blob 直接生成字符串表示