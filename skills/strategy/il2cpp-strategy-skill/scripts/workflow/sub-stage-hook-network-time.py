#!/usr/bin/env python3
"""Record the offline TimeService hook experiment without applying it.

The first experiment proved that directly calling the IL2CPP generic
Task.FromResult<bool> RVA is ABI-sensitive and caused SIGSEGV. Keep this
substage as a guard so it cannot reintroduce the unsafe hook until the exact
rgctx/method-info signature is recovered.
"""
from __future__ import annotations

print("[SKIP] TimeService.TryFetchNetworkTime hook 暂停：Task.FromResult<bool> 的 IL2CPP hidden ABI 尚未确认")
print("[INFO] 上次实验已记录 SIGSEGV；当前工程不再包含该 Hook")
