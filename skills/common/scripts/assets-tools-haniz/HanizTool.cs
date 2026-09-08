using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

class Program
{
    static Dictionary<string, string> translations = new Dictionary<string, string>(StringComparer.Ordinal);

    static void Main(string[] args)
    {
        // args: <data.unity3d> <translations.json> <out>
        if (args.Length < 3)
        {
            Console.Error.WriteLine("usage: HanizTool <data.unity3d> <translations.json> <out>");
            return;
        }
        var bundlePath = args[0];
        var transPath = args[1];
        var outPath = args[2];

        var trans = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, string>>(File.ReadAllText(transPath));
        translations = new Dictionary<string, string>(trans, StringComparer.Ordinal);
        Console.WriteLine($"Translations: {translations.Count}");

        var manager = new AssetsManager();
        var bunInst = manager.LoadBundleFile(bundlePath);
        Console.WriteLine($"Bundle: {bunInst.file.BlockAndDirInfo.DirectoryInfos.Length} files");

        int totalReplaced = 0;
        var bundleReplacers = new List<BundleReplacer>();

        for (int i = 0; i < bunInst.file.BlockAndDirInfo.DirectoryInfos.Length; i++)
        {
            var di = bunInst.file.BlockAndDirInfo.DirectoryInfos[i];
            if (di.Name.EndsWith(".resS"))
                continue;
            var afInst = manager.LoadAssetsFileFromBundle(bunInst, i, false);
            if (afInst == null) continue;
            var af = afInst.file;
            Console.WriteLine($"\n=== {di.Name} ({af.Metadata.AssetInfos.Count} objects) ===");

            var replacers = new List<AssetsReplacer>();
            foreach (var info in af.Metadata.AssetInfos)
            {
                if (info.TypeId != 114) continue; // MonoBehaviour
                try
                {
                    // 读原始数据
                    var reader2 = af.Reader;
                    reader2.Position = info.GetAbsoluteByteStart(af.Header);
                    var bytes = reader2.ReadBytes((int)info.ByteSize);
                    // 找 m_Text: 扫描 string 格式（int32 len + utf8）
                    var mod = ModifyText(bytes);
                    if (mod != null && mod.Length != bytes.Length)
                    {
                        replacers.Add(new AssetsReplacerFromMemory(af, info, mod));
                        totalReplaced++;
                        Console.WriteLine($"  pathID={info.PathId}: size {bytes.Length}->{mod.Length}");
                    }
                }
                catch (Exception)
                {
                }
            }
            if (replacers.Count > 0)
            {
                bundleReplacers.Add(new BundleReplacerFromAssets(di.Name, di.Name, af, replacers));
                Console.WriteLine($"  [{di.Name}] {replacers.Count} replacers");
            }
        }

        // 写回 bundle
        if (totalReplaced > 0)
        {
            using (var fs = File.Create(outPath))
            {
                var w = new AssetsFileWriter(fs);
                bunInst.file.Write(w, bundleReplacers);
            }
            Console.WriteLine($"\n[OK] 写回 {outPath}, replaced {totalReplaced}");
        }
        else
        {
            Console.WriteLine("\n无替换");
        }
    }

    // 修改原始数据中的 m_Text（变长）
    static byte[] ModifyText(byte[] bytes)
    {
        int changed = 0;
        var list = new List<byte[]>();
        // 扫描所有 string（可能多个字段），找匹配翻译的
        int i = 0;
        var newBytes = bytes;
        while (i < newBytes.Length - 4)
        {
            int len = BitConverter.ToInt32(newBytes, i);
            if (len >= 2 && len <= 80 && i + 4 + len <= newBytes.Length)
            {
                var data = newBytes.Skip(i + 4).Take(len).ToArray();
                try
                {
                    var s = System.Text.Encoding.UTF8.GetString(data);
                    if (translations.ContainsKey(s))
                    {
                        var zh = System.Text.Encoding.UTF8.GetBytes(translations[s]);
                        // 重建：头 + 新len + 新str + 尾
                        var head = newBytes.Take(i).ToArray();
                        var tail = newBytes.Skip(i + 4 + len).ToArray();
                        var rebuilt = new byte[head.Length + 4 + zh.Length + tail.Length];
                        Buffer.BlockCopy(head, 0, rebuilt, 0, head.Length);
                        Buffer.BlockCopy(BitConverter.GetBytes(zh.Length), 0, rebuilt, head.Length, 4);
                        Buffer.BlockCopy(zh, 0, rebuilt, head.Length + 4, zh.Length);
                        Buffer.BlockCopy(tail, 0, rebuilt, head.Length + 4 + zh.Length, tail.Length);
                        newBytes = rebuilt;
                        Console.WriteLine($"    '{s}' -> '{translations[s]}' @off{i}");
                        changed++;
                        i += 4 + zh.Length;
                        continue;
                    }
                }
                catch (Exception) { }
            }
            i++;
        }
        return changed > 0 ? newBytes : null;
    }
}
