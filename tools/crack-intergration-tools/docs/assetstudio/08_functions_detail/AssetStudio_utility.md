# `AssetStudio_utility.md` — 工具库函数详细说明

本章详细列出 `AssetStudio.Utility/`（csproj `AssetStudio.Utility.csproj`）下被覆盖的 public/internal 函数。

---

## 1. `AssetStudio.Utility/ModelConverter.cs`

### `ModelConverter(GameObject, Options, AnimationClip[])`
- **签名**：`ModelConverter(GameObject m_GameObject, Options options, AnimationClip[] animationList = null)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:27`
- **可见性**：public ctor
- **副作用**：填充 `RootFrame / MeshList / MaterialList / TextureList / AnimationList / MorphList`
- **调用**：
  - `Exporter.ExportGameObject`（CLI: `Exporter.cs:412`、GUI: `Exporter.cs:411`）
  - `MainForm.PreviewGameObject` (`MainForm.cs:1416`)
- **调用了**：`InitWithAnimator` / `InitWithGameObject`、`CollectAnimationClip`、`ConvertAnimations`
- **简要说明**：构造期就完成 Transform 树、Mesh、Material、Animation 转换；是 GameObject → FBX 中间表示的核心

### `ModelConverter(string, List<GameObject>, Options, AnimationClip[])`
- **签名**：`ModelConverter(string rootName, List<GameObject> m_GameObjects, Options options, AnimationClip[] animationList = null)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:53`
- **可见性**：public ctor
- **调用**：`GUI/Exporter.ExportGameObjectMerge` (`GUI/Exporter.cs:448`)
- **调用了**：`CreateFrame`、`ConvertTransforms`、`CreateBonePathHash`、`ConvertMeshRenderer`、`ConvertAnimations`
- **简要说明**：合并多个 GameObject 到一个 rootName

### `ModelConverter(Animator, Options, AnimationClip[])`
- **签名**：`ModelConverter(Animator m_Animator, Options options, AnimationClip[] animationList = null)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:84`
- **可见性**：public ctor
- **调用**：
  - `Exporter.ExportAnimator`（CLI: `Exporter.cs:374, 375`、GUI: `Exporter.cs:373, 374`）
  - `MainForm.PreviewAnimator` (`MainForm.cs:1431`)
- **调用了**：`InitWithAnimator`、`CollectAnimationClip`、`ConvertAnimations`
- **简要说明**：从 Animator 入口构建 Imported

### `ModelConverter.InitWithAnimator(Animator)`
- **签名**：`void InitWithAnimator(Animator m_Animator)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:106`
- **可见性**：private
- **调用了**：`InitWithGameObject`
- **简要说明**：从 Animator 取 avatar + GameObject 后委托给 InitWithGameObject

### `ModelConverter.InitWithGameObject(GameObject, bool)`
- **签名**：`void InitWithGameObject(GameObject m_GameObject, bool hasTransformHierarchy = true)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:115`
- **可见性**：private
- **调用了**：`ConvertTransforms`、`DeoptimizeTransformHierarchy`、`CreateBonePathHash`、`ConvertMeshRenderer`
- **简要说明**：处理 transform 层次；Unity 5+ 优化后的 Transform hierarchy 需要 deoptimize

### `ModelConverter.ConvertMeshRenderer(Transform)`
- **签名**：`void ConvertMeshRenderer(Transform m_Transform)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:154`
- **可见性**：private
- **调用了**：`ConvertMeshRenderer(Renderer)`
- **简要说明**：递归遍历 GameObject 树，对每个 Renderer 调用 ConvertMeshRenderer(Renderer)

### `ModelConverter.CollectAnimationClip(Animator)`
- **签名**：`void CollectAnimationClip(Animator m_Animator)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:190`
- **可见性**：private
- **调用了**：`AnimatorController.m_AnimationClips`、`AnimatorOverrideController.m_Controller`
- **简要说明**：从 AnimatorController 收集 AnimationClip 到 animationClipHashSet

### `ModelConverter.ConvertTransform(Transform)`
- **签名**：`ImportedFrame ConvertTransform(Transform trans)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:226`
- **可见性**：private
- **调用了**：`SetFrame`
- **简要说明**：单 Transform → ImportedFrame

### `ModelConverter.CreateFrame(string, Vector3, Quaternion, Vector3)`
- **签名**：`static ImportedFrame CreateFrame(string name, Vector3 t, Quaternion q, Vector3 s)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:236`
- **可见性**：private static
- **简要说明**：构造单个 ImportedFrame

### `ModelConverter.SetFrame(ImportedFrame, Vector3, Quaternion, Vector3)`
- **签名**：`static void SetFrame(ImportedFrame frame, Vector3 t, Quaternion q, Vector3 s)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:244`
- **可见性**：private static
- **简要说明**：X 轴取反的 Unity → FBX 坐标系转换

### `ModelConverter.ConvertTransforms(Transform, ImportedFrame)`
- **签名**：`void ConvertTransforms(Transform trans, ImportedFrame parent)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:251`
- **可见性**：private
- **简要说明**：递归构造 Transform 树

### `ModelConverter.ConvertMeshRenderer(Renderer)`
- **签名**：`void ConvertMeshRenderer(Renderer meshR)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:269`
- **可见性**：private
- **调用了**：`GetMesh`、`ConvertMaterial`、`Mesh.GetUV`
- **简要说明**：把 Renderer（含 SkinnedMeshRenderer）的 vertex / normal / UV / tangent / color / bone / morph 转 ImportedMesh

### `ModelConverter.GetMesh(Renderer)`
- **签名**：`static Mesh GetMesh(Renderer meshR)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:588`
- **可见性**：private static
- **简要说明**：取 Renderer 关联的 Mesh

### `ModelConverter.GetTransformPath(Transform)`
- **签名**：`string GetTransformPath(Transform transform)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:612`
- **可见性**：private
- **简要说明**：从 transformDictionary 取帧 path

### `ModelConverter.FixBonePath(AnimationClip, string)`
- **签名**：`string FixBonePath(AnimationClip m_AnimationClip, string path)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:621`
- **可见性**：private
- **简要说明**：在动画路径前拼接 boundAnimationPathDic 中的 basePath

### `ModelConverter.FixBonePath(string)`
- **签名**：`string FixBonePath(string path)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:630`
- **可见性**：private
- **调用了**：`ImportedFrame.FindFrameByPath`
- **简要说明**：用 RootFrame 校验 path

### `ModelConverter.GetTransformPathByFather(Transform)`
- **签名**：`static string GetTransformPathByFather(Transform transform)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:636`
- **可见性**：private static
- **简要说明**：递归构造完整 hierarchy path

### `ModelConverter.ConvertMaterial(Material)`
- **签名**：`ImportedMaterial ConvertMaterial(Material mat)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:647`
- **可见性**：private
- **调用了**：`ImportedHelpers.FindMaterial`、`ConvertTexture2D`
- **简要说明**：Material → ImportedMaterial（diffuse/ambient/emissive/specular/shininess/transparency/textures）

### `ModelConverter.ConvertTexture2D(Texture2D, string)`
- **签名**：`void ConvertTexture2D(Texture2D m_Texture2D, string name)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:770`
- **可见性**：private
- **调用了**：`Texture2D.ConvertToStream`、`ImportedHelpers.FindTexture`
- **简要说明**：构造 ImportedTexture（含流）

### `ModelConverter.ConvertAnimations()`
- **签名**：`void ConvertAnimations()`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:789`
- **可见性**：private
- **调用了**：`ACLClip.Process`、`m_StreamedClip.ReadData`、`m_DenseClip.m_SampleArray`、`ReadCurveData`
- **简要说明**：处理 legacy + mecanim 两种动画格式；ACL 是可选路径

### `ModelConverter.ReadCurveData(...)`
- **签名**：`void ReadCurveData(ImportedKeyframedAnimation iAnim, AnimationClipBindingConstant m_ClipBindingConstant, int index, float time, float[] data, int offset, ref int curveIndex)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:983`
- **可见性**：private
- **简要说明**：根据 binding.typeID 分派（BlendShape / Transform）

### `ModelConverter.GetPathFromHash(uint)`
- **签名**：`string GetPathFromHash(uint hash)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:1065`
- **可见性**：private
- **调用了**：`Avatar.FindBonePath`
- **简要说明**：用 bonePathHash 还原 path，找不到就退到 avatar

### `ModelConverter.CreateBonePathHash(Transform)`
- **签名**：`void CreateBonePathHash(Transform m_Transform)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:1079`
- **可见性**：private
- **调用了**：`SevenZip.CRC`
- **简要说明**：把所有 bone path + 子路径的 CRC32 哈希加入 bonePathHash

### `ModelConverter.DeoptimizeTransformHierarchy()`
- **签名**：`void DeoptimizeTransformHierarchy()`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:1102`
- **可见性**：private
- **调用了**：`Avatar.FindBonePath`、`ImportedFrame.FindRelativeFrameWithPath`
- **抛出/异常**：找不到 Avatar 时抛 `Exception("Transform hierarchy has been optimized, but can't find Avatar to deoptimize.")`
- **简要说明**：Unity 5+ 优化后的 hierarchy 需要重新展开

### `ModelConverter.GetPathByChannelName(string)`
- **签名**：`string GetPathByChannelName(string channelName)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:1147`
- **可见性**：private
- **简要说明**：BlendShape channelName → path

### `ModelConverter.GetChannelNameFromHash(uint)`
- **签名**：`string GetChannelNameFromHash(uint attribute)`
- **位置**：`AssetStudio.Utility/ModelConverter.cs:1162`
- **可见性**：private
- **简要说明**：attribute hash → channelName

---

## 2. `AssetStudio.Utility/Texture2DConverter.cs`

### `Texture2DConverter(Texture2D)`
- **签名**：`Texture2DConverter(Texture2D m_Texture2D)`
- **位置**：`AssetStudio.Utility/Texture2DConverter.cs:18`
- **可见性**：public ctor
- **副作用**：复制 m_Width / m_Height / m_TextureFormat / version / platform / outPutSize
- **简要说明**：构造时缓存源数据引用

### `Texture2DConverter.DecodeTexture2D(byte[])`
- **签名**：`bool DecodeTexture2D(byte[] bytes)`
- **位置**：`AssetStudio.Utility/Texture2DConverter.cs:29`
- **可见性**：public
- **返回值**：`bool`（成功 / 失败）
- **调用了**：30+ 个私有 `DecodeXxx`
- **简要说明**：主解码入口；按 TextureFormat switch 调用对应私有方法

### `Texture2DConverter.SwapBytesForXbox(byte[])`
- **签名**：`void SwapBytesForXbox(byte[] image_data)`
- **位置**：`AssetStudio.Utility/Texture2DConverter.cs:225`
- **可见性**：private
- **简要说明**：Xbox360 平台字节序交换

### `Texture2DConverter.DecodeAlpha8 / ARGB4444 / RGB24 / RGBA32 / ARGB32 / RGB565 / R16 / ...`
- **签名**：`bool DecodeXxx(byte[] image_data, byte[] buff)`
- **位置**：`AssetStudio.Utility/Texture2DConverter.cs:238..693`
- **可见性**：private
- **简要说明**：单个像素格式解码；DXT/BC/ETC/ASTC/PVRTC 委托给 `TextureDecoder.DecodeXxx`

### `Texture2DConverter.DownScaleFrom16BitTo8Bit(ushort)`
- **签名**：`static byte DownScaleFrom16BitTo8Bit(ushort component)`
- **位置**：`AssetStudio.Utility/Texture2DConverter.cs:653`
- **可见性**：public static
- **简要说明**：R16/RG16/RGBA64 等格式用

---

## 3. `AssetStudio.Utility/ShaderConverter.cs`

### `ShaderConverter.Convert(this Shader)`
- **签名**：`static string Convert(this Shader shader)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:18`
- **可见性**：public static extension
- **调用了**：`LZ4.Instance.Decompress`、`ConvertSerializedShader(shader)`
- **抛出/异常**：LZ4 解压失败抛 `IOException`
- **简要说明**：shader → 文本

### `ShaderConverter.ConvertSerializedShader(Shader)`
- **签名**：`static string ConvertSerializedShader(Shader shader)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:44`
- **可见性**：private static
- **调用了**：`LZ4.Instance.Decompress`（GI 子组用 Buffer.BlockCopy 跳过解压）
- **抛出/异常**：解压失败抛 `IOException`
- **简要说明**：5.5+ 压缩格式：逐平台解压每个 blob，构造 ShaderProgram[]

### `ShaderConverter.ConvertSerializedShader(SerializedShader, ShaderCompilerPlatform[], ShaderProgram[])`
- **签名**：`static string ConvertSerializedShader(SerializedShader m_ParsedForm, ShaderCompilerPlatform[] platforms, ShaderProgram[] shaderPrograms)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:82`
- **可见性**：private static
- **调用了**：`ConvertSerializedProperties`、`ConvertSerializedSubShader`、`ConvertSerializedShaderState`、`ConvertSerializedTagMap`
- **简要说明**：构造 Shader 文本主干

### `ShaderConverter.ConvertSerializedSubShader(SerializedSubShader, ShaderCompilerPlatform[], ShaderProgram[])`
- **签名**：`static string ConvertSerializedSubShader(SerializedSubShader m_SubShader, ShaderCompilerPlatform[] platforms, ShaderProgram[] shaderPrograms)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:108`
- **可见性**：private static
- **调用了**：`ConvertSerializedPass`、`ConvertSerializedTagMap`
- **简要说明**：SubShader 块

### `ShaderConverter.ConvertSerializedPass(SerializedPass, ShaderCompilerPlatform[], ShaderProgram[])`
- **签名**：`static string ConvertSerializedPass(SerializedPass m_Passe, ShaderCompilerPlatform[] platforms, ShaderProgram[] shaderPrograms)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:127`
- **可见性**：private static
- **调用了**：`ConvertSerializedShaderState`、`ConvertSerializedSubPrograms`
- **简要说明**：Pass 块（含 vp/fp/gp/hp/dp/rtp 子程序）

### `ShaderConverter.ConvertSerializedSubPrograms(List<SerializedSubProgram>, ShaderCompilerPlatform[], ShaderProgram[])`
- **签名**：`static string ConvertSerializedSubPrograms(List<SerializedSubProgram> m_SubPrograms, ShaderCompilerPlatform[] platforms, ShaderProgram[] shaderPrograms)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:208`
- **可见性**：private static
- **调用了**：`CheckGpuProgramUsable`、`GetPlatformString`
- **简要说明**：按 m_BlobIndex + m_GpuProgramType 分组，输出 SubProgram 块

### `ShaderConverter.ConvertSerializedShaderState(SerializedShaderState)`
- **签名**：`static string ConvertSerializedShaderState(SerializedShaderState m_State)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:243`
- **可见性**：private static
- **调用了**：`ConvertSerializedTagMap`、`ConvertSerializedShaderRTBlendState`、`ConvertStencilOp`、`ConvertStencilComp`、`ConvertBlendFactor`、`ConvertBlendOp`
- **简要说明**：Pass 的 State 块（Blend/ZTest/Cull/Stencil/Fog）

### `ShaderConverter.ConvertSerializedStencilOp(SerializedStencilOp, string)`
- **签名**：`static string ConvertSerializedStencilOp(SerializedStencilOp stencilOp, string suffix)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:444`
- **可见性**：private static
- **简要说明**：StencilOp 子块

### `ShaderConverter.ConvertStencilOp(SerializedShaderFloatValue)`
- **签名**：`static string ConvertStencilOp(SerializedShaderFloatValue op)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:454`
- **可见性**：private static
- **简要说明**：StencilOp enum → Keep/Zero/Replace/IncrSat/...

### `ShaderConverter.ConvertStencilComp(SerializedShaderFloatValue)`
- **签名**：`static string ConvertStencilComp(SerializedShaderFloatValue comp)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:478`
- **可见性**：private static
- **简要说明**：StencilComp enum → Disabled/Never/Less/...

### `ShaderConverter.ConvertSerializedShaderRTBlendState(List<SerializedShaderRTBlendState>, bool)`
- **签名**：`static string ConvertSerializedShaderRTBlendState(List<SerializedShaderRTBlendState> rtBlend, bool rtSeparateBlend)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:504`
- **可见性**：private static
- **调用了**：`ConvertBlendFactor`、`ConvertBlendOp`
- **简要说明**：Blend / BlendOp / ColorMask

### `ShaderConverter.ConvertBlendOp(SerializedShaderFloatValue)`
- **签名**：`static string ConvertBlendOp(SerializedShaderFloatValue op)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:578`
- **可见性**：private static
- **简要说明**：BlendOp enum → Add/Sub/RevSub/Min/Max/LogicalClear/...

### `ShaderConverter.ConvertBlendFactor(SerializedShaderFloatValue)`
- **签名**：`static string ConvertBlendFactor(SerializedShaderFloatValue factor)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:628`
- **可见性**：private static
- **简要说明**：BlendFactor enum → Zero/One/DstColor/SrcColor/...

### `ShaderConverter.ConvertSerializedTagMap(SerializedTagMap, int)`
- **签名**：`static string ConvertSerializedTagMap(SerializedTagMap m_Tags, int intent)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:658`
- **可见性**：private static
- **简要说明**：Tags 块

### `ShaderConverter.ConvertSerializedProperties(SerializedProperties)`
- **签名**：`static string ConvertSerializedProperties(SerializedProperties m_PropInfo)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:674`
- **可见性**：private static
- **调用了**：`ConvertSerializedProperty`
- **简要说明**：Properties 块

### `ShaderConverter.ConvertSerializedProperty(SerializedProperty)`
- **签名**：`static string ConvertSerializedProperty(SerializedProperty m_Prop)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:686`
- **可见性**：private static
- **抛出/异常**：未知类型抛 `ArgumentOutOfRangeException`
- **简要说明**：单条 Property

### `ShaderConverter.CheckGpuProgramUsable(ShaderCompilerPlatform, ShaderGpuProgramType)`
- **签名**：`static bool CheckGpuProgramUsable(ShaderCompilerPlatform platform, ShaderGpuProgramType programType)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:757`
- **可见性**：private static
- **抛出/异常**：NaCl/Flash/PSM 抛 `NotSupportedException`
- **简要说明**：平台/类型配对检查

### `ShaderConverter.GetPlatformString(ShaderCompilerPlatform)`
- **签名**：`static string GetPlatformString(ShaderCompilerPlatform platform)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:825`
- **可见性**：public static
- **简要说明**：platform enum → string（d3d11 / vulkan / metal / ...）

### `ShaderSubProgramEntry(EndianBinaryReader, int[])`
- **签名**：`ShaderSubProgramEntry(EndianBinaryReader reader, int[] version)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:897`
- **可见性**：public ctor
- **简要说明**：SubProgram 索引（offset/length/[segment]）

### `ShaderProgram(EndianBinaryReader, Shader)`
- **签名**：`ShaderProgram(EndianBinaryReader reader, Shader shader)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:915`
- **可见性**：public ctor
- **调用了**：`SerializedSubProgram.HasInstancedStructuredBuffers/HasGlobalLocalKeywordIndices`
- **简要说明**：解析 ShaderProgram 入口表

### `ShaderProgram.Read(EndianBinaryReader, int)`
- **签名**：`void Read(EndianBinaryReader reader, int segment)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:930`
- **可见性**：public
- **调用了**：`new ShaderSubProgram`
- **简要说明**：按 segment 读 entries[i]

### `ShaderProgram.Export(string)`
- **签名**：`string Export(string shader)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:943`
- **可见性**：public
- **简要说明**：替换 shader 文本中的 `GpuProgramIndex N` 为对应 SubProgram

### `ShaderSubProgram(EndianBinaryReader, bool)`
- **签名**：`ShaderSubProgram(EndianBinaryReader reader, bool hasUpdatedGpuProgram)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:963`
- **可见性**：public ctor
- **简要说明**：单个 SubProgram

### `ShaderSubProgram.Export()`
- **签名**：`string Export()`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:1006`
- **可见性**：public
- **调用了**：`Vortice.D3DCompiler.Compiler.Disassemble`、`HLSLDecompiler.DecompileShader`、`SpirVShaderConverter.Convert`
- **简要说明**：输出 SubProgram（按 m_ProgramType 分派）

### `ShaderSubProgram.ComputeHash64(Span<byte>)`
- **签名**：`ulong ComputeHash64(Span<byte> data)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:1158`
- **可见性**：public
- **简要说明**：FNV-1a 64 位

### `HLSLDecompiler.DecompileShader(byte[], int, out string)`
- **签名**：`static void DecompileShader(byte[] shaderByteCode, int shaderByteCodeSize, out string hlslText)`
- **位置**：`AssetStudio.Utility/ShaderConverter.cs:1177`
- **可见性**：public static
- **抛出/异常**：返回非零 error code 抛 `Exception("Unable to decompile shader, Error code: N")`
- **调用了**：内部 P/Invoke `Decompile` → `HLSLDecompiler.dll`
- **简要说明**：DX11 shader 字节码 → HLSL 文本

---

## 4. `AssetStudio.Utility/AssemblyLoader.cs`

### `AssemblyLoader.Load(string folder)`
- **签名**：`void Load(string folder)`
- **位置**：`AssetStudio.Utility/AssemblyLoader.cs`（参见 `Studio.MonoBehaviourToTypeTree` 中的调用）
- **调用**：
  - `AssetStudio.CLI/Program.cs:139`（CLI 的 `--dummy_dlls`）
  - `AssetStudio.GUI/Studio.cs:926`（GUI 弹窗选目录）
- **简要说明**：扫描 folder 下所有 .dll 并用 Mono.Cecil 加载

### `AssemblyLoader.Clear()`
- **签名**：`void Clear()`
- **位置**：`AssetStudio.Utility/AssemblyLoader.cs`
- **调用**：`MainForm.ResetForm` (`MainForm.cs:1585`)
- **简要说明**：清空缓存

### `AssemblyLoader.Loaded` 属性
- **签名**：`bool Loaded { get; set; }`
- **位置**：`AssetStudio.Utility/AssemblyLoader.cs`
- **调用**：`AssetStudio.GUI/Studio.cs:920`
- **简要说明**：是否已经加载

---

## 5. `AssetStudio.Utility/MonoBehaviourConverter.cs`

### `MonoBehaviourConverter.Convert(...)`
- **签名**：`Type Convert(MonoBehaviour m_MonoBehaviour, ...)`
- **位置**：`AssetStudio.Utility/MonoBehaviourConverter.cs`
- **调用**：被 `MonoBehaviour.ToType(TypeTree)` 调用
- **简要说明**：把 MonoBehaviour 的 raw 字节流按 TypeTree 解析为 .NET 对象

---

## 6. `AssetStudio.Utility/TypeDefinitionConverter.cs`

### `TypeDefinitionConverter.ConvertToTypeTree(...)`
- **签名**：`TypeTree ConvertToTypeTree(...)`
- **位置**：`AssetStudio.Utility/TypeDefinitionConverter.cs`
- **调用**：被 `MonoBehaviour.ConvertToTypeTree` 调用
- **简要说明**：从 Mono.Cecil TypeDefinition 构造 TypeTree

---

## 7. `AssetStudio.Utility/ModelExporter.cs`

### `ModelExporter.ExportFbx(string, IImported, Fbx.ExportOptions)`
- **签名**：`static void ExportFbx(string exportPath, IImported convert, Fbx.ExportOptions exportOptions)`
- **位置**：`AssetStudio.Utility/ModelExporter.cs`
- **调用**：
  - `AssetStudio.CLI/Exporter.cs:451`
  - `AssetStudio.GUI/Exporter.cs:479`
- **简要说明**：把 IImported 中间表示写入 .fbx（通过 FbxExporter → FbxDll → 原生 DLL）

---

## 8. `AssetStudio.Utility/AudioClipConverter.cs`

### `AudioClipConverter(AudioClip)`
- **签名**：`AudioClipConverter(AudioClip m_AudioClip)`
- **位置**：`AssetStudio.Utility/AudioClipConverter.cs`
- **调用**：`Exporter.ExportAudioClip`（CLI: `Exporter.cs:47`、GUI: `Exporter.cs:47`）
- **简要说明**：用 FMOD 探测音频格式

### `AudioClipConverter.IsSupport`
- **签名**：`bool IsSupport { get; }`
- **位置**：`AssetStudio.Utility/AudioClipConverter.cs`
- **调用**：`Exporter.ExportAudioClip`（CLI: `Exporter.cs:48`、GUI: `Exporter.cs:48`）
- **简要说明**：是否支持转 WAV

### `AudioClipConverter.ConvertToWav()`
- **签名**：`byte[] ConvertToWav()`
- **位置**：`AssetStudio.Utility/AudioClipConverter.cs`
- **调用**：`Exporter.ExportAudioClip`（CLI: `Exporter.cs:52`、GUI: `Exporter.cs:52`）
- **简要说明**：解码为 WAV

### `AudioClipConverter.GetExtensionName()`
- **签名**：`string GetExtensionName()`
- **位置**：`AssetStudio.Utility/AudioClipConverter.cs`
- **调用**：`Exporter.ExportAudioClip`（CLI: `Exporter.cs:59`、GUI: `Exporter.cs:59`）
- **简要说明**：原始格式扩展名（.fsb/.ogg/.wav/...）

---

## 9. `AssetStudio.Utility/SpriteHelper.cs`

### `Sprite.GetImage(this Sprite)`
- **签名**：`Image GetImage(this Sprite sprite)`
- **位置**：`AssetStudio.Utility/SpriteHelper.cs`
- **调用**：`Exporter.ExportSprite`（CLI: `Exporter.cs:277`、GUI: `Exporter.cs:277`）、`MainForm.PreviewSprite` (`MainForm.cs:1523`)
- **简要说明**：Sprite → Image

---

## 10. `AssetStudio.Utility/FontHelper.cs`

### `FontHelper.AddFontMemResourceEx(IntPtr, uint, IntPtr, ref uint)`
- **签名**：`static IntPtr AddFontMemResourceEx(IntPtr pbFont, uint cbFont, IntPtr pdv, ref uint pcFonts)`
- **位置**：`AssetStudio.Utility/FontHelper.cs`
- **调用**：`MainForm.PreviewFont` (`MainForm.cs:1212`)
- **简要说明**：P/Invoke GDI AddFontMemResourceEx

---

## 11. `AssetStudio.Utility/Texture2DExtensions.cs`

### `Texture2D.ConvertToImage(this Texture2D, bool mipChain)`
- **签名**：`Image ConvertToImage(this Texture2D texture, bool mipChain)`
- **位置**：`AssetStudio.Utility/Texture2DExtensions.cs`
- **调用**：`Exporter.ExportTexture2D`（CLI: `Exporter.cs:20`、GUI: `Exporter.cs:20`）、`MainForm.PreviewTexture2D` (`MainForm.cs:991`)
- **调用了**：`Texture2DConverter.DecodeTexture2D`
- **简要说明**：Texture2D → Image

### `Texture2D.ConvertToStream(this Texture2D, ImageFormat, bool)`
- **签名**：`Stream ConvertToStream(this Texture2D texture, ImageFormat imageFormat, bool mipChain)`
- **位置**：`AssetStudio.Utility/Texture2DExtensions.cs`
- **调用**：`ModelConverter.ConvertTexture2D` (`ModelConverter.cs:778`)
- **简要说明**：Texture2D → 图像 Stream

---

## 12. `AssetStudio.Utility/ImageExtensions.cs`

### `Image.WriteToStream(this Image, Stream, ImageFormat)`
- **签名**：`void WriteToStream(this Image image, Stream stream, ImageFormat format)`
- **位置**：`AssetStudio.Utility/ImageExtensions.cs`
- **调用**：`Exporter.ExportTexture2D`（CLI: `Exporter.cs:27`、GUI: `Exporter.cs:27`）、`Exporter.ExportSprite`（CLI: `Exporter.cs:284`、GUI: `Exporter.cs:284`）
- **简要说明**：写图像到流

### `Image.ConvertToBytes(this Image)`
- **签名**：`byte[] ConvertToBytes(this Image image)`
- **位置**：`AssetStudio.Utility/ImageExtensions.cs`
- **调用**：`MainForm.PreviewTexture2D` (`MainForm.cs:994`)、`MainForm.PreviewSprite` (`MainForm.cs:1526`)
- **简要说明**：Image → BGRA bytes

---

## 13. `AssetStudio.Utility/ImageFormat.cs`

### `ImageFormat` enum
- **位置**：`AssetStudio.Utility/ImageFormat.cs`
- **值**：`Png / Jpeg / Bmp / Webp`
- **简要说明**：导出图像格式选项

---

## 14. `AssetStudio.Utility/ConsoleHelper.cs`

### `ConsoleHelper.AllocConsole()`
- **位置**：`AssetStudio.Utility/ConsoleHelper.cs`
- **调用**：`MainForm.InitializeLogger` (`MainForm.cs:121`)
- **简要说明**：分配控制台（GUI 子窗口）

### `ConsoleHelper.SetConsoleTitle(string)`
- **位置**：`AssetStudio.Utility/ConsoleHelper.cs`
- **调用**：`MainForm.InitializeLogger` (`MainForm.cs:122`)
- **简要说明**：设置标题

### `ConsoleHelper.GetConsoleWindow()`
- **位置**：`AssetStudio.Utility/ConsoleHelper.cs`
- **调用**：`MainForm.InitializeLogger`、`MainForm.enableConsole_CheckedChanged`
- **简要说明**：取控制台窗口句柄

### `ConsoleHelper.ShowWindow(IntPtr, int)`
- **位置**：`AssetStudio.Utility/ConsoleHelper.cs`
- **调用**：`MainForm.InitializeLogger`、`MainForm.enableConsole_CheckedChanged`
- **简要说明**：显示/隐藏窗口（SW_SHOW / SW_HIDE）

---

## 15. `AssetStudio.Utility/SpirVShaderConverter.cs`

### `SpirVShaderConverter.Convert(byte[])`
- **签名**：`static string Convert(byte[] programCode)`
- **位置**：`AssetStudio.Utility/SpirVShaderConverter.cs`
- **调用**：`ShaderSubProgram.Export` (`ShaderConverter.cs:1134`)
- **简要说明**：SPIRV → 文本（通过 Smolv）