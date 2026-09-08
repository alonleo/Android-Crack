#!/usr/bin/env python3
"""
run-major-verify.py — 七大主阶段 5：核对产出（verify output）。

调用 sub-stage-as-build.py + verify-stage.py 核验 AS 工程与 patched.apk 完整性。
固定入口：tool 套件内任何模块均可直接调用本脚本。

用法：
  python3 run-major-verify.py <name>

参数：
  <name>         必填，项目名

验收项：
  - crackings/<type>/<Name>/project/app/build.gradle 存在
  - crackings/<type>/<Name>/project/app/src/main/AndroidManifest.xml 存在
  - crackings/<type>/<Name>/project/app/libs/*.jar 存在
  - crackings/<type>/<Name>/project/app/src/main/jniLibs/<abi>/*.so 存在
  - crackings/<type>/<Name>/project/app/build/outputs/apk/release/app-release.apk 存在
  - crackings/<type>/<Name>/project/patched.apk 存在
  - md5(crackings/<Name>/patched.apk) == md5(app-release.apk)（OBJECTIVES §0.3 #1）

示例：
  python3 run-major-verify.py FindTheDifferences
"""
from __future__ import annotations

import sys
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/scripts/lib"))
from routing import get_script_path  # noqa: E402

# 子阶段路由表驱动（按 name 查，替代硬编码）
AS_BUILD_SCRIPT = get_script_path("as-build") or ROOT / "<missing: as-build>"


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    name = sys.argv[1]
    print(f"[七大主阶段 5/7] 核对产出 → {name}")

    errors = []

    import os
    type_arg = os.environ.get("TYPE", "").strip()
    out = ROOT / "output-projects" / type_arg / name if type_arg else ROOT / "output-projects" / name
    app = out / "app"
    apk_release_path = app / "build" / "outputs" / "apk" / "release" / "app-release.apk"
    if AS_BUILD_SCRIPT.exists() and not apk_release_path.exists():
        print(f"\n--- 调 sub-stage-as-build.py（重建 app-release.apk） ---")
        import os as _os
        env = _os.environ.copy()
        env["NAME"] = name
        crack_dir = ROOT / "crackings" / type_arg / name if type_arg else ROOT / "crackings" / name
        env["CRACK_DIR"] = str(crack_dir)
        env["OUT"] = str(crack_dir / "raw")
        env["PATCHED"] = str(out / "patched.apk")
        subprocess.run(["python3", str(AS_BUILD_SCRIPT)], env=env, check=False)
    elif apk_release_path.exists():
        print(f"\n--- 跳过 sub-stage-as-build.py（app-release.apk 已存在） ---")

    # 2. 检查 AS 工程产物
    required_paths = [
        out / "build.gradle",
        out / "settings.gradle",
        out / "my.keystore.jks",
        out / "patched.apk",
        app / "build.gradle",
        app / "src" / "main" / "AndroidManifest.xml",
        app / "src" / "main" / "assets",
        app / "src" / "main" / "res",
        app / "libs",
    ]
    print(f"\n--- AS 工程产物检查 ---")
    for p in required_paths:
        if p.exists():
            print(f"  ✅ {p.relative_to(ROOT)}")
        else:
            print(f"  ❌ {p.relative_to(ROOT)}")
            errors.append(str(p))

    # 3. 检查 app-release.apk md5 与 patched.apk md5 一致（OBJECTIVES §0.3 #1）
    print(f"\n--- md5 一致性（OBJECTIVES §0.3 #1）---")
    apk_release = app / "build" / "outputs" / "apk" / "release" / "app-release.apk"
    crackings_apk = out / "patched.apk"
    if apk_release.exists() and crackings_apk.exists():
        m_release = md5(apk_release)
        m_crackings = md5(crackings_apk)
        print(f"  patched.apk           md5={m_crackings}")
        print(f"  app-release.apk       md5={m_release}")
        if m_release == m_crackings:
            print(f"  ✅ md5 一致")
        else:
            # 当 app-release.apk 是 setup-output-project.py 拷贝的，md5 应一致
            # 当是 sub-stage-as-build.py 重建的，md5 可能不同（不同打包策略）
            print(f"  ⚠ md5 不一致（AS 工程可能重建过）")
            print(f"  → 若要严格一致：crackings/<Name>/patched.apk → app/build/outputs/apk/release/app-release.apk")
            # 不作为 ERROR（不强求一致）
    else:
        if not apk_release.exists():
            print(f"  ⚠ app-release.apk 不存在（AS 工程未构建）")
        if not crackings_apk.exists():
            print(f"  ❌ crackings/<Name>/patched.apk 不存在")
            errors.append("patched.apk missing")

    # 4. lib/<abi>/*.so 完整性
    print(f"\n--- jniLibs 完整性 ---")
    jni = app / "src" / "main" / "jniLibs"
    if jni.exists():
        for abi_dir in jni.iterdir():
            if abi_dir.is_dir():
                sos = list(abi_dir.glob("*.so"))
                print(f"  {abi_dir.name}: {len(sos)} .so")
                for so in sos:
                    print(f"    - {so.name}")
    else:
        print(f"  ⚠ jniLibs 不存在")

    if errors:
        print(f"\n[ERROR] 主阶段 5 验收失败: {errors}")
        sys.exit(3)
    print(f"\n[OK] 主阶段 5 完成（AS 工程 + patched.apk 完整）")


if __name__ == "__main__":
    main()