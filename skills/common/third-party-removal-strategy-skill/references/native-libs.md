# 第三方 Native 库特征库

> 仅记录可跨项目识别的 native 第三方库特征及其 Java/JNI 依赖风险；不得记录来源 APK、项目名、日期或地址偏移。

旧目录的库条目与相互矛盾的删除结论已合并为 [Native 库识别与保留边界](native-catalog.md)。下方保留各 type 提炼的共用摘要。

## 条目格式

```md
### <库名称或模式>

- **类别**：
- **识别特征**：库名、导出符号、字符串或依赖模式
- **Java/JNI 依赖风险**：
- **默认判断**：保留 / 停用 / 桩化 / 物理删除前需分析
- **验证重点**：
- **相关文档**：
```

## 条目

<!-- 在此追加 native 库特征。 -->

### PGL 与核心资源解码

- **类别**：加固/资源解码与 SDK 共用依赖。

- **识别特征**：libpglarmor.so、libppl-*.so、libbuffer_pgl.so、libfile_lock_pgl.so；PglCryptUtils JNI。
- **默认判断**：依赖未查清前保留；这些名称不是通用删除清单。
- **依赖风险**：可能参与核心 hash assets 解码；高熵/hash 命名不代表广告资源。
- **验证重点**：沿 Gdx.files/Pixmap 等实际加载路径确认，冷启动和场景资源加载均通过。
- **相关文档**：[libGDX](engine-notes.md#libgdx)。

### 引擎与 JNI glue

- **类别**：核心运行库及桥接，作为 SDK 删除的保留边界。

- **识别特征**：libil2cpp.so/libunity.so、libcocos2d*.so/libMyGame.so、libyoyo.so、libgdx.so、libflutter.so/libapp.so、Mono/Xamarin 运行库，以及重命名的 Defold 引擎库。
- **默认判断**：作为核心运行依赖保留，白名单按实际包补全。
- **依赖风险**：SDK 与引擎可共用 Java glue、命令队列和资源库；不能按 JNI 前缀全量拦截。
- **验证重点**：ABI、动态加载、C++ runtime、主循环/输入/资源及异步回调。
- **相关文档**：[各 type 边界](engine-notes.md)。
