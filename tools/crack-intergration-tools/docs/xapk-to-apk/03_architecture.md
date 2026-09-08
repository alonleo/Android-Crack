# 03 架构

## 整体架构

脚本是顺序流水线，没有并发、没有异步，所有逻辑在 `main()` 函数中以串行步骤串起来。架构上分为三层：

```mermaid
flowchart TD
    subgraph Layer1["Layer 1 · CLI 入口"]
        A[main]
        A1[print_help]
        A2[check_sys_args]
        A3[load_sign_properties]
        A --> A2
        A --> A3
        A --> A1
    end

    subgraph Layer2["Layer 2 · XAPK 解包"]
        B1[create_tmp_dir]
        B2[ZipFile.extractall]
        B3[parse manifest.json]
        B4[determine_split_type_by_apk_file_name]
        A --> B1
        B1 --> B2
        B2 --> B3
        B3 --> B4
    end

    subgraph Layer3["Layer 3 · APK 流水线（对每个 split APK）"]
        C1[unpack_apk]
        C2[merge_apk_arch]
        C3[merge_apk_resources]
        C4[merge_apk_assets]
        C5[delete_signature_related_files]
        C6[update_main_manifest_file]
        C7[build_single_apk]
        C8[copy_single_apk_to_working_dir]
        B4 --> C1
        C1 --> C2
        C1 --> C3
        C1 --> C4
        C2 --> C5
        C3 --> C5
        C4 --> C5
        C5 --> C6
        C6 --> C7
        C7 --> C8
    end

    subgraph Ext["外部工具"]
        E1[apktool d -s]
        E2[apktool b]
        E3[zipalign]
        E4[apksigner]
        C1 -.调用.-> E1
        C7 -.调用.-> E2
        C7 -.调用.-> E3
        C7 -.调用.-> E4
    end
```

## 模块依赖（按函数分组）

```mermaid
flowchart LR
    A[CLI 入口]
    B[系统/进程工具]
    C[临时目录]
    D[APK 分片分类]
    E[apktool.yml 处理]
    F[分片合并]
    G[apktool 集成]
    H[后处理 zipalign+sign]
    I[Manifest 清理]
    J[签名配置]
    K[高层编排]
    Ext1[apktool CLI]
    Ext2[zipalign CLI]
    Ext3[apksigner CLI]

    A --> B
    A --> C
    A --> D
    A --> G
    A --> K
    A --> J
    K --> G
    K --> H
    G --> B
    H --> B
    H --> J
    F --> E
    D -. reads .xapk manifest .- XAPK[(XAPK)]
    G -. invokes .- Ext1
    H -. invokes .- Ext2
    H -. invokes .- Ext3
```

## 启动流程

```mermaid
flowchart TD
    Start([python xapktoapk.py app.xapk]) --> CheckArgs{check_sys_args}
    CheckArgs -->|False| Help[print_help] --> Exit1[exit -1]
    CheckArgs -->|True| CheckApktool{apktool in PATH?}
    CheckApktool -->|No| ErrA[print error] --> Exit2[exit -2]
    CheckApktool -->|Yes| CheckZipalign{zipalign in PATH?}
    CheckZipalign -->|No| ErrB[print error] --> Exit2
    CheckZipalign -->|Yes| LoadSign[load_sign_properties]
    LoadSign --> SignOn{sign enabled?}
    SignOn -->|Yes| CheckApksigner{apksigner in PATH?}
    SignOn -->|No| Continue[continue]
    CheckApksigner -->|No| ErrC[print error] --> Exit2
    CheckApksigner -->|Yes| Continue
    Continue --> Pipeline[主流水线<br/>extract → split → merge → repack → sign]
    Pipeline --> Done([exit 0])
```

## 关键设计点

1. **顺序流水线，无并发**：所有操作在 `main()` 单线程串行执行
2. **临时目录隔离**：所有中间产物在 `.xapktoapk/` 下，结束时 `shutil.rmtree` 清理
3. **apktool 作为外部 blackbox**：脚本不解析 APK 内部结构，所有解码/重打包都委托给 apktool CLI
4. **Windows 兼容**：通过 `is_windows()` + `get_path_to_batch()` 双路径（POSIX 用 `shutil.which`；Windows 找 `.bat` 用 `cmd /c` 调）
5. **签名可选**：默认不签；启用签名才检查 apksigner
6. **错误处理极简**：所有外部命令失败都 `raise Exception`，由 Python 默认 traceback 退出