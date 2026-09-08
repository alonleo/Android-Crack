# LSPosed hook 脚手架 — Cocos2d-x 游戏 PairIP 绕过 + 增强

> 来源: KingdomWars2 (com.spcomes.kw2) | 2026-08-08
> 用途: 无法重打包（PairIP 绑定 Google Play 签名）时，用 LSPosed 运行时 hook 达成
>       绕过签名/license + IAP/广告转发 + 强制中文 + 网络绕过。

## 何时使用

- APK 含 `com/pairip/` 包 + `libpairipcore.so` + `assets/Sm4*`（PairIP 加固）
- **任何重签名**（即使零改动）→ `libpairipcore.so` JNI_OnLoad 内 0x41d4c SIGSEGV
- 原始 Google 签名可启动，但 LicenseActivity（Play 许可）验证失败退出
- 结论: 只能原始签名 + LSPosed hook，无法重打包交付

## 文件清单

| 文件 | 角色 |
|------|------|
| `mainHook.template.java` | LSPosed 入口，注册各 hook |
| `SignatureBypass.template.java` | 绕过 PairIP 签名检查（verifyIntegrity→空, verifySignatureMatches→true） |
| `LicenseClientBypass.template.java` | 绕过 Play 许可检查（initializeLicenseCheck→空, performLocalInstallerCheck→true） |
| `LicenseActivityBypass.template.java` | LicenseActivity 退出/paywall 方法置空 |
| `LicenseResponseBypass.template.java` | license 响应验证置空 |
| `GameplayEnhanceHook.template.java` | **游戏增强**: IAP/广告转发 + 强制简体中文 + IsOnline 绕过 |
| `BaseHook.template.java` | hook 基类（findClass/hookDoNothing/hookReturnConstant 等） |

## GameplayEnhanceHook 覆盖点（Cocos2d-x 通用模式）

| 方法 | 桥接 |
|------|------|
| `IAP.purchaseIAB(String productId)` | → `cppSetPendingtoFalse` + `cppAddSucceedPurchaseItemId` + `cppSetOKtoGiveJewel`（IAP 直接下放奖励） |
| `AppActivity.showMediatedVideoAdDefault(String)` | → `cppOKtoGiveV4VCReward`（激励视频直接给奖励） |
| `AppActivity.showMediatedIntersDefault(String)` | → `cppInterstitialSet(true)`（插屏直接成功） |
| `AppActivity.IsOnline()` | → true（网络绕过） |
| `AppActivity.m_Int_Language_Code` | 强制 3（简体中文 D_CHN），系统语言为 zh 时生效 |

## 编译

标准 Android 项目（AGP 8.13 / gradle 8.13 / compileSdk 34）:
```bash
# 依赖 de.robv.android.xposed:api:82 (compileOnly)
# 复制到 Android 工程 app/src/main/java/... 后:
./gradlew assembleDebug
```

## 配置 LSPosed 作用域

见 `skills/common/scripts/lsposed-config.py`（修改 `/data/adb/lspd/config/modules_config.db`）:
```bash
python3 skills/common/scripts/lsposed-config.py <serial> <module_pkg> <target_pkg> --adb $ADB_BIN
```

关键坑位:
- 必须 lspd 停止时改 db；重启 zygote 后 Magisk 拉起 lspd 会覆盖
- 安装原始 split APK 必须 `adb install-multiple`（单独装 base 报 libpairipcore.so not found）
- 游戏 IAP 商品 ID 在 `IAP.productIDs[]`（可用反射读取）
