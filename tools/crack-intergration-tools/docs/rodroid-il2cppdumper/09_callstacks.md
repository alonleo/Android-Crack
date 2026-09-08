# 09 — 关键调用栈汇总

---

## 栈 1 — `start_dump` 总入口

```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend (dumpRunner)
    participant Tauri
    participant CM as start_dump
    participant Thread as std::thread
    participant RD as run_dump
    participant Meta as Metadata
    participant Fmt as init_<format>
    participant Dec as Il2CppDecompiler
    participant SG as StructGenerator
    participant DG as generate_dummy_dlls
    participant Gen as dump_generics
    participant SF as StaticFieldExporter
    participant ES as embedded_scripts::write_scripts
    participant Events as emit_log / emit events

    FE->>Tauri: invoke('start_dump', { binaryPath, metadataPath, outputDir, configJson })
    Tauri->>CM: start_dump
    CM->>CM: state.dump_running lock
    CM->>Thread: spawn(AssertUnwindSafe(run_dump))
    CM-->>Tauri: Ok(())
    Tauri-->>FE: void

    Thread->>RD: run_dump
    RD->>Events: emit_log("Initializing IL2CPP binary...")
    RD->>RD: fs::read(binary_path)
    RD->>Events: emit_log("Unity Version: ...")
    RD->>RD: fs::read(metadata_path)

    RD->>RD: try_decrypt_metadata
    opt decrypted
        RD->>Events: emit_log("Encrypted metadata detected ...")
    end

    RD->>Meta: new_with_options
    RD->>Events: emit_log("Metadata Version: ...")
    RD->>Fmt: detect_format -> init_elf/pe/macho/fat/nso/wasm
    Fmt->>Events: emit_log("Detected ELF64 format")
    Fmt->>Fmt: parse header + segments
    Fmt->>Fmt: set_properties(version, muCount)
    opt check_dump or force_dump
        Fmt->>Events: emit_log("Detected this may be a dump file.")
        Fmt->>RD: prompt_dump_address
        RD->>Events: emit("dump-input-request", "dump_address")
        Note over RD: rx.recv() 阻塞
    end
    Fmt->>Fmt: symbol_search -> SectionHelper -> search_arm32/search_mod_init_func
    opt all failed
        Fmt->>RD: prompt_manual_addresses
        RD->>Events: emit("dump-input-request", "manual_addresses")
    end
    Fmt->>Fmt: Il2Cpp::init(cr, mr)
    Fmt->>Events: emit_log("Found N exported symbols, M IL2CPP APIs")
    Fmt-->>RD: Il2Cpp instance

    opt version >= 27 && is_dumped
        RD->>RD: il2cpp.image_base = type_handle - header.type_definitions_offset
    end

    RD->>Events: emit_log("Dumping...")
    RD->>Dec: decompile(executor, metadata, il2cpp, config, outputDir, log)
    Dec->>Events: emit_log("dump.cs generated")

    opt dumpStaticFieldMetadata
        RD->>SF: StaticFieldCatalog::collect + write_document
        RD->>Events: emit_log("static_metadata.json generated ...")
    end

    opt generateStruct
        RD->>SG: write_all
        RD->>ES: write_scripts
        RD->>Events: emit_log("script.json, il2cpp.h, stringliteral.json generated")
    end

    opt generateDummyDll
        RD->>DG: generate_dummy_dlls
        RD->>Events: emit_log("Dummy dll files generated")
    end

    opt generateGenericsDump
        RD->>Gen: dump_generics
        RD->>Events: emit_log("generics_dump.txt generated")
    end

    RD->>Events: emit_log("Done! (X.XXs)")
    RD-->>Thread: Ok(output_path)

    Thread->>Events: emit("dump-complete", { success: true, output_path })
    alt error
        Thread->>Events: emit("dump-complete", { success: false, error_message })
    else panic
        Thread->>Events: emit("dump-crash", { crash_log })
    end
```

---

## 栈 2 — `try_decrypt_metadata` 7 种方案依序尝试

```mermaid
flowchart TD
    Start([try_decrypt_metadata data]) --> Length{data.len() >= 16?}
    Length -->|否| None[return None]
    Length -->|是| K1["k1 = magic[0] ^ data[0]<br/>if k1 != 0 and (1..4).all(magic[i]^data[i] == k1):<br/>test = data.clone() ^ k1<br/>if is_valid_metadata_version(test): return scheme"]
    K1 -->|None| K4["key4 = magic XOR data[0..4]<br/>test ^= key4[i%4]<br/>if version ok: return scheme"]
    K4 -->|None| K8["key8 = magic XOR data[0..4] ++ data[4..8]<br/>test ^= key8[i%8]"]
    K8 -->|None| Rolling["key_len in 16/32/64/128/256<br/>key[i] = (magic XOR data)[i%4] ++ data[i%4..]<br/>test = data XOR key rolling"]
    Rolling -->|None| Pos["test ^= key4[i%4] ^ (i as u8)<br/>position-dependent XOR"]
    Pos -->|None| Masked["test ^= key4[i%4] ^ ((i & 0xFF) as u8)<br/>masked position XOR"]
    Masked -->|None| Header["for first 256 bytes:<br/>test[i] ^= key4[i%4]<br/>header-only XOR"]
    Header -->|None| Done[return None]
    Header -->|成功| Done
```

---

## 栈 3 — `Il2Cpp::init` 内部

```mermaid
sequenceDiagram
    autonumber
    participant I as Il2Cpp::init
    participant S as self.stream
    participant F as map_vatr closure
    participant Meta as Il2CppMetadataRegistration
    participant Arr as pointer array

    I->>I: code_registration / metadata_registration 缓存
    I->>S: set_position(map_vatr(metadata_registration))
    I->>Meta: Il2CppMetadataRegistration::read(stream, version)
    I->>S: set_position(map_vatr(mr.types))
    I->>S: read_ptr_array_inline(mr.types_count)

    I->>I: types.clear() / type_dic.clear()
    Note over I: tolerant = codm && is_dumped
    loop type_ptrs
        I->>F: map_vatr(ptr)
        alt Ok
            I->>Meta: Il2CppType::read
            I->>I: types.push + type_dic.insert
        else Err && tolerant
            I->>I: types.push(default) + skipped += 1
        end
    end

    I->>I: load method_pointers / generic_method_pointers / invoker_pointers / custom_attribute_generators / reverse_pinvoke_wrappers / unresolved_virtual_call_pointers

    opt version >= 22
        I->>S: read_ptr_array(generic_insts, count)
        I->>I: generic_insts = read_generic_inst for each
    end

    I->>I: field_offsets_are_pointers = version > 21
    opt version == 21
        I->>S: read 6 u32 -> heuristic
    end
    I->>S: read field_offsets

    opt version >= 24.2
        I->>I: load_code_gen_modules
        I->>I: build_method_spec_lookup
    end

    opt version < 24.2
        I->>S: read method_pointers
    end
```

`il2cpp/base.rs:162` 入口。

---

## 栈 4 — `Il2CppDecompiler::decompile` 内部（简化）

```mermaid
sequenceDiagram
    autonumber
    participant D as decompile
    participant E as executor
    participant M as metadata
    participant I as il2cpp
    participant FW as dump.cs writer
    participant FS as DiffableCs/ writer (opt)
    participant CAD as CustomAttributeDataReader

    opt splitDumpPerType
        D->>FS: mkdir DiffableCs/
    end

    loop imageDef
        D->>M: get_string_from_index(imageDef.nameIndex)
        loop typeDef
            opt dumpField
                loop fieldDef
                    D->>E: try_get_default_value
                    D->>I: get_field_offset_from_index
                end
            end
            opt dumpMethod
                loop methodDef
                    opt dumpMethodOffset
                        D->>I: get_method_pointer(image, methodDef)
                        D->>I: get_rva(pointer)
                    end
                    D->>E: get_modifiers(flags)
                    opt dumpDisassembly
                        D->>Dis: format_method_body(bytes, base, max)
                    end
                end
            end
            opt dumpAttribute
                D->>CAD: get_string_custom_attribute_data(metadata)
            end
            opt splitDumpPerType
                D->>FS: DiffableCs/<Type>.cs
            end
        end
    end
```

---

## 栈 5 — V5 Disassembler 流程

```mermaid
sequenceDiagram
    autonumber
    participant D as Decompiler
    participant DIS as Disassembler
    participant ARM as arm::disassemble_*
    participant X86 as x86::disassemble_x86
    participant YX as yaxpeax-arm
    participant IC as iced-x86

    D->>DIS: new(arch)
    D->>DIS: add_*_helper_rva / add_*_literal / set_method_names
    loop 每个 method
        D->>DIS: format_method_body(bytes, base, max)
        alt arch = ARM64 / ARM32
            DIS->>ARM: disassemble_arm64/32(bytes, base, max)
            ARM->>YX: decode(inst)
            YX-->>ARM: instruction stream
            ARM-->>DIS: Vec<DisassembledInstruction>
        else arch = X86 / X64
            DIS->>X86: disassemble_x86(bytes, base, max, is_64bit)
            X86->>IC: decode(inst)
            IC-->>X86: instruction stream
            X86-->>DIS: Vec<DisassembledInstruction>
        end
        DIS->>DIS: annotate (boxing/unboxing/string literal/method/field/type info/static field)
        DIS->>DIS: build CFG + switch table
        DIS-->>D: String
    end
```

---

## 栈 6 — Tauri 事件协议

```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend (Svelte)
    participant DE as dumpEvents.ts
    participant TA as @tauri-apps/api/event
    participant AppState as AppState (Rust)
    participant Thread as dump thread

    FE->>DE: setupDumpEvents()
    DE->>TA: listen("dump-log", handler)
    DE->>TA: listen("dump-complete", handler)
    DE->>TA: listen("dump-input-request", handler)
    DE->>TA: listen("dump-crash", handler)

    FE->>TA: invoke("start_dump", ...)
    TA->>Thread: spawn
    Thread->>AppState: input_sender.send(response) [after prompt]
    Thread->>TA: emit("dump-log", ...)
    TA-->>FE: dump-log event
    FE->>FE: logs.update(arr => [...arr, message])

    opt 成功
        Thread->>TA: emit("dump-complete", { success: true, output_path })
        TA-->>FE: dump-complete event
        FE->>FE: currentScreen.set("result")
    end
```

---

## 栈 7 — C++ Header Scaffolding 拓扑排序

```mermaid
flowchart TD
    Start([CppScaffolding::build]) --> Coll[收集所有 typeDef -> CppTypeDecl]
    Coll --> Group["CppTypeGroupRegistry::assign<br/>UnityApi / UnityTypes / UnityStructs / UnityEnums / GameClasses / ForwardDeclarations"]
    Group --> Dep["cpp_type_dependency_graph<br/>build DAG from field refs + parent + interfaces"]
    Dep --> Topo["topological_sort<br/>promote types when needed"]
    Topo --> Emit["CppHeaderEmitter::emit_all_with_groups<br/>按 group 顺序 + topological order"]
    Emit --> Write[写 cpp_scaffold/*.hpp]
    Write --> OptProject{write_project?}
    OptProject -->|是| Proj[写 CMakeLists.txt / project.txt]
    OptProject -->|否| End
    Proj --> End
```

---

## 栈 8 — Panic Capture

```mermaid
sequenceDiagram
    autonumber
    participant T as start_dump
    participant CU as catch_unwind
    participant RD as run_dump
    participant Crash as CrashEvent

    T->>CU: AssertUnwindSafe(run_dump)
    alt normal
        CU->>RD: run_dump
        RD-->>CU: Ok(output_path) | Err(msg)
    else panic
        Note over CU: panic!
        CU-->>T: Err(panic_info)
    end

    alt success
        T->>Crash: emit("dump-complete", { success: true })
    else error
        T->>Crash: emit("dump-complete", { success: false })
    else panic
        T->>T: format crash_log (time / OS / ARCH / panic msg)
        T->>Crash: emit("dump-crash", { crash_log })
    end
```