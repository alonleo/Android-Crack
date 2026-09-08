# 02 目录结构

## 完整目录树

```
rodroid-il2cppdumper/
├── package.json, package-lock.json, components.json
├── README.md, LICENSE
├── svelte.config.js, vite.config.js, tsconfig.json
│
├── src/                              SvelteKit 前端
│   ├── app.html, app.css
│   ├── routes/
│   │   ├── +page.svelte              (160) 屏幕路由（splash/idle/dumping/result/error/settings/about/crash）
│   │   ├── +layout.svelte, +layout.ts
│   └── lib/
│       ├── components/               13 Svelte 组件
│       │   ├── IdleScreen.svelte
│       │   ├── DumpingScreen.svelte
│       │   ├── ResultScreen.svelte
│       │   ├── ErrorScreen.svelte
│       │   ├── SettingsScreen.svelte
│       │   ├── AboutScreen.svelte
│       │   ├── SplashScreen.svelte
│       │   ├── CrashScreen.svelte
│       │   ├── InputDialog.svelte
│       │   ├── ConfigDialog.svelte
│       │   ├── ConfigSwitch.svelte
│       │   ├── PathInput.svelte
│       │   └── AnimatedExpand.svelte
│       ├── stores.ts                 Svelte stores
│       ├── types.ts                  DumperConfig TS interface + DEFAULT_CONFIG
│       ├── dumpRunner.ts             beginDump() -> invoke('start_dump', ...)
│       ├── dumpEvents.ts             Tauri 事件监听（dump-log, dump-complete, ...）
│       ├── dumpLogs.ts
│       ├── dumpState.ts
│       ├── i18n.ts                   (370) 7 语言翻译
│       └── utils.ts
│
├── static/                           Lottie 动画 + 图标
│   ├── android_logo.json, error.json, like.json, success.json, Rocket Launch.json
│
└── src-tauri/                        Rust 后端
    ├── Cargo.toml, Cargo.lock
    ├── build.rs
    ├── tauri.conf.json
    ├── config.json                   默认 dump 配置
    ├── assets/, icons/, gen/
    ├── scripts/Il2CppBinaryNinja/plugin.json
    ├── capabilities/default.json     Tauri 权限
    ├── dotnetdll-main/               Git submodule（dotnetdll Rust crate）
    └── src/
        ├── main.rs                   (6)  trampoline -> lib::run()
        ├── lib.rs                    (1317) Tauri 命令 + 6 格式 init + run_dump + 元数据解密 + panic capture
        ├── config.rs                 (111) Serde Config (40+ flags)
        ├── error.rs                  (28) Error enum + Result 别名
        │
        ├── io/
        │   ├── mod.rs
        │   ├── binary_stream.rs      BinaryStream
        │   └── version_aware.rs      VersionAwareStream
        │
        ├── formats/                  可执行格式
        │   ├── mod.rs
        │   ├── elf.rs                (1576) ELF32/64 + CODM new_with_codm_diag
        │   ├── macho.rs              (1093) Mach-O + Fat + CODM new_with_codm_fixups
        │   ├── pe.rs                 (369) PE
        │   ├── nso.rs                (467) NSO
        │   └── wasm.rs               (274) WASM
        │
        ├── il2cpp/
        │   ├── mod.rs
        │   ├── base.rs               (707) Il2Cpp struct + VaSegment + Init + get_method_pointer + get_field_offset + get_rva + map_vatr + read_generic_class
        │   ├── metadata.rs           (843) Metadata + MetadataVariant (Standard/Codm) + load_metadata / load_metadata_codm + get_string_from_index + get_custom_attribute_index
        │   ├── enums.rs              (287) Il2CppTypeEnum + Il2CppRGCTXDataType + Il2CppMetadataUsage
        │   ├── structures.rs         (2222) POD (UnityVersion + Il2CppCodeGenModule + Il2CppImageDefinition + ...)
        │   ├── field_layout.rs       (235) StaticFieldKind + DecodedFieldOffset + FieldLayoutInfo + decode_field_offset + analyze_field_layout
        │   │
        │
        ├── search/
        │   ├── mod.rs
        │   └── section_helper.rs     (608) SectionHelper + find_code_registration + find_metadata_registration + find_metadata_registration_v21 + find_metadata_registration_codm + find_refs_fast
        │
        ├── executor/
        │   ├── mod.rs
        │   ├── il2cpp_executor.rs    (693) Il2CppExecutor + get_type_name + get_type_def_name + get_method_spec_name + try_get_default_value + get_modifiers + caches
        │   └── custom_attribute_reader.rs (350) CustomAttributeDataReader + format_custom_attribute_data
        │
        ├── output/                   所有"写出"逻辑
        │   ├── mod.rs
        │   ├── decompiler.rs         (1329) Il2CppDecompiler::decompile -> dump.cs + DiffableCs/*.cs
        │   ├── struct_generator.rs    (2140) StructGenerator::write_all -> il2cpp.h + script.json + stringliteral.json + DiffableCs split
        │   ├── dummy_assembly_generator.rs (1386) generate_dummy_dlls (vendored dotnetdll)
        │   ├── generics.rs           (905) dump_generics -> generics_dump.txt
        │   ├── cpp_scaffolding.rs    (1064) CppScaffolding::build + write_project
        │   ├── cpp_ast.rs            (520) CppHeaderEmitter + CppField + CppVTableEntry + CppRGCTXEntry + CppTypeDecl
        │   ├── cpp_type_model.rs     (256) CppType enum + CppTypeGroup + CppTypeGroupRegistry
        │   ├── cpp_type_dependency_graph.rs (362) 拓扑排序依赖图
        │   ├── name_mangler.rs       (501) MSVC/GCC/Itanium-style C++ name mangling
        │   ├── header_manager.rs     (204) UnityHeaders + UnityResource + guess_headers_for_binary
        │   ├── header_constants.rs   (704) generic_header + header_v29/27/242/241/240/22
        │   ├── static_field_exporter.rs (473) StaticFieldCatalog + StaticFieldExporter + write_document
        │   ├── embedded_scripts.rs    (35) write_scripts (IDA/Ghidra scripts)
        │   ├── script_json.rs        (107) ScriptJson + ScriptMethod + ScriptString + ...
        │   ├── unity_version.rs      (195) UnityVersion + UnityVersionRange + BuildType
        │   └── name_mangler.rs       MangledNameBuilder (MSVC)
        │
        ├── disassembler/             V5 disassembler
        │   ├── mod.rs                (2063) Architecture enum + Disassembler + DisassemblyContext + CfgAnalysis + analyze_propagation + SwitchAnnotation
        │   ├── arm.rs                (987) disassemble_arm64 + disassemble_arm32 (基于 yaxpeax-arm)
        │   └── x86.rs                (545) disassemble_x86 + normalize_x86_reg (基于 iced-x86)
        │
        └── utils/
            ├── mod.rs
            ├── pattern_search.rs     find_bytes
            └── string_utils.rs       sanitize_path_component + sanitize_cpp_identifier + escape_string
```

## 模块注释

| 目录 | 责任 |
|------|------|
| `src/` (SvelteKit) | 前端：屏幕路由、组件、Tauri 命令调用、事件订阅 |
| `src-tauri/src/` | Rust 后端：所有 dump 逻辑 |
| `src-tauri/src/io/` | `BinaryStream`（按 il2cpp 版本决定字段大小）+ `VersionAwareStream` |
| `src-tauri/src/formats/` | ELF / PE / Mach-O / NSO / WASM 的 native 格式解析器（替代 C# 版的 ExecutableFormats） |
| `src-tauri/src/il2cpp/` | Il2Cpp 运行时视图 + metadata POD |
| `src-tauri/src/search/` | `SectionHelper` —— 自动搜索 CodeRegistration / MetadataRegistration |
| `src-tauri/src/executor/` | 名称解析（Il2CppExecutor）+ v29+ attribute blob 解析（CustomAttributeDataReader） |
| `src-tauri/src/output/` | 所有"写出"层 |
| `src-tauri/src/disassembler/` | 内嵌反汇编器 + 注解引擎 |
| `src-tauri/src/utils/` | 通用 helper |
| `dotnetdll-main/` | Rust 写的 .NET assembly 生成库（vendored submodule） |