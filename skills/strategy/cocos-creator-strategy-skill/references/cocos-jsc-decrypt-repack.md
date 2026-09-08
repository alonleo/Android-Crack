# Cocos Creator .jsc 解密 + 可逆重打包方案（经验固化）

> 本文件记录 Cocos Creator (JS/.jsc, 3.x bundle) 手游的**完整脚本解密路径**与
> **可逆重打包方案**。适用于一切 `libcocos2djs.so` + `assets/**/*.jsc` 的 Cocos Creator 3.x 项目。

## 1. 识别与密钥提取

**引擎判据**：`lib/arm64-v8a/libcocos2djs.so` + `assets/src/cocos2d-jsb.<hash>.jsc` +
`assets/src/settings.<hash>.jsc` + `assets/assets/<bundle>/config.<hash>.json`。

> ⚠️ 本类 APK 常被 sub-stage-sniff.py 误判为 `android`（嗅探规则漏检 `libcocos2djs.so`/`.jsc`）。
> 需按 STRATEGY §1.2 cocos-creator 行人工归位到 `crackings/cocos-creator/<Name>/`。

**XXTEA 密钥提取**（`reverse` 是 Go cobra CLI，注意其 `--help` 示例命令是错的，实际用顶层 flag）：
```bash
# reverse 是交互式工具的 TUI，用 --no-tui --json 输出密钥：
tools/crack-intergration-tools/execable/reverse \
  <libcocos2djs.so路径> --no-tui --json
# 输出 setters 段 → jsb_set_xxtea_key(std::string const&) → key: "<16字节密钥>"
```

## 2. 脚本解密（.jsc → .js）

**首选 cocos2d-dec 的 js_xxtea_decrypt.py**（比 cc-reverse 稳定；cc-reverse 解资源成功但
Scripts-recovered 常为 0，因为脚本需密钥且其脚本管线有 bug）。
```bash
# 依赖：lib/libext_xxtea.so（由 xxtea.c 编译：gcc -shared -fPIC -O2 -o lib/libext_xxtea.so xxtea.c）
# 依赖：jsbeautifier（pip install --break-system-packages -i 清华 jsbeautifier）
python3 <cocos2d-dec>/js_xxtea_decrypt.py -k "<密钥>" <assets目录>   # 目录模式
>>> 生成每个 .jsc 同名的 .js（可读 CommonJS / SystemJS）
```
> ⚠️ js_xxtea_decrypt.py 的**单文件模式有 bug**（decrypt_folder 的 else 分支引用未定义的
> `file_path`，UnboundLocalError）→ **必须传目录**（os.walk 分支正常）。

**cc-reverse 用法**（资源 + 重建，备选）：解包目录需指向 `assets` 子目录（因为项目是双层
`assets/assets/<bundle>`，cc-reverse 的 isBundleRoot 检查 `root/assets/<bundle>`）：
```bash
node <cc-reverse>/bin/cc-reverse.js --path <解包目录>/assets -o <输出目录> --key "<密钥>"
```

## 3. 可逆重打包（汉化核心 · 已验证）

**关键结论**：`xxtea_encrypt(xxtea_decrypt(原 .jsc)) == 原 .jsc`（完全一致，可逆双射）。
Cocos 运行时加载 `.jsc` 用同一 XXTEA 库。因此汉化后把改过的 `.js` 用同库 `xxtea_encrypt`
重新加密回 `.jsc`，**与原文件格式完全等价、可被引擎直接加载**。

```python
import ctypes
lib = ctypes.CDLL("<cocos2d-dec>/lib/libext_xxtea.so")
lib.xxtea_encrypt.argtypes=[ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
lib.xxtea_encrypt.restype=ctypes.POINTER(ctypes.c_ubyte)
outlen=ctypes.c_ulong()
p=lib.xxtea_encrypt(js_bytes, len(js_bytes), key_bytes, len(key_bytes), ctypes.byref(outlen))
enc = bytes(p[i] for i in range(outlen.value))   # = 可加载 .jsc
```

**重打包全链路**：
1. 改明文 `.js`（汉化 / 删广告模块）→ 2. `xxtea_encrypt` 加密回 `.jsc`（替换 assets 树）
→ 3. `apktool b` 重打包（或用原有解包树 zip 重建）→ 4. 剥离旧签名 → `zipalign` → `apksigner` v1+v2+v3。

## 4. 广告 SDK 移除清单（Cocos 游戏典型，三层）

| 层 | 目标 |
|----|------|
| native | `libapplovin-native-crash-reporter.so`、`libverbanr.so`、`libdatastore_shared_counter.so`（保留 `libcocos2djs.so`） |
| assets | `ad-viewer/`(OM SDK, omid/omsdk *.js)、`audience_network/`(FB AN classes*.dex)、`mbridge_*`、`res/drawable/applovin_*` |
| manifest | `<provider>/<service>/<activity>` 声明 applovin/facebook/gms/adjust/unity3d（保留 INTERNET） |
| JS | `AdManager` / `AndroidAd` / `CSJ`(穿山甲) / `moreGame` 等 CommonJS 模块（删模块或桩化 showVideo/showInter/loadReward） |

## 5. 备注

- 密钥、引擎判断、可逆重打包这三步是 Cocos Creator 汉化的**全部卡点**；打通后与常规手游汉化路径一致。
- 文本在解密后的 `assets/assets/main/index.<hash>.js`（CommonJS 模块，含大量英文字面量）与各 bundle 脚本中。
