#!/usr/bin/env python3
"""clean.py — 03-sdk-network-removal 步骤2：加载清单 + 统一清理（il2cpp 专用覆盖）。

il2cpp 版比 common 多 3 件事：
1. 清单驱动（load_sdk_removal_registry.py）：so_early_kill / so_keyword_contains / engine_so_keep / raw_apk_drop_entries
2. res/ 资源清理：删除含 SDK 关键字的 drawable/layout/values 文件（防 AAPT resource not found）
3. 生成 BuildConfig stubs（满足 AppLovin mediation reflection 的 IS_WRAPPED 字段）

通过 yaml handlers.clean 声明覆盖 common 默认。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "tools/scripts/lib"))
sys.path.insert(0, str(REPO / "skills/common/general-strategy-skill/scripts/common"))
sys.path.insert(0, str(REPO / "skills/common/general-strategy-skill/scripts/common/handlers/sdk_network"))
from common import log_info, log_warn, log_success  # noqa: E402
from base_stage_handler import StageContext  # noqa: E402
from clean import CommonSdkNetworkCleanHandler as _CommonClean  # noqa: E402


def _load_registry() -> dict:
    """il2cpp 用清单驱动（load_sdk_removal_registry.py）。"""
    sys.path.insert(0, str(REPO / "skills/common/third-party-removal-strategy-skill/scripts"))
    try:
        from load_sdk_removal_registry import load_registry, names_only, class_path_pairs
        reg = load_registry()
        return {
            "registry": reg,
            "early_kill_sos": set(names_only(reg["so_early_kill"])),
            "keyword_contains": set(reg["so_keyword_contains"]),
            "engine_keep": set(reg["engine_so_keep"]),
            "raw_drop": set(reg["raw_apk_drop_entries"]),
            "bc_stubs": class_path_pairs(reg["build_config_stubs"]),
        }
    except Exception as e:
        log_warn(f"[stage-03] load_sdk_removal_registry 失败: {e}")
        return {"registry": {}, "early_kill_sos": set(), "keyword_contains": set(),
                "engine_keep": {"libil2cpp.so"}, "raw_drop": set(), "bc_stubs": []}


def _clean_sos_by_registry(lib_dir: Path, state: dict) -> int:
    """按清单清理 SDK .so（保留引擎 .so）。"""
    cleaned = 0
    if not lib_dir.exists():
        return cleaned
    for so in lib_dir.rglob("*.so"):
        if so.name in state["engine_keep"]:
            continue
        if so.name in state["early_kill_sos"]:
            so.unlink()
            cleaned += 1
            log_info(f"[stage-03] 删早期自杀 .so: {so.name}")
            continue
        sname = so.name.lower()
        if any(kw in sname for kw in state["keyword_contains"]):
            so.unlink()
            cleaned += 1
            log_info(f"[stage-03] 删 SDK .so: {so.name}")
    return cleaned


def _clean_res_by_keywords(res_dir: Path, keywords: set) -> int:
    """删除 res/ 下含 SDK 关键字的资源文件（防 AAPT resource not found）。"""
    cleaned = 0
    if not res_dir.exists():
        return cleaned
    for kw in sorted(keywords):
        for pattern in [f"*{kw}*", f"*{kw.upper()}*"]:
            for f in res_dir.rglob(pattern):
                try:
                    f.unlink()
                    cleaned += 1
                    log_info(f"[stage-03] 删 SDK 资源: {f.relative_to(res_dir)}")
                except Exception:
                    pass
    return cleaned


def _gen_build_config_stubs(java_root: Path, bc_stubs: list) -> int:
    """生成 BuildConfig stubs（满足 AppLovin mediation reflection）。"""
    if not java_root or not java_root.exists() or not bc_stubs:
        return 0
    from_text = '''package {pkg};

/**
 * Stub BuildConfig - {cls}.
 * [FLOWFIX 2026-08-18] 满足 AppLovin/Unity mediation 在静态初始化时
 * 通过反射查找 BuildConfig 字段（sget-object IS_WRAPPED:java/lang/Boolean;）。
 * 必须用 java.lang.Boolean（不是 primitive Z）匹配字节码签名。
 */
public final class {cls} {
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
}
'''
    count = 0
    for relpath, pkg in bc_stubs:
        full = java_root / relpath
        full.parent.mkdir(parents=True, exist_ok=True)
        cls = full.stem
        full.write_text(from_text.replace("{pkg}", pkg).replace("{cls}", cls), encoding="utf-8")
        count += 1
    return count


def clean_stage4(ctx: StageContext, collected: dict) -> dict:
    """04 步骤2：加载清单 + 统一清理（il2cpp：清单驱动 + res 清理 + BuildConfig stub）。"""
    log_info(f"[stage-{ctx.stage}] 步骤2：加载清单 + 统一清理（il2cpp）")
    state = _load_registry()
    ctx.set("registry_state", state)

    apktool_root = ctx.apktool_root
    so_log = ctx.stage_dir / "so-removal.log"

    # 1) 清理 manifest（il2cpp 复用 common 的 clean 脚本 helper）
    used_defold_clean = False
    clean_script = REPO / "skills/strategy/il2cpp-strategy-skill/scripts/common/clean-manifest-3rd-sdk.py"
    if clean_script.exists():
        import subprocess
        try:
            subprocess.run([sys.executable, str(clean_script), "--name", ctx.name, "--type", ctx.type],
                           check=True, timeout=120)
            used_defold_clean = True
        except Exception as e:
            log_warn(f"[stage-03] clean-manifest-3rd-sdk.py 失败: {e}")

    # 2) 清理 SDK .so（清单驱动，保留引擎）
    lib_dir = apktool_root / "lib"
    cleaned_so = _clean_sos_by_registry(lib_dir, state)
    log_info(f"[stage-03] SDK .so 清理: {cleaned_so} 个")

    # 3) 清理 res/（防 AAPT resource not found）
    cleaned_res = _clean_res_by_keywords(apktool_root / "res", state["keyword_contains"])
    if cleaned_res:
        log_info(f"[stage-03] SDK 资源文件清理: {cleaned_res} 个")

    # 4) 删 raw apk 里同名的 .so / assets（apktool 重建会再复制回来）
    raw_apk = None
    for cand in (ctx.crackings_root).rglob("*.apk"):
        if cand.suffix == ".apk":
            raw_apk = cand
            break
    dropped = 0
    if raw_apk and raw_apk.exists() and state["raw_drop"]:
        import zipfile
        tmp = raw_apk.with_suffix(".apk.tmp")
        with zipfile.ZipFile(raw_apk, "r") as zin, zipfile.ZipFile(tmp, "w") as zout:
            for item in zin.namelist():
                if item in state["raw_drop"]:
                    dropped += 1
                    continue
                zout.writestr(item, zin.read(item))
        if dropped:
            import os as _os
            _os.replace(tmp, raw_apk)
            log_info(f"[stage-03] 删 raw apk 早期自杀资源: {dropped} 个")

    # 5) 生成 BuildConfig stubs
    java_root = ctx.output_projects_root / "app/src/main/java"
    stub_count = _gen_build_config_stubs(java_root, state["bc_stubs"])
    if stub_count:
        log_info(f"[stage-03] 生成 {stub_count} 个 BuildConfig stub")

    manifest_result = {"removed_components": -1, "removed_permissions": -1, "removed_meta": -1}
    if used_defold_clean:
        log_info("[stage-03] 已通过 clean-manifest-3rd-sdk.py 完成 manifest 清理")

    result = {
        "manifest_result": manifest_result,
        "so_removed": [],
        "cleaned_so": cleaned_so,
        "cleaned_res": cleaned_res,
        "used_defold_clean": used_defold_clean,
        "registry_added": state.get("registry", {}),
    }
    ctx.set("cleaned_so", cleaned_so)
    ctx.set("cleaned_res", cleaned_res)
    return result


class Il2cppSdkNetworkCleanHandler(_CommonClean):
    """il2cpp 03-sdk-network-removal 的统一清理 handler（B 模式类，继承 common 默认父类）。

    复用上方 clean_stage4 纯函数逻辑（清单驱动 + res 清理 + BuildConfig stub）。
    """

    stage_id = "03"
    stage_name = "sdk-network-removal"
    type = "il2cpp"

    def clean(self, ctx: StageContext, collected: dict) -> dict:
        """04 步骤2：加载清单 + 统一清理（il2cpp）。"""
        return clean_stage4(ctx, collected)
