# 04 核心数据流

## 关键数据结构

### `Il2Cpp` (`il2cpp/base.rs:15`)

| 字段 | 类型 | 说明 |
|------|------|------|
| `stream` | `BinaryStream` | 整个 il2cpp 二进制的字节视图 |
| `version` | `f64` | il2cpp 版本（v16~v39 + CODM） |
| `is_32bit` | `bool` | |
| `va_segments` | `Vec<VaSegment>` | VA 段表（替代 C# 版的 sections） |
| `data_sections` | `Vec<SearchSection>` | 用于 metadata usage 搜索 |
| `types` | `Vec<Il2CppType>` | 所有 Il2CppType |
| `method_pointers` | `Vec<u64>` | 当前 image 的所有 method 指针 |
| `generic_method_pointers` | `Vec<u64>` | |
| `invoker_pointers` | `Vec<u64>` | |
| `custom_attribute_generators` | `Vec<u64>` | |
| `reverse_pinvoke_wrappers` | `Vec<u64>` | |
| `unresolved_virtual_call_pointers` | `Vec<u64>` | |
| `generic_insts` | `Vec<Il2CppGenericInst>` | |
| `generic_inst_pointers` | `Vec<u64>` | |
| `method_specs` | `Vec<Il2CppMethodSpec>` | |
| `field_offsets` | `Vec<u64>` | |
| `code_gen_modules` | `HashMap<String, Il2CppCodeGenModule>` | v24.2+ |
| `rgctxs_dictionary` | `HashMap<String, HashMap<u32, Vec<Il2CppRGCTXDefinition>>>` | v24.2+ |
| `method_spec_generic_method_pointers` | `HashMap<...>` | |
| `image_base` | `u64` | dump 模式用的反推 image base |
| `is_pe` | `bool` | 是否 PE |
| `codm` | `bool` | CODM 模式开关 |
| `arch` | `Option<Architecture>` | 决定 disassembler 后端 |
| `exported_symbols` | `Vec<String>` | |
| `api_export_rvas` | `HashMap<String, u64>` | il2cpp_*/mono_* 导出 |
| `e_machine` | `u16` | ELF machine code |
| `data_search_sections` | `Vec<SearchSection>` | |
| `is_dumped` | `bool` | |
| `type_definition_sizes` | `Vec<u32>` | |

### `Metadata` (`il2cpp/metadata.rs:66`)

| 字段 | 说明 |
|------|------|
| `data: Vec<u8>` | 整文件 |
| `version: f64` | il2cpp 版本 |
| `variant: MetadataVariant` | Standard / Codm |
| `header: Il2CppGlobalMetadataHeader` | |
| `image_defs / assembly_defs / type_defs / method_defs / parameter_defs / field_defs / property_defs / event_defs / generic_containers / generic_parameters / string_literals / field_refs` | |
| `attribute_type_ranges` | v21~v28 |
| `attribute_data_ranges` | v29+ |
| `attribute_types` | v21~v28 |
| `metadata_usage_dic` | v19~v26 |
| `metadata_usages_count` | |
| `interface_indices / nested_type_indices / constraint_indices / vtable_methods` | |
| `rgctx_entries` | v<=24.1 |
| `unity_version` | 自动从 binary 探测 |
| `version_aware` | 缓存 |
| `attribute_lookup` | token → range index |

### `Config` (`config.rs:5`)

40+ 字段，serde，JSON 序列化 camelCase。

关键字段（详见 `07_functions_index.md` / `08_functions_detail/core.md`）：
- dumpMethod / Field / Property / Attribute / MethodOffset / FieldOffset / TypeDefIndex / AssemblyName
- generateStruct / generateDummyDll / requireAnyKey / dummyDllAddToken
- forceIl2cppVersion / forceVersion / forceDump / noRedirectedPointer
- splitDumpPerType
- generateGenericsDump / dumpGenerics{Rgctx,MethodSpecs,...}
- dumpDisassembly / dumpDisassemblyTarget / dumpDisassemblyHexBytes / dumpDisassemblyFieldNames / dumpDisassemblyAnnotations / dumpDisassemblyCfg / maxDisassemblyInstructions
- generateCppScaffold / mangleNames / enhancedIdaMetadata / generateUnityHeaders / compilerLayout / useTopologicalSort
- codm
- dumpStaticFieldMetadata / dumpFieldRvaData / maxFieldRvaDumpBytes

### `Il2CppType` 等 POD（`il2cpp/structures.rs`）

完整 Rust port，包括 `UnityVersion` + `BuildType`、所有 il2cpp 元数据 POD。

## 数据生命周期

```mermaid
flowchart TD
    A["<b>磁盘</b><br/>il2cpp binary<br/>global-metadata.dat"] -->|fs::read| B1[Vec<u8> il2cppBytes]
    A -->|fs::read| B2[Vec<u8> metadataBytes]
    B2 --> C1{"magic == 0xFAB11BAF?"}
    C1 -->|否| D1[try_decrypt_metadata]
    D1 --> C1
    C1 -->|是| E1["Metadata::new_with_options<br/>(data, unity_version_str, codm)"]
    E1 --> F1[detect_variant Standard/Codm<br/>load_metadata or load_metadata_codm]

    B1 --> C2[detect_unity_version]
    C2 -->|optional| E1
    B1 --> C3["detect_format<br/>(ELF/PE/Mach-O/Fat/NSO/WASM)"]
    C3 --> D2[init_<format>]

    D2 --> D2a["format::new<br/>(parse header, sections, ...)"]
    D2a --> D2b[set version + muCount]
    D2b --> D2c{forceDump or check_dump?}
    D2c -->|是| D2d[prompt dump address via Tauri]
    D2c -->|否| D2e
    D2d --> D2e

    D2e --> D2f{symbol_search?}
    D2f -->|是| D2g[Init cr, mr]
    D2f -->|否| D2h{section_helper find}
    D2h --> D2g
    D2h -.失败.-> D2i[search_arm32 / search_mod_init_func]
    D2i -.失败.-> D2j[prompt manual addresses]
    D2j --> D2g

    D2g --> E2[Il2Cpp struct with all tables]
    F1 --> E2
    E2 --> F2[Il2CppExecutor::new]
    F2 --> G1[Il2CppDecompiler::decompile -> dump.cs]
    F2 --> G2[StructGenerator::write_all -> il2cpp.h + script.json + stringliteral.json]
    F2 --> G3[generate_dummy_dlls -> DummyDll/]
    F2 --> G4["dump_generics -> generics_dump.txt"]
    F2 --> G5["StaticFieldCatalog::collect + StaticFieldExporter::write_document -> static_metadata.json"]
    G1 --> H[emit dump-complete]
    G2 --> H
    G3 --> H
    G4 --> H
    G5 --> H
```

## 关键映射

- **RVA → FileOffset**：`Il2Cpp::map_vatr(addr)` (`base.rs:582`) 按 `va_segments` 线性扫描。
- **FileOffset → RVA**：`Il2Cpp::map_rtva(offset)` (`base.rs:591`)。
- **methodIndex → methodPointer**：`Il2Cpp::get_method_pointer(image, methodDef)` (`base.rs:492`)。
- **fieldIndex → fieldOffset**：`Il2Cpp::get_field_offset_from_index(...)` (`base.rs:547`)。
- **typeHandle → TypeDef**：在 IsDumped + v>=27 下用 `type_handle - metadata.image_base - metadata.header.type_definitions_offset` / sizeOf(TypeDef)。

## Tauri 事件协议

```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend
    participant Tauri as Tauri Shell
    participant BE as Backend
    participant Thread as dump thread

    FE->>Tauri: invoke('start_dump', { binaryPath, metadataPath, outputDir, configJson })
    Tauri->>BE: start_dump
    BE->>Thread: thread::spawn(run_dump)
    BE-->>Tauri: Ok(())
    Tauri-->>FE: {}

    loop dump 阶段
        Thread->>Tauri: emit('dump-log', { message })
        Tauri-->>FE: dump-log event
    end

    opt 需要用户输入
        Thread->>Tauri: emit('dump-input-request', { prompt_type })
        Tauri-->>FE: dump-input-request event
        FE->>FE: 显示 InputDialog
        FE->>Tauri: invoke('submit_input', { response })
        Tauri->>Thread: state.input_sender.send(response)
        Note over Thread: rx.recv() 返回，dump 继续
    end

    alt 成功
        Thread->>Tauri: emit('dump-complete', { success: true, output_path })
    else 错误
        Thread->>Tauri: emit('dump-complete', { success: false, error_message })
    else panic
        Thread->>Tauri: emit('dump-crash', { crash_log })
    end

    Tauri-->>FE: dump-complete / dump-crash event
    FE->>FE: 切到 ResultScreen / CrashScreen
```