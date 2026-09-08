#!/usr/bin/env python3
"""配置 LSPosed 模块作用域（通用工具）
用途：将已安装的 LSPosed 模块启用并添加到目标应用作用域。
原理：直接修改 /data/adb/lspd/config/modules_config.db（SQLite），
      需在 lspd 停止时进行，否则 daemon 会用内存状态覆盖。
用法（在已 root + adb 设备上）：
  python3 lsposed-config.py <device_serial> <module_pkg> <target_pkg> [--adb <path>]
示例：
  python3 lsposed-config.py 712KPDT1165978 io.github...pairipfix com.spcomes.kw2
"""
import argparse
import sqlite3
import subprocess
import sys
import tempfile
import os

LOCAL_DB = "/tmp/lsposed_modules_config.db"
DEV_DB = "/data/local/tmp/lsposed_modules_config.db"
REAL_DB = "/data/adb/lspd/config/modules_config.db"


def adb(serial, args):
    cmd = [ADB_BIN, "-s", serial] + args
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def main():
    global ADB_BIN
    ap = argparse.ArgumentParser()
    ap.add_argument("serial")
    ap.add_argument("module_pkg")
    ap.add_argument("target_pkg")
    ap.add_argument("--adb", default="adb")
    a = ap.parse_args()
    ADB_BIN = a.adb

    # 1. 停止 lspd
    out, err, rc = adb(a.serial, ["shell", "su -c 'killall lspd 2>/dev/null; sleep 1'"])
    print("[*] stop lspd:", rc == 0)

    # 2. 拉取数据库
    adb(a.serial, ["shell", f"su -c 'cp {REAL_DB} {DEV_DB} && chmod 666 {DEV_DB}'"])
    out, err, rc = adb(a.serial, ["pull", DEV_DB, LOCAL_DB])
    if rc != 0:
        print("[!] pull failed:", err)
        sys.exit(1)
    print("[*] db pulled")

    # 3. 修改数据库
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    cur.execute("SELECT mid FROM modules WHERE module_pkg_name=?", (a.module_pkg,))
    rows = cur.fetchall()
    if not rows:
        print(f"[!] module not found: {a.module_pkg}")
        sys.exit(1)
    mid = rows[0][0]
    cur.execute("UPDATE modules SET enabled=1 WHERE mid=?", (mid,))
    cur.execute("DELETE FROM scope WHERE mid=? AND app_pkg_name=?", (mid, a.target_pkg))
    cur.execute("INSERT INTO scope (mid, app_pkg_name, user_id) VALUES (?, ?, 0)", (mid, a.target_pkg))
    conn.commit()
    conn.close()
    print(f"[*] enabled module mid={mid}, scope={a.target_pkg}")

    # 4. 推送并清理 wal/shm
    adb(a.serial, ["push", LOCAL_DB, DEV_DB])
    adb(a.serial, ["shell",
        f"su -c 'cp {DEV_DB} {REAL_DB} && chmod 660 {REAL_DB} "
        f"&& rm -f {REAL_DB}-wal {REAL_DB}-shm'"])
    print("[*] db pushed")

    # 5. 重启 zygote 让 LSPosed 重新加载
    adb(a.serial, ["shell", "su -c 'setprop ctl.restart zygote'"])
    print("[*] zygote restarting, lspd will auto-start via Magisk")
    os.remove(LOCAL_DB)


if __name__ == "__main__":
    main()
