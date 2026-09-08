/**
 * native-lib.iap.template.cpp — il2cpp IAP 内购模拟模板（转发 MainActivity 控制）
 * 项目来源: AltosAdventure (2026-08-04)
 *
 * ⚠️ 使用前必读:
 *  1. 本模板 RVA 基于 AltosAdventure 的 InAppPurchaseManager (dump.cs TypeDefIndex 2344)，
 *     **其他项目需重新定位**（用 verify-il2cpp-rva.py 验证 RVA 是函数入口）
 *  2. 架构遵循 OBJECTIVES.md §1.6 模板：IAP 转发到 MainActivity.java 控制，
 *     **不要 native 硬编码 Is* 返回 true**（无法分别控制/持久化）
 *  3. 需配套:
 *     - SDKUtils.java 含 purchasedSkus 集合 + recordPurchase() + isPurchased()
 *     - MainActivity.java 含 case "processPurchase"（解析 payload → SDKUtils）
 *     - base 用 find_module_base(/proc/self/maps)，勿用 dlopen
 *
 * 架构:
 *   il2cpp PurchaseProduct(id)
 *     → hook → callJava("processPurchase:<id>") [JNI]
 *       → MainActivity.onJniCall → SDKUtils.processPurchase → recordPurchase(id)
 *         → onIapSuccess(id) [JNI 回 native]
 *   Is* 判断 → JNI 查 SDKUtils.isPurchased(id) → Java 层控制结果
 *
 * 以下函数需合并到项目 native-lib.cpp；RVA 按项目 dump.cs 调整。
 */

// ── il2cpp 字符串读取辅助 ────────────────────────────────────────
// Il2CppString: klass(0) + monitor(8) + length(0x10) + chars(0x14, UTF-16LE)
static std::string il2cppStr(const void* s) {
    if (!s) return "";
    const char* p = static_cast<const char*>(s);
    int32_t len = *reinterpret_cast<const int32_t*>(p + 0x10);
    if (len <= 0 || len > 512) return "";
    const uint16_t* u = reinterpret_cast<const uint16_t*>(p + 0x14);
    std::string out;
    for (int32_t i = 0; i < len; i++) {
        uint32_t cp = u[i];
        if (cp < 0x80) out += static_cast<char>(cp);
        else if (cp < 0x800) {
            out += static_cast<char>(0xC0 | (cp >> 6));
            out += static_cast<char>(0x80 | (cp & 0x3F));
        } else if (cp < 0x10000) {
            out += static_cast<char>(0xE0 | (cp >> 12));
            out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
            out += static_cast<char>(0x80 | (cp & 0x3F));
        }
    }
    return out;
}

// ── JNI: 查询 Java 层 SDKUtils.isPurchased(productId) ────────────
// 由 MainActivity/SDKUtils 控制内购结果（而非 native 硬编码）
static bool javaIsPurchased(const std::string& productId) {
    if (g_jvm == nullptr) return false;
    JNIEnv* env = nullptr;
    if (g_jvm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_1_6) != JNI_OK || !env) return false;
    jclass cls = env->FindClass("com/android/common/SDKUtils");
    if (!cls) return false;
    jmethodID mid = env->GetStaticMethodID(cls, "isPurchased", "(Ljava/lang/String;)Z");
    if (!mid) return false;
    jstring js = env->NewStringUTF(productId.c_str());
    jboolean res = env->CallStaticBooleanMethod(cls, mid, js);
    env->DeleteLocalRef(js);
    env->DeleteLocalRef(cls);
    return res == JNI_TRUE;
}

// ── IAP 购买入口: PurchaseProduct(string) → 转发 MainActivity ────
// InAppPurchaseManager.PurchaseProduct(string) RVA 0x1233E00
// 拦截后: callJava("processPurchase:<id>") → MainActivity → SDKUtils 模拟
// 不调用原函数（不走真实 Google Play Billing）
static void Hooked_PurchaseProduct(uintptr_t x1) {
    std::string sku = il2cppStr(reinterpret_cast<void*>(x1));
    LOGI("[hook] PurchaseProduct('%s') → forwarding to MainActivity", sku.c_str());
    std::string evt = "processPurchase:" + sku;
    callJava(evt.c_str());
}

// ── IAP 判断转发: Is* → JNI 查 Java 层 SDKUtils.isPurchased ──────
// InAppPurchaseManager 的 Is* 方法（RVA 见下方 setupHooks 注释）
// 无参方法: 直接查固定商品 ID
static bool Hooked_IsRemoveAdsPurchased() {
    bool r = javaIsPurchased("removeads");
    LOGI("[hook] IsRemoveAdsPurchased → %d (Java 层)", r);
    return r;
}

static bool Hooked_IsCoinDoublerPurchased() {
    bool r = javaIsPurchased("coindoubler");
    LOGI("[hook] IsCoinDoublerPurchased → %d", r);
    return r;
}

static bool Hooked_IsPremiumUser() {
    bool r = javaIsPurchased("premium") || javaIsPurchased("playpass");
    LOGI("[hook] IsPremiumUser → %d", r);
    return r;
}

static bool Hooked_IsUnlockAllCharactersPurchased() {
    bool r = javaIsPurchased("allcharacters");
    LOGI("[hook] IsUnlockAllCharactersPurchased → %d", r);
    return r;
}

// 带 string 参数方法: x1 = Il2CppString*
static bool Hooked_IsOwned(uintptr_t x1) {
    std::string sku = il2cppStr(reinterpret_cast<void*>(x1));
    bool r = javaIsPurchased(sku);
    LOGI("[hook] IsOwned('%s') → %d", sku.c_str(), r);
    return r;
}

static bool Hooked_IsCharacterPurchasedOrUnlocked(uintptr_t x1) {
    std::string sku = il2cppStr(reinterpret_cast<void*>(x1));
    bool r = javaIsPurchased(sku);
    LOGI("[hook] IsCharacterPurchasedOrUnlocked('%s') → %d", sku.c_str(), r);
    return r;
}

// ── setupHooks 中安装（RVA 基于 AltosAdventure，其他项目重定位） ──
// InAppPurchaseManager (dump.cs TypeDefIndex 2344):
//   PurchaseProduct                 0x1233E00  void(string)
//   IsCharacterPurchased            0x122863C  bool(Character.Type)
//   IsCharacterPurchasedOrUnlocked  0x12318AC  bool(string)
//   IsUnlockAllCharactersPurchased  0x123184C  bool()
//   IsRemoveAdsPurchased            0x1231B80  bool()
//   IsCoinDoublerPurchased          0x1231BC8  bool()
//   IsPremiumUser                   0x1231C10  bool()
//   IsOwned                         0x1231604  bool(string)
/*
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x1233E00),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_PurchaseProduct)),
        nullptr);
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x1231B80),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_IsRemoveAdsPurchased)),
        nullptr);
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x1231BC8),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_IsCoinDoublerPurchased)),
        nullptr);
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x1231C10),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_IsPremiumUser)),
        nullptr);
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x123184C),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_IsUnlockAllCharactersPurchased)),
        nullptr);
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x1231604),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_IsOwned)),
        nullptr);
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x12318AC),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_IsCharacterPurchasedOrUnlocked)),
        nullptr);
    LOGI("[hook] IAP Is* hooks → Java 层 SDKUtils");
*/
