# 05 操作链

脚本的"操作链"是 8 条从输入到局部产物的数据流。所有链都汇聚到 `main()` 的最终返回（`application.apk`）。

## 链 1 — CLI 入口与依赖检查

```mermaid
flowchart TD
    A([python xapktoapk.py app.xapk]) --> B[check_sys_args<br/>行 59]
    B -->|False| C[print_help 行 43] --> X1[exit -1]
    B -->|True| D{apktool 存在?}
    D -->|No| E[print error] --> X2[exit -2]
    D -->|Yes| F{zipalign 存在?}
    F -->|No| G[print error] --> X2
    F -->|Yes| H[load_sign_properties<br/>行 434]
    H --> I{sign.enabled?}
    I -->|No| L[sign_properties = None]
    I -->|Yes| J{apksigner 存在?}
    J -->|No| K[print error] --> X2
    J -->|Yes| L
    L --> M[continue main loop]
```

**关键函数**：`check_sys_args`(59) · `print_help`(43) · `load_sign_properties`(434) · `check_if_executable_exists_in_path`(100) · `get_path_to_batch`(107)

## 链 2 — XAPK 解包为目录

```mermaid
sequenceDiagram
    participant Main as main()
    participant FS as FileSystem
    participant Zip as ZipFile

    Main->>FS: os.getcwd() → cwd (行 547)
    Main->>Main: create_tmp_dir(cwd) (行 549 → 115)
    Main->>FS: shutil.copy(xapk, target.xapk) (行 551)
    Main->>FS: os.rename → target.zip (行 555)
    Main->>Zip: ZipFile(target.zip, 'r') (行 558)
    Main->>Zip: extractall(.xapktoapk/) (行 559)
    Main->>FS: os.remove(target.zip) (行 560)
    Main->>Main: load manifest.json (行 564-566)
```

**关键函数**：`create_tmp_dir`(115) · `create_or_recreate_dir`(89) · `file_split_name_and_extension`(121)

## 链 3 — APK 列表构建与 split 类型分类

```mermaid
flowchart LR
    A[os.listdir .xapktoapk/] --> B{是 .apk 文件?}
    B -->|Yes| C[append to target_apk_file_names]
    B -->|No| D[skip]
    C --> E[for each apk file]
    E --> F[determine_split_type_by_apk_file_name<br/>行 126]
    F --> G[properties dict]
    G --> H[target_apks 字典]
```

分类规则（行 126-145）：
- `xapk_package_name.apk` 或 `base.apk` → `main`
- `config.<X>.apk` 且 `<X>` 以 `dpi` 结尾 → `dpi`
- `config.<X>.apk` 且 `<X>` ∈ `[arm64_v8a, armeabi_v7a, armeabi, x86, x86_64]` → `arch`
- `config.<X>.apk` 其他 → `locale`
- 其余文件 → `locale`（兜底）

**关键函数**：`determine_split_type_by_apk_file_name`(126) · `get_apks_of_type`(148) · `get_main_apk`(157)

## 链 4 — 每个 APK 用 apktool 解包

```mermaid
flowchart TD
    A[main 循环每个 APK] --> B[unpack_apk 行 313]
    B --> C[os.chdir .xapktoapk/]
    C --> D{apktool 可执行?}
    D -->|Yes| E[execute_command_subprocess<br/>行 76]
    E -->|RC != 0| F[raise Exception] --> X1[exit]
    E -->|RC == 0| G[os.remove apkfile]
    D -->|No| H[Popen list2cmdline 行 322]
    H --> I[stderr 异常?]
    I -->|Yes| F
    I -->|No| G
```

**关键函数**：`unpack_apk`(313) · `execute_command_subprocess`(76) · `get_executable_in_path`(104) · `get_path_to_batch`(107)

## 链 5 — arch 分片合并到 main

```mermaid
flowchart LR
    A[main 遍历 apks_arch] --> B[merge_apk_arch<br/>行 221]
    B --> C[os.path.join main/lib]
    C --> D{lib 目录存在?}
    D -->|No| E[os.mkdir]
    D -->|Yes| F[shutil.copytree 每个 ABI]
    E --> F
    F --> G[parse arch apktool.yml]
    G --> H[insert_new_lines_do_not_compress<br/>行 199]
    H --> I[更新 main apktool.yml]
```

**关键函数**：`merge_apk_arch`(221) · `parse_apktool_config`(183) · `get_do_not_compress_lines`(161) · `insert_new_lines_do_not_compress`(199)

## 链 6 — dpi / locale 分片合并到 main

```mermaid
flowchart TD
    A[main 遍历 apks_dpi_prioritzed] --> B[merge_apk_resources<br/>行 239]
    A2[main 遍历 apks_locale] --> B
    B --> C[os.walk res_dir]
    C --> D[collect files_to_copy]
    D --> E{for each file}
    E -->|path 存在| F[skip drawable/* 等]
    E -->|path 不存在| G[os.makedirs + shutil.copy]
    A3[merge_apk_assets 行 274] --> H[合并 assets/assetpack/]
    H --> I[parse apktool.yml + insert doNotCompress]
```

DPI 优先级（行 500）：`xxxhdpi → xxhdpi → xhdpi → hdpi → mdpi → ldpi → nodpi → tvdpi`，剩余字典序倒排兜底（行 494）。

**关键函数**：`merge_apk_resources`(239) · `merge_apk_assets`(274) · `prioritize_dpi_apk_list`(499) · `prioritize_dpi_apk_list_rev_sort`(494)

## 链 7 — 清理与 Manifest 修改

```mermaid
flowchart TD
    A[main 收尾阶段] --> B[delete_signature_related_files<br/>行 402]
    B --> B1[删除 original/META-INF/BNDLTOOL.RSA]
    B --> B2[删除 original/META-INF/BNDLTOOL.SF]
    B --> B3[删除 original/META-INF/MANIFEST.MF]
    A --> C[update_main_manifest_file<br/>行 410]
    C --> C1[读取 AndroidManifest.xml]
    C --> C2[字符串替换 replacements 字典]
    C --> C3[写回 AndroidManifest.xml]
```

**关键函数**：`delete_signature_related_files`(402) · `delete_file_if_exists`(397) · `update_main_manifest_file`(410)

## 链 8 — 重打包 + zipalign + sign

```mermaid
sequenceDiagram
    participant Main as main()
    participant Builder as build_single_apk
    participant FS as FileSystem

    Main->>Builder: build_single_apk (行 470)
    Builder->>FS: pack_apk (行 330) → apktool b
    Builder->>FS: zipalign_apk (行 355) → zipalign -p -f 4
    alt should_sign_apk
        Builder->>FS: sign_apk (行 378) → apksigner sign
    else
        Builder->>Builder: print "skip signing"
    end
    Main->>FS: copy_single_apk_to_working_dir (行 479)
    Main->>FS: shutil.rmtree .xapktoapk (行 617)
```

**关键函数**：`build_single_apk`(470) · `pack_apk`(330) · `zipalign_apk`(355) · `sign_apk`(378) · `copy_single_apk_to_working_dir`(479)