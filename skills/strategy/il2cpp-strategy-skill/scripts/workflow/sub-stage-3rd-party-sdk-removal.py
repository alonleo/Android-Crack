#!/usr/bin/env python3
"""stage-04-sdk-removal.py — il2cpp 阶段 04：去第三方 SDK（il2cpp 专用入口）。

职责（10 步）：
  1. 收集 SDK 信息（manifest + lib/*.so 扫描）
  2. 加载/更新清单（skills/common/third-party-removal-strategy-skill/references/third-party-sdk-removal-registry.yaml）
  3. 清理 AndroidManifest 中已移除 SDK 的引用（activity/service/receiver/provider/meta-data/权限）
  4. 清理 SDK .so（保留引擎 libil2cpp.so）
  5. 清理 smali（按清单 smali_exclude_prefixes）
  6. hook/桩化（sub-stage-hook-plan.py）
  7. 关键字验证
  8. 生成报告
  9. smali→jar
 10. gradlew 构建

产出 3rd-party-sdk.yaml + sdk-removal-report.yaml + third-party-libs/

历史重构记录（保留不改）：
- 阶段 06 - 去第三方 SDK + Hook计划生成（il2cpp 专用）
- 路径修正：原 stage-06-hook-plan.py → sub-stage-hook-plan.py
- [FLOWFIX 2026-08-18] 清单驱动 SDK 移除：所有 type 共用 registry YAML，stage 04 步骤 2 加载+更新
   - 步骤 1 收集后，步骤 2 加载清单 + 把 step1 收集到但清单未含的 SDK 写回清单
   - 步骤 3-7 按清单处理，不再硬编码 SDK 名字
"""
from __future__ import annotations

import os
import sys
import shutil
import subprocess
import datetime as _dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools" / "scripts" / "lib"))
from common import (  # noqa: F403
    ensure_env,
    ensure_dir,
    setup_paths_from_name,
    setup_paths_from_apk,
    log_step,
    log_info,
    log_warn,
    log_success,
    log_error,
    register_artifact,
    die,
)

SCRIPT_PKG = ROOT / "skills" / "strategy" / "il2cpp-strategy-skill" / "scripts"
REGISTRY_PATH = ROOT / "skills" / "common" / "third-party-removal-strategy-skill" / "references/third-party-sdk-removal-registry.yaml"
LOADER_PATH = ROOT / "skills" / "common" / "third-party-removal-strategy-skill" / "scripts" / "load_sdk_removal_registry.py"


def _run_script(script_name: str, extra_args: list = None) -> bool:
    """运行 il2cpp skill scripts 下的 helper 脚本（common/ 或 workflow/）。"""
    script = SCRIPT_PKG / "common" / script_name
    if not script.exists():
        script = SCRIPT_PKG / "workflow" / script_name
    if not script.exists():
        log_warn(f"[stage-04] helper 脚本缺失: {script_name}")
        return False
    cmd = [sys.executable, str(script)]
    name = os.environ.get("NAME", "")
    type_arg = os.environ.get("TYPE", "")
    if name:
        cmd += ["--name", name]
    if type_arg:
        cmd += ["--type", type_arg]
    if extra_args:
        cmd += extra_args
    log_info(f"[stage-04] 运行 helper: {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, timeout=1800)
        return r.returncode == 0
    except Exception as e:
        log_error(f"[stage-04] helper 运行异常 {script_name}: {e}")
        return False


def collect_sdk_info(name: str, type_arg: str, out_yaml: Path) -> dict:
    """步骤1：收集 SDK 信息，生成 3rd-party-sdk.yaml。"""
    import re
    crackings = ROOT / "crackings" / type_arg / name if type_arg else ROOT / "crackings" / name
    apktool = crackings / "raw" / "01-apktool"

    sdk_keywords = [
        "applovin", "ironsource", "vungle", "facebook", "chartboost",
        "inmobi", "mbridge", "pangle", "appsflyer", "adjust", "tapjoy",
        "bytedance", "yandex", "digitalturbine", "safedk", "google.android.gms.ads",
        "firebase", "moloco", "pubnative", "adjoe", "adn",
    ]

    found_components = []
    manifest = apktool / "AndroidManifest.xml"
    if manifest.exists():
        text = manifest.read_text(encoding="utf-8", errors="ignore")
        for kw in sdk_keywords:
            for m in re.finditer(r'android:name="([^"]*' + re.escape(kw) + r'[^"]*)"', text, re.IGNORECASE):
                found_components.append(m.group(1))

    found_sos = []
    lib_dir = apktool / "lib"
    if lib_dir.exists():
        for so in lib_dir.rglob("*.so"):
            sname = so.name.lower()
            if any(kw in sname for kw in sdk_keywords):
                found_sos.append(so.name)

    info = {
        "name": name,
        "type": type_arg,
        "sdk_keywords_hits": len(set(found_components)),
        "components": sorted(set(found_components)),
        "sos": sorted(set(found_sos)),
    }
    ensure_dir(out_yaml.parent)
    out_yaml.write_text(
        "name: %s\ntype: %s\nsdk_keyword_hits: %s\ncomponents:\n%s\nsos:\n%s\n"
        % (
            info["name"], info["type"], info["sdk_keywords_hits"],
            "".join("  - %s\n" % c for c in info["components"]) or "  []\n",
            "".join("  - %s\n" % s for s in info["sos"]) or "  []\n",
        ),
        encoding="utf-8",
    )
    log_info(f"[stage-04] 3rd-party-sdk.yaml 已生成: {out_yaml}")
    return info


def update_registry_with_collected(info: dict, registry: dict) -> list[str]:
    """步骤2（[FLOWFIX 2026-08-18]）：把 step1 收集到的 SDK 关键字写回清单。

    行为：
    - 检查 step1 收集到的 components / sos，命中清单已有关键字 → 跳过
    - 命中 sample_keywords 但清单未含 → 追加到 manifest_drop_keyword_contains + so_keyword_contains
    - 返回新增关键字列表（用于报告）
    """
    import yaml
    added = []
    collected_tokens = (info.get("components", []) or []) + (info.get("sos", []) or [])
    if not collected_tokens:
        return added

    # 现有清单的 keyword 集合
    existing_kw = set()
    for entry in registry.get("manifest_drop_keyword_contains", []):
        if isinstance(entry, dict):
            existing_kw.add(entry["name"])
        else:
            existing_kw.add(entry)
    for entry in registry.get("so_keyword_contains", []):
        if isinstance(entry, str):
            existing_kw.add(entry)
    for entry in registry.get("so_early_kill", []):
        if isinstance(entry, dict):
            existing_kw.add(entry["name"])
    for entry in registry.get("manifest_drop_exact", []):
        if isinstance(entry, dict):
            existing_kw.add(entry["name"])

    # 候选关键字（命中 step1 收集到的 token 子串）
    sample_keywords = [
        "applovin", "ironsource", "vungle", "facebook", "chartboost",
        "inmobi", "mbridge", "pangle", "appsflyer", "adjust", "tapjoy",
        "bytedance", "yandex", "digitalturbine", "safedk", "firebase",
        "google.android.gms.ads", "moloco", "pubnative", "adjoe", "adn",
        "bugly", "hms", "tencent", "baidu", "alibaba", "safedk",
    ]
    new_kw = set()
    for token in collected_tokens:
        t = token.lower()
        for kw in sample_keywords:
            if kw in t and kw not in existing_kw and kw not in new_kw:
                new_kw.add(kw)
    if not new_kw:
        return added

    # 写回清单（用 PyYAML 重新 dump，注释会丢但语义不变）
    if not REGISTRY_PATH.exists():
        log_warn(f"[stage-04] 清单不存在: {REGISTRY_PATH}，跳过 update")
        return added

    original_text = REGISTRY_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(original_text)
    if not isinstance(data, dict):
        log_warn("[stage-04] 清单不是 dict，跳过 update")
        return added

    # 追加到对应段
    for kw in sorted(new_kw):
        entry = {"name": kw, "why": "auto-added by stage-04 step2 [FLOWFIX 2026-08-18]: step1 scan detected"}
        existing_mdc = data.get("manifest_drop_keyword_contains", [])
        if not any(isinstance(it, dict) and it.get("name") == kw for it in existing_mdc):
            existing_mdc.append(entry)
            data["manifest_drop_keyword_contains"] = existing_mdc
        if kw not in data.get("so_keyword_contains", []):
            existing_skc = data.get("so_keyword_contains", [])
            existing_skc.append(kw)
            data["so_keyword_contains"] = existing_skc
        added.append(kw)

    if not added:
        return added

    new_text = "# auto-updated by stage-04 step2 [FLOWFIX 2026-08-18]\n" + yaml.safe_dump(
        data, allow_unicode=True, sort_keys=False
    )
    REGISTRY_PATH.write_text(new_text, encoding="utf-8")
    log_info(f"[stage-04] 已更新清单，写入 {len(added)} 个新 SDK 关键字: {added}")
    return added


def load_or_init_registry() -> dict:
    """步骤2 上半：加载清单（加载器路径在 skills/strategy/scripts/）。"""
    sys.path.insert(0, str(ROOT / "skills" / "common" / "third-party-removal-strategy-skill" / "scripts"))
    from load_sdk_removal_registry import load_registry, names_only, class_path_pairs
    registry = load_registry()
    return {
        "registry": registry,
        "early_kill_sos": set(names_only(registry["so_early_kill"])),
        "keyword_contains": set(registry["so_keyword_contains"]),
        "engine_keep": set(registry["engine_so_keep"]),
        "raw_drop": set(registry["raw_apk_drop_entries"]),
        "bc_stubs": class_path_pairs(registry["build_config_stubs"]),
    }


def write_report(report_yaml: Path, info: dict, cleaned_manifest: bool, cleaned_so: int, registry_added: list = None) -> None:
    """步骤8：生成 sdk-removal-report.yaml。"""
    ensure_dir(report_yaml.parent)
    report_yaml.write_text(
        "name: %s\ntype: %s\nmanifest_cleaned: %s\nso_removed_count: %s\ncomponents_found: %s\n"
        "registry_added: %s\nreport_time: %s\n"
        % (
            info.get("name", ""), info.get("type", ""),
            "true" if cleaned_manifest else "false",
            cleaned_so, info.get("sdk_keywords_hits", 0),
            registry_added if registry_added else [],
            _dt.datetime.now().isoformat(timespec="seconds"),
        ),
        encoding="utf-8",
    )
    log_info(f"[stage-04] sdk-removal-report.yaml 已生成: {report_yaml}")


def main() -> int:
    ensure_env()
    apk_arg = os.environ.get("APK", "")
    name = os.environ.get("NAME", "")
    type_arg = os.environ.get("TYPE", "").strip()

    if apk_arg and not name:
        setup_paths_from_apk(apk_arg, type=type_arg)
    elif name:
        setup_paths_from_name(name, type=type_arg)
    else:
        log_error("需要 NAME 或 APK 环境变量")
        return 1

    name = os.environ.get("NAME", "") or die("NAME 未设置")
    log_step(f"阶段 04: 去第三方 SDK ({name})")

    # 定位 stage 输出目录
    crackings = ROOT / "crackings" / type_arg / name if type_arg else ROOT / "crackings" / name
    stage_dir = crackings / "stages" / "04-3rd-party-sdk-removal"
    ensure_dir(stage_dir)
    out_yaml = stage_dir / "3rd-party-sdk.yaml"
    report_yaml = stage_dir / "sdk-removal-report.yaml"

    # === 步骤1：收集 SDK 信息 ===
    info = collect_sdk_info(name, type_arg, out_yaml)

    # === 步骤2（[FLOWFIX 2026-08-18]）：加载/更新清单 ===
    # 加载清单放在收集信息之后：能拿到 step1 检测到的 SDK 名单，
    # 用它跟清单 diff，未含的 SDK 自动追加到清单（清单成为"实际应用"）。
    state = load_or_init_registry()
    log_info(f"[stage-04] 加载清单: {len(state['early_kill_sos'])} early-kill + "
             f"{len(state['keyword_contains'])} keyword + {len(state['bc_stubs'])} BuildConfig stub")

    # 把 step1 收集到但清单未含的 SDK 写回清单
    registry_added = update_registry_with_collected(info, state["registry"])
    if registry_added:
        # 重新加载并刷新所有变量
        state = load_or_init_registry()
        log_info(f"[stage-04] 重新加载清单: 已加入 {len(registry_added)} 个 SDK 关键字")

    # === 步骤3：清理 manifest（helper 会处理 app 的 AndroidManifest） ===
    ok_manifest = _run_script("clean-manifest-3rd-sdk.py")

    # === 步骤4：清理 SDK .so（跨 ABI，保留引擎 .so，名单来自清单） ===
    early_kill_sos = state["early_kill_sos"]
    keyword_contains = state["keyword_contains"]
    engine_keep = state["engine_keep"]
    raw_drop = state["raw_drop"]
    bc_stubs = state["bc_stubs"]

    cleaned_so = 0
    lib_dir = crackings / "raw" / "01-apktool" / "lib"
    if lib_dir.exists():
        for so in lib_dir.rglob("*.so"):
            if so.name in engine_keep:
                continue
            if so.name in early_kill_sos:
                so.unlink()
                cleaned_so += 1
                log_info(f"[stage-04] 删早期自杀 .so: {so.name}")
                continue
            sname = so.name.lower()
            if any(kw in sname for kw in keyword_contains):
                so.unlink()
                cleaned_so += 1
                log_info(f"[stage-04] 删 SDK .so: {so.name}")
    if cleaned_so:
        log_info(f"[stage-04] SDK .so 清理: {cleaned_so} 个")

    # [FLOWFIX] 步骤4b：清理 res/ 中 SDK 资源文件（drawable/layout/values 等）
    # AndroidManifest 清理了组件声明，但 applovin_*.xml / mbridge_*.xml 等资源文件
    # 仍在 res/ 中，残留引用导致 AAPT 报 "resource not found" 构建失败。
    # 按清单 keyword_contains 删除 res/ 下所有含 SDK 关键字的文件。
    res_dir = crackings / "raw" / "01-apktool" / "res"
    cleaned_res = 0
    if res_dir.exists():
        sdk_res_keywords = sorted(keyword_contains)  # applovin, mbridge, ironsource 等
        for kw in sdk_res_keywords:
            for pattern in [f"*{kw}*", f"*{kw.upper()}*"]:
                for f in res_dir.rglob(pattern):
                    try:
                        f.unlink()
                        cleaned_res += 1
                        log_info(f"[stage-04] 删 SDK 资源: {f.relative_to(res_dir)}")
                    except Exception:
                        pass
    if cleaned_res:
        log_info(f"[stage-04] SDK 资源文件清理: {cleaned_res} 个")

    # 同时删 raw apk 里同名的 .so（apktool 重建会再复制回来）
    raw_apk = crackings / "raw" / "CrowdCity.apk"
    if not raw_apk.exists():
        for cand in crackings.rglob("*.apk"):
            if cand.suffix == ".apk":
                raw_apk = cand
                break
    if raw_apk.exists():
        import zipfile
        tmp = raw_apk.with_suffix(".apk.tmp")
        dropped = 0
        with zipfile.ZipFile(raw_apk, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                if item in raw_drop:
                    dropped += 1
                    continue
                zout.writestr(item, zin.read(item))
        if dropped:
            import os as _os
            _os.replace(tmp, raw_apk)
            log_info(f"[stage-04] 删 raw apk 早期自杀资源: {dropped} 个")

    # === 步骤5：清理 smali（按清单 smali_exclude_prefixes，由 sub-stage-extract-filtered-smali-jars.py） ===
    # 实际过滤发生在 extract-filtered-smali-jars.py，它读清单的 smali_exclude_prefixes
    # 步骤6：hook/桩化（sub-stage-hook-plan.py）

    # === 步骤7：生成 BuildConfig stubs（满足 AppLovin mediation reflection 查找） ===
    # 名单来自清单 build_config_stubs；IS_WRAPPED 必须是 java.lang.Boolean 匹配字节码签名
    from_text = '''package {pkg};

/**
 * Stub BuildConfig - {cls}.
 *
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
    java_root = (ROOT / "output-projects" / type_arg / name
                 / "app/src/main/java") if type_arg else None
    if java_root is not None and java_root.exists() and bc_stubs:
        for relpath, pkg in bc_stubs:
            full = java_root / relpath
            full.parent.mkdir(parents=True, exist_ok=True)
            cls = full.stem
            full.write_text(from_text.replace("{pkg}", pkg).replace("{cls}", cls), encoding="utf-8")
        log_info(f"[stage-04] 生成 {len(bc_stubs)} 个 BuildConfig stub（IS_WRAPPED 字段 java.lang.Boolean）")

    # 步骤8：重建 apktool 工作树
    _run_script("rebuild-apk-from-apktool.py")

    # 步骤9：生成 hook-plan.yaml
    _run_script("sub-stage-hook-plan.py")

    # 步骤10：生成报告
    write_report(report_yaml, info, ok_manifest, cleaned_so, registry_added)

    register_artifact(str(out_yaml), "file", "3rd-party-sdk.yaml", name=name)
    register_artifact(str(report_yaml), "file", "sdk-removal-report.yaml", name=name)
    register_artifact(str(stage_dir / "third-party-libs"), "dir", "third-party-libs", name=name)

    log_success(f"阶段 04 完成 -> {stage_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
