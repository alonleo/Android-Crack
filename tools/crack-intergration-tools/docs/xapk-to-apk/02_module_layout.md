# 02 模块布局

`xapktoapk.py` 是单文件脚本，按"职责分组"组织。无类、无模块分割，所有内容在 module-level。

## 顶层结构

| 行号范围 | 区块 | 说明 |
|----------|------|------|
| 1-2 | shebang + encoding | `#!/usr/bin/python3` + UTF-8 |
| 4-16 | imports | 标准库 only；`DEVNULL` 兼容老版本 |
| 19-40 | 常量 | 全部以 `const_` 前缀，10 个分组 |
| 43-47 | `print_help` | 帮助文本 |
| 51-618 | 函数定义 | 36 个函数（按"前置 helper → 主流程"顺序排列） |
| 622-623 | entry | `if __name__ == '__main__': main()` |

## 常量分组（19-40 行）

| 分组 | 行 | 常量 |
|------|----|----|
| 目录与文件扩展名 | 19-23 | `const_dir_tmp`、`const_file_target_file`、`const_ext_apk`、`.xapk`、`.zip` |
| XAPK manifest | 25-26 | `const_file_xapk_manifest = "manifest.json"`、`const_file_xapk_manifest_key_package_name` |
| APK split 配置 | 28-30 | `const_prefix_apk_split_type_config`、`const_suffix_apk_split_type_dpi`、架构白名单 |
| APK split 类型 | 32-35 | `main` / `arch` / `dpi` / `locale` |
| Apktool 输出约定 | 37-38 | `apktool.yml` 文件名、`lib` 目录名 |
| 签名配置 | 40 | `xapktoapk.sign.properties` |

## 函数分组（36 个函数，按职责分类）

### A. CLI 入口与参数解析（5 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `print_help` | 43 | 打印使用说明 |
| `get_param_xapk_file_name` | 51 | 取命令行第一个参数 |
| `get_param_xapk_abs_path` | 55 | 转绝对路径 |
| `check_sys_args` | 59 | 校验参数个数、扩展名、文件存在 |
| `main` | 519 | 入口编排 |

### B. 系统与进程工具（8 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `execute_command_os_system` | 71 | `os.system` 包装（代码中实际未使用） |
| `execute_command_subprocess` | 76 | `subprocess.call` 包装，返回 RC |
| `is_windows` | 81 | 平台判断 |
| `windows_hide_file` | 85 | Windows `attrib +h` |
| `create_or_recreate_dir` | 89 | 删旧建新目录 |
| `check_if_executable_exists_in_path` | 100 | 用 `shutil.which` 检测 |
| `get_executable_in_path` | 104 | 返回可执行文件绝对路径 |
| `get_path_to_batch` | 107 | Windows 下找 `.bat` 包装 |

### C. 临时目录与文件操作（2 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `create_tmp_dir` | 115 | 在 cwd 下建 `.xapktoapk` 临时目录 |
| `file_split_name_and_extension` | 121 | 用 `os.path.splitext` 拆文件名 |

### D. APK 分片分类与查询（3 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `determine_split_type_by_apk_file_name` | 126 | 根据文件名判定 `main` / `arch` / `dpi` / `locale` |
| `get_apks_of_type` | 148 | 按类型过滤 APK 列表 |
| `get_main_apk` | 157 | 取 main 分片 |

### E. apktool.yml 处理（3 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `get_do_not_compress_lines` | 161 | 解析 yaml 块 |
| `parse_apktool_config` | 183 | 读取整个 yml，返回结构化 dict |
| `insert_new_lines_do_not_compress` | 199 | 把新行合并回 yml |

### F. 分片合并（3 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `merge_apk_arch` | 221 | 合并 `lib/` + apktool.yml 的 doNotCompress |
| `merge_apk_resources` | 239 | 合并 `res/`，跳过 `values/public.xml` 与冲突 |
| `merge_apk_assets` | 274 | 合并 `assets/assetpack/` |

### G. apktool 集成（2 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `unpack_apk` | 313 | `apktool d -s` |
| `pack_apk` | 330 | `apktool b` |

### H. 后处理（zipalign + sign）（2 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `zipalign_apk` | 355 | `zipalign -p -f 4` |
| `sign_apk` | 378 | `apksigner sign` |

### I. Manifest 与签名清理（3 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `delete_file_if_exists` | 397 | 安全的 `os.remove` |
| `delete_signature_related_files` | 402 | 删 META-INF 签名残留 |
| `update_main_manifest_file` | 410 | 字符串替换去 split 标记 |

### J. 签名配置加载（1 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `load_sign_properties` | 434 | 读 `xapktoapk.sign.properties` |

### K. 高层编排（4 个）
| 函数 | 行号 | 职责 |
|------|------|------|
| `build_single_apk` | 470 | pack → zipalign → sign 三步组合 |
| `copy_single_apk_to_working_dir` | 479 | 把临时目录的 target.apk 拷到工作目录 |
| `prioritize_dpi_apk_list_rev_sort` | 494 | 字典序倒排（fallback） |
| `prioritize_dpi_apk_list` | 499 | DPI 优先级排序（xxxhdpi → ldpi） |