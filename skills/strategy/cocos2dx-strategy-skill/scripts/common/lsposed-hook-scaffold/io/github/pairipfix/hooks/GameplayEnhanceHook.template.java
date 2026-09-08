package io.github.ahmedmani.pairipfix.hooks;

import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;

import io.github.ahmedmani.pairipfix.BaseHook;

/**
 * 游戏增强 hook：
 * 1. IAP 直接转发成功（purchaseIAB → cppAddSucceedPurchaseItemId + cppSetOKtoGiveJewel）
 * 2. 激励视频广告直接给奖励（showMediatedVideoAdDefault → cppOKtoGiveV4VCReward）
 * 3. 插屏广告直接成功（showMediatedIntersDefault → cppInterstitialSet(true)）
 * 4. 网络检测绕过（IsOnline → true）
 */
public class GameplayEnhanceHook extends BaseHook {
    private static final String TAG = "KW2Enhance";
    private static final String APP_ACTIVITY = "org.cocos2dx.cpp.AppActivity";
    private static final String IAP_CLASS = "org.cocos2dx.cpp.IAP";

    @Override
    public String getName() {
        return "GameplayEnhanceHook";
    }

    @Override
    public boolean apply() {
        boolean status = false;
        try {
            status |= hookIapForwarding();
        } catch (Throwable t) {
            XposedBridge.log("[" + TAG + "] IAP hook error: " + t.getMessage());
        }
        try {
            status |= hookAdForwarding();
        } catch (Throwable t) {
            XposedBridge.log("[" + TAG + "] AD hook error: " + t.getMessage());
        }
        try {
            status |= hookNetworkBypass();
        } catch (Throwable t) {
            XposedBridge.log("[" + TAG + "] Network hook error: " + t.getMessage());
        }
        try {
            status |= hookForceChinese();
        } catch (Throwable t) {
            XposedBridge.log("[" + TAG + "] Chinese hook error: " + t.getMessage());
        }
        return status;
    }

    /**
     * 强制简体中文：游戏内置多语言，系统语言为中文时强制简体（D_CHN=3）
     * 在 AppActivity 初始化后设置 m_Int_Language_Code=3 并调 cppSetLanguage(3)
     */
    private boolean hookForceChinese() throws Throwable {
        boolean ok = false;
        try {
            Class<?> actClazz = findClass(APP_ACTIVITY);
            if (actClazz == null) {
                XposedBridge.log("[" + TAG + "] AppActivity not found for chinese hook");
                return false;
            }
            // AppActivity.onActivityResult 或 onResume 在生命周期稳定后执行，此时设置语言
            XposedHelpers.findAndHookMethod(actClazz, "onResume", new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    forceChineseSimple();
                }
            });
            // 备选：onWindowFocusChanged
            XposedHelpers.findAndHookMethod(actClazz, "onWindowFocusChanged",
                    boolean.class, new XC_MethodHook() {
                        @Override
                        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                            forceChineseSimple();
                        }
                    });
            ok = true;
        } catch (Throwable t) {
            XposedBridge.log("[" + TAG + "] chinese hook fail: " + t.getMessage());
        }
        return ok;
    }

    private void forceChineseSimple() {
        try {
            Class<?> actClazz = findClass(APP_ACTIVITY);
            if (actClazz == null) return;
            // 检查当前语言：仅当系统为中文时才强制简体，避免破坏韩/日/英
            String lang = java.util.Locale.getDefault().getLanguage();
            if (lang == null || !lang.toLowerCase().startsWith("zh")) {
                return;
            }
            Object cur = XposedHelpers.getStaticObjectField(actClazz, "m_Int_Language_Code");
            int curCode = (cur == null) ? 0 : ((Integer) cur).intValue();
            if (curCode != 3) {
                XposedBridge.log("[" + TAG + "] forcing chinese simplified: " + curCode + " -> 3");
                XposedHelpers.setStaticIntField(actClazz, "m_Int_Language_Code", 3);
                try {
                    XposedHelpers.callStaticMethod(actClazz, "cppSetLanguage", 3);
                } catch (Throwable t) {
                    XposedBridge.log("[" + TAG + "] cppSetLanguage err: " + t.getMessage());
                }
            }
        } catch (Throwable t) {
            XposedBridge.log("[" + TAG + "] forceChineseSimple err: " + t.getMessage());
        }
    }

    /**
     * IAP 转发：hook purchaseIAB(String productId)
     * 直接通知 C++ 购买成功并下放奖励，跳过 Google Billing
     */
    private boolean hookIapForwarding() throws Throwable {
        try {
            Class<?> iapClazz = findClass(IAP_CLASS);
            if (iapClazz == null) {
                XposedBridge.log("[" + TAG + "] IAP class not found");
                return false;
            }
            XposedHelpers.findAndHookMethod(iapClazz, "purchaseIAB",
                    String.class, new XC_MethodHook() {
                        @Override
                        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                            String productId = (String) param.args[0];
                            XposedBridge.log("[" + TAG + "] purchaseIAB intercepted: " + productId);
                            Class<?> cls = findClass(IAP_CLASS);
                            if (cls == null) return;
                            try {
                                XposedHelpers.callStaticMethod(cls, "cppSetPendingtoFalse");
                            } catch (Throwable t) {
                                XposedBridge.log("[" + TAG + "] cppSetPendingtoFalse err: " + t.getMessage());
                            }
                            try {
                                XposedHelpers.callStaticMethod(cls, "cppAddSucceedPurchaseItemId", productId);
                            } catch (Throwable t) {
                                XposedBridge.log("[" + TAG + "] cppAddSucceedPurchaseItemId err: " + t.getMessage());
                            }
                            try {
                                XposedHelpers.callStaticMethod(cls, "cppSetOKtoGiveJewel");
                            } catch (Throwable t) {
                                XposedBridge.log("[" + TAG + "] cppSetOKtoGiveJewel err: " + t.getMessage());
                            }
                            param.setResult(null);
                        }
                    });
            return true;
        } catch (Throwable t) {
            XposedBridge.log("[" + TAG + "] purchaseIAB hook fail: " + t.getMessage());
            throw t;
        }
    }

    /**
     * 广告转发：
     * - 激励视频：showMediatedVideoAdDefault(String) → cppOKtoGiveV4VCReward（直接给奖励）
     * - 插屏：showMediatedIntersDefault(String) → cppInterstitialSet(true)（直接成功）
     */
    private boolean hookAdForwarding() throws Throwable {
        boolean ok = false;
        Class<?> actClazz = findClass(APP_ACTIVITY);
        if (actClazz == null) {
            XposedBridge.log("[" + TAG + "] AppActivity class not found");
            return false;
        }
        // 激励视频
        try {
            XposedHelpers.findAndHookMethod(actClazz, "showMediatedVideoAdDefault",
                    String.class, new XC_MethodHook() {
                        @Override
                        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                            XposedBridge.log("[" + TAG + "] showMediatedVideoAdDefault intercepted");
                            Class<?> cls = findClass(APP_ACTIVITY);
                            if (cls != null) {
                                try {
                                    XposedHelpers.callStaticMethod(cls, "cppOKtoGiveV4VCReward");
                                } catch (Throwable t) {
                                    XposedBridge.log("[" + TAG + "] cppOKtoGiveV4VCReward err: " + t.getMessage());
                                }
                            }
                            param.setResult(null);
                        }
                    });
            ok = true;
        } catch (Throwable t) {
            XposedBridge.log("[" + TAG + "] showMediatedVideoAdDefault hook fail: " + t.getMessage());
        }
        // 插屏
        try {
            XposedHelpers.findAndHookMethod(actClazz, "showMediatedIntersDefault",
                    String.class, new XC_MethodHook() {
                        @Override
                        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                            XposedBridge.log("[" + TAG + "] showMediatedIntersDefault intercepted");
                            Class<?> cls = findClass(APP_ACTIVITY);
                            if (cls != null) {
                                try {
                                    XposedHelpers.callStaticMethod(cls, "cppInterstitialSet", true);
                                } catch (Throwable t) {
                                    XposedBridge.log("[" + TAG + "] cppInterstitialSet err: " + t.getMessage());
                                }
                            }
                            param.setResult(null);
                        }
                    });
            ok = true;
        } catch (Throwable t) {
            XposedBridge.log("[" + TAG + "] showMediatedIntersDefault hook fail: " + t.getMessage());
        }
        return ok;
    }

    /**
     * 网络检测绕过：IsOnline() → true
     */
    private boolean hookNetworkBypass() throws Throwable {
        try {
            Class<?> actClazz = findClass(APP_ACTIVITY);
            if (actClazz == null) {
                XposedBridge.log("[" + TAG + "] AppActivity class not found for IsOnline");
                return false;
            }
            XposedHelpers.findAndHookMethod(actClazz, "IsOnline",
                    new XC_MethodHook() {
                        @Override
                        protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                            param.setResult(Boolean.TRUE);
                        }
                    });
            return true;
        } catch (Throwable t) {
            XposedBridge.log("[" + TAG + "] IsOnline hook fail: " + t.getMessage());
            return false;
        }
    }
}
