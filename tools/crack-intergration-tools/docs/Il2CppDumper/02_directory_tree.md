# 02 目录结构

## 完整目录树

```
Il2CppDumper/
├── Il2CppDumper.sln
├── README.md, README.zh-CN.md, LICENSE
├── .github/
│   └── ISSUE_TEMPLATE/                       GitHub issue 模板
├── Il2CppDumper/                             唯一 C# 项目
│   ├── Il2CppDumper.csproj
│   ├── Program.cs                            (276 LoC) Main 入口：CLI 解析、Init + Dump
│   ├── Config.cs                             (21 LoC)  JSON-loaded 配置类
│   ├── config.json                           默认配置（复制到 exe 同级）
│   ├── Resource1.Designer.cs / Resource1.resx 嵌入图标 + Il2CppDummyDll.dll 资源
│   │
│   ├── Il2Cpp/                               核心 il2cpp 结构 + 解析
│   │   ├── Il2Cpp.cs                         (348) abstract Il2Cpp 基类
│   │   ├── Metadata.cs                       (300) global-metadata.dat 解析
│   │   ├── Il2CppClass.cs                    (303) P/Invoke 布局 struct（Il2CppCodeRegistration 等）
│   │   └── MetadataClass.cs                  (420) metadata 文件的 POD struct
│   │
│   ├── ExecutableFormats/                    二进制格式解析器
│   │   ├── PE.cs                             (139) PE 解析
│   │   ├── PEClass.cs                        (138) PE 头/节 struct
│   │   ├── Elf.cs                            (394) ELF32 解析
│   │   ├── Elf64.cs                          (337) ELF64 解析
│   │   ├── ElfBase.cs                        (15)  ELF 抽象基类
│   │   ├── ElfClass.cs                       (198) ELF 头/段/符号 struct + 常量
│   │   ├── Macho.cs                          (209) Mach-O 32 位
│   │   ├── Macho64.cs                        (288) Mach-O 64 位（带地址回环修正）
│   │   ├── MachoFat.cs                       (38)  Fat Mach-O 切片选择
│   │   ├── MachoClass.cs                     (27)  Mach-O 段 struct
│   │   ├── NSO.cs                            (336) Nintendo Switch NSO（含 LZ4 解压）
│   │   ├── NSOClass.cs                       (42)  NSO 头/段 struct
│   │   ├── WebAssembly.cs                    (60)  WASM 二进制（data section）
│   │   ├── WebAssemblyMemory.cs              (75)  WASM 内存视图
│   │   └── WebAssemblyClass.cs               (9)   DataSection struct
│   │
│   ├── IO/
│   │   ├── BinaryStream.cs                   (251) 二进制流（带版本感知的 ReadClass）
│   │   └── Lz4DecoderStream.cs               (540) LZ4 流式解码（NSO 用）
│   │
│   ├── Attributes/                           版本感知的 struct 字段属性
│   │   ├── ArrayLengthAttribute.cs           固定长度数组字段
│   │   └── VersionAttribute.cs               il2cpp 版本范围字段
│   │
│   ├── Utils/
│   │   ├── Il2CppExecutor.cs                 (478) 名称解析、默认值、attribute 范围
│   │   ├── DummyAssemblyGenerator.cs         (722) Mono.Cecil 生成空 stub DLL
│   │   ├── SectionHelper.cs                  (427) 跨平台 CR/MR 自动搜索核心
│   │   ├── CustomAttributeDataReader.cs      (168) v29+ attribute blob 解析
│   │   ├── CustomAttributeReaderVisitor.cs   (10)  v29+ 解析结果
│   │   ├── AttributeArgument.cs              (8)   解析单元
│   │   ├── BlobValue.cs                      (9)   通用常量值
│   │   ├── PELoader.cs                       (73)  Windows PE 保护绕过（LoadLibrary + Marshal.Copy）
│   │   ├── ArmUtils.cs                       (46)  ARM MOV/ADR/ADRP/ADD 解码
│   │   ├── SearchSection.cs                  (17)  exec/data/bss 区段描述
│   │   ├── OpenFileDialog.cs                 Win32 OpenFileDialog 包装
│   │   ├── FileDialogNative.cs               IFileDialog COM 接口
│   │   └── MyAssemblyResolver.cs             Cecil 程序集解析器
│   │
│   ├── Outputs/                              所有"写出"逻辑
│   │   ├── Il2CppDecompiler.cs               (501) dump.cs 输出
│   │   ├── StructGenerator.cs                (1422) il2cpp.h + script.json + stringliteral.json
│   │   ├── DummyAssemblyExporter.cs          (23)  DummyDll/ 目录输出
│   │   ├── ScriptJson.cs                     (41)  JSON 数据类
│   │   ├── StructInfo.cs                     (37)  struct 元数据中间表示
│   │   ├── HeaderConstants.cs                (683) il2cpp.h 头部字符串常量
│   │   └── Il2CppConstants.cs                (73)  TypeAttributes/FieldAttributes 常量
│   │
│   ├── Extensions/                           实用扩展
│   │   ├── BinaryReaderExtensions.cs         ReadCompressedUInt32/Int32/ULeb128
│   │   ├── StringExtensions.cs               转义
│   │   ├── HexExtensions.cs                  byte[] ↔ bin string
│   │   └── BoyerMooreHorspool.cs             子串搜索（featureBytes 用）
│   │
│   └── Il2CppBinaryNinja/                    Binary Ninja 插件
│       ├── plugin.json
│       └── il2cpp_header_to_binja.py
│
├── ida.py, ida_py3.py                        IDA Pro 7.x 加载脚本
├── ida_with_struct.py / ida_with_struct_py3.py
├── ghidra.py / ghidra_wasm.py / ghidra_with_struct.py
├── hopper-py3.py                             Hopper 反编译器脚本
├── il2cpp_header_to_ghidra.py                Ghidra 头转换脚本
└── il2cpp_header_to_binja.py                 Binary Ninja 头转换脚本
```

## 模块注释

| 目录 | 责任 |
|------|------|
| `Il2CppDumper/` (根) | 应用入口（`Program.Main`） + 配置加载 |
| `Il2Cpp/` | **il2cpp 二进制镜像**——`Il2Cpp` 抽象类把 PE/ELF/Mach-O/NSO/WASM 的地址映射差异封装成统一的 `MapVATR / MapRTVA` |
| `ExecutableFormats/` | 把各种可执行格式解析为统一的 `Sections[]` 或 `ProgramSegments[]` |
| `IO/` | 跨平台的二进制流 + LZ4 解码（NSO 的 .text/.rodata/.data 可能被压缩） |
| `Attributes/` | **版本驱动 struct sizing** 的核心：`VersionAttribute` + `ArrayLengthAttribute` 让一个 C# 类兼容 v16~v31 |
| `Utils/` | "工具层"：名称解析、Dummy 生成、PE Loader、ARM 指令解码 |
| `Outputs/` | **所有"写出"逻辑**——dump.cs / il2cpp.h / script.json / DummyDll |
| `Extensions/` | 静态方法扩展，避免每个文件重复 boilerplate |
| `Il2CppBinaryNinja/` | Binary Ninja 插件入口 |
| 根 `.py` 脚本 | 把 `il2cpp.h` 与 `script.json` 翻译成 IDA / Ghidra / Hopper / Binary Ninja 的导入命令 |