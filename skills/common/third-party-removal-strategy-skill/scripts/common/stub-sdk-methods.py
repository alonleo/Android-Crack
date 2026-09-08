#!/usr/bin/env python3
"""stub-sdk-methods.py — 把第三方 SDK 的指定方法桩化为 no-op（保留类，C# 兼容）。

背景: FlyingGorillaEndlessRunner (2026-08-02) 移除/停用 AppsFlyer、Lofelt 等 SDK。
C# (libil2cpp) 引用这些 SDK 的 Java 类 → 不能物理删除类，只能把"真正干活的"方法
（start / logEvent / play 等入口）桩化为 return-void，停掉网络调用/副作用。

用法:
  python3 stub-sdk-methods.py <smali_file> <method_sig1> [method_sig2 ...]
  # 例:
  python3 stub-sdk-methods.py AFa1ySDK.smali \
      ".method public final start(Landroid/content/Context;)V" \
      ".method public final logEvent(Landroid/content/Context;Ljava/lang/String;Ljava/util/Map;)V"

说明:
  - 只替换匹配签名的方法体（保留签名行 + 注释）
  - 返回 void 的方法 → return-void + 日志；返回引用的方法需手动处理
  - 幂等（重复运行安全）
  - 桩化后需重跑 inject-smali-dex.py --force 生效
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

TEMPLATE_VOID = (
    "{sig}\n"
    "    .locals 2\n\n"
    "    # === STUBBED by stub-sdk-methods.py: SDK 停用（保留类，C# 兼容）===\n"
    "    const-string v0, \"{tag}\"\n\n"
    "    const-string v1, \"STUB: {desc}\"\n\n"
    "    invoke-static {{v0, v1}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I\n\n"
    "    return-void\n"
    ".end method"
)


def stub_file(smali: Path, sigs: list[str], tag: str, desc: str) -> int:
    text = smali.read_text(encoding="utf-8")
    count = 0
    for sig in sigs:
        start = text.find(sig)
        if start < 0:
            print(f"  [SKIP] 未找到: {sig.split('(')[0]}")
            continue
        # 方法签名完整行（到行尾，处理多参数）
        line_end = text.find("\n", start)
        sig_full = text[start:line_end]
        end = text.find(".end method", start) + len(".end method")
        new_body = TEMPLATE_VOID.format(sig=sig_full, tag=tag, desc=desc)
        text = text[:start] + new_body + text[end:]
        print(f"  [OK] stub {sig_full[:80]}...")
        count += 1
    if count:
        smali.write_text(text, encoding="utf-8")
        print(f"[OK] {smali}: 桩化 {count} 个方法")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="桩化 SDK 入口方法为 no-op")
    parser.add_argument("smali", help="目标 .smali 文件路径")
    parser.add_argument("methods", nargs="+", help="方法签名（.method 开头），可多个")
    parser.add_argument("--tag", default="SDK", help="log tag")
    parser.add_argument("--desc", default="disabled", help="log 描述")
    args = parser.parse_args()

    f = Path(args.smali)
    if not f.is_file():
        print(f"[ERROR] 文件不存在: {f}")
        return 1
    n = stub_file(f, args.methods, args.tag, args.desc)
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
