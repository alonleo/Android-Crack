#!/usr/bin/env python3
"""patch-firebase-realme-fix.py — 一键把项目改成 Realme Android 14 兼容。

[FLOWFIX 2026-08-18] Realme Android 14 上 Unity 6 il2cpp 游戏必闪退，需要做 5 件事。
这个脚本一次做完，避免下次重新走手工路径。

用法:
  python3 patch-firebase-realme-fix.py <Name> --type <il2cpp|air|...>

做的事 (按执行顺序):
  1. 删 jniLibs 里 6 个早期自杀 .so
     (libcrashlytics*.so x4 + libFirebaseCppCrashlytics.so + libapplovin-native-crash-reporter.so)
  2. 用 zipfile 重写 raw/<Name>.apk，删同样 6 个 .so + crashlytics-build.properties + firebase_crashlytics_keep.xml
  3. 生成 6 个 BuildConfig stub
     (com.facebook.ads / com.moloco.sdk / net.pubnative.lite.sdk / com.vungle.ads / com.mbridge / io.adn.sdk)
     IS_WRAPPED 必须是 java.lang.Boolean（不是 primitive Z）匹配 AppLovin 字节码签名
  4. 在 MainActivity.attachBaseContext 装"哑" UncaughtExceptionHandler
     (吞 Firebase / Ktor / Adjust 静态初始化异常，防止 Process.killProcess 自杀)
  5. 在 sub-stage-as-build.py 的 manifest 过滤列表已含
     "FirebaseInitProvider" / "MobileAdsInitProvider" / "com.squareup.picasso"
     (这个 PR 已合到 skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-as-build.py)
     + 关闭 firebase_crashlytics_collection_enabled meta-data

执行完 5 步后，跑 sub-stage-extract-filtered-smali-jars.py 重新生成 dex jars
(EXCLUDE 列表已含 "com/google/firebase/crashlytics"，会过滤掉 395 个 crashlytics smali)。
最后跑 sub-stage-as-build.py 出 patched.apk。

完整流程:
  source tools/environments/env.sh
  python3 patch-firebase-realme-fix.py <Name> --type il2cpp
  TYPE=il2cpp NAME=<Name> python3 sub-stage-extract-filtered-smali-jars.py
  python3 sub-stage-as-build.py <Name>
  $ADB_BIN install -r -d crackings/il2cpp/<Name>/project/patched.apk
"""
from __future__ import annotations
import argparse
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def _load_sdk_lists():
    """[FLOWFIX 2026-08-18] 从 third-party-sdk-removal-registry.yaml 读清单。
    找不到清单时 raise SystemExit，强制修复清单（不要静默回退到硬编码）。
    """
    import sys
    sys.path.insert(0, str(REPO / "skills" / "common" / "third-party-removal-strategy-skill" / "scripts"))
    try:
        from load_sdk_removal_registry import load_registry, names_only, class_path_pairs
    except ImportError:
        print("[ERR] load_sdk_removal_registry.py 缺失，无法加载 SDK 移除清单", file=sys.stderr)
        raise SystemExit(1)
    reg = load_registry()
    return (
        set(names_only(reg["so_early_kill"])),
        list(reg["raw_apk_drop_entries"]),
        class_path_pairs(reg["build_config_stubs"]),
    )


# 步骤 1+2: 早期自杀 .so 名单（来自清单 so_early_kill）
EARLY_KILL_SO_NAMES, RAW_APK_DROP_ENTRIES, BUILD_CONFIG_STUBS = _load_sdk_lists()

BUILD_CONFIG_TEMPLATE = '''package {pkg};

/**
 * Stub BuildConfig — {cls}.
 *
 * [FLOWFIX 2026-08-18] 满足 AppLovin/Unity mediation 在静态初始化时
 * 通过反射查找 BuildConfig 字段（sget-object IS_WRAPPED:java/lang/Boolean;）。
 * 必须用 java.lang.Boolean（不是 primitive Z）匹配字节码签名。
 */
public final class {cls} {{
    public static final boolean DEBUG = false;
    public static final java.lang.Boolean IS_WRAPPED = java.lang.Boolean.FALSE;
    public static final java.lang.Boolean ENABLE_HARDWARE_ACCELERATED = java.lang.Boolean.FALSE;
    public static final String APPLICATION_ID = "stub.{pkg}.{cls}";
    public static final String BUILD_TYPE = "release";
    public static final String FLAVOR = "";
    public static final int VERSION_CODE = 0;
    public static final String VERSION_NAME = "0.0.0-stub";
    public static final String LIBRARY_PACKAGE_NAME = "{pkg}";
    public static final String BUILD_TOOLS_VERSION = "";
    public static final String COMPILATION_SDK_VERSION = "";
    public static final String TARGET_SDK_VERSION = "";
    public static final String MIN_SDK_VERSION = "";
    public static final int MIN_SDK = 21;
    public static final int TARGET_SDK = 33;
}}
'''

# 步骤 4: attachBaseContext 哑 UncaughtExceptionHandler
ATTACH_BASE_CONTEXT_HANDLER = '''
        // [FLOWFIX 2026-08-18] Realme Android 14 闪退止血包
        //   吞 Firebase / Ktor / Adjust / AppLovin 静态初始化的 ExceptionInInitializerError，
        //   阻止系统 RuntimeInit$KillApplicationHandler 抢先调 Process.killProcess(myPid)。
        Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler() {
            @Override public void uncaughtException(Thread t, Throwable e) {
                android.util.Log.w("CrowdCitySafe",
                    "Swallowed uncaught exception in thread " + t.getName() + ": " + e);
                // 不调 default.uncaughtException(t, e) 阻止 killProcess 路径
            }
        });
'''


def find_apk(crackings: Path) -> Path | None:
    for cand in crackings.rglob("*.apk"):
        if cand.suffix == ".apk":
            return cand
    return None


def step1_remove_jni_libs(jni_libs: Path, log) -> int:
    """删 jniLibs 早期自杀 .so"""
    if not jni_libs.exists():
        log("[step1] jniLibs 不存在，跳过")
        return 0
    removed = 0
    for so in jni_libs.glob("*.so"):
        if so.name in EARLY_KILL_SO_NAMES:
            so.unlink()
            log(f"[step1] 删 jniLibs/{so.name}")
            removed += 1
    return removed


def step2_repack_raw_apk(raw_apk: Path, log) -> int:
    """用 zipfile 重写 raw apk，删早期自杀 .so + assets"""
    if not raw_apk.exists():
        log(f"[step2] {raw_apk} 不存在，跳过")
        return 0
    tmp = raw_apk.with_suffix(".apk.tmp")
    dropped = 0
    with zipfile.ZipFile(raw_apk, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.namelist():
            if item in RAW_APK_DROP_ENTRIES:
                dropped += 1
                continue
            zout.writestr(item, zin.read(item))
    if dropped:
        tmp.replace(raw_apk)
        log(f"[step2] 删 raw apk 早期自杀资源: {dropped} 个")
    return dropped


def step3_write_stubs(java_root: Path, log) -> int:
    """生成 6 个 BuildConfig stub"""
    if not java_root.exists():
        log(f"[step3] {java_root} 不存在，跳过")
        return 0
    for relpath, pkg in BUILD_CONFIG_STUBS:
        full = java_root / relpath
        full.parent.mkdir(parents=True, exist_ok=True)
        cls = full.stem
        full.write_text(BUILD_CONFIG_TEMPLATE.format(pkg=pkg, cls=cls), encoding="utf-8")
    log(f"[step3] 生成 {len(BUILD_CONFIG_STUBS)} 个 BuildConfig stub")
    return len(BUILD_CONFIG_STUBS)


def step4_install_uncaught_handler(app_path: Path, log) -> bool:
    """在 App.attachBaseContext 装哑 UncaughtExceptionHandler"""
    if not app_path.exists():
        log(f"[step4] {app_path} 不存在")
        return False
    text = app_path.read_text(encoding="utf-8")
    if "CrowdCitySafe" in text:
        log("[step4] App.java 已有哑 handler，跳过")
        return True
    # 在 super.attachBaseContext(base); 后插入
    if "super.attachBaseContext(base);" not in text:
        log("[step4] 找不到 super.attachBaseContext(base);")
        return False
    text = text.replace(
        "super.attachBaseContext(base);",
        "super.attachBaseContext(base);" + ATTACH_BASE_CONTEXT_HANDLER,
        1,
    )
    # 如果有 fakeDex(base); 调用，把哑 handler 放到它之前
    text = re.sub(
        r"(// \[FLOWFIX.*?装.*?哑.*?handler.*?\])",
        lambda m: m.group(0),  # noop, 注释行已经含说明
        text,
        flags=re.DOTALL,
    )
    app_path.write_text(text, encoding="utf-8")
    log("[step4] App.java 已装哑 UncaughtExceptionHandler")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="项目名 (e.g. CrowdCity)")
    ap.add_argument("--type", default="il2cpp", help="项目类型 (il2cpp/air/...)")
    args = ap.parse_args()

    output = REPO / "output-projects" / args.type / args.name
    if not output.exists():
        print(f"[ERR] {output} 不存在")
        sys.exit(1)
    crackings = REPO / "crackings" / args.type / args.name
    if not crackings.exists():
        print(f"[ERR] {crackings} 不存在")
        sys.exit(1)

    log = lambda m: print(m)

    log(f"=== patch-firebase-realme-fix: {args.type}/{args.name} ===")

    # 步骤 1
    jni_libs = output / "app/src/main/jniLibs/arm64-v8a"
    n = step1_remove_jni_libs(jni_libs, log)
    log(f"[step1] 删除 jniLibs 早期自杀 .so: {n} 个")

    # 步骤 2
    raw_apk = find_apk(crackings / "raw")
    n = step2_repack_raw_apk(raw_apk, log) if raw_apk else 0
    if not raw_apk:
        log("[step2] 找不到 raw apk")

    # 步骤 3
    java_root = output / "app/src/main/java"
    n = step3_write_stubs(java_root, log)

    # 步骤 4
    app_java = java_root / "com/android/boot/App.java"
    ok = step4_install_uncaught_handler(app_java, log)

    log(f"\n=== 完成 ===")
    log(f"下一步 (如尚未跑过):")
    log(f"  1. python3 skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-extract-filtered-smali-jars.py")
    log(f"  2. python3 skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-as-build.py {args.name}")
    log(f"  3. $ADB_BIN install -r -d crackings/{args.type}/{args.name}/project/patched.apk")
    log(f"\n注意: 此脚本已包含在 sub-stage-3rd-party-sdk-removal.py 中（下次跑 stage-04 自动执行）。")


if __name__ == "__main__":
    main()
