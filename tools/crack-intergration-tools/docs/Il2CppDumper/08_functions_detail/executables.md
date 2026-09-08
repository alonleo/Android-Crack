# 08 — Functions Detail: Executable Formats (PE / ELF / Mach-O / NSO / WASM)

本文件覆盖所有 `ExecutableFormats/` 下的子类函数。

---

## `PE` (`ExecutableFormats/PE.cs`)

### `PE` 构造器
- **签名**：`public PE(Stream stream) : base(stream)`
- **位置**：`Il2CppDumper/ExecutableFormats/PE.cs:12`
- **可见性**：public
- **副作用**：解析 DOS 头、PE 签名、FileHeader、可选 OptionalHeader(32/64)；缓存 `sections[]`
- **抛出**：`InvalidDataException`（DOS magic、PE 签名错）、`NotSupportedException`（OptionalHeader magic 错）
- **调用**：被 `Program.Main:143` 调用

### `PE.LoadFromMemory(ulong addr)`
- **签名**：`public void LoadFromMemory(ulong addr)`
- **位置**：`Il2CppDumper/ExecutableFormats/PE.cs:47`
- **可见性**：public
- **副作用**：设置 `ImageBase = addr`；把所有 section 的 `PointerToRawData = VirtualAddress`、`SizeOfRawData = VirtualSize`
- **调用**：被 `PELoader.Load:69` 调用
- **说明**：用于 PE 保护绕过（LoadLibrary + Marshal.Copy 后的内存重定向）。

### `PE.MapVATR(ulong absAddr)`
- **签名**：`public override ulong MapVATR(ulong absAddr)`
- **位置**：`Il2CppDumper/ExecutableFormats/PE.cs:57`
- **可见性**：public override
- **返回值**：对应 file offset；未命中返回 0
- **调用**：由 `Il2Cpp` 基类调用

### `PE.MapRTVA(ulong addr)`
- **签名**：`public override ulong MapRTVA(ulong addr)`
- **位置**：`Il2CppDumper/ExecutableFormats/PE.cs:68`
- **可见性**：public override

### `PE.Search()`
- **签名**：`public override bool Search()`
- **位置**：`Il2CppDumper/ExecutableFormats/PE.cs:78`
- **返回值**：固定 false（PE 无字节模式扫描入口，依赖 `PlusSearch`）

### `PE.PlusSearch(int methodCount, int typeDefinitionsCount, int imageCount)`
- **签名**：`public override bool PlusSearch(int methodCount, int typeDefinitionsCount, int imageCount)`
- **位置**：`Il2CppDumper/ExecutableFormats/PE.cs:83`
- **可见性**：public override
- **返回值**：true 表示 CR/MR 找到且 init 成功
- **调用**：`GetSectionHelper`、`SectionHelper.FindCodeRegistration`、`SectionHelper.FindMetadataRegistration`、`AutoPlusInit`

### `PE.SymbolSearch()`
- **签名**：`public override bool SymbolSearch()`
- **位置**：`Il2CppDumper/ExecutableFormats/PE.cs:91`
- **返回值**：固定 false（PE 无导出符号表）

### `PE.GetRVA(ulong pointer)`
- **签名**：`public override ulong GetRVA(ulong pointer)`
- **位置**：`Il2CppDumper/ExecutableFormats/PE.cs:96`
- **返回值**：`pointer - ImageBase`
- **说明**：把 VA 转 RVA。

### `PE.GetSectionHelper(int methodCount, int typeDefinitionsCount, int imageCount)`
- **签名**：`public override SectionHelper GetSectionHelper(int methodCount, int typeDefinitionsCount, int imageCount)`
- **位置**：`Il2CppDumper/ExecutableFormats/PE.cs:101`
- **可见性**：public override
- **副作用**：按 `Characteristics` 把 sections 分类为 exec (`0x60000020`) / data (`0x40000040`, `0xC0000040`)；填充 `SectionHelper`

### `PE.CheckDump()`
- **签名**：`public override bool CheckDump()`
- **位置**：`Il2CppDumper/ExecutableFormats/PE.cs:127`
- **返回值**：`ImageBase != 0x10000000` (32位) / `!= 0x180000000` (64位)
- **说明**：默认 PE 加载基址偏离即视为 dump。

---

## `Elf` (`ExecutableFormats/Elf.cs`)

### `Elf` 构造器
- **签名**：`public Elf(Stream stream) : base(stream)`
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:26`
- **可见性**：public
- **副作用**：调用 `Load()`
- **调用**：`Load:32`

### `Elf.Load()` (protected override)
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:32`
- **可见性**：protected override
- **副作用**：读 ELF32 头、programSegment、dynamicSection、symbolTable；若 `IsDumped` 调用 `FixedProgramSegment`、`FixedDynamicSection`；否则 `RelocationProcessing`、`CheckProtection`

### `Elf.CheckSection()` (protected override)
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:57`
- **返回值**：sectionTable 中含 `.text` 则 true
- **调用**：被 `ElfBase.CheckDump:11` 调用

### `Elf.MapVATR(ulong addr)`
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:80`
- **可见性**：public override

### `Elf.MapRTVA(ulong addr)`
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:86`
- **可见性**：public override

### `Elf.Search()`
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:96`
- **可见性**：public override
- **副作用**：扫描 EXEC 段 ARM/x86 字节模式 `? 0x10 ? 0xE7 ? 0x00 ? 0xE0 ? 0x20 ? 0xE0`（即 LDR/ADD 模板），找到后解析 `CodeRegistration` / `MetadataRegistration`
- **说明**：v<24 与 v>=24 用不同的偏移量。

### `Elf.PlusSearch(int methodCount, int typeDefinitionsCount, int imageCount)`
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:152`

### `Elf.SymbolSearch()`
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:160`
- **可见性**：public override
- **副作用**：扫 `DT_SYMTAB` + `DT_STRTAB`，找 `g_CodeRegistration` 与 `g_MetadataRegistration`

### `Elf.ReadSymbol()` (private)
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:190`
- **可见性**：private
- **副作用**：用 `DT_HASH` 或 `DT_GNU_HASH` 算 symbol 数量，读全部 `Elf32_Sym`

### `Elf.RelocationProcessing()` (private)
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:243`
- **副作用**：遍历 `DT_REL` 表，应用 `R_ARM_ABS32` / `R_386_32`

### `Elf.CheckProtection()` (private)
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:275`
- **返回值**：true 表示 `.init_proc` 或 `JNI_OnLoad` 或 `SHT_LOUSER` 命中

### `Elf.GetRVA(ulong pointer)`
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:310`
- **说明**：dump 模式 = `pointer - ImageBase`；否则直接返回

### `Elf.FixedProgramSegment()` (private)
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:319`
- **副作用**：dump 模式中把 `p_offset = p_vaddr`、`p_vaddr += ImageBase`、`p_filesz = p_memsz`，并写回

### `Elf.FixedDynamicSection()` (private)
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:335`
- **副作用**：dump 模式中给 `DT_PLTGOT/HASH/STRTAB/SYMTAB/...` 加 `ImageBase`

### `Elf.GetSectionHelper(int methodCount, int typeDefinitionsCount, int imageCount)`
- **位置**：`Il2CppDumper/ExecutableFormats/Elf.cs:361`
- **副作用**：按 `p_flags` 分 EXEC (1/3/5/7) 和 DATA (2/4/6)

---

## `Elf64` (`ExecutableFormats/Elf64.cs`)

完全镜像 `Elf`，差异：
- 字段类型 uint → ulong
- 使用 `Elf64_Ehdr/Phdr/Dyn/Sym/Rela`
- `RelocationProcessing` 应用 `R_AARCH64_ABS64/RELATIVE` 和 `R_X86_64_64/RELATIVE`

关键函数位置（结构与 Elf 对应）：

| 函数 | 行 |
|------|----|
| `Elf64` ctor | 18 |
| `Load()` | 23 |
| `CheckSection()` | 48 |
| `MapVATR` | 71 |
| `MapRTVA` | 77 |
| `Search()` | 87（恒 false） |
| `PlusSearch` | 92 |
| `SymbolSearch` | 100 |
| `ReadSymbol` | 130 |
| `RelocationProcessing` | 183 |
| `CheckProtection` | 218 |
| `GetRVA` | 253 |
| `FixedProgramSegment` | 262 |
| `FixedDynamicSection` | 278 |
| `GetSectionHelper` | 304 |

---

## `ElfBase` (`ExecutableFormats/ElfBase.cs`)

```csharp
public abstract class ElfBase : Il2Cpp
{
    protected ElfBase(Stream stream) : base(stream) { }
    protected abstract void Load();
    protected abstract bool CheckSection();
    public override bool CheckDump() => !CheckSection();
    public void Reload() => Load();
}
```

### `ElfBase.CheckDump()`
- **位置**：`Il2CppDumper/ExecutableFormats/ElfBase.cs:11`
- **返回值**：`!CheckSection()` — dump 模式 section 表通常缺失 `.text`

### `ElfBase.Reload()`
- **位置**：`Il2CppDumper/ExecutableFormats/ElfBase.cs:13`
- **可见性**：public
- **副作用**：再跑一次 `Load()`（dump 模式下 `IsDumped=true` 后重新 locate segment）

---

## `Macho` (`ExecutableFormats/Macho.cs`)

### `Macho` 构造器
- **位置**：`Il2CppDumper/ExecutableFormats/Macho.cs:17`
- **副作用**：扫所有 LC_SEGMENT；记 `__TEXT` 的 vmaddr；若 `LC_ENCRYPTION_INFO.cryptID != 0` 仅打印警告（不阻止）

### `Macho.Init(ulong, ulong)` (override)
- **位置**：`Il2CppDumper/ExecutableFormats/Macho.cs:70`
- **副作用**：调用 `base.Init` 后 `methodPointers[i] -= 1`（Thumb 修正），`customAttributeGenerators[i] -= 1`

### `Macho.MapVATR(ulong)`
- **位置**：`Il2CppDumper/ExecutableFormats/Macho.cs:77`

### `Macho.MapRTVA(ulong)`
- **位置**：`Il2CppDumper/ExecutableFormats/Macho.cs:83`

### `Macho.Search()`
- **位置**：`Il2CppDumper/ExecutableFormats/Macho.cs:93`
- **副作用**：扫 `__mod_init_func` section；按 v<21 和 v>=21 走不同的 MOV/ADD 偏移；调用 `DecodeMov` 解 32-bit MOV 立即数

### `Macho.PlusSearch` / `SymbolSearch` / `GetRVA` / `GetSectionHelper` / `CheckDump`
- `PlusSearch` :177
- `SymbolSearch` :185（恒 false）
- `GetRVA` :190（`pointer - vmaddr`）
- `GetSectionHelper` :195（按 sectname/flags 分类）
- `CheckDump` :207（恒 false）

---

## `Macho64` (`ExecutableFormats/Macho64.cs`)

差异（除字段类型 32→64）：
- `FeatureBytes1 = {0x02, 0x00, 0x80, 0xD2}` = `MOV X2, #0`
- `FeatureBytes2 = {0x03, 0x00, 0x80, 0x52}` = `MOV W3, #0`
- 用 `DecodeAdr` / `DecodeAdrp` / `DecodeAdd` / `IsAdr`（来自 `ArmUtils.cs`）解 64-bit ARM 指令

| 函数 | 行 |
|------|----|
| `Macho64` ctor | 17 |
| `MapVATR` | 69（`__bss` 抛异常） |
| `MapRTVA` | 79 |
| `Search` | 93（v<23 / 23 / >=24 三种字节模板） |
| `PlusSearch` | 239 |
| `SymbolSearch` | 247（恒 false） |
| `GetRVA` | 252 |
| `GetSectionHelper` | 257 |
| `CheckDump` | 269（恒 false） |
| `ReadUIntPtr()` (override) | 271（处理 64-bit VM 地址回环） |

---

## `MachoFat` (`ExecutableFormats/MachoFat.cs`)

### `MachoFat` 构造器
- **位置**：`Il2CppDumper/ExecutableFormats/MachoFat.cs:10`
- **副作用**：解析 fat 头；缓存 `fats[]`
- **抛出**：当 magic 错误时 `IOException`

### `MachoFat.GetMacho(int index)`
- **签名**：`public byte[] GetMacho(int index)`
- **位置**：`Il2CppDumper/ExecutableFormats/MachoFat.cs:32`
- **可见性**：public
- **返回值**：单个切片（含 magic + load commands + data）
- **调用**：被 `Program.Main:168` 调用

---

## `NSO` (`ExecutableFormats/NSO.cs`)

### `NSO` 构造器
- **位置**：`Il2CppDumper/ExecutableFormats/NSO.cs:21`
- **副作用**：解析 NSO header（含 3 个段是否压缩的 flags）；若未压缩，进一步从 `__text+4` 读 `modOffset`、从 mod 区段读 `BssSegment` 和 dynamic section；`ReadSymbol`、`RelocationProcessing`

### `NSO.ReadSymbol()` (private)
- **位置**：`Il2CppDumper/ExecutableFormats/NSO.cs:114`

### `NSO.RelocationProcessing()` (private)
- **位置**：`Il2CppDumper/ExecutableFormats/NSO.cs:167`
- **说明**：应用 `R_AARCH64_ABS64` / `R_AARCH64_RELATIVE`

### `NSO.MapVATR(ulong)` / `MapRTVA(ulong)`
- `MapVATR` :203
- `MapRTVA` :209

### `NSO.Search()` / `SymbolSearch()`
- `Search` :219（恒 false）
- `SymbolSearch` :232（恒 false）

### `NSO.PlusSearch` / `GetSectionHelper` / `CheckDump`
- `PlusSearch` :224
- `GetSectionHelper` :325（按 NSOSegmentHeader 直接分）
- `CheckDump` :334（恒 false）

### `NSO.UnCompress()`
- **签名**：`public NSO UnCompress()`
- **位置**：`Il2CppDumper/ExecutableFormats/NSO.cs:237`
- **可见性**：public
- **返回值**：新的 NSO 实例（未压缩 + flags=0）；未压缩时返回 this
- **副作用**：用 `Lz4DecoderStream` 解 .text/.rodata/.data
- **调用**：被 `Program.Main:140` 调用

---

## `WebAssembly` (`ExecutableFormats/WebAssembly.cs`)

### `WebAssembly` 构造器
- **位置**：`Il2CppDumper/ExecutableFormats/WebAssembly.cs:10`
- **副作用**：扫 wasm section；命中 `id==11` (data section) 后读所有 `DataSection`；`Is32Bit=true`
- **抛出**：`InvalidOperationException` 当 opcode 不为 `0x41` (i32.const) 或 `0xB` (end)

### `WebAssembly.CreateMemory()`
- **签名**：`public WebAssemblyMemory CreateMemory()`
- **位置**：`Il2CppDumper/ExecutableFormats/WebAssembly.cs:47`
- **可见性**：public
- **返回值**：拼接好的 `WebAssemblyMemory`（虚拟地址 = file offset）
- **调用**：被 `Program.Main:136` 调用

---

## `WebAssemblyMemory` (`ExecutableFormats/WebAssemblyMemory.cs`)

| 函数 | 行 | 说明 |
|------|----|------|
| 构造器 | 9 | Is32Bit=true |
| `MapVATR` | 15 | return addr（WASM 不做偏移） |
| `MapRTVA` | 20 | return addr |
| `PlusSearch` | 25 | 委托 SectionHelper |
| `Search` | 33 | 恒 false |
| `SymbolSearch` | 38 | 恒 false |
| `GetSectionHelper` | 43 | 用 methodCount 做 exec 范围（hack） |
| `CheckDump` | 73 | 恒 false |

---

## POD struct（无方法）

| 类 | 行 |
|----|----|
| `DosHeader` | `PEClass.cs:5` |
| `FileHeader` | `PEClass.cs:30` |
| `OptionalHeader` | `PEClass.cs:41` |
| `OptionalHeader64` | `PEClass.cs:76` |
| `SectionHeader` | `PEClass.cs:116` |
| `SectionCharacteristics` enum | `PEClass.cs:132` |
| `Elf32_Ehdr` | `ElfClass.cs:3` |
| `Elf32_Phdr` | `ElfClass.cs:28` |
| `Elf32_Shdr` | `ElfClass.cs:40` |
| `Elf32_Sym` | `ElfClass.cs:54` |
| `Elf32_Dyn` | `ElfClass.cs:64` |
| `Elf32_Rel` | `ElfClass.cs:70` |
| `Elf64_Ehdr` | `ElfClass.cs:76` |
| `Elf64_Phdr` | `ElfClass.cs:101` |
| `Elf64_Shdr` | `ElfClass.cs:113` |
| `Elf64_Sym` | `ElfClass.cs:127` |
| `Elf64_Dyn` | `ElfClass.cs:137` |
| `Elf64_Rela` | `ElfClass.cs:143` |
| `ElfConstants` | `ElfClass.cs:150` |
| `MachoSection` | `MachoClass.cs:3` |
| `MachoSection64Bit` | `MachoClass.cs:12` |
| `Fat` | `MachoClass.cs:21` |
| `NSOHeader` | `NSOClass.cs:3` |
| `NSOSegmentHeader` | `NSOClass.cs:30` |
| `NSORelativeExtent` | `NSOClass.cs:37` |
| `DataSection` | `WebAssemblyClass.cs:3` |
| `SearchSectionType` enum | `SearchSection.cs:3` |
| `SearchSection` | `SearchSection.cs:10` |

---

## 实用函数（Utils）

### `PELoader.Load(string fileName)` (static)
- **位置**：`Il2CppDumper/Utils/PELoader.cs:14`
- **可见性**：public static
- **副作用**：用 Win32 `LoadLibrary` 把 PE 装载到进程，再用 `Marshal.Copy` 复制 section 到 `MemoryStream`，新建 `PE` 实例并 `LoadFromMemory(handle)`
- **抛出**：`InvalidDataException`（PE magic）、`InvalidOperationException`（32/64 位不匹配）、`Win32Exception`
- **调用**：被 `Program.Main:216` 调用（仅 Windows + 失败回退）

### `ArmUtils.DecodeMov(byte[] asm)`
- **位置**：`Il2CppDumper/Utils/ArmUtils.cs:7`
- **可见性**：public static
- **说明**：解 32-bit ARM `MOVW/MOVT` 立即数对，返回完整 32-bit 立即数。
- **调用**：被 `Macho.Search:114,117,124,154,157,164` 调用

### `ArmUtils.DecodeAdr(ulong pc, byte[] inst)`
- **位置**：`Il2CppDumper/Utils/ArmUtils.cs:14`
- **可见性**：public static
- **说明**：解 ARM64 `ADR` 指令

### `ArmUtils.DecodeAdrp(ulong pc, byte[] inst)`
- **位置**：`Il2CppDumper/Utils/ArmUtils.cs:22`

### `ArmUtils.DecodeAdd(byte[] inst)`
- **位置**：`Il2CppDumper/Utils/ArmUtils.cs:31`

### `ArmUtils.IsAdr(byte[] inst)`
- **位置**：`Il2CppDumper/Utils/ArmUtils.cs:40`
- **调用**：被 `Macho64.Search:116,134` 调用

---

## `IO` 层

### `BinaryStream` 类

| 成员 | 行 | 说明 |
|------|----|------|
| `Version` | 12 | il2cpp 版本，default 0 |
| `Is32Bit` | 13 | |
| `ImageBase` | 14 | |
| `Position` | 86 | ulong 别名 |
| `Length` | 92 | |
| `ReadPrimitive(Type)` | 94 | private，switch Int32/UInt32/Int16/UInt16/Byte/IntPtr/UIntPtr |
| `ReadClass<T>(ulong addr)` | 109 | 定位后 ReadClass<T>() |
| `ReadClass<T>()` | 115 | 反射遍历字段，遵守 VersionAttribute 缓存（attributeCache + genericMethodCache） |
| `ReadClassArray<T>(long count)` | 185 | 当前位置读 count 个 |
| `ReadClassArray<T>(ulong addr, ulong count)` | 195 | 转换 long 后委托 |
| `ReadClassArray<T>(ulong addr, long count)` | 200 | 定位 + 读 |
| `ReadStringToNull(ulong addr)` | 206 | UTF-8 读到 0 |
| `ReadIntPtr()` | 216 | 32/64 自适应 |
| `ReadUIntPtr()` | 221 | virtual，64-bit 用 ulong |
| `PointerSize` | 226 | 4 或 8 |
| `Dispose` | 245 | 关闭 stream |

### `Lz4DecoderStream`

完整的 LZ4 解码流（`IO/Lz4DecoderStream.cs`），仅用于 NSO 解压。

构造器：`Lz4DecoderStream(Stream input, long inputLength = long.MaxValue)` (line 12)

主要方法：
- `Reset` (private) :17
- `Dispose` (override) :34
- `Read` (override) :87 — 核心状态机 ReadToken → ReadExLiteralLength → CopyLiteral → ReadOffset → ReadExMatchLength → CopyMatch
- `ReadByteCore` (private) :377
- `ReadOffsetCore` (private) :400
- `ReadCore` (private) :449
- Stream overrides (CanRead/CanSeek/CanWrite/Flush/Length/Position/Seek/SetLength/Write) :503-537

---

## Attributes

### `ArrayLengthAttribute`
- **位置**：`Il2CppDumper/Attributes/ArrayLengthAttribute.cs:6`
- **可见性**：internal（AttributeUsage Field）
- **成员**：`int Length { get; set; }`
- **调用**：被 `BinaryStream.ReadClass:163,279` 反射读取

### `VersionAttribute`
- **位置**：`Il2CppDumper/Attributes/VersionAttribute.cs:6`
- **可见性**：internal（AttributeUsage Field, AllowMultiple=true）
- **成员**：`double Min { get; set; } = 0`、`double Max { get; set; } = 99`
- **调用**：被 `BinaryStream.ReadClass:127-149`、`Metadata.SizeOf:261` 使用