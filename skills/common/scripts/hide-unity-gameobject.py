#!/usr/bin/env python3
"""hide-unity-gameobject.py — 隐藏 Unity 场景中的 GameObject（m_IsActive=False）。

背景: Unity il2cpp 游戏打包为 BundleFile（data.unity3d），内含 level0/level1/... 场景。
移除游戏 Logo/游戏名：找到目标 GameObject（如 logo/Title/imgTitle），设 m_IsActive=False，
在场景加载时该对象不实例化，无需 native hook（ARM32 兼容）。

用法:
  # 隐藏单个场景单个对象
  python3 hide-unity-gameobject.py <data.unity3d> <scene> <name> [-o out]

  # 多场景多名称（逗号分隔，批量）—— 主菜单 + 加载页标题一次处理
  python3 hide-unity-gameobject.py data.unity3d "level0,level1" "imgTitle,imgtitle,Title,logo" -o data-hidden.unity3d

  # 列出 BundleFile 子文件
  python3 hide-unity-gameobject.py <data.unity3d> --list

  # 空 name + --list-objects：列出指定场景全部 GameObject（含 pid/active）辅助定位
  python3 hide-unity-gameobject.py <data.unity3d> <scene> --list-objects

匹配规则:
  - 名称大小写不敏感匹配（Title 匹配 title/TITLE/Title）
  - 支持多个 name 逗号分隔（任一命中即隐藏）
  - 支持多个 scene 逗号分隔（全部处理）

原理:
  - UnityPy 加载 data.unity3d（BundleFile）
  - 进入子文件 scene_file（SerializedFile）
  - 遍历 GameObject，匹配 m_Name → 设 m_IsActive=False
  - 用 file.save() 重打包 BundleFile 写回

参考: HighwayBikeAttackRaceGame (2026-08-09) 移除主菜单 Title + 加载页 imgTitle/imgtitle
"""
from __future__ import annotations

import argparse
import sys

import UnityPy


def list_scenes(input: str) -> int:
    env = UnityPy.load(input)
    f = env.file
    if not hasattr(f, 'files'):
        print("[ERROR] 不是 BundleFile，无子文件")
        return 1
    print("BundleFile 内子文件:")
    for name in f.files.keys():
        print(f"  {name}")
    return 0


def list_objects(input: str, scene: str) -> int:
    env = UnityPy.load(input)
    f = env.file
    if not hasattr(f, 'files') or scene not in f.files:
        print(f"[ERROR] 子文件 {scene!r} 不存在（用 --list 查看）")
        return 1
    sf = f.files[scene]
    print(f"=== {scene} GameObject 清单（pid / name / active）===")
    for obj in sf.objects.values():
        if obj.type.name != 'GameObject':
            continue
        try:
            t = obj.read_typetree()
            print(f"  pid={obj.path_id:6d}  {t.get('m_Name',''):30s} active={t.get('m_IsActive')}")
        except Exception as e:
            print(f"  pid={obj.path_id}: ERR {str(e)[:60]}")
    return 0


def hide_objects(input: str, scenes: list[str], names: list[str], out: str | None, pids: list[int] | None = None) -> int:
    env = UnityPy.load(input)
    f = env.file
    if not hasattr(f, 'files'):
        print("[ERROR] 不是 BundleFile，无子文件")
        return 1

    # 归一化名称（小写集合）
    name_set = {n.strip().lower() for n in names if n.strip()}

    total_changed = 0
    for scene in scenes:
        if scene not in f.files:
            print(f"[WARN] 子文件 {scene!r} 不存在，跳过")
            continue
        sf = f.files[scene]
        changed = 0
        for obj in sf.objects.values():
            if obj.type.name != 'GameObject':
                continue
            try:
                t = obj.read_typetree()
                gname = t.get('m_Name', '')
                gpid = obj.path_id
                # 匹配：name 命中 或 pid 命中
                name_hit = gname.lower() in name_set
                pid_hit = pids and gpid in pids
                if not (name_hit or pid_hit):
                    continue
                label = f"{scene}/{gname}(pid={gpid})"
                if t.get('m_IsActive', True) is not False:
                    t['m_IsActive'] = False
                    raw = obj.save_typetree(t)
                    if not raw:
                        print(f"[WARN] {label} save_typetree 空")
                        continue
                    obj.set_raw_data(raw)
                    changed += 1
                    print(f"[OK] {label} → m_IsActive=False")
                else:
                    print(f"[SKIP] {label} 已隐藏")
            except Exception as e:
                print(f"[ERR] {scene} pid={obj.path_id}: {e}")
        if changed:
            print(f"[INFO] {scene}: 隐藏 {changed} 个对象")
        total_changed += changed

    if total_changed == 0:
        print(f"[ERROR] 未找到任何匹配对象（scene={scenes} names={names}）")
        return 1

    target = out or input
    data = env.file.save()
    with open(target, 'wb') as fh:
        fh.write(data)
    print(f"[OK] 已保存 → {target}（{len(data)} bytes，共隐藏 {total_changed} 个）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="data.unity3d 路径")
    ap.add_argument("scene", nargs="?", default=None, help="子场景名，可逗号分隔（level0,level1/...）")
    ap.add_argument("name", nargs="?", default=None, help="GameObject m_Name，可逗号分隔（imgTitle,Title/...）")
    ap.add_argument("--list", action="store_true", help="列出 BundleFile 子文件")
    ap.add_argument("--list-objects", action="store_true", help="列出指定 scene 全部 GameObject")
    ap.add_argument("--pid", default=None, help="按 path_id 精确隐藏（逗号分隔；与 name 二选一或并用）")
    ap.add_argument("-o", "--out", default=None, help="输出路径（默认覆盖）")
    args = ap.parse_args()

    if args.list:
        return list_scenes(args.input)
    if args.list_objects:
        if not args.scene:
            ap.error("--list-objects 需要 scene 参数")
        return list_objects(args.input, args.scene)
    if not args.scene or not (args.name or args.pid):
        ap.error("需要 scene + name（或 --pid / --list / --list-objects）")
    scenes = [s.strip() for s in args.scene.split(',') if s.strip()]
    names = [n.strip() for n in (args.name or '').split(',') if n.strip()]
    pids = [int(p) for p in (args.pid or '').split(',') if p.strip().isdigit()]
    return hide_objects(args.input, scenes, names, args.out, pids or None)


if __name__ == "__main__":
    sys.exit(main())
