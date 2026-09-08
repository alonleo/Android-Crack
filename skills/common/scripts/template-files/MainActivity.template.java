/**
 * MainActivity — FakerAndroid 模板架构的主 Activity
 *
 * 本文件是跨项目复用的模板，使用时替换 {PLACEHOLDER} 即可。
 *
 * ## 占位符
 *
 * | 占位符 | 示例值 | 说明 |
 * |--------|--------|------|
 * | {PACKAGE_NAME} | com.android.boot | FakerAndroid 的 Java 包名 |
 * | {ORIGINAL_ACTIVITY} | UnityPlayerActivity | 游戏原始 Activity 类名 |
 * | {ORIGINAL_ACTIVITY_IMPORT} | com.unity3d.player.UnityPlayerActivity | 原始 Activity 的完整 import |
 * | {NATIVE_LIB_LOAD} | System.loadLibrary("native-lib") | native 库加载语句 |
 * | {VIDEO_COMPLETE_CALLBACK} | onVideoReward(isSucess) | 激励视频完成后的 JNI 回调 |
 *
 * ## 贯通链路（以激励视频为例）
 *
 *   il2cpp ShowRewardAd 被调用
 *     → A64HookFunction 拦截 → callJava("showVideo") [JNI]
 *       → JniBridge.onJniCall("showVideo")
 *         → MainActivity.onJniCall("showVideo")
 *           → Handler → callJava("showVideo")
 *             → SDKUtils.showRewardedVideo(listener)
 *               → 延迟 500ms → onRewardLoaded()
 *                 → 延迟 1500ms → listener.onReward()
 *                   → videoComplete(true)
 *                     → onVideoReward(true) [JNI 回 native]
 *                       → 调用原始 il2cpp OnRewardComplete
 *
 *   IAP 链路（与广告对称，经 SDKUtils）：
 *   il2cpp InitiatePurchase(id) 被调用
 *     → A64HookFunction 拦截 → callJava("processPurchase:<id>")
 *       → JniBridge.onJniCall("processPurchase:<id>")
 *         → MainActivity.onJniCall("processPurchase:<id>")
 *           → Handler → callJava("processPurchase:<id>") [解析 payload=id]
 *             → SDKUtils.processPurchase(id, onSuccess → onIapSuccess(id), onError)
 *               → onIapSuccess(id) [JNI 回 native]
 *                 → 调用原始 il2cpp PurchaseSuccessful
 */
package {PACKAGE_NAME};

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.res.Configuration;
import android.os.Bundle;
import android.os.Handler;
import android.os.LocaleList;
import android.os.Looper;
import android.os.Message;
import android.view.KeyEvent;
import android.widget.Toast;

import com.android.common.SDKUtils;
import {ORIGINAL_ACTIVITY_IMPORT};

import java.util.Locale;


public class MainActivity extends {ORIGINAL_ACTIVITY} {

    static {
        {NATIVE_LIB_LOAD};
    }

    /**
     * 强制锁定系统 Locale 为简体中文（zh-CN）。
     *
     * 原因：Unity 的 `Application.systemLanguage` 由 Android 默认 Locale 决定，
     * 游戏的 `Localization.LoadAndSelect()` 通常按 systemLanguage 选词条。
     * 若设备 Locale = en-US / ja-JP 等，Unity 会选非中文词条 → UI 全英文/日文/等。
     *
     * 修复：在 `attachBaseContext`（比 onCreate 更早，所有资源加载前），
     * 用 Locale.setDefault(SIMPLIFIED_CHINESE) + Configuration 覆盖，
     * 确保 Unity 读到的 systemLanguage == "Chinese"。
     *
     * [规则] 任何多语言 APK → 强制 zh-CN（用户全局规则）
     * [FLOWFIX]
     */
    @Override
    protected void attachBaseContext(Context base) {
        Locale zhCN = Locale.SIMPLIFIED_CHINESE;
        Locale.setDefault(zhCN);

        Configuration cfg = new Configuration(base.getResources().getConfiguration());
        cfg.setLocale(zhCN);
        cfg.setLocales(new LocaleList(zhCN));
        Context ctx = base.createConfigurationContext(cfg);
        super.attachBaseContext(ctx);
    }

    public static Activity mActivity;
    public static MainActivity instance = null;
    static final int HANDLER_MSG_CALLJAVA = 1000;

    final Handler handler = new Handler(Looper.getMainLooper()) {
        @Override
        public void handleMessage(Message msg) {
            switch (msg.what) {
                case HANDLER_MSG_CALLJAVA:
                    String cmsg = (String) msg.obj;
                    callJava(cmsg);
                    break;
            }
            super.handleMessage(msg);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        mActivity = this;
        instance = this;
        SDKUtils.onCreate(this);

        // 注册 JNI 回调通道：native hooks → JniBridge → onJniCall()
        registerCallBack(new JniBridge(this));

        // Unity 初始化完成后，重试 hook 设置（il2cpp.so 此时应已加载）
        retryNativeHooks();
    }

    @Override
    protected void onDestroy() {
        SDKUtils.onDestroy(this);
        mActivity = null;
        instance = null;
        super.onDestroy();
    }

    // ──────────────────────────────────────────────────────────────
    // JNI 回调入口（由 native-lib.cpp 的 callJava() 触发）
    // ──────────────────────────────────────────────────────────────

    /**
     * 由 native-lib.cpp 的 callJava() 通过 JNI 调用。
     * 将消息投递到主线程 Handler 处理。
     */
    public void onJniCall(String msg) {
        Message message = new Message();
        message.what = HANDLER_MSG_CALLJAVA;
        message.obj = msg;
        handler.sendMessage(message);
    }

    /**
     * 主线程上处理来自 native hook 的事件。
     * 支持 "action" 和 "action:payload" 两种格式。
     */
    private void callJava(String msg) {
        // 解析事件（支持 "action:payload" 格式）
        String action = msg;
        String payload = "";
        int colonIdx = msg.indexOf(':');
        if (colonIdx > 0) {
            action = msg.substring(0, colonIdx);
            payload = msg.substring(colonIdx + 1);
        }

        switch (action) {
            case "showInterstitial":
                // 插屏广告 — 跳过（无操作）
                break;

            case "showVideo":
                // 激励视频 — 走 SDKUtils 模拟三阶段播放流程
                SDKUtils.showRewardedVideo(new SDKUtils.IRewardVideoListener() {
                    @Override
                    public void onRewardLoaded() {
                        showToast("广告加载完成");
                    }

                    @Override
                    public void onRewardLoadedFail() {
                        showToast("广告加载失败");
                    }

                    @Override
                    public void onReward() {
                        // SDKUtils 三阶段模拟完成后触发此回调
                        videoComplete(true);
                    }

                    @Override
                    public void onRewardHidden() {
                        showToast("广告关闭");
                    }

                    @Override
                    public void onRewardClicked() {
                        // 广告被点击（不处理）
                    }
                });
                break;

            case "processPurchase":
                // IAP 购买 → 走 SDKUtils 模拟购买流程（与激励视频转发逻辑一致）
                final String productId = payload;
                SDKUtils.processPurchase(
                        productId,
                        () -> onIapSuccess(productId),
                        () -> onIapSuccess(productId));
                break;

            case "premiumUnlock":
                // Premium 解锁
                showToast("Premium 已解锁");
                onPremiumUnlock();
                break;

            case "premiumBuyPass":
                // Premium Pass 购买
                showToast("Premium Pass 购买成功");
                onPremiumBuyPass();
                break;

            default:
                showToast("模拟: " + msg);
                break;
        }
    }

    // ──────────────────────────────────────────────────────────────
    // 视频完成回调
    // ──────────────────────────────────────────────────────────────

    /**
     * 激励视频播放完成 → 回调 native 触发原始 il2cpp OnRewardComplete。
     * 由 SDKUtils.IRewardVideoListener.onReward() 触发。
     */
    public void videoComplete(boolean isSucess) {
        {VIDEO_COMPLETE_CALLBACK};
    }

    // ──────────────────────────────────────────────────────────────
    // Native JNI 方法声明
    // ──────────────────────────────────────────────────────────────

    /**
     * 注册 JNI 回调对象（JniBridge）
     */
    public native void registerCallBack(JniBridge bridge);

    /**
     * Unity 初始化完成后重试 hook 设置（il2cpp.so 可能在 App.onCreate 时未加载）
     */
    public native void retryNativeHooks();

    /**
     * 激励视频完成回调 → native 调用原始 OnRewardComplete
     */
    public native void onVideoReward(boolean isSucess);

    /**
     * IAP 购买成功回调 → native 调用原始 PurchaseSuccessful
     */
    public native void onIapSuccess(String productId);

    /**
     * Premium 解锁回调 → native 调用原始 UnlockPremuim
     */
    public native void onPremiumUnlock();

    /**
     * Premium Pass 购买回调 → native 调用原始 BuyPremiumPass
     */
    public native void onPremiumBuyPass();

    // ──────────────────────────────────────────────────────────────
    // UI 反馈
    // ──────────────────────────────────────────────────────────────

    public void showToast(String str) {
        if (mActivity != null) {
            Toast.makeText(mActivity, str, Toast.LENGTH_SHORT).show();
        }
    }

    // ──────────────────────────────────────────────────────────────
    // 生命周期转发到 SDKUtils
    // ──────────────────────────────────────────────────────────────

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (SDKUtils.onKeyDown(this, keyCode, event)) {
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    protected void onRestart() {
        super.onRestart();
        SDKUtils.onRestart(this);
    }

    @Override
    protected void onPause() {
        super.onPause();
        SDKUtils.onPause(this);
    }

    @Override
    protected void onResume() {
        super.onResume();
        SDKUtils.onResume(this);
    }

}
