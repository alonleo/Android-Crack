# FFmpeg

> 音视频处理工具（转码/剪辑/流媒体）

## 概述

FFmpeg 是一个开源的音视频处理工具集，支持：
- 音视频转码（几乎所有格式）
- 音视频剪辑、合并、分割
- 流媒体处理
- 音视频滤镜和特效

## 工具路径

```
tools/crack-intergration-tools/execable/ffmpeg/
├── ffmpeg      ← 主程序（转码工具）
├── ffprobe     ← 媒体信息分析工具
└── ffplay      ← 播放器
```

## 版本信息

- 版本：N-125978-g95c43d7df7-20260806
- 编译日期：2026-08-06
- 架构：Linux x64 静态编译
- 支持的编码器：x264, x265, libvpx, libaom, libsvtav1 等

## 使用方法

### 基本转码
```bash
# 查看媒体信息
./tools/crack-intergration-tools/execable/ffmpeg/ffprobe input.mp4

# 转换格式
./tools/crack-intergration-tools/execable/ffmpeg/ffmpeg -i input.mp4 output.avi

# 提取音频
./tools/crack-intergration-tools/execable/ffmpeg/ffmpeg -i input.mp4 -vn output.mp3

# 提取视频
./tools/crack-intergration-tools/execable/ffmpeg/ffmpeg -i input.mp4 -an output.mp4
```

### 常用操作
```bash
# 剪辑视频（从00:01:00开始，持续30秒）
./tools/crack-intergration-tools/execable/ffmpeg/ffmpeg -ss 00:01:00 -i input.mp4 -t 30 -c copy output.mp4

# 合并视频
./tools/crack-intergration-tools/execable/ffmpeg/ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4

# 调整分辨率
./tools/crack-intergration-tools/execable/ffmpeg/ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4

# 压缩视频
./tools/crack-intergration-tools/execable/ffmpeg/ffmpeg -i input.mp4 -crf 23 output.mp4
```

## 与其他工具的配合

| 场景 | 工具组合 |
|------|---------|
| 游戏资源提取 | AssetRipper → ffmpeg 转码 |
| 音频处理 | ffmpeg + Audacity |
| 视频编辑 | ffmpeg + 视频编辑器 |
| 流媒体 | ffmpeg + OBS |

## 参考链接

- [官方文档](https://ffmpeg.org/documentation.html)
- [FFmpeg Wiki](https://trac.ffmpeg.org/)
- [FFmpeg 命令行教程](https://ffmpeg.org/ffmpeg.html)
