/**
 * SDKUtils — 统一的 SDK 模拟工具类
 *
 * 本文件是跨项目复用的模板，直接复制到 com/android/common/SDKUtils.java 即可。
 *
 * ## 职责
 *
 * 1. 激励视频三阶段模拟（加载 → 播放 → 关闭）
 * 2. IRewardVideoListener 接口定义完整回调生命周期
 * 3. IAP 购买成功模拟 + Premium 解锁模拟
 * 4. Activity 生命周期钩子（供 MainActivity.template.java 调度）
 *
 * ## 三阶段模拟流程
 *
 *   主线程 Handler 启动
 *   → 延迟 500ms: onRewardLoaded()  [模拟广告加载]
 *     → 延迟 1500ms: listener.onReward()  [模拟广告播放完成，发放奖励]
 *       → 延迟 300ms: listener.onRewardHidden()  [模拟关闭]
 *
 * 每个阶段都有 Toast 实时反馈给用户。
 */
package com.android.common;

import android.app.Activity;
import android.app.Application;
import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.view.KeyEvent;
import android.widget.Toast;

public class SDKUtils {
    private static Application g_App = null;
    private static Activity g_Activity = null;

    public static final int MSG_REFRESH_RV = 9000;

    private static final Handler handler = new Handler(Looper.getMainLooper()) {
        @Override
        public void handleMessage(Message msg) {
            switch (msg.what) {
                case MSG_REFRESH_RV: {
                    break;
                }
            }
            super.handleMessage(msg);
        }
    };

    // ── 激励视频监听器接口 ──────────────────────────────────

    public interface IRewardVideoListener {
        void onRewardLoaded();
        void onRewardLoadedFail();
        void onReward();
        void onRewardHidden();
        void onRewardClicked();
    }

    public static IRewardVideoListener g_listener = null;

    // ── 生命周期 ──────────────────────────────────────────────

    public static void init(Application app) {
        g_App = app;
        // 恢复已购买集合（IAP 模拟持久化）
        try {
            if (app != null) {
                java.util.Set<String> saved = app.getSharedPreferences("iap_cache", Context.MODE_PRIVATE)
                    .getStringSet("purchased", null);
                if (saved != null) {
                    purchasedSkus.addAll(saved);
                }
            }
        } catch (Exception ignored) { }
    }

    public static void onCreate(Activity activity) {
        g_Activity = activity;
        if (activity != null) {
            g_App = activity.getApplication();
        }
        showToast(activity, "SDK 初始化完成");
    }

    public static void onResume(Activity activity) {
        g_Activity = activity;
    }

    public static void onPause(Activity activity) {
    }

    public static void onRestart(Activity activity) {
    }

    public static void onDestroy(Activity activity) {
        if (g_Activity == activity) {
            g_Activity = null;
        }
    }

    public static boolean onKeyDown(Activity activity, int keyCode, KeyEvent event) {
        return false;
    }

    // ── 激励视频模拟 ──────────────────────────────────────────

    /**
     * 模拟激励视频播放流程（三阶段延迟）
     *
     * 阶段1: 500ms — 广告加载（onRewardLoaded）
     * 阶段2: 1500ms — 广告播放（listener.onReward 发放奖励）
     * 阶段3: 300ms — 广告关闭（onRewardHidden）
     *
     * @param listener IRewardVideoListener 回调接口
     */
    public static void showRewardedVideo(final IRewardVideoListener listener) {
        if (listener == null) return;

        showToast("广告加载中...");

        // 阶段1: 延迟 500ms 模拟广告加载
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                listener.onRewardLoaded();
                showToast("广告播放中...");

                // 阶段2: 延迟 1500ms 模拟广告播放
                handler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        // 奖励发放
                        listener.onReward();

                        // 阶段3: 延迟 300ms 后关闭
                        handler.postDelayed(new Runnable() {
                            @Override
                            public void run() {
                                listener.onRewardHidden();
                            }
                        }, 300);
                    }
                }, 1500);
            }
        }, 500);
    }

    /**
     * 模拟激励视频加载但不播放（用于预加载场景）
     */
    public static void loadRewardedVideo(final IRewardVideoListener listener) {
        if (listener == null) return;
        showToast("广告加载中...");
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                listener.onRewardLoaded();
                showToast("广告已就绪");
            }
        }, 500);
    }

    /**
     * 模拟插屏广告（直接跳过，无显示）
     */
    public static void showInterstitial() {
        // 插屏广告 — 跳过，不影响游戏流程
    }

    // ── IAP 购买模拟 ──────────────────────────────────────────

    /**
     * 模拟 IAP 购买成功
     * @param productId 商品 ID
     * @param onSuccess 购买成功回调（Runnable）
     * @param onError   购买失败回调（Runnable）
     */
    /** 已购买商品集合（Java 层维护，native Is* hook 通过 isPurchased() 查询） */
    private static final java.util.Set<String> purchasedSkus = new java.util.HashSet<>();

    /**
     * 记录已购买商品（模拟购买成功后调用，持久化到 SharedPreferences）
     * @param productId 商品 ID（完整，含 com.<pkg>. 前缀）
     */
    public static void recordPurchase(String productId) {
        purchasedSkus.add(productId);
        try {
            if (g_App != null) {
                g_App.getSharedPreferences("iap_cache", Context.MODE_PRIVATE)
                    .edit()
                    .putStringSet("purchased", purchasedSkus)
                    .apply();
            }
        } catch (Exception ignored) { }
    }

    /**
     * 查询商品是否已购买（供 native Is* hook 调用）
     * @param productId 完整商品 ID；也可传短名（如 "removeads"）
     * @return true=已购买
     */
    public static boolean isPurchased(String productId) {
        if (productId == null) return false;
        if (purchasedSkus.contains(productId)) return true;
        // 支持短名匹配（strip 前缀）
        String shortName = productId;
        int dot = productId.lastIndexOf('.');
        if (dot >= 0) shortName = productId.substring(dot + 1);
        for (String s : purchasedSkus) {
            if (s.endsWith("." + shortName) || s.equals(shortName)) return true;
        }
        return false;
    }

    public static void processPurchase(String productId, final Runnable onSuccess, final Runnable onError) {
        showToast("购买中: " + productId);
        // 延迟 800ms 模拟网络请求
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                recordPurchase(productId);
                showToast("购买成功: " + productId);
                if (onSuccess != null) onSuccess.run();
            }
        }, 800);
    }

    // ── Premium 解锁模拟 ──────────────────────────────────────

    /**
     * 模拟 Premium 解锁
     * @param onComplete 完成回调
     */
    public static void unlockPremium(final Runnable onComplete) {
        showToast("Premium 解锁中...");
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                showToast("Premium 已解锁");
                if (onComplete != null) onComplete.run();
            }
        }, 500);
    }

    // ── 通用广告控制 ──────────────────────────────────────────

    public static void showAd(boolean bShow) {
    }

    // ── UI 反馈 ──────────────────────────────────────────────

    /**
     * 在主线程显示 Toast
     * @param msg 消息内容
     */
    private static void showToast(final String msg) {
        handler.post(new Runnable() {
            @Override
            public void run() {
                Context ctx = g_Activity != null ? g_Activity : g_App;
                if (ctx != null) {
                    Toast.makeText(ctx, msg, Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    /**
     * 使用指定 Context 在主线程显示 Toast
     */
    private static void showToast(final Context context, final String msg) {
        if (context == null) {
            showToast(msg);
            return;
        }
        handler.post(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(context, msg, Toast.LENGTH_SHORT).show();
            }
        });
    }

    /**
     * 获取当前 Activity（供外部使用）
     */
    public static Activity getActivity() {
        return g_Activity;
    }
}
