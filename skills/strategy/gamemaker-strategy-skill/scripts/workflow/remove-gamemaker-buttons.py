#!/usr/bin/env python3
"""
remove-gamemaker-buttons.py — 从 GameMaker .droid 归档移除指定对象实例（按钮）。

来源: FindTheDifferences (com.TanApps.FindTheDifferences300) | 2026-08-09

原理:
  GameMaker 的按钮对象实例可能出现在两处：
  1. **房间实例**（ROOM chunk）：GMS2 每个房间有三份实例数据，必须全清：
     - layer.InstancesData.Instances（层实例）
     - room.GameObjects（扁平列表，引擎 VM 实际据此创建实例）★关键
     - room.InstanceCreationOrderIDs（创建顺序）
  2. **动态创建**（GML 代码）：如 `instance_create_depth(..., oShare)` → 需用
     UndertaleModCli `replace -c 'gml_...=./new.gml'` 重编译替换代码。

  ⚠️ 教训（2026-08-09）: 只清 layer 实例不够 —— 引擎从 room.GameObjects 创建，
  必须三处全清按钮才真正消失/不可点击。

用法:
  python3 remove-gamemaker-buttons.py <game.droid> --objects oMore,oPrivacyPolicy,oShare \
      --replace "gml_Object_oPlayOptions_Mouse_7=/path/to/new.gml" \
      --out <out.droid>

参数:
  <game.droid>      GameMaker 数据归档（assets/game.droid）
  --objects         逗号分隔的要移除的对象名（房间实例）
  --replace         可选，可重复。代码替换（动态创建）："代码条目=新.gml 路径"
  --out             输出路径（默认在输入目录生成 game.modified.droid）

依赖:
  - dotnet
  - tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll

示例:
  # 移除房间按钮 + 替换动态创建代码
  python3 remove-gamemaker-buttons.py assets/game.droid \
      --objects oMore,oPrivacyPolicy,oShare,oInf \
      --replace "gml_Object_oPlayOptions_Mouse_7=./noShare.gml" \
      --out /tmp/game-modified.droid
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
CLI_DLL = REPO / "tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll"

# C# 脚本模板：按对象名移除房间实例
# 注意：这是普通字符串（非 f-string），C# 的花括号保留原样，%OBJECTS% 用 replace 填充
# GMS2 房间实例存在三处：layer.InstancesData.Instances + room.GameObjects（扁平列表）+ room.InstanceCreationOrderIDs
# 引擎 VM 从 room.GameObjects 创建实例 → 必须三处都清，否则按钮仍会创建/可点击
CSX_TEMPLATE = r'''
var targets = new HashSet<string> { %OBJECTS% };
int removed = 0;
foreach (var room in Data.Rooms)
{
    // 1) 层实例列表
    foreach (var layer in room.Layers)
    {
        if (layer.InstancesData == null) continue;
        var instances = layer.InstancesData.Instances;
        for (int i = instances.Count - 1; i >= 0; i--)
        {
            string objName = instances[i].ObjectDefinition?.Name?.Content;
            if (objName != null && targets.Contains(objName))
            {
                string rname = room.Name != null ? room.Name.Content : "?";
                string lname = layer.LayerName != null ? layer.LayerName.Content : "?";
                Console.WriteLine("  [layer] 移除 Room '" + rname + "' layer '" + lname + "' inst id=" + instances[i].InstanceID + " obj='" + objName + "' pos=(" + instances[i].X + "," + instances[i].Y + ")");
                instances.RemoveAt(i);
                removed++;
            }
        }
    }
    // 2) 扁平 GameObjects 列表（引擎实际创建实例用）
    for (int i = room.GameObjects.Count - 1; i >= 0; i--)
    {
        string objName = room.GameObjects[i].ObjectDefinition?.Name?.Content;
        if (objName != null && targets.Contains(objName))
        {
            uint instId = room.GameObjects[i].InstanceID;
            Console.WriteLine("  [flat]  移除 Room '" + (room.Name != null ? room.Name.Content : "?") + "' inst id=" + instId + " obj='" + objName + "'");
            room.GameObjects.RemoveAt(i);
            removed++;
            // 3) 同步清理 InstanceCreationOrderIDs
            if (room.InstanceCreationOrderIDs != null)
            {
                for (int j = room.InstanceCreationOrderIDs.InstanceIDs.Count - 1; j >= 0; j--)
                {
                    if (room.InstanceCreationOrderIDs.InstanceIDs[j] == instId)
                    {
                        room.InstanceCreationOrderIDs.InstanceIDs.RemoveAt(j);
                    }
                }
            }
        }
    }
}
Console.WriteLine("\n共移除 " + removed + " 个实例");
'''


def run_cli(args_list: list) -> int:
    """运行 UndertaleModCli 并打印输出。"""
    r = subprocess.run(
        ["dotnet", str(CLI_DLL)] + args_list,
        capture_output=True, text=True,
    )
    print(r.stdout)
    if r.stderr:
        print(r.stderr)
    return r.returncode


def main():
    parser = argparse.ArgumentParser(description="从 GameMaker .droid 移除对象实例（按钮）")
    parser.add_argument("droid", help="game.droid 路径")
    parser.add_argument("--objects", default="oMore,oPrivacyPolicy,oShare",
                        help="要移除的对象名（逗号分隔），房间实例三处全清")
    parser.add_argument("--replace", action="append", default=[],
                        help="代码替换（动态创建）：'代码条目=新.gml路径'，可重复")
    parser.add_argument("--out", default="", help="输出 .droid 路径（默认 game.modified.droid 同目录）")
    args = parser.parse_args()

    droid = Path(args.droid)
    if not droid.exists():
        print(f"[ERROR] 文件不存在: {droid}")
        sys.exit(2)
    if not CLI_DLL.exists():
        print(f"[ERROR] UndertaleModCli.dll 不存在: {CLI_DLL}（需先构建 UndertaleModTool）")
        sys.exit(2)
    if not shutil.which("dotnet"):
        print("[ERROR] 需要 dotnet")
        sys.exit(2)

    objects = [o.strip() for o in args.objects.split(",") if o.strip()]
    out = Path(args.out) if args.out else droid.parent / "game.modified.droid"

    # 1) 生成 .csx 脚本：移除房间实例（三处全清）
    obj_list = ", ".join(f'"{o}"' for o in objects)
    csx = CSX_TEMPLATE.replace("%OBJECTS%", obj_list)
    with tempfile.TemporaryDirectory(prefix="umbutton_") as tmp:
        script = Path(tmp) / "remove.csx"
        script.write_text(csx)
        print(f"[1/3] 移除房间对象: {objects}")
        print(f"      源: {droid}")
        print(f"      出: {out}")
        rc = run_cli(["load", str(droid), "-s", str(script), "-o", str(out), "-f"])
        if rc != 0:
            print(f"[ERROR] 房间移除失败 rc={rc}")
            sys.exit(3)

    # 2) 代码替换（动态创建的对象）
    if args.replace:
        print(f"[2/3] 代码替换: {args.replace}")
        for kv in args.replace:
            if "=" not in kv:
                print(f"  [WARN] 忽略无效 --replace: {kv}（应为 '代码条目=文件路径'）")
                continue
            code_name, file_path = kv.split("=", 1)
            if not Path(file_path).exists():
                print(f"  [WARN] 新代码文件不存在: {file_path}")
                continue
            rc = run_cli(["replace", str(out), "-c", f"{code_name}={file_path}", "-o", str(out)])
            if rc != 0:
                print(f"[ERROR] 代码替换失败 rc={rc}")
                sys.exit(3)
            print(f"  [OK] 已替换 {code_name}")
    else:
        print("[2/3] 无代码替换（--replace 未指定）")

    if not out.exists():
        print(f"[ERROR] 未生成输出: {out}")
        sys.exit(3)

    print(f"[3/3] 输出: {out} ({out.stat().st_size} bytes)")
    print(f"      用修改后的 .droid 替换 APK 内 assets/game.droid")
    return 0


if __name__ == "__main__":
    main()