# 07 — 函数索引表

行号基于仓库实际状态。所有函数可见性 = `pub`（除非特别标注）。

---

## `src-tauri/src/main.rs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `fn main()` | 4 | private | runtime entry |

## `src-tauri/src/lib.rs`

| 函数 / 类型 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `struct LogEvent` | 44 | private | emit_log |
| `struct InputRequestEvent` | 49 | private | request_input |
| `struct DumpCompleteEvent` | 54 | private | start_dump |
| `struct CrashEvent` | 61 | private | start_dump panic branch |
| `struct BinaryInfo` | 66 | private | detect_binary return |
| `struct AppState` | 71 | private | run() |
| `MAGIC_METADATA` | 34 | const | try_decrypt_metadata / detect_format |
| `MAGIC_ELF / MAGIC_PE / MAGIC_MACHO32 / MAGIC_MACHO64 / MAGIC_MACHOFAT / MAGIC_NSO / MAGIC_WASM` | 35-41 | const | detect_format |
| `fn emit_log` | 76 | private | 7+ callers (init_<format>, run_dump) |
| `fn request_input` | 85 | private | prompt_dump_address / prompt_manual_addresses |
| `fn parse_hex` | 102 | private | prompt_dump_address / prompt_manual_addresses |
| `fn prompt_dump_address` | 107 | private | 6 init_<format> |
| `fn prompt_manual_addresses` | 113 | private | 6 init_<format> |
| `fn read_magic_u32` | 126 | private | try_decrypt_metadata / detect_format |
| `fn read_magic_u16` | 133 | private | detect_format |
| `fn is_valid_metadata_version` | 140 | private | try_decrypt_metadata |
| `fn try_decrypt_metadata` | 148 | private | run_dump:1043 |
| `fn detect_unity_version` | 279 | private | run_dump:1033, detect_binary:1184 |
| `fn detect_format` | 324 | private | run_dump:1064, detect_binary:1183 |
| `fn resolve_codm` | 338 | private | 6 init_<format> |
| `fn init_elf` | 342 | private | run_dump:1068 |
| `fn init_pe` | 476 | private | run_dump:1069 |
| `fn init_macho_fat` | 611 | private | run_dump:1071 |
| `fn init_macho` | 644 | private | run_dump:1070, init_macho_fat:641 |
| `fn init_nso` | 828 | private | run_dump:1072 |
| `fn init_wasm` | 928 | private | run_dump:1073 |
| `fn run_dump` | 1009 | private | start_dump:1221 |
| `struct DumpGuard` | 1210 | private | start_dump |
| `impl Drop for DumpGuard::drop` | 1212 | private | GC |
| `#[tauri::command] fn detect_binary` | 1181 | Tauri command | 前端 |
| `#[tauri::command] fn start_dump` | 1192 | Tauri command | 前端 dumpRunner.beginDump |
| `#[tauri::command] fn submit_input` | 1284 | Tauri command | 前端 InputDialog |
| `#[tauri::command] fn get_default_config` | 1292 | Tauri command | 前端（首屏 load） |
| `pub fn run` | 1297 | pub | main.rs:5 |

## `src-tauri/src/config.rs`

| 成员 | 行 | 可见性 |
|------|----|----|
| `pub struct Config` | 5 | pub |
| `impl Default::default` | 51 | private |
| `pub fn load_from_file` | 100 | pub |
| `pub fn save_to_file` | 106 | pub |

## `src-tauri/src/error.rs`

| 成员 | 行 | 可见性 |
|------|----|----|
| `pub enum Error` | 2 | pub |
| `pub type Result<T>` | 28 | pub |

## `src-tauri/src/io/`

`BinaryStream` + `VersionAwareStream` —— 标准二进制流 + 版本感知读取。

## `src-tauri/src/il2cpp/base.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct VaSegment` | 9 | pub | everywhere |
| `pub struct Il2Cpp` | 15 | pub | everywhere |
| `pub fn new(stream, version, is_32bit) -> Self` | 62 | pub | init_pe:580, init_macho:763, init_nso:897, init_wasm:997 |
| `pub fn from_elf(elf) -> Self` | 104 | pub | init_elf:456 |
| `pub fn init(cr, mr, map_vatr)` | 162 | pub | 6 init_<format> |
| `fn build_method_spec_lookup` | 433 | private | init |
| `fn load_code_gen_modules` | 457 | private | init |
| `pub fn get_method_pointer(image, methodDef)` | 492 | pub | Decompiler, StructGenerator, Disassembler |
| `pub fn get_raw_field_offset` | 511 | pub | get_field_offset_from_index |
| `pub fn get_field_offset_from_index` | 547 | pub | Decompiler, StructGenerator |
| `pub fn get_rva(pointer)` | 570 | pub | Decompiler, StructGenerator, DummyGen |
| `pub fn get_il2cpp_type(pointer)` | 578 | pub | Executor |
| `pub fn map_vatr(addr)` | 582 | pub | everywhere |
| `pub fn map_rtva(offset)` | 591 | pub | everywhere |
| `pub fn read_generic_class` | 600 | pub | Executor |
| `pub fn read_generic_inst` | 606 | pub | Executor |
| `pub fn read_ptr_array` | 612 | pub | init, Executor |
| `pub fn detect_architecture` | 622 | pub | Disassembler |
| `pub fn build_sorted_method_addresses` | 629 | pub | Disassembler |
| `pub fn get_method_body_size` | 661 | pub | Disassembler |
| `pub fn read_bytes_at_rva` | 679 | pub | Disassembler |

## `src-tauri/src/il2cpp/metadata.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub enum MetadataVariant` | 9 | pub | resolve_codm, load_metadata |
| `fn detect_codm_variant` | 14 | private | new_with_options |
| `pub struct Metadata` | 66 | pub | everywhere |
| `pub fn new(data)` | 113 | pub | – |
| `pub fn new_with_unity_version(data, unity_version_str)` | 117 | pub | – |
| `pub fn new_with_options(data, unity_version_str, codm)` | 121 | pub | run_dump:1056 |
| `fn detect_subversion` | 237 | private | new* |
| `fn load_metadata` | 262 | private | new* |
| `fn load_metadata_codm` | 418 | private | new* |
| `fn read_metadata_array_codm<T>` | 524 | private | load_metadata_codm |
| `fn read_metadata_array<T>` | 541 | private | load_metadata |
| `fn read_metadata_array_with_offsets<T>` | 578 | private | load_metadata |
| `fn process_metadata_usage` | 624 | private | load_metadata |
| `fn calculate_metadata_usages_count` | 656 | private | load_metadata |
| `fn build_attribute_lookup` | 672 | private | load_metadata |
| `pub fn get_string_from_index` | 693 | pub | everywhere |
| `pub fn get_string_literal_from_index` | 703 | pub | Decompiler, StructGenerator |
| `pub fn get_field_default_value` | 725 | pub | Decompiler |
| `pub fn get_parameter_default_value` | 729 | pub | Decompiler |
| `pub fn get_default_value_offset` | 733 | pub | Executor.try_get_default_value |
| `pub fn get_custom_attribute_index` | 737 | pub | Decompiler, DummyGen |
| `trait MetadataReadable` | 757 | pub | macro for all POD |
| `trait CodmReadable` | 827 | pub | macro for all POD |

## `src-tauri/src/il2cpp/enums.rs`

| 成员 | 行 | 可见性 |
|------|----|----|
| `pub enum Il2CppTypeEnum` | 3 | pub |
| `pub fn from_u8` | 44 | pub |
| `pub fn type_name` | 87 | pub |
| `pub fn is_il2cpp_primitive` | 111 | pub |
| `pub fn is_numeric` | 123 | pub |
| `pub fn is_reference_type` | 134 | pub |
| `pub enum Il2CppRGCTXDataType` | 144 | pub |
| `pub fn from_u32` | 154 | pub |
| `pub enum Il2CppMetadataUsage` | 169 | pub |
| `pub fn from_u32` | 180 | pub |
| `pub fn encoded_index_shift` | 193 | pub |
| `pub fn encoded_index_mask` | 197 | pub |

## `src-tauri/src/il2cpp/field_layout.rs`

| 成员 | 行 | 可见性 |
|------|----|----|
| `pub enum StaticFieldKind` | 12 | pub |
| `pub struct DecodedFieldOffset` | 21 | pub |
| `pub struct FieldLayoutInfo` | 28 | pub |
| `pub fn is_static_storage` | 45 | pub |
| `pub fn decode_field_offset` | 55 | pub |
| `pub fn estimate_field_rva_size` | 72 | pub |
| `pub fn read_metadata_bytes` | 101 | pub |
| `pub fn read_binary_bytes` | 120 | pub |
| `pub fn analyze_field_layout` | 127 | pub |

## `src-tauri/src/il2cpp/structures.rs`

POD 全部，无独立方法（除 UnityVersion 与 PackingSize 枚举）。所有 POD 通过宏实现 `MetadataReadable` + `CodmReadable`。

| struct / enum | 行 | 说明 |
|------|----|----|
| `pub struct UnityVersion` | 8 | version 解析 |
| `pub enum UnityBuildType` | 17 | |
| `impl UnityVersion::new` | 25 | |
| `impl UnityVersion::parse` | 29 | |
| `impl UnityVersion::gte` | 67 | |
| `impl UnityVersion::gte_simple` | 73 | |
| `impl UnityVersion::gte_major_minor` | 77 | |
| `impl UnityVersion::gte_major` | 81 | |
| `impl UnityVersion::resolve_sub_version` | 85 | |
| `impl Display for UnityVersion::fmt` | 137 | |
| `fn decode_packing_size` (private) | 148 | |
| `pub enum Il2CppPackingSizeEnum` | 165 | |
| `impl Il2CppPackingSizeEnum::from_u32` | 178 | |
| `pub struct Il2CppGlobalMetadataHeader` | (约 200) | |
| `pub struct Il2CppImageDefinition` | (约 280) | |
| `pub struct Il2CppAssemblyDefinition` | (约 350) | |
| `pub struct Il2CppTypeDefinition` | (约 420) | |
| `pub struct Il2CppMethodDefinition` | (约 540) | |
| `pub struct Il2CppParameterDefinition` | | |
| `pub struct Il2CppFieldDefinition` | | |
| `pub struct Il2CppFieldDefaultValue` | | |
| `pub struct Il2CppParameterDefaultValue` | | |
| `pub struct Il2CppPropertyDefinition` | | |
| `pub struct Il2CppEventDefinition` | | |
| `pub struct Il2CppGenericContainer` | | |
| `pub struct Il2CppGenericParameter` | | |
| `pub struct Il2CppFieldRef` | | |
| `pub struct Il2CppStringLiteral` | | |
| `pub struct Il2CppCustomAttributeTypeRange` | | |
| `pub struct Il2CppCustomAttributeDataRange` | | |
| `pub struct Il2CppMetadataUsageList` | | |
| `pub struct Il2CppMetadataUsagePair` | | |
| `pub struct Il2CppType` | (约 1500) | |
| `pub struct Il2CppGenericClass` | | |
| `pub struct Il2CppGenericContext` | | |
| `pub struct Il2CppGenericInst` | | |
| `pub struct Il2CppArrayType` | | |
| `pub struct Il2CppGenericMethodFunctionsDefinitions` | | |
| `pub struct Il2CppGenericMethodIndices` | | |
| `pub struct Il2CppMethodSpec` | | |
| `pub struct Il2CppCodeGenModule` | | |
| `pub struct Il2CppRange` | | |
| `pub struct Il2CppTokenRangePair` | | |
| `pub struct Il2CppCodeRegistration` | | |
| `pub struct Il2CppMetadataRegistration` | | |
| `pub struct Il2CppRGCTXDefinition` | | |
| `pub struct Il2CppRGCTXDefinitionData` | | |
| `pub struct Il2CppTypeDefinitionSizes` | | |

## `src-tauri/src/formats/elf.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct ElfHeader / ElfPhdr / ElfDyn / ElfSym / ElfShdr` | 67/85/97/103/113 | pub | – |
| `pub struct Elf` | 126 | pub | – |
| `pub fn new(data, is_32bit)` | 163 | pub | init_elf:358 |
| `pub fn new_with_codm_diag` | 204 | pub | init_elf:356 |
| `pub fn load` | 251 | pub | init_elf:374 |
| `pub fn map_vatr` | 756 | pub | base::init |
| `pub fn map_rtva` | 765 | pub | base::init |
| `pub fn map_vatr_array` | 774 | pub | – |
| `pub fn map_vatr_u32_array` | 782 | pub | – |
| `pub fn list_exported_symbols` | 790 | pub | init_elf:455 |
| `pub fn symbol_search` | 859 | pub | init_elf:422 |
| `pub fn get_section_helper` | 885 | pub | init_elf:404 |
| `pub fn check_dump` | 927 | pub | init_elf:368 |
| `pub fn check_protection` | 977 | pub | – |
| `pub fn get_rva` | 1004 | pub | – |
| `pub fn set_properties` | 1012 | pub | init_elf:365 |
| `pub fn init` | 1017 | pub | init_elf:393/426/437 |
| `pub fn get_field_offset_from_index` | 1406 | pub | – |
| `pub fn get_method_pointer` | 1437 | pub | – |
| `pub fn auto_plus_init` | 1455 | pub | init_elf:419 |
| `pub fn search_arm32` | 1497 | pub | init_elf:433 |

## `src-tauri/src/formats/pe.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct PeSectionHeader` | 15 | pub | – |
| `pub struct DataDirectory` | 29 | pub | – |
| `pub struct Pe` | 34 | pub | – |
| `pub fn new(data)` | 43 | pub | init_pe:483 |
| `pub fn map_vatr` | 143 | pub | – |
| `pub fn map_rtva` | 157 | pub | – |
| `pub fn list_exported_symbols` | 168 | pub | init_pe:592 |
| `pub fn symbol_search` | 213 | pub | init_pe:535 |
| `pub fn data_search_sections` | 272 | pub | init_pe:591 |
| `pub fn get_section_helper` | 294 | pub | init_pe:545 |
| `pub fn check_dump` | 345 | pub | init_pe:501 |
| `pub fn load_from_memory` | 353 | pub | – |
| `pub fn get_rva` | 362 | pub | – |
| `pub fn image_base` | 366 | pub | init_pe:569 |

## `src-tauri/src/formats/macho.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct FatArch` | 23 | pub | – |
| `pub struct Segment` | 33 | pub | – |
| `pub fn parse_fat` | 68 | pub | init_macho_fat:619 |
| `pub fn extract_fat_slice` | 116 | pub | init_macho_fat:640 |
| `pub struct MachO` | 137 | pub | – |
| `pub fn new(data, is_32bit)` | 152 | pub | init_macho:664 |
| `pub fn new_with_codm_fixups` | 156 | pub | init_macho:662 |
| `pub fn map_vatr` | 383 | pub | – |
| `pub fn map_rtva` | 413 | pub | – |
| `pub fn read_uint_ptr` | 430 | pub | – |
| `pub fn symbol_search` | 451 | pub | init_macho:705 |
| `pub fn list_exported_symbols` | 471 | pub | init_macho:808 |
| `pub fn search_mod_init_func` | 483 | pub | init_macho:715 |
| `pub fn data_search_sections` | 664 | pub | init_macho:793 |
| `pub fn get_section_helper` | 687 | pub | init_macho:726 |
| `pub fn check_dump` | 949 | pub | init_macho:674 |
| `pub fn get_rva` | 960 | pub | – |

## `src-tauri/src/formats/nso.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct Nso` | 19 | pub | – |
| `pub fn new(data)` | 29 | pub | init_nso:836 |
| `pub fn map_vatr` | 336 | pub | – |
| `pub fn map_rtva` | 345 | pub | – |
| `pub fn data_search_sections` | 354 | pub | init_nso:905 |
| `pub fn get_section_helper` | 375 | pub | init_nso:868 |
| `pub fn check_dump` | 420 | pub | init_nso:844 |
| `pub fn list_exported_symbols` | 424 | pub | init_nso:907 |
| `pub fn get_rva` | 447 | pub | – |

## `src-tauri/src/formats/wasm.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub enum WasmSectionId` | 10 | pub | – |
| `impl From<u8> for WasmSectionId` | 27 | pub trait impl | – |
| `pub struct Wasm` | 62 | pub | – |
| `pub fn new(data)` | 70 | pub | init_wasm:936 |
| `pub fn map_vatr` | 195 | pub | – |
| `pub fn map_rtva` | 205 | pub | – |
| `pub fn data_search_sections` | 214 | pub | init_wasm:1005 |
| `pub fn get_section_helper` | 228 | pub | init_wasm:968 |
| `pub fn check_dump` | 267 | pub | init_wasm:944 |
| `pub fn get_rva` | 271 | pub | – |

## `src-tauri/src/search/section_helper.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct SearchSection` | 4 | pub | – |
| `pub fn new` | 12 | pub | – |
| `pub struct SectionHelper<'a>` | 17 | pub | – |
| `pub fn new` | 34 | pub | 各 init_<format> |
| `pub fn find_code_registration` | 69 | pub | 各 init_<format> |
| `pub fn find_metadata_registration` | 94 | pub | 各 init_<format> |
| `pub fn find_metadata_registration_codm` | 492 | pub | init_elf:407, init_macho:728 |

## `src-tauri/src/executor/il2cpp_executor.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub enum DefaultValue` | 10 | pub | – |
| `impl Display for DefaultValue::fmt` | 27 | pub trait impl | – |
| `pub struct Il2CppExecutor` | 61 | pub | – |
| `pub fn new(metadata, il2cpp)` | 73 | pub | run_dump:1094 |
| `pub fn get_type_name` | 97 | pub | Decompiler, StructGenerator, DummyGen |
| `pub fn get_type_def_name` | 270 | pub | Decompiler, StructGenerator, DummyGen |
| `pub fn get_generic_inst_params` | 320 | pub | Decompiler, StructGenerator, DummyGen |
| `pub fn get_generic_container_params` | 359 | pub | Decompiler, StructGenerator, DummyGen |
| `pub fn get_method_spec_name` | 384 | pub | Decompiler, StructGenerator, DummyGen |
| `pub fn try_get_default_value` | 434 | pub | Decompiler, DummyGen |
| `pub fn get_modifiers` | 516 | pub | Decompiler |
| `pub fn get_generic_class_type_definition` | 544 | pub | – |
| `pub fn get_generic_parameter_from_type` | 602 | pub | – |
| `pub fn get_rgctx_definition_for_type` | 631 | pub | StructGenerator |
| `pub fn get_rgctx_definition_for_method` | 655 | pub | StructGenerator |
| `pub fn get_method_spec_generic_context` | 679 | pub | StructGenerator |

## `src-tauri/src/executor/custom_attribute_reader.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct CustomAttributeDataReader` | 9 | pub | – |
| `pub fn new(data)` | 18 | pub | Decompiler, DummyGen |
| `pub fn get_string_custom_attribute_data` | 48 | pub | Decompiler |
| `pub fn get_ctor_type_name` | 127 | pub | Decompiler |
| `pub fn format_custom_attribute_data` (free fn) | 299 | pub | – |

## `src-tauri/src/output/decompiler.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct Il2CppDecompiler` | 15 | pub | – |
| `pub fn decompile(executor, metadata, il2cpp, config, outDir, log)` | 18 | pub | run_dump:1097 |

## `src-tauri/src/output/struct_generator.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct StructGenerator` | 58 | pub | – |
| `pub fn write_all(...)` | 72 | pub | run_dump:1133 |
| `pub fn resolve_generic_type_var_pub` | 408 | pub | cpp_scaffolding |
| `pub fn build_struct_name_dic_pub` | 576 | pub | cpp_scaffolding |
| `pub fn build_type_def_image_names_pub` | 597 | pub | cpp_scaffolding |

## `src-tauri/src/output/dummy_assembly_generator.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub fn generate_dummy_dlls` | 142 | pub | run_dump:1144 |

## `src-tauri/src/output/generics.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub fn dump_generics` | 22 | pub | run_dump:1158 |

## `src-tauri/src/output/cpp_scaffolding.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct CppScaffolding` | 13 | pub | – |
| `pub fn build` | 24 | pub | run_dump, StructGenerator |
| `pub fn write_project` | 440 | pub | – |

## `src-tauri/src/output/cpp_ast.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub struct CppField` | 33 | pub | – |
| `pub struct CppVTableEntry` | 41 | pub | – |
| `pub struct CppRGCTXEntry` | 46 | pub | – |
| `pub struct CppTypeDecl` | 54 | pub | – |
| `pub struct CppHeaderEmitter` | 64 | pub | – |
| `pub fn new` | 73 | pub | – |
| `pub fn emit_all_with_groups` | 156 | pub | – |
| `pub fn emit_all` | 270 | pub | – |

## `src-tauri/src/output/cpp_type_model.rs`

| 成员 | 行 | 可见性 |
|------|----|----|
| `pub enum CppTypeGroup` | 4 | pub |
| `pub fn tag` | 13 | pub |
| `pub fn section_header` | 23 | pub |
| `pub enum ComplexValueKind` | 35 | pub |
| `pub enum CppType` | 43 | pub |
| `pub fn name` | 83 | pub |
| `pub fn size_bytes` | 96 | pub |
| `pub fn alignment_bytes` | 109 | pub |
| `pub fn is_enum` | 122 | pub |
| `pub fn is_complex_struct` | 126 | pub |
| `pub fn is_forward_declarable` | 133 | pub |
| `pub fn as_pointer` | 143 | pub |
| `pub fn as_array` | 150 | pub |
| `pub fn as_alias` | 157 | pub |
| `pub fn to_field_string` | 164 | pub |
| `pub struct CppTypeGroupRegistry` | 203 | pub |
| `pub fn new` | 209 | pub |
| `pub fn assign` | 213 | pub |
| `pub fn group_of` | 227 | pub |
| `pub fn members` | 231 | pub |
| `pub fn promote` | 238 | pub |
| `pub fn all_names` | 253 | pub |

## `src-tauri/src/output/name_mangler.rs`

| 成员 | 行 | 可见性 |
|------|----|----|
| `pub struct MangledNameBuilder` | 8 | pub |
| `pub fn mangle_method` | 322 | pub |
| `pub fn mangle_method_info` | 335 | pub |
| `pub fn mangle_method_spec` | 348 | pub |
| `pub fn mangle_type_info` | 363 | pub |
| `pub fn mangle_type_ref` | 373 | pub |

## `src-tauri/src/output/header_manager.rs`

| 成员 | 行 | 可见性 |
|------|----|----|
| `pub struct UnityResource` | 9 | pub |
| `pub fn get_text` | 17 | pub |
| `pub struct UnityHeaders` | 26 | pub |
| `pub fn new` | 34 | pub |
| `pub fn get_type_header_text` | 47 | pub |
| `pub fn get_api_header_text` | 61 | pub |
| `pub fn get_all_type_headers` | 65 | pub |
| `pub fn get_all_api_headers` | 83 | pub |
| `pub fn guess_headers_for_binary` | 116 | pub |

## `src-tauri/src/output/header_constants.rs`

| 函数 | 行 |
|------|----|
| `generic_header()` | 1 |
| `header_v29()` | 42 |
| `header_v27()` | 152 |
| `header_v242()` | 260 |
| `header_v241()` | 368 |
| `header_v240()` | 475 |
| `header_v22()` | 581 |
| `get_version_header(version)` | 686 |

## `src-tauri/src/output/unity_version.rs`

| 成员 | 行 | 可见性 |
|------|----|----|
| `pub enum BuildType` | 5 | pub |
| `pub fn from_str_safe` | 15 | pub |
| `pub struct UnityVersion` | 29 | pub |
| `impl Default::default` | 38 | pub trait impl |
| `impl PartialOrd::partial_cmp` | 50 | pub trait impl |
| `impl Ord::cmp` | 56 | pub trait impl |
| `impl FromStr::from_str` | 80 | pub trait impl |
| `pub struct UnityVersionRange` | 131 | pub |
| `pub fn new` | 137 | pub |
| `pub fn contains` | 141 | pub |
| `pub fn intersect` | 153 | pub |
| `pub fn from_filename` | 174 | pub |

## `src-tauri/src/output/static_field_exporter.rs`

| 成员（推断） | 可见性 |
|------|----|
| `StaticFieldCatalog::collect(...)` | pub |
| `StaticFieldExporter::write_document(...)` | pub |

## `src-tauri/src/output/embedded_scripts.rs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `pub fn write_scripts` | 23 | pub | run_dump:1137 |

## `src-tauri/src/output/script_json.rs`

POCO + `impl ScriptJson::new + to_json`。

## `src-tauri/src/disassembler/mod.rs`

| 成员 | 行 | 可见性 |
|------|----|----|
| `pub enum Architecture` | 10 | pub |
| `impl Display::fmt` | 17 | pub trait impl |
| `pub fn from_elf_machine` | 29 | pub |
| `pub fn from_pe_machine` | 39 | pub |
| `pub fn from_macho_cputype` | 49 | pub |
| `pub fn from_bitness` | 59 | pub |
| `pub struct RegRegAccess` | 69 | pub |
| `pub struct LoadInfo` | 76 | pub |
| `pub enum ConstantOp` | 83 | pub |
| `pub struct DisassembledInstruction` | 94 | pub |
| `impl Display::fmt` | 114 | pub trait impl |
| `pub struct DisassemblyContext` | 124 | pub |
| `pub fn new` | 135 | pub |
| `pub fn resolve_register` | 147 | pub |
| `pub fn resolve_operands` | 155 | pub |
| `pub enum MetadataAnnotationKind` | 177 | pub |
| `pub struct MetadataAnnotation` | 185 | pub |
| `pub struct Disassembler` | 190 | pub |
| `pub fn new` | 204 | pub |
| `pub fn add_string_new_wrapper_rva` | 219 | pub |
| `pub fn add_box_helper_rva` | 223 | pub |
| `pub fn add_object_new_helper_rva` | 227 | pub |
| `pub fn add_unbox_helper_rva` | 231 | pub |
| `pub fn add_static_field` | 235 | pub |
| `pub fn lookup_static_field` | 245 | pub |
| `pub fn type_name_at_va` | 252 | pub |
| `pub fn set_string_literal_table` | 262 | pub |
| `pub fn arch` | 266 | pub |
| `pub fn set_method_names` | 269 | pub |
| `pub fn has_method_name` | 273 | pub |
| `pub fn annotation_count` | 277 | pub |
| `pub fn add_string_literal` | 281 | pub |
| `pub fn add_type_info` | 303 | pub |
| `pub fn add_method_ref` | 310 | pub |
| `pub fn add_field_ref` | 317 | pub |
| `pub fn disassemble` | 324 | pub |
| `pub fn format_method_body` | 333 | pub |
| `pub struct PropagationResults` | 1226 | pub |
| `pub fn analyze_propagation` | 1234 | pub |
| `pub enum SwitchAnnotation` | 1419 | pub |

## `src-tauri/src/disassembler/arm.rs`

| 函数 | 行 | 可见性 |
|------|----|----|
| `pub fn disassemble_arm64` | 6 | pub |
| `pub fn disassemble_arm32` | 111 | pub |

## `src-tauri/src/disassembler/x86.rs`

| 函数 | 行 | 可见性 |
|------|----|----|
| `pub fn disassemble_x86` | 6 | pub |
| `pub fn normalize_x86_reg` | 289 | pub |

## `src-tauri/src/utils/pattern_search.rs`

| 函数 | 行 | 可见性 |
|------|----|----|
| `pub fn find_bytes` | 1 | pub |

## `src-tauri/src/utils/string_utils.rs`

| 成员 | 行 | 可见性 |
|------|----|----|
| `pub struct NameSanitizerOptions` | 21 | pub |
| `pub fn sanitize_path_component` | 26 | pub |
| `pub fn sanitize_cpp_identifier` | 39 | pub |
| `pub fn sanitize_mangled_identifier_chars` | 71 | pub |
| `pub fn escape_string` | 83 | pub |
| `pub fn escape_string_preview` | 102 | pub |

## `src/routes/+page.svelte`

| 成员 | 行 | 可见性 |
|------|----|----|
| 默认 export (组件) | 1 | default |
| `currentOs` state | 25 | local |
| `draftConfig` state | 26 | local |
| `$effect` | 28-32 | svelte rune |
| `confirmConfigDialog` | 34 | local |
| `cancelConfigDialog` | 39 | local |
| `onMount` callback | 43-76 | svelte |
| `handleSplashFinished` | 78 | local |
| `handleCrashRestart` | 82 | local |

## `src/lib/types.ts`

| 成员 | 行 | 可见性 |
|------|----|----|
| `interface DumperConfig` | 1 | export |
| `interface BinaryInfo` | 45 | export |
| `interface DumpCompleteEvent` | 50 | export |
| `interface InputRequestEvent` | 55 | export |
| `type AppState` | 60 | export |
| `DEFAULT_CONFIG` | 62 | export |

## `src/lib/stores.ts`

| 成员 | 行 | 可见性 |
|------|----|----|
| `type ScreenState` | 7 | export |
| `interface PersistedPrefs` | 11 | (private) |
| `function loadPrefs` | 18 | private |
| `function defaultPrefs` | 34 | private |
| `function savePrefs` | 43 | private |
| `themeMode` writable | 52 | export |
| `language` writable | 53 | export |
| `config` writable | 54 | export |
| `configDialogOpen` writable | 55 | export |
| `outputDir` writable | 56 | export |
| `t` derived | 63 | export |
| `defaultOutputDir` writable | 65 | export |
| `currentScreen` writable | 66 | export |
| `crashLog` writable | 67 | export |
| `appState` writable | 68 | export |
| `logs` writable | 69 | export |
| `binaryPath` writable | 70 | export |
| `metadataPath` writable | 71 | export |
| `binaryInfo` writable | 72 | export |
| `outputPath` writable | 73 | export |
| `errorMessage` writable | 74 | export |
| `inputRequest` writable | 75 | export |
| `elapsedSeconds` writable | 76 | export |
| `function resetAll` | 78 | export |
| `function resetForNewDump` | 93 | export |
| `function applyTheme` | 104 | export |

## `src/lib/dumpRunner.ts`

| 成员 | 行 | 可见性 |
|------|----|----|
| `function beginDump` | 18 | export |

## `src/lib/dumpEvents.ts`

| 成员 | 行 | 可见性 |
|------|----|----|
| `unlisteners` | 14 | private |
| `setupPromise` | 15 | private |
| `function registerDumpEvents` | 17 | private |
| `function setupDumpEvents` | 49 | export |
| `function teardownDumpEvents` | 59 | export |

## `src/lib/components/*.svelte` (13 个)

每个组件均为 Svelte 5 组件 default export，无独立命名 export。具体 props / events 见 `08_functions_detail/frontend.md`。