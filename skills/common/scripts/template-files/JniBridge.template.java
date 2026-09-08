/**
 * JniBridge — Java ← Native 双向回调桥接
 *
 * 本文件是跨项目复用的模板，直接复制到 {PACKAGE_NAME}/JniBridge.java 即可。
 *
 * ## 职责
 *
 * 1. 接收 native-lib.cpp 通过 JNI 回调的事件字符串
 * 2. 路由到 MainActivity.onJniCall() → Handler → callJava()
 *
 * ## 贯通链路
 *
 *   Native Hook 触发 → callJava("showVideo")
 *     → JniBridge.onJniCall(msg)
 *       → MainActivity.onJniCall(msg)
 *         → Handler → callJava("showVideo")
 *           → SDKUtils.showRewardedVideo(listener)
 *             → listener.onReward() → videoComplete(true)
 *               → onVideoReward(true) [native JNI]
 *                 → 调用原始 il2cpp 函数
 */
package {PACKAGE_NAME};

import android.util.Log;

public class JniBridge {

    private static final String TAG = "xNative";
    private final MainActivity activity;

    public JniBridge(MainActivity activity) {
        this.activity = activity;
    }

    /**
     * 由 native-lib.cpp 的 callJava() 通过 JNI 调用。
     *
     * @param msg 事件字符串，例如 "showVideo" / "processPurchase" / "premiumUnlock"
     */
    public void onJniCall(String msg) {
        Log.i(TAG, "[JniBridge] native event: " + msg);
        if (activity != null) {
            activity.onJniCall(msg);
        } else {
            Log.w(TAG, "[JniBridge] activity is null, dropping: " + msg);
        }
    }

    /**
     * 检查桥接是否有效（供 native 层调用前检查）
     */
    public boolean isValid() {
        return activity != null;
    }
}
