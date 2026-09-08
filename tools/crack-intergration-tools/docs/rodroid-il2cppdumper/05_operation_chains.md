# 05 操作链

下面用 mermaid 图描述 8 条主操作链。

---

## 链 1 — 启动 / GUI Dump 入口（Tauri command start_dump）

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant IDLE as IdleScreen.svelte
    participant DR as dumpRunner.ts
    participant Tauri as Tauri Shell
    participant CM as start_dump (lib.rs:1192)
    participant TH as std::thread::spawn
    participant RD as run_dump (lib.rs:1009)
    participant DE as dumpEvents.ts
    participant RES as ResultScreen.svelte

    U->>IDLE: 点击 "Start"
    IDLE->>DR: beginDump(binaryPath, metadataPath, outputDir, configJson)
    DR->>Tauri: invoke('start_dump', { ... })
    Tauri->>CM: start_dump
    CM->>CM: state.dump_running 锁检查
    CM->>TH: thread::spawn(run_dump)
    CM-->>Tauri: Ok(())
    Tauri-->>DR: void

    TH->>RD: run_dump
    RD-->>TH: result: Result<String, String>

    TH->>Tauri: emit('dump-log', "Initializing...")
    Tauri-->>DE: dump-log event
    DE->>DE: stores.append(log)
    loop 多个 log
        TH->>Tauri: emit('dump-log', "Searching...")
        Tauri-->>DE: dump-log event
    end

    alt 成功
        TH->>Tauri: emit('dump-complete', { success: true, output_path })
        Tauri-->>DE: dump-complete event
        DE->>RES: stores.currentScreen = 'result'
    else 错误
        TH->>Tauri: emit('dump-complete', { success: false, error_message })
        Tauri-->>DE: dump-complete event
        DE->>RES: stores.currentScreen = 'error'
    else panic
        TH->>Tauri: emit('dump-crash', { crash_log })
        Tauri-->>DE: dump-crash event
        DE->>RES: stores.currentScreen = 'crash'
    end
```

---

## 链 2 — 二进制 + Metadata 格式探测 + XOR 解密

```mermaid
flowchart TD
    Start([run_dump 开始]) --> ReadBin[fs::read binary_path]
    ReadBin --> UnityVer[detect_unity_version<br/>扫描 '2xxx.x' / '6xxx.x' 字符串]
    ReadBin --> ReadMeta[fs::read metadata_path]
    ReadMeta --> Magic{"magic == 0xFAB11BAF?"}
    Magic -->|是| MetaCtor[Metadata::new_with_options]
    Magic -->|否| Decrypt["try_decrypt_metadata<br/>依次尝试 7 种 XOR 方案"]

    Decrypt -->|None| FailErr[返回错误]
    Decrypt -->|Some scheme| LogDec[emit log 'Encrypted metadata detected (...)']
    LogDec --> MetaCtor

    MetaCtor --> DetectVariant["detect_codm_variant<br/>heuristic 启发式判断"]
    DetectVariant --> LoadMeta{Standard?}
    LoadMeta -->|是| StdLoad[load_metadata<br/>解析所有 Defs]
    LoadMeta -->|否| CodmLoad[load_metadata_codm<br/>用 read_metadata_array_codm]

    ReadBin --> DetFmt[detect_format<br/>按 magic 分类]
    DetFmt -->|ELF| InitElf
    DetFmt -->|PE| InitPe
    DetFmt -->|Mach-O| InitMacho
    DetFmt -->|Fat Mach-O| InitMachoFat
    DetFmt -->|NSO| InitNso
    DetFmt -->|WASM| InitWasm

    StdLoad --> InitX
    CodmLoad --> InitX[统一调度]
```

---

## 链 3 — PE / ELF / Mach-O / NSO / WASM 分支 init

```mermaid
flowchart TD
    Init([init_<format>]) --> Ctor["format::new / new_with_codm_diag / new_with_codm_fixups<br/>解析 header + sections + symbols + relocations"]
    Ctor --> Ver["设置 stream.version"]
    Ver --> Dump{"force_dump or check_dump?"}
    Dump -->|是| Prompt[request_input dump_address<br/>emit dump-input-request]
    Prompt --> SetDump[image_base = addr; is_dumped = true]
    Dump -->|否| Search

    SetDump --> Search{开始搜索}

    Search --> Sym{symbol_search?}
    Sym -->|是| Init[il2cpp.init cr, mr]
    Sym -->|否| Helper{section_helper.find}
    Helper -->|找到| Init
    Helper -.失败.-> ModInit[search_arm32 / search_mod_init_func]
    ModInit -.失败.-> Manual[request_input manual_addresses]
    Manual --> Init

    Init --> BuildIl2cpp["Build Il2Cpp struct<br/>+ va_segments + api_export_rvas"]
    BuildIl2cpp --> Done([return Il2Cpp])
```

各分支差异：

| 格式 | symbol_search | search_arm32 | search_mod_init_func | codm 路径 |
|------|---------------|--------------|----------------------|-----------|
| ELF | `Elf::symbol_search` (`elf.rs:859`) | `Elf::search_arm32` (`elf.rs:1497`) | – | `Elf::new_with_codm_diag` (`elf.rs:204`) |
| PE | `Pe::symbol_search` (`pe.rs:213`) | – | – | – |
| Mach-O | `MachO::symbol_search` (`macho.rs:451`) | – | `MachO::search_mod_init_func` (`macho.rs:483`) | `MachO::new_with_codm_fixups` (`macho.rs:156`) |
| NSO | – | – | – | – |
| WASM | – | – | – | – |

---

## 链 4 — `dump.cs` + DiffableCs 写出

```mermaid
sequenceDiagram
    autonumber
    participant RD as run_dump
    participant Dec as Il2CppDecompiler::decompile
    participant Exe as Il2CppExecutor
    participant Meta as Metadata
    participant I as Il2Cpp
    participant FW as StreamWriter (dump.cs)
    participant DIS as Disassembler
    participant FS as FileSystem

    RD->>Dec: decompile(executor, metadata, il2cpp, config, outputDir, log)
    opt splitDumpPerType
        Dec->>FS: 创建 DiffableCs/
    end
    Dec->>FW: new StreamWriter(dump.cs)
    loop imageIndex
        Dec->>Meta: get_string_from_index(imageDef.nameIndex)
        Dec->>FW: Write("// Image N: name")
    end
    loop imageDef
        Dec->>Exe: get_type_name(parent)
        Dec->>FW: Write(namespace + class header)
        opt dumpField
            loop field
                Dec->>Exe: try_get_default_value
                Dec->>I: get_field_offset_from_index
                Dec->>FW: Write(field with offset)
            end
        end
        opt dumpMethod
            loop method
                opt dumpMethodOffset
                    Dec->>I: get_method_pointer(image, methodDef)
                    Dec->>I: get_rva(pointer)
                    Dec->>FW: Write("// RVA: 0xN Offset: 0xN VA: 0xN")
                end
                Dec->>Exe: get_modifiers
                Dec->>FW: Write(signature)
                opt dumpDisassembly
                    Dec->>DIS: add_method_names(map)
                    Dec->>DIS: disassemble(methodBody, base, max)
                    Dec->>FW: Write("/* disasm */")
                end
            end
        end
        opt splitDumpPerType
            Dec->>FS: DiffableCs/<TypeName>.cs
        end
    end
    Dec->>FW: Close()
```

`output/decompiler.rs:18 decompile` 入口。

---

## 链 5 — `il2cpp.h` + C++ scaffolding（拓扑排序）

```mermaid
flowchart TD
    Start([StructGenerator::write_all]) --> BuildNames[build_type_def_image_names_pub]
    BuildNames --> BuildDict[build_struct_name_dic_pub]
    BuildDict --> LoopM[遍历 methodDef 构造 ScriptMethod]
    LoopM --> GenSig[generate_method_signature]
    GenSig --> Order[合并 method_pointers + ... 去重排序]
    Order --> Addr[填 Addresses[]]
    Addr --> MU{"Version >= 27?"}
    MU -->|是| Scan[SectionHelper.Data 扫描 metadataUsage]
    MU -->|否| Skip[跳过]
    Scan --> AddMU[AddMetadataUsage*]
    Skip --> AddMU

    AddMU --> StrLit[写 stringliteral.json]
    StrLit --> ScriptJSON[写 script.json]
    ScriptJSON --> HeaderChoice{Version?}
    HeaderChoice -->|22| H22[header_v22]
    HeaderChoice -->|23/24| H240[header_v240]
    HeaderChoice -->|24.1| H241[header_v241]
    HeaderChoice -->|24.2~| H242[header_v242]
    HeaderChoice -->|27| H27[header_v27]
    HeaderChoice -->|29| H29[header_v29]
    H22 --> Emit
    H240 --> Emit
    H241 --> Emit
    H242 --> Emit
    H27 --> Emit
    H29 --> Emit[emit il2cpp.h]

    Emit --> OptCpp{config.generateCppScaffold?}
    OptCpp -->|是| CppBuild["CppScaffolding::build<br/>-> CppTypeGroupRegistry"]
    CppBuild --> DepGraph[cpp_type_dependency_graph<br/>拓扑排序]
    DepGraph --> Emitter["CppHeaderEmitter::emit_all_with_groups<br/>按 CppTypeGroup 分文件输出"]
    Emitter --> WriteCpp[写 .hpp + .h]
    OptCpp -->|否| End
    WriteCpp --> End([结束])
```

`output/struct_generator.rs:72 write_all` 入口。

---

## 链 6 — DummyDll + generics + static_field_exporter

```mermaid
flowchart TD
    Start([run_dump 后期]) --> GenDll{generateDummyDll?}
    GenDll -->|是| Gen["generate_dummy_dlls<br/>(dotnetdll crate)"]
    Gen --> WriteDll[DummyDll/<ImageName>.dll]
    WriteDll --> GenGen
    GenDll -->|否| GenGen{generateGenericsDump?}

    GenGen -->|是| DumpG["dump_generics<br/>7 个子开关:<br/>Rgctx / MethodSpecs / CustomAttributes / StringLiterals / MetadataUsages / Vtables / Interfaces"]
    DumpG --> WriteGen[generics_dump.txt]
    WriteGen --> SF
    GenGen -->|否| SF

    SF{dumpStaticFieldMetadata?}
    SF -->|是| Cat["StaticFieldCatalog::collect<br/>遍历 typeDefs + fields<br/>识别 thread-static + FieldRVA"]
    Cat --> Exp["StaticFieldExporter::write_document"]
    Exp --> WriteSF[static_metadata.json]
    SF -->|否| End
    WriteSF --> End([emit dump-complete])
```

---

## 链 7 — V5 disassembler 引擎（ARM + x86）

```mermaid
sequenceDiagram
    autonumber
    participant D as Decompiler
    participant DIS as Disassembler
    participant ARM as disassemble_arm64/32
    participant X86 as disassemble_x86
    participant YX as yaxpeax-arm
    participant IC as iced-x86

    D->>DIS: new(arch)
    D->>DIS: add_string_new_wrapper_rva(rva)
    D->>DIS: add_box_helper_rva(rva)
    D->>DIS: add_unbox_helper_rva(rva)
    D->>DIS: add_object_new_helper_rva(rva)
    D->>DIS: set_string_literal_table(table)
    D->>DIS: set_method_names(map)
    D->>DIS: add_string_literal(rva, value)
    D->>DIS: add_type_info(rva, name)
    D->>DIS: add_method_ref(rva, name)
    D->>DIS: add_field_ref(rva, name)

    loop 每个 method
        D->>DIS: format_method_body(methodBody, base, max)
        alt arch = ARM
            DIS->>ARM: disassemble_arm64/32
            ARM->>YX: yaxpeax-arm decode
            YX-->>ARM: instruction
            ARM-->>DIS: DisassembledInstruction
        else arch = x86
            DIS->>X86: disassemble_x86
            X86->>IC: iced-x86 decode
            IC-->>X86: instruction
            X86-->>DIS: DisassembledInstruction
        end
        DIS->>DIS: 注解匹配（boxing/unboxing/string literal/method/field/type info/static field）
        DIS->>DIS: format_method_body 输出文本（含 CFG / switch table）
    end
```

`disassembler/mod.rs:333 format_method_body` 入口。

---

## 链 8 — UI 事件流（前端 dumpEvents.ts + Tauri 事件）

```mermaid
flowchart LR
    subgraph Frontend
        S1[SplashScreen]
        S2[IdleScreen]
        S3[DumpingScreen]
        S4[ResultScreen]
        S5[ErrorScreen]
        S6[SettingsScreen]
        S7[AboutScreen]
        S8[CrashScreen]
    end

    User([User 点击]) --> S2
    S2 -->|beginDump| S3
    S3 -->|dump-log| S3
    S3 -->|dump-input-request| Dialog[InputDialog]
    Dialog -->|submit| S3

    S3 -->|dump-complete success| S4
    S3 -->|dump-complete failure| S5
    S3 -->|dump-crash| S8

    S2 -->|齿轮按钮| S6
    S2 -->|? 按钮| S7
    S4 -->|返回| S2

    subgraph stores
        ST[stores.ts<br/>config, currentScreen, logs]
    end

    S3 <-->|append log| ST
    S2 <-->|load config| ST
    S6 <-->|save config| ST
```

```mermaid
sequenceDiagram
    autonumber
    participant DE as dumpEvents.ts
    participant TA as @tauri-apps/api/event
    participant Logs as dumpLogs.ts (svelte store)
    participant State as dumpState.ts
    participant Screens as +page.svelte

    DE->>TA: listen('dump-log', handler)
    DE->>TA: listen('dump-complete', handler)
    DE->>TA: listen('dump-input-request', handler)
    DE->>TA: listen('dump-crash', handler)

    Note over DE,Tauri: 整个 app 生命周期内单次 setup

    TA-->>DE: 事件触发
    DE->>Logs: logs.update(arr => [...arr, message])
    DE->>State: state.inputRequest = { prompt_type }
    DE->>State: state.complete = { success, output_path, error_message }
    DE->>State: state.crash = crash_log
```

`src/lib/dumpEvents.ts` 通过 `setupDumpEvents()` 一次性注册所有监听。