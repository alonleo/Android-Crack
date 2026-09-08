#!/usr/bin/env python3
"""
inspect-gamemaker-rooms.py — 检查 GameMaker .droid 的房间/实例/对象/代码结构。

来源: FindTheDifferences (com.TanApps.FindTheDifferences300) | 2026-08-09

用途:
  「去功能点/按钮移除」前的探索阶段：列出所有房间、图层、实例（含对象名/坐标），
  以及可选列出全部对象名、引用指定对象的代码条目（定位动态创建）。

用法:
  python3 inspect-gamemaker-rooms.py <game.droid> [--rooms] [--objects] [--code <对象名>]

参数:
  <game.droid>   GameMaker 数据归档（assets/game.droid）
  --rooms        列出所有房间 + 图层 + 实例（对象名/坐标/ID）
  --objects      列出全部 Game Object 名
  --code <name>  列出引用指定对象名的代码条目（如 oShare → 找动态创建）

依赖:
  - dotnet
  - tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll

示例:
  # 看所有房间和按钮实例
  python3 inspect-gamemaker-rooms.py assets/game.droid --rooms
  # 看对象名
  python3 inspect-gamemaker-rooms.py assets/game.droid --objects
  # 找谁动态创建 oShare
  python3 inspect-gamemaker-rooms.py assets/game.droid --code oShare
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
CLI_DLL = REPO / "tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll"

# 房间/实例 dump（包含 layer + flat GameObjects 双列表）
ROOMS_CSX = r'''
foreach (var room in Data.Rooms)
{
    Console.WriteLine("Room '" + (room.Name != null ? room.Name.Content : "?") + "' size=" + room.Width + "x" + room.Height);
    foreach (var layer in room.Layers)
    {
        if (layer.InstancesData == null || layer.InstancesData.Instances.Count == 0) continue;
        string lname = layer.LayerName != null ? layer.LayerName.Content : "?";
        foreach (var inst in layer.InstancesData.Instances)
        {
            string on = inst.ObjectDefinition?.Name?.Content ?? "?";
            Console.WriteLine("  L inst=" + inst.InstanceID + " pos=(" + inst.X + "," + inst.Y + ") obj='" + on + "'");
        }
    }
    foreach (var go in room.GameObjects)
    {
        string on = go.ObjectDefinition?.Name?.Content ?? "?";
        Console.WriteLine("  F inst=" + go.InstanceID + " pos=(" + go.X + "," + go.Y + ") obj='" + on + "'");
    }
}
'''

# 对象名 dump
OBJECTS_CSX = r'''
foreach (var obj in Data.GameObjects)
{
    Console.WriteLine(obj.Name?.Content);
}
'''

def run_csx(droid: Path, csx_body: str) -> int:
    """把 C# 脚本喂给 UndertaleModCli load 运行。"""
    with tempfile.TemporaryDirectory(prefix="gminspect_") as tmp:
        script = Path(tmp) / "inspect.csx"
        script.write_text(csx_body)
        r = subprocess.run(
            ["dotnet", str(CLI_DLL), "load", str(droid), "-s", str(script)],
            capture_output=True, text=True,
        )
        out = r.stdout.replace("Trying to load file: '" + str(droid) + "'\n", "")
        if out.strip():
            print(out)
        if r.stderr and "error" in r.stderr.lower():
            print(r.stderr)
        return r.returncode


def find_code_refs(droid: Path, target: str) -> None:
    """用 CLI dump 全部代码 → grep 引用指定对象名的代码条目。"""
    with tempfile.TemporaryDirectory(prefix="gminspect_") as tmp:
        dump_dir = Path(tmp)
        r = subprocess.run(
            ["dotnet", str(CLI_DLL), "dump", str(droid), "-c", "UMT_DUMP_ALL", "-o", str(dump_dir)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"[ERROR] dump 失败: {r.stderr}")
            return
        hits = 0
        for gml in sorted((dump_dir / "CodeEntries").glob("*.gml")):
            content = gml.read_text(errors="replace")
            if target in content:
                print(gml.name)
                hits += 1
        if hits == 0:
            print(f"（未找到引用 {target} 的代码）")


def main():
    parser = argparse.ArgumentParser(description="检查 GameMaker .droid 结构")
    parser.add_argument("droid", help="game.droid 路径")
    parser.add_argument("--rooms", action="store_true", help="列出房间/图层/实例")
    parser.add_argument("--objects", action="store_true", help="列出全部对象名")
    parser.add_argument("--code", default="", help="列出引用指定对象名的代码条目")
    args = parser.parse_args()

    droid = Path(args.droid)
    if not droid.exists():
        print(f"[ERROR] 文件不存在: {droid}")
        sys.exit(2)
    if not CLI_DLL.exists():
        print(f"[ERROR] UndertaleModCli.dll 不存在: {CLI_DLL}")
        sys.exit(2)

    if args.rooms:
        print("=== ROOMS / INSTANCES ===")
        run_csx(droid, ROOMS_CSX)
    if args.objects:
        print("=== GAME OBJECTS ===")
        run_csx(droid, OBJECTS_CSX)
    if args.code:
        print(f"=== 引用 {args.code} 的代码条目 ===")
        find_code_refs(droid, args.code)

    if not (args.rooms or args.objects or args.code):
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())