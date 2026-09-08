/**
 * native-lib.network-stub.template.cpp — il2cpp 网络检测桩化模板
 * 项目来源: FormulaCarStuntCarGames (2026-08-06)
 *
 * ⚠️ 使用前必读:
 *  1. 本模板 RVA 基于 FormulaCarStuntCarGames 的 AdsManager 类，
 *     **其他项目需重新定位**（用 verify-il2cpp-rva.py 验证 RVA 是函数入口）
 *  2. ⚠️ **只 hook void 方法**：IEnumerator 方法（返回对象）hook 成 void 空函数
 *     会因返回寄存器 x0 未定义导致 UnityMain 线程 SIGSEGV（fault addr 0x1）。
 *     若网络检测在 IEnumerator 协程内，hook 其**内部调用的 void 方法**（如 PingToCheck）。
 *  3. base 用 /proc/self/maps 解析 mmap 基址（见 stage-04 native-lib.cpp 模板）
 *
 * 架构:
 *   AdsManager.CheckInternet/VerifyingInternet/PingToCheck 网络检测
 *     → hook CheckInternetAgain + PingToCheck → no-op
 *       → 游戏不再等待网络，直接进入主界面（飞行模式可玩）
 */

// ── 网络桩化（[FLOWFIX] FormulaCarStuntCarGames]） ─────────
// AdsManager 启动时跑网络检测，无网会弹 "No internet connection" / 等待卡流程。
// arm64 约定：hook 函数不调用原函数 → 直接返回（A64Hook 后即返回）。
static void Hooked_AdsManager_CheckInternetAgain() {
    LOGI("[hook] AdsManager.CheckInternetAgain → no-op (network stub)");
}

static void Hooked_AdsManager_PingToCheck() {
    LOGI("[hook] AdsManager.PingToCheck → no-op (network stub)");
}

// 在 setupHooks 中安装（RVA 基于 FormulaCarStuntCarGames AdsManager，其他项目重定位）：
/*
    //   CheckInternetAgain 0x1403FC0  public void CheckInternetAgain()
    //   PingToCheck        0x1403FE8  private void PingToCheck()
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x1403FC0),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_AdsManager_CheckInternetAgain)),
        nullptr);
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x1403FE8),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_AdsManager_PingToCheck)),
        nullptr);
    LOGI("[hook] network stubs installed");
*/
