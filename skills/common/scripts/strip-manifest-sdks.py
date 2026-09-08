#!/usr/bin/env python3
"""strip-manifest-sdks.py — 从 AndroidManifest.xml 移除第三方 SDK 组件。

自动化 manifest 清理（按 third-party-sdk-removal-registry.yaml）:
- 移除 manifest_drop_exact 的精确组件（<activity/service/receiver/provider android:name=...>）
- 移除 manifest_drop_keyword_contains 关键字命中的组件（含多个 SDK 如 applovin / firebase 等）
- 简化权限（仅保留 INTERNET / VIBRATE / WAKE_LOCK 等核心权限；移除 AD_ID / BILLING / ACCESS_ADSERVICES_* 等广告相关）
- 移除 <queries> 中的广告 service query（如 com.applovin.am.intent.action.APPHUB_SERVICE）

策略:
- 仅删除**整行 <activity/service/receiver/provider>**，不动其他元素
- 移除 SDK permission（如 com.applovin.array.apphub.permission.BIND_APPHUB_SERVICE）
- 保留 application/androidx/META-INF 等核心结构

用法:
    python3 skills/common/scripts/strip-manifest-sdks.py \
        --manifest crackings/il2cpp/<name>/project/app/src/main/AndroidManifest.xml \
        --registry skills/common/third-party-removal-strategy-skill/references/third-party-sdk-removal-registry.yaml
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


# 必须保留的核心权限（游戏本体需要）
CORE_PERMISSIONS = {
    "android.permission.INTERNET",
    "android.permission.ACCESS_NETWORK_STATE",
    "android.permission.VIBRATE",
    "android.permission.WAKE_LOCK",
}

# 已知必须移除的广告/SDK 权限（即使清单里没列）
AD_SDK_PERMISSIONS = {
    "com.google.android.gms.permission.AD_ID",
    "com.applovin.array.apphub.permission.BIND_APPHUB_SERVICE",
    "com.android.vending.BILLING",
    "android.permission.ACCESS_ADSERVICES_TOPICS",
    "android.permission.ACCESS_ADSERVICES_ATTRIBUTION",
    "android.permission.ACCESS_WIFI_STATE",
    "android.permission.FOREGROUND_SERVICE",
    "android.permission.RECEIVE_BOOT_COMPLETED",
}


def _load_registry(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _is_component_block(line: str) -> bool:
    """判断是否 <activity/service/receiver/provider ... /> 或开始标签。"""
    return bool(re.search(r"<(activity|service|receiver|provider)\b", line))


def _strip(text: str, registry: dict) -> str:
    """按清单删除组件/权限/queries，返回新文本。"""
    out_lines: list[str] = []
    in_component = False
    component_name = ""
    component_buf: list[str] = []
    skip_depth = 0

    exact_names = set()
    for item in registry.get("manifest_drop_exact", []):
        if isinstance(item, str):
            exact_names.add(item)
        elif isinstance(item, dict):
            exact_names.add(item.get("name", ""))
    keywords = set()
    for item in registry.get("manifest_drop_keyword_contains", []):
        if isinstance(item, str):
            keywords.add(item)
        elif isinstance(item, dict):
            keywords.add(item.get("name", ""))

    i = 0
    while i < len(text.splitlines()):
        line = text.splitlines()[i]
        stripped = line.strip()

        # 权限 / queries 简化
        if "<uses-permission" in line:
            m = re.search(r'android:name="([^"]+)"', line)
            if m:
                perm = m.group(1)
                if perm in AD_SDK_PERMISSIONS or (
                    keywords and any(kw in perm for kw in keywords)
                ):
                    i += 1
                    continue  # 跳过
        if "<queries>" in line or "</queries>" in line:
            i += 1
            continue

        # 组件整段匹配：精确名 或 关键字命中
        if re.search(r"<(activity|service|receiver|provider)\b", line):
            name_m = re.search(r'android:name="([^"]+)"', line)
            if name_m:
                name = name_m.group(1)
                should_drop = (
                    name in exact_names
                    or (keywords and any(kw in name for kw in keywords))
                )
                if should_drop:
                    # 跨多行直到该组件关闭标签
                    depth = 0
                    if line.rstrip().endswith("/>"):
                        i += 1
                        continue
                    depth += 1
                    i += 1
                    while i < len(text.splitlines()) and depth > 0:
                        l2 = text.splitlines()[i]
                        if re.search(r"<(activity|service|receiver|provider)\b", l2) and not l2.rstrip().endswith("/>"):
                            depth += 1
                        if re.search(r"</(activity|service|receiver|provider)>", l2):
                            depth -= 1
                        i += 1
                    continue

        out_lines.append(line)
        i += 1

    return "\n".join(out_lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True, help="AndroidManifest.xml 路径")
    p.add_argument("--registry", default="skills/common/third-party-removal-strategy-skill/references/third-party-sdk-removal-registry.yaml")
    args = p.parse_args()

    manifest = Path(args.manifest)
    if not manifest.is_file():
        sys.exit(f"[ERR] manifest 不存在: {manifest}")

    repo = Path(__file__).resolve().parents[2]
    reg_path = Path(args.registry)
    if not reg_path.is_absolute():
        reg_path = repo / reg_path
    reg = _load_registry(reg_path)

    original = manifest.read_text(encoding="utf-8", errors="ignore")
    cleaned = _strip(original, reg)

    # 对比统计
    orig_lines = len(original.splitlines())
    new_lines = len(cleaned.splitlines())
    print(f"[INFO] 原始: {orig_lines} 行  清理后: {new_lines} 行  减少: {orig_lines - new_lines}")

    manifest.write_text(cleaned, encoding="utf-8")
    print(f"[OK] 写入 {manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())