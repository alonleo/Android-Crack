# 07 函数索引

所有 36 个函数按行号排序。完整说明见 [`08_functions_detail.md`](08_functions_detail.md)。

| # | 函数名 | 行号 | 分组 | 一句话职责 |
|---|--------|------|------|------------|
| 1 | `print_help` | 43 | CLI 入口 | 打印使用说明到 stdout |
| 2 | `get_param_xapk_file_name` | 51 | CLI 入口 | 返回 `sys.argv[1]` |
| 3 | `get_param_xapk_abs_path` | 55 | CLI 入口 | 返回参数绝对路径 |
| 4 | `check_sys_args` | 59 | CLI 入口 | 校验参数个数 + 扩展名 + 文件存在 |
| 5 | `execute_command_os_system` | 71 | 系统/进程 | `os.system` 包装（实际未调用） |
| 6 | `execute_command_subprocess` | 76 | 系统/进程 | `subprocess.call` 包装，返回 RC |
| 7 | `is_windows` | 81 | 系统/进程 | `platform.system() == "Windows"` |
| 8 | `windows_hide_file` | 85 | 系统/进程 | `attrib +h <path>` |
| 9 | `create_or_recreate_dir` | 89 | 系统/进程 | 删旧建新目录 |
| 10 | `check_if_executable_exists_in_path` | 100 | 系统/进程 | `shutil.which` 非 None 判断 |
| 11 | `get_executable_in_path` | 104 | 系统/进程 | 返回 `shutil.which` 结果 |
| 12 | `get_path_to_batch` | 107 | 系统/进程 | Windows 下找 `<batch>.bat` |
| 13 | `create_tmp_dir` | 115 | 临时目录 | 在 `cwd` 下建 `.xapktoapk/` |
| 14 | `file_split_name_and_extension` | 121 | 临时目录 | `os.path.splitext` 包装 |
| 15 | `determine_split_type_by_apk_file_name` | 126 | APK 分类 | 根据文件名判定 `main/arch/dpi/locale` |
| 16 | `get_apks_of_type` | 148 | APK 分类 | 按 split 类型过滤 |
| 17 | `get_main_apk` | 157 | APK 分类 | 取 main 分片 |
| 18 | `get_do_not_compress_lines` | 161 | apktool.yml | 解析 `doNotCompress:` YAML 块 |
| 19 | `parse_apktool_config` | 183 | apktool.yml | 读整个 yml，返回结构化 dict |
| 20 | `insert_new_lines_do_not_compress` | 199 | apktool.yml | 把新行合并回 yml |
| 21 | `merge_apk_arch` | 221 | 分片合并 | 合并 `lib/` + doNotCompress |
| 22 | `merge_apk_resources` | 239 | 分片合并 | 合并 `res/`，跳过冲突 |
| 23 | `merge_apk_assets` | 274 | 分片合并 | 合并 `assets/assetpack/` |
| 24 | `unpack_apk` | 313 | apktool 集成 | `apktool d -s` |
| 25 | `pack_apk` | 330 | apktool 集成 | `apktool b` |
| 26 | `zipalign_apk` | 355 | 后处理 | `zipalign -p -f 4` |
| 27 | `sign_apk` | 378 | 后处理 | `apksigner sign` |
| 28 | `delete_file_if_exists` | 397 | Manifest 清理 | 安全的 `os.remove` |
| 29 | `delete_signature_related_files` | 402 | Manifest 清理 | 删 META-INF 签名残留 |
| 30 | `update_main_manifest_file` | 410 | Manifest 清理 | 字符串替换去 split 标记 |
| 31 | `load_sign_properties` | 434 | 签名配置 | 读 `xapktoapk.sign.properties` |
| 32 | `build_single_apk` | 470 | 高层编排 | pack → zipalign → sign 三步组合 |
| 33 | `copy_single_apk_to_working_dir` | 479 | 高层编排 | 拷 target.apk 到工作目录 |
| 34 | `prioritize_dpi_apk_list_rev_sort` | 494 | 高层编排 | DPI 字典序倒排（fallback） |
| 35 | `prioritize_dpi_apk_list` | 499 | 高层编排 | DPI 优先级排序（xxxhdpi→ldpi） |
| 36 | `main` | 519 | CLI 入口 | 顶层编排 |

## 按调用频度统计（被 `main` 直接调用）

`main` 直接调用的函数（行 519-619）：

```python
check_sys_args, print_help, check_if_executable_exists_in_path, get_path_to_batch,
load_sign_properties, get_param_xapk_file_name, get_param_xapk_abs_path,
file_split_name_and_extension, create_tmp_dir, determine_split_type_by_apk_file_name,
unpack_apk, get_main_apk, get_apks_of_type, merge_apk_arch, prioritize_dpi_apk_list,
merge_apk_resources, merge_apk_assets, delete_signature_related_files,
update_main_manifest_file, build_single_apk, copy_single_apk_to_working_dir
```

共 **22** 个函数被 `main` 直接调用；其余 14 个为间接调用方 / helper。

## 模块统计

| 分组 | 函数数 | 占比 |
|------|--------|------|
| A. CLI 入口 | 5 | 14% |
| B. 系统/进程 | 8 | 22% |
| C. 临时目录 | 2 | 6% |
| D. APK 分类 | 3 | 8% |
| E. apktool.yml | 3 | 8% |
| F. 分片合并 | 3 | 8% |
| G. apktool 集成 | 2 | 6% |
| H. 后处理 | 2 | 6% |
| I. Manifest 清理 | 3 | 8% |
| J. 签名配置 | 1 | 3% |
| K. 高层编排 | 4 | 11% |
| **总计** | **36** | **100%** |