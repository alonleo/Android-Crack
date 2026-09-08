# Cocos Creator Strategy Skill — Workflow Scripts

> Cocos Creator (JS/TS) 类型使用 cc-reverse 工具链，**无专用阶段 Python 脚本**。
> 阶段 cocos-03 和 cocos-05 由外部工具 cc-reverse / reverse / cocos2d-dec 直接驱动。

| 阶段 | 工具 | 调用方式 |
|------|------|---------|
| cocos-03 | cc-reverse | `cc-reverse --path <解包目录>` |
| cocos-05 | cocos2d-dec / JSC-PyDecrypt-Tool | `python3 cocos2d-dec.py --key <XXTEA> ...` |

## 同步规则

Cocos Creator 的阶段由外部命令行工具直接调用，不依赖 Python 脚本封装。如需新增，请放置在此目录并同步到 `skills/common/scripts/`。