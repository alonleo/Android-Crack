#!/usr/bin/env python3
"""collect.py — 03-sdk-network-removal 步骤1：信息收集（il2cpp 专用覆盖 · B 模式类）。

改为继承 BaseStageHandler（B 模式）：
  class Il2cppSdkNetworkCollectHandler(BaseStageHandler)
    - stage_id / stage_name / type 类属性标识归属
    - 重写 collect() 实现 il2cpp 针对性收集

il2cpp 差异点：
  - SDK 扫描加入 step1-signatures/（dump.cs 等）更多 SDK 关键字
  - 网络检测优先从 dump.cs/il2cpp.h/script.json/stringliteral.json 收集
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPO / "tools/scripts/lib"))
sys.path.insert(0, str(REPO / "skills/common/general-strategy-skill/scripts/common"))
sys.path.insert(0, str(REPO / "skills/common/general-strategy-skill/scripts/common/handlers/sdk_network"))
from common import log_info, log_success  # noqa: E402
from base_stage_handler import StageContext  # noqa: E402
from collect import CommonSdkNetworkCollectHandler as _CommonCollect  # noqa: E402

# il2cpp 额外 SDK 关键字
SDK_KEYWORDS = [
    "applovin", "ironsource", "vungle", "facebook", "chartboost",
    "inmobi", "mbridge", "pangle", "appsflyer", "adjust", "tapjoy",
    "bytedance", "yandex", "digitalturbine", "safedk", "google.android.gms.ads",
    "firebase", "moloco", "pubnative", "adjoe", "adn", "bugly", "hms", "tencent", "baidu", "alibaba",
]
NETWORK_METHOD_KEYWORDS = [
    "isNetworkAvailable", "isOnline", "isConnected", "hasNetwork",
    "hasActiveNetwork", "checkNetwork", "networkAvailable",
    "getActiveNetworkInfo", "getNetworkInfo",
]
NETWORK_CLASS_KEYWORDS = [
    "NetworkUtil", "NetworkUtils", "ConnectivityUtil", "ConnectivityManager",
    "NetworkManager", "NetworkChecker", "VersionChecker", "UpdateManager",
]


class Il2cppSdkNetworkCollectHandler(_CommonCollect):
    """il2cpp 03-sdk-network-removal 的信息收集 handler（继承 common 默认父类）。"""

    stage_id = "03"
    stage_name = "sdk-network-removal"
    type = "il2cpp"

    def collect(self, ctx: StageContext) -> dict:
        """04 步骤1：收集 SDK + 网络检测信息（il2cpp 覆盖）。"""
        log_info(f"[stage-{ctx.stage}] 步骤1：信息收集（SDK + 网络检测 · il2cpp）")
        apktool_root = ctx.apktool_root
        sdk_info = self._collect_sdk_info(apktool_root)

        sdk_yaml = {
            "stage": "03", "name": "3rd-party-sdk",
            "collected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "components": sdk_info["components"], "sos": sdk_info["sos"],
            "smali_prefixes": sdk_info["smali_prefixes"],
        }
        (ctx.stage_dir / "3rd-party-sdk.yaml").write_text(
            yaml.dump(sdk_yaml, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        log_success(
            f"[stage-{ctx.stage}] SDK 扫描：组件 {len(sdk_info['components'])} 个 / "
            f".so {len(sdk_info['sos'])} 个 / smali 前缀 {len(sdk_info['smali_prefixes'])} 个"
        )

        # 网络检测：il2cpp 优先从签名文件收集，其次 smali
        network_methods = []
        if ctx.sig_dir and ctx.sig_dir.exists():
            network_methods = self._collect_network_methods_from_signatures(ctx.sig_dir)
        if not network_methods and ctx.as_smali_root and ctx.as_smali_root.exists():
            network_methods = self._collect_network_methods_from_smali_fallback(ctx.as_smali_root)
        for item in network_methods:
            item["strategy"] = self._determine_strategy(item)

        network_yaml = {
            "stage": "03", "name": "network-detection",
            "collected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_count": len(network_methods), "methods": network_methods,
        }
        (ctx.stage_dir / "network-detection.yaml").write_text(
            yaml.dump(network_yaml, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        log_success(f"[stage-{ctx.stage}] 网络检测扫描：{len(network_methods)} 个方法")

        return {
            "sdk": sdk_info,
            "network_methods": network_methods,
            "sdk_yaml": sdk_yaml,
            "network_yaml": network_yaml,
        }

    # ---- il2cpp 私有辅助 ----

    @staticmethod
    def _collect_sdk_info(apktool_root: Path) -> dict:
        """扫描 manifest + lib/*.so + smali，识别第三方 SDK（il2cpp 版）。"""
        result = {"components": [], "sos": [], "smali_prefixes": []}
        manifest = apktool_root / "AndroidManifest.xml"
        if manifest.exists():
            text = manifest.read_text(encoding="utf-8", errors="ignore")
            for kw in SDK_KEYWORDS:
                for m in re.finditer(
                    rf'android:name="([^"]*{re.escape(kw)}[^"]*)"', text, re.IGNORECASE
                ):
                    result["components"].append(m.group(1))
        lib_dir = apktool_root / "lib"
        if lib_dir.exists():
            for so in lib_dir.rglob("*.so"):
                sname = so.name.lower()
                if any(kw in sname for kw in SDK_KEYWORDS):
                    result["sos"].append(so.name)
        smali_dir = apktool_root / "smali"
        if smali_dir.exists():
            for pkg_dir in smali_dir.iterdir():
                if pkg_dir.is_dir() and any(kw in pkg_dir.name.lower() for kw in SDK_KEYWORDS):
                    result["smali_prefixes"].append(pkg_dir.name)
        result["components"] = sorted(set(result["components"]))
        result["sos"] = sorted(set(result["sos"]))
        result["smali_prefixes"] = sorted(set(result["smali_prefixes"]))
        return result

    @staticmethod
    def _collect_network_methods_from_signatures(sig_dir: Path) -> list[dict]:
        """从 step1-signatures（dump.cs/il2cpp.h/script.json/stringliteral.json）收集网络方法。"""
        import subprocess
        results = []
        if not sig_dir.exists():
            return results
        for sig_file in sig_dir.rglob("*"):
            if sig_file.is_dir():
                continue
            if (sig_file.name.lower() not in ("dump.cs", "il2cpp.h")
                    and sig_file.suffix not in (".json", ".h")):
                continue
            try:
                text = sig_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if not text:
                continue
            kw_pattern = "|".join(re.escape(k) for k in NETWORK_METHOD_KEYWORDS)
            try:
                grep_out = subprocess.check_output(
                    f"grep -n -E '{kw_pattern}' '{sig_file}' 2>/dev/null",
                    shell=True, text=True, timeout=30,
                )
            except Exception:
                continue
            for line in grep_out.strip().split("\n"):
                if not line:
                    continue
                parts = line.split(":", 2)
                if len(parts) < 2:
                    continue
                line_content = parts[1] if len(parts) == 2 else parts[1] + ":" + parts[2]
                if "//" in line_content:
                    continue
                for kw in NETWORK_METHOD_KEYWORDS:
                    if kw in line_content:
                        ret_type = ""
                        m = re.match(r"^([\w:.<>\[\]ues]+)\s+\S", line_content)
                        if m:
                            ret_type = m.group(1)
                        results.append({
                            "method": kw, "return_type": ret_type,
                            "source_file": str(sig_file.relative_to(sig_dir)),
                            "source": "signature_file",
                        })
                        break
        return results

    @staticmethod
    def _collect_network_methods_from_smali_fallback(smali_root: Path) -> list[dict]:
        """il2cpp 兜底：从 AS 工程 smali 收集网络方法。"""
        results = []
        if not smali_root.exists():
            return results
        for smali_file in smali_root.rglob("*.smali"):
            text = smali_file.read_text(encoding="utf-8", errors="replace")
            for method_name in NETWORK_METHOD_KEYWORDS:
                if method_name in text:
                    pattern = re.compile(
                        rf"(\.method[^\n]*?\b{method_name}\b\s*\([^\)]*\)\s*[^\n]*\.)"
                        r"[^\n]*?(\.end method)",
                        re.DOTALL,
                    )
                    for m in pattern.finditer(text):
                        ret_type = ""
                        ret_m = re.search(r"\)\s*([ZSBIJFLjavalangObject;V])", m.group(0))
                        if ret_m:
                            ret_type = ret_m.group(1)
                        results.append({
                            "method": method_name,
                            "file": str(smali_file.relative_to(REPO)),
                            "return_type": ret_type, "source": "smali",
                        })
        return results

    @staticmethod
    def _determine_strategy(method_info: dict) -> str:
        method = method_info.get("method", "")
        return_type = method_info.get("return_type", "")
        if (return_type in ("Z", "bool", "boolean")
                or method.startswith("is") or method.startswith("has")
                or method.startswith("check")):
            return "stub"
        if "Version" in method or "Update" in method or "CheckUpdate" in method:
            return "stub"
        if return_type in ("V", "void", ""):
            return "keep"
        return "stub"
