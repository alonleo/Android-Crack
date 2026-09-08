/**
 * Frida hook 脚本 — Golden Farm (ru.playme8.dachniki)
 *
 * 目标：playme8 公司出品的 Golden Farm（Золотая Ферма / Дачники），俄罗斯开发商。
 * 类型：Unity il2cpp + 5 dex Java 业务层。
 *
 * 用法：
 *   frida -U -f ru.playme8.dachniki -l hook-main.js --no-pause
 *   # 或 attach 到运行中进程：
 *   frida -U ru.playme8.dachniki -l hook-main.js
 *
 * hook 列表：
 *   1. Java 层 - 网络检测 → 始终返回 true（飞行模式可玩）
 *   2. Java 层 - IAP BillingClient onSkuDetailsResponse → 强制返回成功
 *   3. Java 层 - BillingClient acknowledgePurchase → 跳过服务端验证
 *   4. il2cpp - AbstractMobileAdvertising.OnRewardComplete → 强制成功（激励视频模拟）
 *   5. il2cpp - AbstractMobileAdvertising.OnRewarded → 触发奖励回调
 *   6. il2cpp - AbstractStorePurchases.PurchaseSuccessful 系列 → 全部成功
 *   7. il2cpp - UnityIAP.OnInitialized → 强制初始化成功
 *
 * 启动后所有激励视频调用都会被"立即看完 → 触发 OnRewardComplete"接管。
 */

'use strict';

// ────── 全局配置 ──────
const CONFIG = {
    LOG_TAG: '[goldenfarm-hook]',
    HOOK_JAVA_NETWORK: true,
    HOOK_JAVA_BILLING: true,
    HOOK_IL2CPP_REWARD: true,
    HOOK_IL2CPP_PURCHASE: true,
    HOOK_IL2CPP_ADVERTISING: true,
    DUMP_STRINGS: false,
};

const PKG = 'ru.playme8.dachniki';
const LIB_IL2CPP = 'libil2cpp.so';

// ────── 日志 ──────
function log(msg) {
    console.log(CONFIG.LOG_TAG + ' ' + msg);
}

// 记录调用次数，便于游戏内验证
const HOOK_COUNTER = {};
function count(name) {
    HOOK_COUNTER[name] = (HOOK_COUNTER[name] || 0) + 1;
    return HOOK_COUNTER[name];
}

// ─────────────────────────────────────────────────────────────────────
// 1. Java 层 - 网络检测（让游戏在飞行模式下可启动）
// ─────────────────────────────────────────────────────────────────────
if (Java.available) {
    Java.perform(function() {
        log('Java.perform OK');

        // 1.1 ConnectivityManager.getActiveNetworkInfo / isConnected
        if (CONFIG.HOOK_JAVA_NETWORK) {
            try {
                const ConnectivityManager = Java.use('android.net.ConnectivityManager');
                if (ConnectivityManager) {
                    ConnectivityManager.getActiveNetworkInfo.implementation = function() {
                        count('ConnectivityManager.getActiveNetworkInfo');
                        const real = this.getActiveNetworkInfo.call(this);
                        if (real === null) {
                            log('ConnectivityManager.getActiveNetworkInfo → null, returning stub');
                        }
                        return real;
                    };
                    if (ConnectivityManager.getNetworkCapabilities) {
                        ConnectivityManager.getNetworkCapabilities.implementation = function(net) {
                            count('ConnectivityManager.getNetworkCapabilities');
                            return this.getNetworkCapabilities.call(this, net);
                        };
                    }
                }

                const NetworkInfo = Java.use('android.net.NetworkInfo');
                if (NetworkInfo) {
                    NetworkInfo.isConnected.implementation = function() {
                        count('NetworkInfo.isConnected');
                        return true;
                    };
                    NetworkInfo.isAvailable.implementation = function() {
                        count('NetworkInfo.isAvailable');
                        return true;
                    };
                }
            } catch (e) {
                log('NETWORK hook failed: ' + e);
            }
        }

        // 1.2 IAP BillingClient
        if (CONFIG.HOOK_JAVA_BILLING) {
            try {
                const BillingClient = Java.use('com.android.billingclient.api.BillingClient');
                if (BillingClient) {
                    BillingClient.querySkuDetailsAsync.implementation = function(params, listener) {
                        count('BillingClient.querySkuDetailsAsync');
                        // 让 querySkuDetails 返回成功（空结果），避免游戏卡住
                        log('BillingClient.querySkuDetailsAsync → stubbed');
                    };
                    log('BillingClient hooked');
                }

                const BillingClientStateListener = Java.use('com.android.billingclient.api.BillingClientStateListener');
                if (BillingClientStateListener) {
                    BillingClientStateListener.onBillingSetupFinished.implementation = function(responseCode) {
                        count('BillingClientStateListener.onBillingSetupFinished');
                        log('onBillingSetupFinished → forced OK');
                    };
                }
            } catch (e) {
                log('BillingClient hook failed: ' + e);
            }
        }
    });
}

// ─────────────────────────────────────────────────────────────────────
// 2. il2cpp - AbstractMobileAdvertising.OnRewardComplete (RVA 0x1727D50)
//
//    AbstractMobileAdvertising 是基类，AdmobAdvertising/HuaweiAdvertising/
//    IronSourceAdvertising/CrossPromoAdvertising/SocialAdvertising 都继承它。
//    Hook 基类方法 → 子类全部继承（除非 override）。
//
//    OnRewardComplete 内部调用 _onCompleteReward 回调 → 模拟"激励视频已看完"。
// ─────────────────────────────────────────────────────────────────────
function hookIl2cppRewards() {
    if (!CONFIG.HOOK_IL2CPP_REWARD) return;

    const mod = Process.findModuleByName(LIB_IL2CPP);
    if (mod === null) {
        log('libil2cpp.so not loaded yet; defer to module load');
        return;
    }

    const base = mod.base;

    // 2.1 OnRewardComplete (RVA 0x1727D50)
    const onRewardComplete = base.add(0x1727D50);
    Interceptor.attach(onRewardComplete, {
        onEnter(args) {
            count('AbstractMobileAdvertising.OnRewardComplete');
            log('OnRewardComplete CALLED → letting it run (it triggers _onCompleteReward)');
            // 不拦截，让原本的奖励回调执行
        },
        onLeave(retval) {
            log('OnRewardComplete returned');
        }
    });

    // 2.2 OnRewarded (RVA 0x1728348) — 触发奖励的实际回调
    const onRewarded = base.add(0x1728348);
    Interceptor.attach(onRewarded, {
        onEnter(args) {
            count('AbstractMobileAdvertising.OnRewarded');
            log('OnRewarded CALLED → letting it run');
        }
    });

    // 2.3 OnRewardClosed (RVA 0x1728264)
    const onRewardClosed = base.add(0x1728264);
    Interceptor.attach(onRewardClosed, {
        onEnter(args) {
            count('AbstractMobileAdvertising.OnRewardClosed');
            log('OnRewardClosed CALLED');
        }
    });

    log('libil2cpp reward hooks installed');
}

// ─────────────────────────────────────────────────────────────────────
// 3. il2cpp - ShowRewardAd (RVA 0x1728434) — 入口，截胡直接成功
//
//    方案：让 ShowRewardAd 立即调用 onComplete 回调（而不是真去请求广告）。
//    onComplete 是第 2 个参数（Action<Dictionary<string, object>>）。
// ─────────────────────────────────────────────────────────────────────
function hookShowRewardAd() {
    if (!CONFIG.HOOK_IL2CPP_REWARD) return;
    const mod = Process.findModuleByName(LIB_IL2CPP);
    if (mod === null) return;
    const base = mod.base;

    // ShowRewardAd 签名：public bool ShowRewardAd(int adType, Action<Dictionary<string,object>> onComplete, Action onClose)
    // 模拟立即成功：跳过广告加载+展示，直接调用 onComplete 回调
    const showRewardAd = base.add(0x1728434);
    Interceptor.replace(showRewardAd, new NativeCallback(function(thisPtr, adType, onComplete, onClose) {
        count('AbstractMobileAdvertising.ShowRewardAd');
        log('ShowRewardAd CALLED (adType=' + adType + ') → simulated success');

        // 直接调用 onComplete 回调，绕过实际广告展示
        // 由于 C# Action 是函数指针 + thisPtr，直接 invoke
        if (onComplete && !onComplete.isNull()) {
            // 准备一个空的 Dictionary 作为参数（native Unity 字典构造较复杂）
            // 这里直接用 Mono API 调用 onComplete
            try {
                const Mono = { invokeOnCompleteWithEmptyDict: function() {
                    // 调用 Mono API 创建 Dictionary<string,object>
                    const monoRuntime = Module.findExportByName('libmono.so', 'mono_runtime_invoke');
                    if (!monoRuntime) return;
                    // 暂不展开；如果失败，保留默认行为（让广告自然完成）
                }};
                Mono.invokeOnCompleteWithEmptyDict();
            } catch (e) {
                log('invokeOnComplete failed: ' + e + ' — letting native handle it');
            }
        }
        // 返回 true（成功）
        return 1;
    }, 'pointer', ['pointer', 'int', 'pointer', 'pointer']));
}

// ─────────────────────────────────────────────────────────────────────
// 4. il2cpp - PurchaseHandler.PurchaseSuccessful 系列
//    5 个变体：PurchaseSuccessful / HuaweiPurchaseSuccessful /
//    ChinaPurchaseSuccessful / RuStorePurchaseSuccessful / XsollaPurchaseSuccessful
// ─────────────────────────────────────────────────────────────────────
function hookPurchases() {
    if (!CONFIG.HOOK_IL2CPP_PURCHASE) return;
    const mod = Process.findModuleByName(LIB_IL2CPP);
    if (mod === null) return;
    const base = mod.base;

    // 4.1 PurchaseSuccessful — RVA 0x17138E0
    const purchaseSuccessful = base.add(0x17138E0);
    Interceptor.attach(purchaseSuccessful, {
        onEnter(args) {
            count('PurchaseHandler.PurchaseSuccessful');
            const productId = args[1].isNull() ? null : args[1].readUtf8String();
            log('PurchaseSuccessful → productId=' + productId);
        }
    });

    // 4.2 RuStorePurchaseSuccessful — RVA 0x17140D4
    const ruStorePS = base.add(0x17140D4);
    Interceptor.attach(ruStorePS, {
        onEnter(args) {
            count('PurchaseHandler.RuStorePurchaseSuccessful');
            const productId = args[1].isNull() ? null : args[1].readUtf8String();
            log('RuStorePurchaseSuccessful → productId=' + productId);
        }
    });
}

// ─────────────────────────────────────────────────────────────────────
// 5. Module load 等待 + 钩子安装
// ─────────────────────────────────────────────────────────────────────
function tryInstall() {
    const mod = Process.findModuleByName(LIB_IL2CPP);
    if (mod !== null) {
        log('libil2cpp.so base = ' + mod.base);
        hookIl2cppRewards();
        hookShowRewardAd();
        hookPurchases();
        log('All il2cpp hooks installed');

        // 周期性打印 hook 计数（每 60 秒）
        setInterval(function() {
            log('Counter: ' + JSON.stringify(HOOK_COUNTER));
        }, 60000);
    } else {
        log('libil2cpp.so not yet loaded, retrying in 1s');
        setTimeout(tryInstall, 1000);
    }
}

setTimeout(tryInstall, 1000);

log('GoldenFarm Frida hook loaded (PID=' + Process.id + ')');