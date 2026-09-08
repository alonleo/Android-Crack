# 09 关键调用栈

## 栈 1 — 启动到参数校验

```
用户执行
└── main()  (行 519)
    ├── check_sys_args()  (行 520 → 59)
    │   └── get_param_xapk_file_name()  (行 62 → 51)
    │       └── sys.argv[1]
    └── [失败] print_help()  (行 521 → 43)
```

## 栈 2 — 依赖工具检查

```
main()  (行 524-540)
├── check_if_executable_exists_in_path("apktool")  (行 525 → 100)
│   └── shutil.which("apktool")
├── [若 None] get_path_to_batch("apktool")  (行 525 → 107)
│   └── os.environ['PATH'] 扫描 apktool.bat
├── check_if_executable_exists_in_path("zipalign")  (行 530)
├── [签名启用] load_sign_properties()  (行 534 → 434)
│   └── 读 xapktoapk.sign.properties
└── [签名启用] check_if_executable_exists_in_path("apksigner")  (行 538)
```

## 栈 3 — XAPK 解包为目录

```
main()  (行 547-560)
├── os.getcwd() → cwd  (行 547)
├── create_tmp_dir(cwd)  (行 549 → 115)
│   └── create_or_recreate_dir()  (行 117 → 89)
│       ├── os.path.exists / isdir
│       ├── shutil.rmtree / os.remove
│       ├── os.mkdir
│       └── [Windows] is_windows() (96 → 81)
│           └── windows_hide_file() (97 → 85)
│               └── execute_command_subprocess(["attrib", "+h", ...])
├── shutil.copy(xapk, target.xapk)  (行 551)
├── os.rename(target.xapk → target.zip)  (行 555)
├── ZipFile(target.zip).extractall(.xapktoapk/)  (行 558-559)
└── json.load(open(manifest.json))  (行 564-566)
```

## 栈 4 — APK 列表与分类

```
main()  (行 568-588)
├── os.listdir(.xapktoapk/) → 文件名列表  (行 569)
├── [遍历每个文件名]
│   ├── endswith(".apk") 过滤  (行 570)
│   └── append 到 target_apk_file_names  (行 573)
├── [遍历每个 apk_file_name]
│   └── determine_split_type_by_apk_file_name(apk_name, pkg_name)  (行 577 → 126)
│       ├── 检查 main 匹配
│       ├── os.path.splitext → config.X 解析
│       ├── endswith("dpi") / in arch 白名单
│       └── 返回 main/arch/dpi/locale
└── 构造 target_apks dict（每个 apk 一个 properties dict）  (行 580-586)
```

## 栈 5 — 每个 APK 解包（循环）

```
main()  (行 591-594)
└── for apk_file_key in target_apks:
    └── unpack_apk(path_dir_tmp, apk_file, i+1, total)  (行 594 → 313)
        ├── print progress
        ├── os.chdir(.xapktoapk/)
        ├── apktool = get_executable_in_path("apktool")  (316 → 104)
        ├── [POSIX] execute_command_subprocess([apktool, "d", "-s", apk])  (318 → 76)
        │   └── subprocess.call(..., stdout=DEVNULL, stderr=STDOUT)
        ├── [Windows] Popen(list2cmdline(params))  (323)
        │   └── p.communicate()  (324)
        └── os.remove(apk_file)  (327)
```

## 栈 6 — 合并到 main

```
main()  (行 596-608)
├── apk_main = get_main_apk(target_apks)  (596 → 157)
│   └── get_apks_of_type(target_apks, "main")[0]  (158 → 148)
├── apks_arch = get_apks_of_type(target_apks, "arch")  (597)
├── apks_dpi = get_apks_of_type(target_apks, "dpi")  (598)
├── apks_locale = get_apks_of_type(target_apks, "locale")  (599)
│
├── [遍历 apks_arch]
│   └── merge_apk_arch(main_dir, arch_dir)  (602 → 221)
│       ├── 建 main/lib/
│       ├── shutil.copytree 每个 ABI
│       └── parse_apktool_config + insert_new_lines_do_not_compress
│           ├── parse_apktool_config (235 → 183)
│           │   ├── open(r).readlines()
│           │   └── get_do_not_compress_lines (188 → 161)
│           └── insert_new_lines_do_not_compress (236 → 199)
│               ├── parse_apktool_config (200)
│               ├── set union + sort
│               └── open(w).writelines
│
├── apks_dpi_prioritzed = prioritize_dpi_apk_list(apks_dpi)  (603 → 499)
│   └── [fallback] prioritize_dpi_apk_list_rev_sort (512 → 494)
│       └── sorted(..., reverse=True)
│
├── [遍历 apks_dpi_prioritzed]
│   └── merge_apk_resources(main_dir, dpi_dir)  (605 → 239)
│       ├── os.walk res_dir
│       ├── 跳过 values/public.xml
│       └── 冲突跳过，缺失则 makedirs + shutil.copy
│
└── [遍历 apks_locale]
    ├── merge_apk_resources(main_dir, locale_dir)  (607)
    └── merge_apk_assets(main_dir, locale_dir)  (608 → 274)
        ├── 检查 assets/assetpack 存在
        ├── os.walk asset_pack_dir
        └── parse_apktool_config + insert_new_lines_do_not_compress
```

## 栈 7 — Manifest 修改与清理

```
main()  (行 610-611)
├── delete_signature_related_files(main_dir)  (610 → 402)
│   ├── delete_file_if_exists("original/META-INF/BNDLTOOL.RSA")  (405 → 397)
│   ├── delete_file_if_exists("original/META-INF/BNDLTOOL.SF")  (406)
│   └── delete_file_if_exists("original/META-INF/MANIFEST.MF")  (407)
│       └── os.path.exists + os.remove
│
└── update_main_manifest_file(main_dir)  (611 → 410)
    ├── open("AndroidManifest.xml", r).read()
    ├── for from, to in replacements.items(): str.replace
    └── open("AndroidManifest.xml", w).write(data)
```

## 栈 8 — 重打包 + zipalign + sign

```
main()  (行 613)
└── build_single_apk(tmp_dir, main_dir, should_sign, sign_cfg)  (613 → 470)
    ├── pack_apk(tmp_dir, main_dir)  (471 → 330)
    │   ├── os.chdir(tmp_dir)
    │   ├── execute_command_subprocess(["apktool", "b", main_dir])  (335)
    │   └── shutil.copy(<main>/dist/<name>.apk → <tmp>/target.apk)  (352)
    │
    ├── zipalign_apk(tmp_dir)  (472 → 355)
    │   ├── os.chdir(tmp_dir)
    │   ├── execute_command_subprocess(["zipalign", "-p", "-f", "4", ...])  (368)
    │   └── shutil.move(aligned → target)  (375)
    │
    └── [若 should_sign] sign_apk(tmp_dir, sign_cfg)  (474 → 378)
        ├── os.chdir(tmp_dir)
        ├── check_if_executable_exists_in_path("apksigner")  (385)
        ├── execute_command_subprocess(["apksigner", "sign", "--ks", ..., "target.apk"])  (386)
        └── [Windows] Popen(list2cmdline(...))  (391)
```

## 栈 9 — 收尾

```
main()  (行 614-619)
├── copy_single_apk_to_working_dir(tmp_dir, cwd, original_name)  (614 → 479)
│   ├── shutil.copy(<tmp>/target.apk → <cwd>/<name>.apk)  (491)
│   └── [若存在] os.remove / shutil.rmtree 旧产物  (487-489)
├── os.chdir(cwd)  (616)
├── shutil.rmtree(.xapktoapk/)  (617)
└── print("[*] complete")  (619)
```