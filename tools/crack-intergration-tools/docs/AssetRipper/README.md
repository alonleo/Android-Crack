# AssetRipper

> Unity 资源提取 + C# 反编译工具

## 概述

AssetRipper 是一个用于从 Unity 游戏中提取资源的工具，支持：
- 提取纹理、音频、视频、动画等资源
- 反编译 C# 代码（MonoBehaviour 等）
- 支持 Unity 5.x 到 Unity 6.x 全版本
- 跨平台支持（Windows/Linux/macOS）

## 工具路径

```
tools/crack-intergration-tools/execable/AssetRipper/
├── AssetRipper.GUI.Free    ← 主程序（GUI 模式）
├── libcapstone.so          ← 反汇编引擎
└── compile_time.txt        ← 编译时间
```

## 使用方法

### GUI 模式
```bash
# 启动 GUI
./tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free

# 指定端口启动
./tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free --port 8080
```

### CLI 模式（headless）
```bash
# 无头模式运行
./tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free --headless

# 启用日志
./tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free --log --log-path /tmp/assetripper.log
```

## 与其他工具的配合

| 场景 | 工具组合 |
|------|---------|
| Unity 资源提取 | AssetRipper → 提取纹理/音频/动画 |
| IL2CPP 反编译 | Il2CppDumper + AssetRipper |
| 完整逆向 | AssetRipper + ILSpy + dnSpy |

## 参考链接

- [GitHub 仓库](https://github.com/AssetRipper/AssetRipper)
- [官方文档](https://assetripper.com)
- [下载页面](https://assetripper.com/download.html)
