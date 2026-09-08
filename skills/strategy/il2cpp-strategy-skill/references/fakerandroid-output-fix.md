# FakerAndroid fake 输出修复模式

> 来源: RealmDefenseHeroLegendsTD | 2026-07-26

## 已知问题

`java -jar ASBuilder.jar fake` 在某些 APK 上会损坏输出：

1. **AndroidManifest.xml 严重损坏** — 多个 `android:name=""` 为空（`sensitiveOptions.collapsePackage` 误开）
2. **jniLibs/ 缺失** — 仅生成 smali + cpp + java 骨架
3. **assets/ 缺失** — 不复制原始资源
4. **smali 桥接缺失** — `com/unity3d/player/` 类不全
5. **结构错位** — `app-as-generated/app/...` 而非 `app/...`

## 修复流程

### 1. 修复 AndroidManifest.xml

```bash
# 用原始 apktool 备份覆盖
cp crackings/<type>/<Name>/raw/01-apktool/AndroidManifest.xml \
   crackings/<type>/<Name>/project/app/src/main/AndroidManifest.xml

# 修改 application 标签
#   android:name="com.android.boot.App" (FakerAndroid 模板 Application)
#   启动 activity android:name 改为 "com.android.boot.MainActivity"
```

### 2. 补 jniLibs/

```bash
# 优先用原始 APK（apktool 抽出的 .so 经常是 0 字节）
cd crackings/<type>/<Name>/project/app/src/main/jniLibs/armeabi-v7a/
unzip -o apks/<Name>.apk 'lib/armeabi-v7a/*' -d /tmp/libextract
cp /tmp/libextract/lib/armeabi-v7a/* .
```

### 3. 补 assets/

```bash
# 注意：避免 assets/assets/... 嵌套
cd crackings/<type>/<Name>/project/app/src/main/
rm -rf assets && mkdir assets && cd assets
unzip -o apks/<Name>.apk 'assets/*'
# 验证：find . -maxdepth 1 -type d 应该只有 . 和 aa/ bin/ 等
# 错误: 看到 assets/ 子目录 → 删除外层后重做
```

### 4. 补 Unity smali 桥接

```bash
# 必须从 apktool smali 备份复制 player/ + plugin/ 子目录
# 硬性要求：smali 文件数 >= 10
for d in smali smali_classes2 smali_classes3 smali_classes4; do
  if [ -d "raw/01-apktool-smali-backup/$d" ]; then
    cp -r raw/01-apktool-smali-backup/$d crackings/<type>/<Name>/project/app/src/main/
  fi
done

# 验证
find crackings/<type>/<Name>/project/app/src/main -name "*.smali" -path "*unity3d/player*" | wc -l
# 应 >= 10
```

### 5. 修正项目结构（app-as-generated/ → app/）

```bash
# FakerAndroid 输出嵌套在 app-as-generated/app/...
# 需要把根文件提到上一级
mv crackings/<type>/<Name>/project/app-as-generated/build.gradle crackings/<type>/<Name>/project/
mv crackings/<type>/<Name>/project/app-as-generated/settings.gradle crackings/<type>/<Name>/project/
mv crackings/<type>/<Name>/project/app-as-generated/gradlew crackings/<type>/<Name>/project/
mv crackings/<type>/<Name>/project/app-as-generated/gradle crackings/<type>/<Name>/project/
mv crackings/<type>/<Name>/project/app-as-generated/app/* crackings/<type>/<Name>/project/app/
rmdir crackings/<type>/<Name>/project/app-as-generated/app
mv crackings/<type>/<Name>/project/app-as-generated crackings/<type>/<Name>/project/app
```

### 6. 修改 app/build.gradle

```gradle
android {
    namespace '<原包名>'                  // AGP 8.x 必填
    signingConfigs {
        debug { storeFile file("../my.keystore.jks"); ... }
        release { storeFile file("../my.keystore.jks"); ... }
    }
    compileSdk 33                         // 不是 compileSdkVersion
    defaultConfig {
        abiFilters 'armeabi-v7a'          // 与原 APK 一致
    }
    lint { abortOnError false; ... }      // 不是 lintOptions
}
```

## 完整流程（建议固化为脚本）

```bash
# stage-02b-fix.py — 修复 FakerAndroid 输出
# 1. 重命名 app-as-generated → app
# 2. 补 jniLibs/ from original APK
# 3. 补 assets/ from original APK
# 4. 补 smali/ from apktool backup
# 5. 覆盖 AndroidManifest.xml
# 6. 重写 build.gradle (AGP 8.x)
# 7. 链接 my.keystore.jks 符号链接
```
