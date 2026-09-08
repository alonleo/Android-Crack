# 03 — Architecture

This document captures the static structure of ILSpy: how sub-projects depend on each other, the inheritance hierarchy of the public engine API, and the lifetime of one decompilation request as a state diagram.

## 3.1 Module dependency graph

The CLI and the GUI share the same engine. `ICSharpCode.ILSpyX` is a UI-host-agnostic layer that both runtimes can consume. The GUI adds Avalonia-specific views; the CLI uses the engine directly.

```mermaid
flowchart TD
    subgraph "Entry points"
        A1[ILSpy.exe<br/>ILSpy/Program.cs:35<br/>Avalonia GUI]
        A2[ilspycmd<br/>ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:71<br/>CLI]
        A3[ICSharpCode.Decompiler.dll<br/>NuGet library]
        A4[ICSharpCode.Decompiler.PowerShell.dll<br/>PS cmdlets]
        A5[ILSpy.AddIn.VS2022<br/>VS extension]
    end

    subgraph "UI-host-agnostic core (cross-platform)"
        X1[ICSharpCode.ILSpyX<br/>AssemblyList / LoadedAssembly / Search / Settings]
        X2[ICSharpCode.BamlDecompiler]
    end

    subgraph "Decompiler engine (netstandard2.0)"
        D1[ICSharpCode.Decompiler<br/>Decompiler.cs facade]
        D2[IL/CSharp/AST/Resolver/<br/>OutputVisitor/Transforms]
        D3[TypeSystem/<br/>Metadata/]
    end

    subgraph "Source generators"
        G1[ICSharpCode.Decompiler.Generators<br/>emits DecompilerVersionInfo.cs]
    end

    A1 --> X1
    A1 --> D1
    A1 --> D2
    A2 --> D1
    A2 --> X1
    A2 --> X2
    A3 --> D1
    A4 --> D1
    A5 --> D1
    X1 --> D1
    D1 --> D2
    D2 --> D3
    G1 -.->|emits at build| D1
```

## 3.2 Public engine class hierarchy

```mermaid
classDiagram
    class IDecompiler {
        <<interface>>
        +DecompileType(type)
        +Decompile(member)
        +DecompileAsString(member)
    }
    class Decompiler {
        +Task~SyntaxTree~ DecompileAsync(...)
        +Task~string~ DecompileTypeAsStringAsync(...)
        +IAssemblyResolver AssemblyResolver
    }
    class CSharpDecompiler {
        +IDecompilerTypeSystem TypeSystem
        +DecompilerSettings Settings
        +Stepper Stepper
        +SyntaxTree DecompileWholeModuleAsSingleFile()
        +SyntaxTree DecompileType(FullTypeName)
        +SyntaxTree Decompile(IEnumerable~EntityHandle~)
        +static List~IILTransform~ GetILTransforms()
        +static List~IAstTransform~ GetAstTransforms()
    }
    class ILAstPipeline {
        <<utility>>
        +ILReader.ReadIL(...)
        +BlockBuilder
        +StatementBuilder.ConvertAsBlock(...)
        +ExpressionBuilder
    }
    class SyntaxTreeOutput {
        <<utility>>
        +CSharpOutputVisitor.WriteTo(TextWriter)
        +InsertParenthesesVisitor
        +InsertRequiredSpacesDecorator
    }
    IDecompiler <|.. Decompiler
    IDecompiler <|.. CSharpDecompiler
    Decompiler ..> CSharpDecompiler : delegates
    CSharpDecompiler ..> ILAstPipeline : uses
    CSharpDecompiler ..> SyntaxTreeOutput : uses
    CSharpDecompiler --> "1" DecompilerTypeSystem : owns
    CSharpDecompiler --> "1" DecompilerSettings : owns
```

## 3.3 Per-decompilation state

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle: ctor / settings load
    Idle --> Loading: Decompile(handle)
    Loading: PEFile open + resolver<br/>UniversalAssemblyResolver
    Loading --> BuildingTypeSystem: success
    BuildingTypeSystem: DecompilerTypeSystem.CreateAsync<br/>Type references wired
    BuildingTypeSystem --> ReadingIL: success
    ReadingIL: ILReader.ReadIL<br/>CIL bytes -> ILFunction<br/>(stack-type inference)
    ReadingIL --> RunningILTransforms: success
    RunningILTransforms: 30 IILTransforms<br/>GetILTransforms() order matters
    RunningILTransforms --> ShortCircuit: !DecompileMemberBodies<br/>and IsAsync/IsIterator known
    ShortCircuit --> BuildingSyntaxTree: sequence points only
    RunningILTransforms --> BuildingSyntaxTree: full path
    BuildingSyntaxTree: StatementBuilder.ConvertAsBlock<br/>ExpressionBuilder.Convert<br/>CallBuilder.Convert
    BuildingSyntaxTree --> RunningAstTransforms: 16 IAstTransforms
    RunningAstTransforms --> PrettyPrinting: CSharpOutputVisitor<br/>+ decorators
    PrettyPrinting --> Idle: result written
    ReadingIL --> Failed: unsupported pattern
    BuildingTypeSystem --> Failed: missing reference
    RunningILTransforms --> Failed: StepLimitReachedException
    Failed: DecompilerException raised<br/>DebugSteps pane populated
    Failed --> Idle
```

## 3.4 Engine layering

There are four concentric layers; the inner layers do not know about the outer ones.

| Layer | Concrete types | Responsibility |
|---|---|---|
| Metadata | `PEFile`, `MetadataFile`, `UniversalAssemblyResolver`, `MetadataExtensions` | Read PE / NuGet / bundle / WebCIL; resolve `AssemblyRef` to files |
| Type system | `DecompilerTypeSystem`, `IType`, `IMethod`, `IField`, ... `Implementation/MetadataTypeDefinition`, `MetadataMethod`, `MetadataField` | Adapt SRM types to a resolver-friendly `ICompilation` |
| IL | `ILReader`, `IL/Instructions/*.cs` (`Block`, `ILFunction`, `IfInstruction`, `Call`, `Branch`, ...), `IL/Transforms/*.cs` (49 transforms), `IL/ControlFlow/*.cs` | CIL bytes -> ILAst -> de-sugared statement list |
| C# AST | `Syntax/*.cs` (AstNode, statements, expressions, types), `Transforms/*.cs` (21 AST transforms), `Resolver/*.cs` (CSharpResolver, overload resolution, conversions), `OutputVisitor/CSharpOutputVisitor.cs` | ILAst -> NRefactory SyntaxTree -> C# text |

The split between IL and C# AST layers is the key design decision: by the time control reaches the AST layer, the IL has been maximally de-sugared so the AST only does cosmetic work (introducing operators as syntactic sugar, joining adjacent `using` statements, fixing name collisions, etc.). This makes the C# output largely independent of the IL dialect the input was compiled from.

## 3.5 MEF composition graph (GUI)

```mermaid
flowchart LR
    subgraph "AppComposition"
        C[ContainerConfiguration<br/>System.Composition]
    end

    subgraph "Core"
        CS[ICSharpCode.Decompiler.dll]
        ILX[ICSharpCode.ILSpyX.dll]
    end

    subgraph "ILSpy assembly"
        APP[App.axaml.cs]
        MW[MainWindow<br/>ViewLocator]
        VMS[ViewModels]
        VIEWS[Views]
        CMDS[Commands/*]
        TREE[AssemblyTreeModel]
    end

    subgraph "Plugins (*.Plugin.dll next to ILSpy.exe)"
        P1[ILSpy.ReadyToRun]
        P2[User plugins]
    end

    C --> CS
    C --> ILX
    C --> APP
    C --> MW
    C --> VMS
    C --> VIEWS
    C --> CMDS
    C --> TREE
    C --> P1
    C --> P2

    APP -->|resolves| MW
    MW --> VIEWS
    MW --> VMS
    VIEWS -->|bind| VMS
    CMDS -->|operate on| TREE
    P1 -->|adds| CMDS
    P2 -->|adds| CMDS
```