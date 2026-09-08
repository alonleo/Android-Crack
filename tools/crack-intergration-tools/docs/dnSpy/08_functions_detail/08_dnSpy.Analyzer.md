# 08 — `dnSpy.Analyzer` (Static Analyzer)

This file documents the static analyzer extension (`Extensions/dnSpy.Analyzer/`). It provides the "Used By", "Base Type", "Derived Type", "Is Overridden By", "Interface Implemented By", etc. analysis when the user right-clicks a member and picks Analyze.

## `TheExtension.cs`

### `TheExtension`

- **位置**: `Extensions/dnSpy.Analyzer/TheExtension.cs`
- **MEF**: `[ExportExtension] sealed class TheExtension : IExtension`
- **可见性**: public, sealed
- **简要说明**: top-level MEF plugin

## `dnSpy.Analyzer.csproj`

- **位置**: `Extensions/dnSpy.Analyzer/dnSpy.Analyzer.csproj`
- **简要说明**: csproj

## `AnalyzerService.cs`

### `AnalyzerService` (sealed) — `Extensions/dnSpy.Analyzer/AnalyzerService.cs`

- **MEF**: `[Export]`
- **可见性**: public, sealed
- **简要说明**: the analyzer driver

#### `public IEnumerable<AnalyzerTreeNodeData> GetResults(DsDocumentNode node)`

- **位置**: `Extensions/dnSpy.Analyzer/AnalyzerService.cs:1`
- **可见性**: public
- **副作用**: streams `AnalyzerTreeNodeData` instances to the tool window
- **调用了**: each registered `IAnalyzer.GetResults(...)`
- **简要说明**: runs all analyzers on a node

## `AnalyzerSettings.cs`

- **位置**: `Extensions/dnSpy.Analyzer/AnalyzerSettings.cs`
- **简要说明**: persisted options

## `AnalyzerToolWindowContent.cs`

- **位置**: `Extensions/dnSpy.Analyzer/AnalyzerToolWindowContent.cs`
- **简要说明**: the analyzer tool window

#### `public void Add(AnalyzerTreeNodeData node)`

- **位置**: `Extensions/dnSpy.Analyzer/AnalyzerToolWindowContent.cs:1`
- **可见性**: public
- **简要说明**: stream a node

## `AnalyzerTreeNodeDataContext.cs`

- **位置**: `Extensions/dnSpy.Analyzer/AnalyzerTreeNodeDataContext.cs`
- **简要说明**: per-node analysis context

## `Commands.cs`

- **位置**: `Extensions/dnSpy.Analyzer/Commands.cs`
- **简要说明**: command bindings

## `ContentTypeDefinitions.cs`

- **位置**: `Extensions/dnSpy.Analyzer/ContentTypeDefinitions.cs`
- **简要说明**: content-type registration

## `TreeTraversal.cs`

- **位置**: `Extensions/dnSpy.Analyzer/TreeTraversal.cs`
- **简要说明**: tree-traversal helpers

## `TreeNodes/` (~40 files, one per analyzer finding)

### `EntityNode.cs` (+ derived)

- **位置**: `Extensions/dnSpy.Analyzer/TreeNodes/`
- **可见性**: public
- **简要说明**: abstract base; `EntityNode` -> `MethodNode`, `TypeNode`, `FieldNode`, `EventNode`, `PropertyNode`, `AssemblyNode`

### Other analyzer node kinds (all `public class : AnalyzerTreeNodeData`)

| Node | File | Meaning |
|---|---|---|
| `AttributeAppliedToNode` | `AttributeAppliedToNode.cs` | types/members where the attribute is applied |
| `BaseTypesTreeNode` | `BaseTypesTreeNode.cs` | base types of a type |
| `DerivedTypesTreeNode` | `DerivedTypesTreeNode.cs` | derived types |
| `EventAccessorNode` | `EventAccessorNode.cs` | event accessor (add/remove) |
| `EventFiredByNode` | `EventFiredByNode.cs` | methods that fire the event |
| `EventOverriddenNode` | `EventOverriddenNode.cs` | events overridden by this event |
| `EventOverridesNode` | `EventOverridesNode.cs` | events this event overrides |
| `FieldAccessNode` | `FieldAccessNode.cs` | methods that read/write the field |
| `InterfaceEventImplementedByNode` | `InterfaceEventImplementedByNode.cs` | types implementing this interface event |
| `InterfaceMethodImplementedByNode` | `InterfaceMethodImplementedByNode.cs` | types implementing this interface method |
| `InterfacePropertyImplementedByNode` | `InterfacePropertyImplementedByNode.cs` | types implementing this interface property |
| `MethodNode` | `MethodNode.cs` | a method entity |
| `MethodOverriddenNode` | `MethodOverriddenNode.cs` | methods overridden by this method |
| `MethodOverridesNode` | `MethodOverridesNode.cs` | methods this method overrides |
| `MethodUsedByNode` | `MethodUsedByNode.cs` | methods calling this method |
| `MethodUsesNode` | `MethodUsesNode.cs` | methods called by this method |
| `ModuleNode` | `ModuleNode.cs` | a module entity |
| `PropertyAccessorNode` | `PropertyAccessorNode.cs` | property accessor (get/set) |
| `PropertyNode` | `PropertyNode.cs` | a property entity |
| `PropertyOverriddenNode` | `PropertyOverriddenNode.cs` | properties overridden by this property |
| `PropertyOverridesNode` | `PropertyOverridesNode.cs` | properties this property overrides |
| `TypeNode` | `TypeNode.cs` | a type entity |
| (etc.) | | |

### Helpers

- `AsyncFetchChildrenHelper.cs` — `Extensions/dnSpy.Analyzer/TreeNodes/AsyncFetchChildrenHelper.cs`
  - async fetch of children (for cross-assembly resolution)
- `ComUtils.cs` — COM helper
- `Helpers.cs` — misc helpers
- `IAnalyzerTreeNodeDataContext.cs` — per-node context
- `IAsyncCancellable.cs` — cancellation contract

## Analysis call stack

```
[user right-clicks a type]
└── MenuItem "Analyze" clicked
    └── AnalyzerService.GetResults(node)        (AnalyzerService.cs:1)
        └── for each IAnalyzer registered via MEF:
            └── analyzer.GetResults(node, scope)
                └── yields AnalyzerTreeNodeData instances
                    ├── MethodUsedByNode
                    ├── BaseTypesTreeNode
                    ├── DerivedTypesTreeNode
                    ├── AttributeAppliedToNode
                    └── ...
        └── streamed to AnalyzerToolWindowContent via Add(node)
            └── each node fetches children asynchronously via AsyncFetchChildrenHelper
            └── double-click -> DocumentTreeView.SelectItems(target)
```