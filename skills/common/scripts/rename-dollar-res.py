#!/usr/bin/env python3
"""
rename-dollar-res.py — 修复 APK 内 `$` 前缀资源文件（Android 资源命名不规范）。

背景: 部分游戏（如 Nexters Hero Wars）为反破解，在 APK 内使用 `$` 前缀资源文件
（如 res/drawable/$mtrl_switch_thumb_checked_pressed__0.xml），并由其他 XML 通过
`@drawable/$name__N` 引用。AGP/aapt2 编译时拒绝 `$` 作为 file-based 资源名。

方案: 将 `$name__N.xml` 重命名为合法名 `_f` + 原 base（小写字母/数字/下划线），
并同步更新所有 XML 中对该资源的引用（@type/$name → @type/新名）。

用法:
  python3 rename-dollar-res.py <project_root_or_res_dir>

依赖: Python 3 标准库。幂等：重复运行无副作用。
"""
import os
import re
import sys

DOLLAR_RE = re.compile(r"\$([a-z0-9_]+__[0-9]+)")


def safe_name(base: str) -> str:
    # $mtrl_switch_thumb_checked_pressed__0 → _f_mtrl_switch_thumb_checked_pressed__0
    return "_f_" + base


def iter_res_files(res_dir: str):
    for root, _dirs, files in os.walk(res_dir):
        for f in files:
            yield os.path.join(root, f)


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: rename-dollar-res.py <res_dir>", file=sys.stderr)
        return 1
    res_dir = sys.argv[1]
    if not os.path.isdir(res_dir):
        print(f"res 目录不存在: {res_dir}", file=sys.stderr)
        return 1

    # 1. 收集 $ 前缀文件 → 新名（key = 裸资源名，如 mtrl_switch_thumb_checked_pressed__0）
    #    双重来源：res 文件系统 + values/public.xml（apktool 生成的 <public name="$...">）
    rename_map = {}
    for path in iter_res_files(res_dir):
        base = os.path.basename(path)
        m = DOLLAR_RE.match(base)
        if m:
            bare = m.group(1)
            rename_map[bare] = {"file": base, "new_file": safe_name(bare) + os.path.splitext(base)[1]}
    public_path = os.path.join(res_dir, "values", "public.xml")
    if os.path.isfile(public_path):
        for m in re.finditer(r'name="(\$[a-z0-9_]+__[0-9]+)"', open(public_path, encoding="utf-8").read()):
            bare = m.group(1)[1:]
            rename_map.setdefault(bare, {"file": None, "new_file": safe_name(bare) + ".xml"})

    # 2. 重命名文件（幂等：已重命名的跳过）
    if rename_map:
        for bare, info in rename_map.items():
            if info["file"] is None:
                continue
            for path in iter_res_files(res_dir):
                if os.path.basename(path) == info["file"]:
                    new_path = os.path.join(os.path.dirname(path), info["new_file"])
                    os.rename(path, new_path)
                    print(f"[RENAME] {os.path.relpath(path, res_dir)} -> {info['new_file']}")
                    break
    else:
        print("[INFO] 无 $ 前缀资源，跳过")
        return 0

    # 3. 更新 XML 引用 @type/$name → @type/新名
    ref_updates = 0
    for path in iter_res_files(res_dir):
        if not path.endswith(".xml"):
            continue
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        orig = content

        def _repl(m):
            nonlocal ref_updates
            res_type, name = m.group(1), m.group(2)
            if name in rename_map:
                new_bare = safe_name(name)
                ref_updates += 1
                return f"@{res_type}/{new_bare}"
            return m.group(0)

        content = re.sub(r"@([a-z0-9_]+)/\$([a-z0-9_]+__[0-9]+)", _repl, content)
        # 4. public.xml 的 <public type="X" name="$name" id="..."/> 同步改名
        if "public.xml" in path:
            content = re.sub(
                r'(<public[^>]*name=")(\$[a-z0-9_]+__[0-9]+)(")',
                lambda m: m.group(1) + safe_name(m.group(2)[1:]) + m.group(3),
                content,
            )
        if content != orig:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            print(f"[REF] {os.path.relpath(path, res_dir)}")

    print(f"[OK] 重命名 {len(rename_map)} 个文件，更新 {ref_updates} 处引用")
    return 0


if __name__ == "__main__":
    sys.exit(main())
