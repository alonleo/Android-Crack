# Network Analysis Tools

> 本文件收录 Android 逆向工程工作区中与**网络抓包、流量分析、反向 USB 共享**相关的工具与脚本。
> 对应 AGENTS.md §5.5 Internet & Network Tools。

## 工具清单

### 1. gnirehtet v2.5.1

| 字段 | 值 |
|------|-----|
| **路径** | `tools/crack-intergration-tools/execable/gnirehtet/` |
| **来源** | [Genymobile/gnirehtet](https://github.com/Genymobile/gnirehtet) |
| **用途** | USB reverse tethering — 把宿主机网络通过 USB 共享给 Android 设备（无需 root） |
| **文件** | `gnirehtet`（Linux/macOS CLI 可执行）+ `gnirehtet.apk`（Android 客户端） |

**工作流**：

```bash
# 1. 安装 Android 端 APK
adb install -r tools/crack-intergration-tools/execable/gnirehtet/gnirehtet.apk

# 2. 启动反向代理（CLI 自动处理中继）
tools/crack-intergration-tools/execable/gnirehtet/gnirehtet run

# 或分开执行（先安装 + 再启动中继）
tools/crack-intergration-tools/execable/gnirehtet/gnirehtet start
```

**原理**：Android 端通过 VpnService 建立虚拟接口 → USB 隧道 → 宿主机转发，为 APK 提供无需 WiFi 的互联网连接。

---

### 2. tcpdump 4.99.6 (Android)

| 字段 | 值 |
|------|-----|
| **路径** | 需手动 push 到设备 `/data/local/tmp/tcpdump` |
| **来源** | [androidtcpdump.com](https://www.androidtcpdump.com/) |
| **用途** | Android 端数据包捕获（需 root 权限） |
| **架构** | ARM64 / ARM / x86 / x86_64 预编译二进制 |

**工作流**：

```bash
# 1. push 到设备
adb push tcpdump /data/local/tmp/tcpdump
adb shell chmod 755 /data/local/tmp/tcpdump

# 2. 捕获所有接口流量（需 root）
adb shell su -c "/data/local/tmp/tcpdump -i any -w /sdcard/capture.pcap"

# 3. 捕获指定端口（例如游戏服务器 8001）
adb shell su -c "/data/local/tmp/tcpdump -i any port 8001 -w /sdcard/capture.pcap"

# 4. 拉回本地分析
adb pull /sdcard/capture.pcap .
wireshark capture.pcap
```

**配合 gnirehtet 使用**：在 gnirehtet 建立 USB 隧道后，tcpdump 可在 Android 端捕获应用产生的所有 TCP/UDP 流量。

---

### 3. 本地网络分析脚本

集中存放于 `tools/scripts/network-analyze/`。

#### 3.1 mock-server.py

| 字段 | 值 |
|------|-----|
| **路径** | `tools/scripts/network-analyze/mock-server.py` |
| **语言** | Python 3 |
| **用途** | 多端口 TCP 监听器 + Mock Server，用于捕获游戏协议（专为 Cocos2d-x LuaSocket 设计） |

```bash
python3 tools/scripts/network-analyze/mock-server.py --ports 8001,8002,8003
```

#### 3.2 setup-reverse-tether.sh

| 字段 | 值 |
|------|-----|
| **路径** | `tools/scripts/network-analyze/setup-reverse-tether.sh` |
| **Shell** | bash |
| **用途** | 自动设置 USB 反向代理。优先使用 gnirehtet，回退到 iptables NAT 方式 |

```bash
./tools/scripts/network-analyze/setup-reverse-tether.sh
```

#### 3.3 capture-and-analyze.sh

| 字段 | 值 |
|------|-----|
| **路径** | `tools/scripts/network-analyze/capture-and-analyze.sh` |
| **Shell** | bash |
| **用途** | 完整游戏流量捕获流水线：建立反向代理 → 启动 tcpdump → 运行应用 → 拉取 pcap → 协议分析 |

```bash
./tools/scripts/network-analyze/capture-and-analyze.sh com.example.game
```

---

## 典型组合工作流

```bash
# 1. 反向 USB 共享（让游戏能联网）
./tools/scripts/network-analyze/setup-reverse-tether.sh

# 2. 启动 mock server 捕获协议（新终端）
python3 tools/scripts/network-analyze/mock-server.py --ports 8001,8002

# 3. 或使用全自动流水线（一步到位）
./tools/scripts/network-analyze/capture-and-analyze.sh com.example.game
```

---

## 相关文档

- `ARMT64_HOOK_COMPARISON.md` — ARM64 inline hook 方案对比（与网络 hook 配合使用）
- `tools/crack-intergration-tools/source-projects/docs/README.md` — 工具深度文档总导航
- `tools/scripts/README.md` — 13 阶段工作流脚本说明
