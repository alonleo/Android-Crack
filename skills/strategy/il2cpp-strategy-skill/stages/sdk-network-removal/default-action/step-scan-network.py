#!/usr/bin/env python3
"""step-02-scan-network.py — collect_sdk action step2: 扫描网络检测方法(签名文件优先)。

03-sdk-network-removal/collect_sdk action。
读 step-01(scan_manifest)累积结果 + 扫网络方法。
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
# 兼容读取旧项目分析产物；fn-analyze 已不再参与路由。
from step_base import stage_path, REPO, Step

NETWORK_METHOD_KEYWORDS = [
    "isNetworkAvailable", "isOnline", "isConnected", "hasNetwork",
    "hasActiveNetwork", "checkNetwork", "networkAvailable",
]
NETWORK_CLASS_KEYWORDS = [
    "NetworkUtil", "NetworkUtils", "ConnectivityUtil", "ConnectivityManager",
    "NetworkManager", "VersionChecker", "UpdateManager",
]


class ScanNetworkStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        cracking_root = REPO / "crackings" / type_ / name

        # 读 step-01 累积(跨 step 累积验证)
        manifest_result = steps_results.get(
            "sdk-network-removal.default-action.scan-manifest", {}
        )

        methods = []
        # 优先从 step1-signatures(dump.cs/il2cpp.h)收集
        sig_dir = cracking_root / "stages" / "03-fn-analyze" / "step1-signatures"
        if sig_dir.exists():
            kw_pattern = "|".join(re.escape(k) for k in NETWORK_METHOD_KEYWORDS)
            for sig_file in sig_dir.rglob("*"):
                if sig_file.is_dir():
                    continue
                if sig_file.name.lower() not in ("dump.cs", "il2cpp.h") and sig_file.suffix not in (".json", ".h"):
                    continue
                try:
                    out = subprocess.check_output(
                        f"grep -n -E '{kw_pattern}' '{sig_file}' 2>/dev/null",
                        shell=True, text=True, timeout=30,
                    )
                except Exception:
                    continue
                for line in out.strip().split("\n"):
                    if not line:
                        continue
                    for kw in NETWORK_METHOD_KEYWORDS:
                        if kw in line:
                            methods.append({"method": kw, "source": "signature_file",
                                            "source_file": str(sig_file.relative_to(sig_dir))})
                            break

        # 兜底从 smali 收集
        if not methods:
            smali_root = cracking_root / "raw" / "01-apktool" / "smali"
            if smali_root.exists():
                for smali_file in smali_root.rglob("*.smali"):
                    text = smali_file.read_text(encoding="utf-8", errors="replace")
                    for m_name in NETWORK_METHOD_KEYWORDS:
                        if m_name in text:
                            methods.append({"method": m_name, "source": "smali",
                                            "file": str(smali_file.relative_to(REPO))})
                            break

        # 策略判定
        for item in methods:
            item["strategy"] = self._determine_strategy(item)

        return {
            "rc": 0,
            "network_method_count": len(methods),
            "methods": methods,
            "prior_sdk_components": manifest_result.get("sdk_component_count", -1),  # 验证跨 action 累积
            "sig_dir_exists": sig_dir.exists(),
        }

    @staticmethod
    def _determine_strategy(method_info: dict) -> str:
        method = method_info.get("method", "")
        if method.startswith("is") or method.startswith("has") or method.startswith("check"):
            return "stub"
        return "keep"