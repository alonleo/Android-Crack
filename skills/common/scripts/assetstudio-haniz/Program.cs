using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using AssetStudio;

class Program
{
    // 导出 MonoBehaviour 的 TypeTree 字段布局
    static int Main(string[] args)
    {
        // args: <data.unity3d> <dummydll> <out.json>
        if (args.Length < 3)
        {
            Console.Error.WriteLine("usage: HanizationTool <data.unity3d> <dummydll> <out.json>");
            return 1;
        }
        var dataPath = args[0];
        var dllPath = args[1];
        var outJson = args[2];

        var assemblyLoader = new AssemblyLoader();
        assemblyLoader.Load(dllPath);
        Console.WriteLine($"DummyDll loaded: {assemblyLoader.Loaded}");

        var assetsManager = new AssetsManager();
        assetsManager.Game = GameManager.GetGame("Normal");
        // 诊断 FileType
        using (var testReader = new FileReader(dataPath))
        {
            Console.WriteLine($"FileType: {testReader.FileType}");
            if (testReader.FileType == FileType.BundleFile)
            {
                var bf = new BundleFile(testReader, assetsManager.Game);
                Console.WriteLine($"Bundle files: {bf.fileList?.Count}");
                if (bf.fileList != null)
                    foreach (var f in bf.fileList.Take(20))
                        Console.WriteLine($"  {f.fileName} ({f.stream?.Length})");
            }
        }
        assetsManager.LoadFiles(dataPath);
        Console.WriteLine($"Assets loaded: {assetsManager.assetsFileList.Count} files");

        var results = new List<object>();
        int mbCount = 0;
        foreach (var af in assetsManager.assetsFileList)
        {
            foreach (var obj in af.Objects)
            {
                if (obj is MonoBehaviour mb)
                {
                    mbCount++;
                    try
                    {
                        var scriptName = mb.m_Script?.TryGet(out var ms) == true ? ms.m_ClassName : "";
                        // 对 Text 组件，dump 原始数据用于布局分析
                        if (scriptName == "Text" || scriptName == "TextMeshProUGUI" || scriptName == "TMP_Text")
                        {
                            var bytes = mb.GetRawData();
                            if (bytes != null)
                            {
                                var entry = new
                                {
                                    file = af.fileName,
                                    pathID = mb.m_PathID,
                                    name = mb.Name,
                                    script = scriptName,
                                    rawLen = bytes.Length,
                                    hex = Convert.ToHexString(bytes),
                                };
                                results.Add(entry);
                            }
                        }
                    }
                    catch (Exception)
                    {
                    }
                }
            }
        }
        var json = JsonSerializer.Serialize(results, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(outJson, json);
        Console.WriteLine($"MonoBehaviour total={mbCount}, parsed={results.Count} → {outJson}");
        return 0;
    }

    static void DumpNodes(List<TypeTreeNode> nodes, int idx, int level, List<object> outList)
    {
        if (idx >= nodes.Count) return;
        var n = nodes[idx];
        outList.Add(new { type = n.m_Type, name = n.m_Name, byteSize = n.m_ByteSize, level = n.m_Level });
        // 子节点
        var childIdx = idx + 1;
        if (childIdx < nodes.Count && nodes[childIdx].m_Level > n.m_Level)
        {
            while (childIdx < nodes.Count && nodes[childIdx].m_Level > n.m_Level)
            {
                DumpNodes(nodes, childIdx, level + 1, outList);
                // 跳到同级
                int next = childIdx + 1;
                while (next < nodes.Count && nodes[next].m_Level > n.m_Level) next++;
                childIdx = next;
            }
        }
    }
}
