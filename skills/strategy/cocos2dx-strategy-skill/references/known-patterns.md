# Cocos2d-x 已知逆向模式

## SDK 登录绕过模式（通用）
```smali
# 将 login() 替换为直接回调 onSocialResult
.method public login()V
    .locals 2
    const-string v0, "TAG"
    const-string v1, "BYPASS login"
    invoke-static {v0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    const-string v1, "fake_sid"
    invoke-static {p0, v1}, L...;->access$(...)  ; set auth token
    iget-object v0, p0, ...;->mAdapter:...
    const/4 v1, 0x5
    const-string v2, "fake_sid"
    invoke-static {v0, v1, v2}, L.../SocialWrapper;->onSocialResult(...)V
    return-void
.end method
```

## LuaSocket 阻断模式
```
socket_connect 函数签名: push.w {r0,r1,r4,r5,r6,r7,r8,lr}
替换为: movs r0,#0; add sp,#8; pop.w {r4,r5,r6,r7,r8,pc}
```

## .mt 文件解密
- Magic: "Antm"
- 加密库: Bangcle AES (libilongyuan_encryption.so)
- Key: com.ilongyuan.encryption.EncryptionTool.KEY (640 hex chars)

## AGP 项目结构 — apktool 资源直接构建

apktool 解码后的标准目录 (apktool-source/) 是 smali-only 项目的天然 AS 工程源。
**AGP 8.x 不原生支持 smali 编译**，需要自定义 Gradle 任务接入 apktool b：

```groovy
// app/build.gradle — 关键片段
android {
    sourceSets {
        main {
            // apktool 生成的 smali_classesN/ 需作为 java 源目录
            java.srcDirs = ['smali', 'smali_classes2', 'smali_classes3',
                            'smali_classes4', 'smali_classes5']
        }
    }
    defaultConfig { ... abiFilters 'arm64-v8a' ... }
}

// 自定义任务: apktool b → zipalign → apksigner
task smali2dexApk(type: Exec) {
    workingDir = file('src/main')
    commandLine 'java', '-jar', apktoolJar, 'b', '.', '-o', outApk, '--force-all'
}
task signApk(type: Exec, dependsOn: smali2dexApk) {
    commandLine apksigner, 'sign', '--ks', keystore, '--v1/v2/v3', '--out', signedApk, alignedApk
}
afterEvaluate {
    tasks.named('assembleRelease').configure { dependsOn signApk }
}
```

**关键差异**：
- AGP 期望 `jniLibs/`，但 **apktool b 期望 `lib/`** → 编译时放在 `lib/`，不是 `jniLibs/`
- `apktool.yml` 必须存在于 `src/main/` (apktool b 启动时会读取)
- 不要复制 `apktool-source/build/` 和 `apktool-source/unknown/` — 前者是上次构建产物，后者是 apktool 元数据

**资源修复（必经）**：
apktool 解码常含 `$`-前缀 drawable（如 `$applovin_ic_unmute_to_mute__0.xml`），
AGP 拒绝 `$` 在资源名 → 删除 `$`-前缀文件 + 它们的 animated-vector 包装器 + public.xml 条目。
检查命令：`find app/src/main/res/drawable -name '$*'`

**运行时验证**：
```
adb shell pidof <pkg>           → 应返回 PID
adb shell dumpsys window | grep mCurrentFocus   → 应聚焦 MainActivity
logcat | grep "SurfaceView.*\(BLAST\)"           → 应输出 fps=N.N
logcat | grep "UnsatisfiedLink"  → 应为空 (libMyGame.so 加载成功)
logcat | grep "FATAL EXCEPTION"  → 应为空 (无崩溃)
```

| 常见错误 | 原因 | 修复 |
|---------|------|------|
| `R8 already present` | AGP 默认 R8 + 已编译 smali | `release { minifyEnabled false }` |
| `'$' is not a valid file-based resource name` | apktool 输出含 `$`-前缀 drawable | 删除 16 个 `$`-前缀 + 包装器 |
| `compileSdkVersion is not specified` | sourceSets 配置错误导致 android 块未求值 | 检查 sourceSets 语法 |
| `libMyGame.so not found` | `lib/` 被改名成 `jniLibs/` | apktool 路径下用 `lib/` |
| `apktool.yml not found` | 缺失 apktool 配置 | 从 raw/01-apktool/apktool.yml 复制 |
| `ClassNotFoundException: androidx.core.app.CoreComponentFactory` | 多 dex 编译未触发 | smali 路径必须作为 java.srcDirs 注册 |

来源：JurassicPixelCraft 2026-07-28（com.tappocket.dinovillage，libMyGame.so 23MB，PGL 加固）

## 关键坑：AGP `packageRelease` 会清空 `build/outputs/apk/release/`

**症状**：`./gradlew clean assembleRelease` 失败，但 `./gradlew assembleRelease` 成功。
**根因**：自定义 `Exec` 任务用 `outputs.file = file("$buildDir/outputs/apk/release/app-release-unsigned.apk")`
输出 APK 时，运行正常。但 AGP 的 `packageRelease` 任务后续会**清空** `outputs/apk/release/` 目录
然后写入它自己的 `app-release.apk`（不含 smali 的 98MB 空壳），把 smali APK 删掉。
后续 `signApk` 找不到输入文件 → `Unable to open '...10-smali-unsigned.apk' as zip archive`。

**修复**：把自定义任务的输出放到 `build/` 之外的目录（如 `build/smali-build/app-unsigned.apk`），
避免被 AGP 清空。`signApk` 再从那里读取 → zipalign → 覆盖 AGP 的 `app-release.apk`。

```groovy
task smali2dexApk(type: Exec) {
    def outApk = file("$buildDir/smali-build/app-unsigned.apk")  // 不放 outputs/apk/
    ...
}
task signApk(type: Exec, dependsOn: smali2dexApk) {
    def signedApk = file("$buildDir/outputs/apk/release/app-release.apk")
    inputs.files smali2dexApk.outputs.files
    outputs.file signedApk
    mustRunAfter 'packageRelease'  // 必须晚于 AGP packageRelease
    doFirst {
        def unsignedApk = smali2dexApk.outputs.files.singleFile
        exec { commandLine zipalign, '-p', '-f', '4', unsignedApk, alignedApk }
        commandLine apksigner, 'sign', '--ks', keystore, '--v1/v2/v3', '--out', signedApk, alignedApk
    }
}
```

来源：JurassicPixelCraft 2026-07-28（com.tappocket.dinovillage）
