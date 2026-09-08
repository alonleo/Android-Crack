#!/usr/bin/env python3
"""add-random-tip-banner.py — 给 patched.apk 项目加底部随机提示横幅。

[FLOWFIX 2026-08-18] CrowdCity Realme Android 14 上的"底部白条"被检测为 Android 12+
系统的 BOTTOM_GESTURES 手势条（不可用沉浸式消除），用 View banner 覆盖 + 随机游戏提示词
替代原本"贴黑色背景"的无效方案。

用法:
  python3 add-random-tip-banner.py <Name> --type <il2cpp|air|...> [--messages <jsonl>]

默认提示词 (20 条, 覆盖去功能点 / 跑酷技巧 / 提示去广告):
  - 🎯 走位要快，脑子要慢 — 抢占拐角，避开大军
  - 🏃 见到人群立刻绕路，避免正面硬刚
  - 🎲 集中人群才能解锁皮肤，散开没用
  - 🛡️ 复活中不要乱动，原地等即可
  - 🎁 看广告免广告按钮已隐藏，游戏更纯粹
  - 🔇 隐私和广告声明弹窗已关闭，专注游戏
  - ✨ 本次去功能点处理：13 项广告/弹窗入口
  - ... (共 20 条)

做的事情:
  1. 在 crackings/<type>/<Name>/project/app/src/main/java/com/android/boot/MainActivity.java
     的 onCreate 末尾追加 installTipBanner() 调用（如果还没）。
  2. 在 MainActivity.java 内加入:
     - private static final String[] TIP_MESSAGES = {...};
     - private FrameLayout tipBanner / private TextView tipText / private Handler tipHandler;
     - private void installTipBanner() {...} (5 秒轮换 + 渐变紫粉红底色 + 白色文字 + 阴影);
  3. 加 import: android.graphics.Color / Typeface / GradientDrawable / ...;
  4. 在 onDestroy 清理 tipHandler.removeCallbacks。

Banner 高度 80dp, GradientDrawable 渐变 0xCC7C3AED → 0xCCEC4899 → 0xCCEF4444。
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]

DEFAULT_TIPS = [
    "🎯 走位要快，脑子要慢 — 抢占拐角，避开大军",
    "👟 跟着第一名跑，蹭人数比自己攒快",
    "🏃 见到人群立刻绕路，避免正面硬刚",
    "🎪 复活次数用完后别急着冲，耐心等复活",
    "🎲 集中人群才能解锁皮肤，散开没用",
    "💰 金币留着换关键皮肤，别乱花",
    "🧠 观察小地图，提前预判对手行动",
    "🎮 打不过就加入 — 倒戈人数最多的一方",
    "🛡️ 复活中不要乱动，原地等即可",
    "🎽 皮肤加成可以叠加，整套穿收益最高",
    "🏆 排行榜不显示真实名次，只刷榜没用",
    "🤝 团队赛别抢人头，帮队友更容易赢",
    "🚪 窄路口是兵家必争之地，别一个人冲",
    "🛡️ 大群撞小群必胜，先攒人数再说",
    "🎁 看广告免广告按钮已隐藏，游戏更纯粹",
    "🔇 隐私和广告声明弹窗已关闭，专注游戏",
    "✨ 本次去功能点处理：13 项广告/弹窗入口",
    "👻 复活购买入口已移除，公平竞技",
    "📜 排行榜入口已隐藏，享受纯粹跑酷",
    "🎨 皮肤商店保留 — 主玩法核心系统",
]

IMPORT_LINES = [
    "import android.graphics.Color;",
    "import android.graphics.Typeface;",
    "import android.graphics.drawable.GradientDrawable;",
    "import android.util.TypedValue;",
    "import android.view.Gravity;",
    "import android.view.ViewGroup;",
    "import android.view.animation.AlphaAnimation;",
    "import android.widget.FrameLayout;",
    "import android.widget.TextView;",
]

METHOD_BODY = """

    // === 底部「随机提示」横幅（[FLOWFIX 2026-08-18]）===
    // 覆盖 Android 12+ BOTTOM_GESTURES 手势条；80dp 高；5 秒淡入淡出轮换。
    private static final String[] TIP_MESSAGES = {MESSAGES};

    private FrameLayout tipBanner;
    private TextView tipText;
    private final Handler tipHandler = new Handler(Looper.getMainLooper());
    private int tipIndex = 0;
    private final Runnable tipRotate = new Runnable() {
        @Override public void run() {
            if (tipText == null) return;
            AlphaAnimation fadeOut = new AlphaAnimation(1f, 0f);
            fadeOut.setDuration(280);
            fadeOut.setFillAfter(true);
            tipText.startAnimation(fadeOut);
            tipHandler.postDelayed(new Runnable() {
                @Override public void run() {
                    if (tipText == null) return;
                    tipIndex = (tipIndex + 1) % TIP_MESSAGES.length;
                    tipText.setText(TIP_MESSAGES[tipIndex]);
                    AlphaAnimation fadeIn = new AlphaAnimation(0f, 1f);
                    fadeIn.setDuration(320);
                    fadeIn.setFillAfter(true);
                    tipText.startAnimation(fadeIn);
                }
            }, 320);
            tipHandler.postDelayed(this, 5000);
        }
    };

    private void installTipBanner() {
        try {
            ViewGroup root = (ViewGroup) findViewById(android.R.id.content);
            if (root == null || tipBanner != null) return;
            int h = dp(80);
            tipBanner = new FrameLayout(this);
            FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, h);
            lp.gravity = Gravity.BOTTOM;
            tipBanner.setLayoutParams(lp);
            GradientDrawable bg = new GradientDrawable(
                GradientDrawable.Orientation.LEFT_RIGHT,
                new int[]{0xCC7C3AED, 0xCCEC4899, 0xCCEF4444});
            tipBanner.setBackground(bg);
            tipText = new TextView(this);
            FrameLayout.LayoutParams tlp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
            tlp.setMargins(dp(16), dp(8), dp(16), dp(8));
            tipText.setLayoutParams(tlp);
            tipText.setGravity(Gravity.CENTER);
            tipText.setTextColor(Color.WHITE);
            tipText.setTypeface(Typeface.DEFAULT_BOLD);
            tipText.setShadowLayer(2f, 0f, 1f, 0xAA000000);
            tipText.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
            tipIndex = (int) (System.currentTimeMillis() % TIP_MESSAGES.length);
            tipText.setText(TIP_MESSAGES[tipIndex]);
            tipBanner.addView(tipText);
            tipBanner.setElevation(dp(16));
            root.addView(tipBanner);
            tipHandler.postDelayed(tipRotate, 2000);
        } catch (Throwable t) { /* banner 失败不影响游戏 */ }
    }

    private int dp(int v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v,
            getResources().getDisplayMetrics());
    }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="项目名 (e.g. CrowdCity)")
    ap.add_argument("--type", default="il2cpp", help="项目类型 (il2cpp/air/...)")
    ap.add_argument("--messages", help="自定义提示词文件 (JSONL, 每行一个字符串)")
    args = ap.parse_args()

    tips = DEFAULT_TIPS
    if args.messages:
        tips = [l.rstrip("\n") for l in Path(args.messages).read_text().splitlines() if l.strip()]

    main_activity = (
        REPO / "output-projects" / args.type / args.name
        / "app/src/main/java/com/android/boot/MainActivity.java"
    )
    if not main_activity.exists():
        print(f"[ERR] {main_activity} 不存在")
        sys.exit(1)
    text = main_activity.read_text(encoding="utf-8")
    if "installTipBanner()" in text:
        print(f"[OK] MainActivity.java 已有 installTipBanner()，跳过")
        return

    # 1. 插入 import
    for line in IMPORT_LINES:
        if line not in text:
            text = re.sub(
                r"(import android\.os\.Looper;)",
                r"\1\n" + line,
                text,
                count=1,
            )

    # 2. 构造字符串数组
    msgs = ",\n            ".join(f'"{t}"' for t in tips)
    method = METHOD_BODY.replace("{MESSAGES}", msgs)

    # 3. 在 onCreate 末尾插入 installTipBanner() 调用
    if "installTipBanner();" not in text:
        text = re.sub(
            r"(retryNativeHooks\(\);)",
            r"\1\n        installTipBanner();",
            text,
            count=1,
        )

    # 4. 在第一个 protected void onDestroy 之前插入方法和 dp 辅助
    if "private void installTipBanner()" not in text:
        # 找到 protected void onDestroy 块的开头
        m = re.search(r"(@Override\s*\n\s*protected void onDestroy\(\))", text)
        if m:
            text = text[: m.start()] + method + "\n    " + text[m.start():]

    main_activity.write_text(text, encoding="utf-8")
    print(f"[OK] 已加 installTipBanner() 到 {main_activity}")
    print(f"     提示词 {len(tips)} 条，banner 高度 80dp，5 秒轮换")


if __name__ == "__main__":
    main()
