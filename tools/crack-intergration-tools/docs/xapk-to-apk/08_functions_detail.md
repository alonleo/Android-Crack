# 08 函数详细说明

所有函数位于 `xapktoapk.py`，按文件行号排列。每个函数标注：签名、位置、可见性、参数、副作用、调用栈关系。

---

## `print_help()` (行 43)

- **签名**：`def print_help() -> None`
- **位置**：`xapktoapk.py:43`
- **可见性**：module-level（隐式 public）
- **参数**：无
- **返回值**：None
- **抛出**：无
- **副作用**：向 stdout 打印 5 行
- **调用**：被 `main()` 调用（行 521，仅当 `check_sys_args()` 返回 False）
- **调用了**：无
- **简要说明**：打印使用说明到 stdout

---

## `get_param_xapk_file_name()` (行 51)

- **签名**：`def get_param_xapk_file_name() -> str`
- **位置**：`xapktoapk.py:51`
- **可见性**：module-level
- **参数**：无
- **返回值**：`sys.argv[1]`（用户传入的 .xapk 文件名）
- **抛出**：`IndexError` 当 `sys.argv` 长度不足（实际由 `check_sys_args()` 先保证）
- **副作用**：无
- **调用**：被 `main()` 调用（行 542），被 `get_param_xapk_abs_path()` 调用（行 56），被 `check_sys_args()` 调用（行 62）
- **调用了**：无（仅读 `sys.argv`）
- **简要说明**：取命令行第一个参数

---

## `get_param_xapk_abs_path()` (行 55)

- **签名**：`def get_param_xapk_abs_path() -> str`
- **位置**：`xapktoapk.py:55`
- **可见性**：module-level
- **参数**：无
- **返回值**：参数文件的绝对路径
- **抛出**：无
- **副作用**：无
- **调用**：被 `main()` 调用（行 543）
- **调用了**：`get_param_xapk_file_name()` (行 56 → 51), `os.path.abspath()`
- **简要说明**：返回参数文件的绝对路径

---

## `check_sys_args()` (行 59)

- **签名**：`def check_sys_args() -> bool`
- **位置**：`xapktoapk.py:59`
- **可见性**：module-level
- **参数**：无
- **返回值**：`True` 当且仅当：① `len(sys.argv) == 2` ② 参数以 `.xapk` 结尾 ③ 文件存在
- **抛出**：无（失败返回 `False`）
- **副作用**：无
- **调用**：被 `main()` 调用（行 520）
- **调用了**：`get_param_xapk_file_name()` (行 62 → 51), `os.path.abspath()` (行 65), `os.path.exists()` (行 66), `endswith()` (行 63)
- **简要说明**：校验 CLI 参数是否合法

---

## `execute_command_os_system(command)` (行 71)

- **签名**：`def execute_command_os_system(command: str) -> int`
- **位置**：`xapktoapk.py:71`
- **可见性**：module-level
- **参数**：`command: str` —— 整条 shell 命令字符串
- **返回值**：shell 返回码
- **抛出**：无
- **副作用**：通过 `os.system` 同步执行命令
- **调用**：**未在脚本其他位置调用**（备用 helper，已被 `execute_command_subprocess` 取代）
- **调用了**：`os.system()`
- **简要说明**：`os.system` 包装，返回 RC

---

## `execute_command_subprocess(command_tokens_list)` (行 76)

- **签名**：`def execute_command_subprocess(command_tokens_list: list[str]) -> int`
- **位置**：`xapktoapk.py:76`
- **可见性**：module-level
- **参数**：`command_tokens_list: list[str]` —— argv 形式的命令列表
- **返回值**：进程退出码
- **抛出**：无（RC 反映失败）
- **副作用**：同步执行子进程，stdout 重定向到 `DEVNULL`，stderr 合并到 stdout
- **调用**：被 `windows_hide_file()` 调用（行 86），被 `unpack_apk()` 调用（行 318），被 `pack_apk()` 调用（行 335），被 `zipalign_apk()` 调用（行 368），被 `sign_apk()` 调用（行 386）
- **调用了**：`subprocess.call()`
- **简要说明**：POSIX 路径下执行外部命令，丢弃 stdout

---

## `is_windows()` (行 81)

- **签名**：`def is_windows() -> bool`
- **位置**：`xapktoapk.py:81`
- **可见性**：module-level
- **参数**：无
- **返回值**：`True` 当 `platform.system() == "Windows"`
- **抛出**：无
- **副作用**：无
- **调用**：被 `create_or_recreate_dir()` 调用（行 96）
- **调用了**：`platform.system()`
- **简要说明**：判断当前是否 Windows 平台

---

## `windows_hide_file(file_path)` (行 85)

- **签名**：`def windows_hide_file(file_path: str) -> None`
- **位置**：`xapktoapk.py:85`
- **可见性**：module-level
- **参数**：`file_path: str` —— 要隐藏的文件/目录绝对路径
- **返回值**：None
- **抛出**：外部 `attrib` 失败时通过 `execute_command_subprocess` 返回非零 RC（但本函数不检查 RC）
- **副作用**：调用 `attrib +h <path>`
- **调用**：被 `create_or_recreate_dir()` 调用（行 97）
- **调用了**：`execute_command_subprocess()` (行 86 → 76)
- **简要说明**：Windows 下设置文件隐藏属性

---

## `create_or_recreate_dir(dir_path)` (行 89)

- **签名**：`def create_or_recreate_dir(dir_path: str) -> None`
- **位置**：`xapktoapk.py:89`
- **可见性**：module-level
- **参数**：`dir_path: str` —— 目标目录路径
- **返回值**：None
- **抛出**：若路径存在但是文件（不是目录）时 `os.remove` 后再 `os.mkdir`；其他 IO 异常
- **副作用**：删旧建新；Windows 下隐藏
- **调用**：被 `create_tmp_dir()` 调用（行 117）
- **调用了**：`os.path.exists()` (90), `os.path.isdir()` (91), `shutil.rmtree()` (92), `os.remove()` (94), `os.mkdir()` (95), `is_windows()` (96), `windows_hide_file()` (97 → 85)
- **简要说明**：清理并重建目录

---

## `check_if_executable_exists_in_path(executable)` (行 100)

- **签名**：`def check_if_executable_exists_in_path(executable: str) -> bool`
- **位置**：`xapktoapk.py:100`
- **可见性**：module-level
- **参数**：`executable: str` —— 可执行文件名
- **返回值**：`True` 当 `shutil.which` 找到
- **抛出**：无
- **副作用**：无
- **调用**：被 `main()` 调用（行 525, 530, 538），被 `sign_apk()` 调用（行 385）
- **调用了**：`shutil.which()` (行 101)
- **简要说明**：判断命令是否在 `$PATH` 中

---

## `get_executable_in_path(executable)` (行 104)

- **签名**：`def get_executable_in_path(executable: str) -> Optional[str]`
- **位置**：`xapktoapk.py:104`
- **可见性**：module-level
- **参数**：`executable: str` —— 可执行文件名
- **返回值**：绝对路径或 `None`
- **抛出**：无
- **副作用**：无
- **调用**：被 `unpack_apk()` 调用（行 316），被 `pack_apk()` 调用（行 333）
- **调用了**：`shutil.which()` (行 105)
- **简要说明**：返回可执行文件的绝对路径

---

## `get_path_to_batch(batch)` (行 107)

- **签名**：`def get_path_to_batch(batch: str) -> Optional[str]`
- **位置**：`xapktoapk.py:107`
- **可见性**：module-level
- **参数**：`batch: str` —— Windows 下 `.bat` 文件的基础名（不含扩展名）
- **返回值**：`<batch>.bat` 的绝对路径或 `None`
- **抛出**：无
- **副作用**：无
- **调用**：被 `main()` 调用（行 525, 538），被 `unpack_apk()` 调用（行 322），被 `pack_apk()` 调用（行 339），被 `sign_apk()` 调用（行 390）
- **调用了**：`os.environ['PATH'].split()` (行 108), `os.path.isfile()` (行 111), `os.path.join()` (行 112)
- **简要说明**：Windows 专用：找 `<batch>.bat`

---

## `create_tmp_dir(working_dir)` (行 115)

- **签名**：`def create_tmp_dir(working_dir: str) -> str`
- **位置**：`xapktoapk.py:115`
- **可见性**：module-level
- **参数**：`working_dir: str` —— 临时目录要建立在哪个目录下
- **返回值**：临时目录的绝对路径
- **抛出**：可能 `os.mkdir` 失败
- **副作用**：建一个名为 `.xapktoapk` 的目录（Windows 下隐藏）
- **调用**：被 `main()` 调用（行 549）
- **调用了**：`os.path.abspath()` (行 116), `create_or_recreate_dir()` (行 117 → 89)
- **简要说明**：建临时工作目录

---

## `file_split_name_and_extension(file_path)` (行 121)

- **签名**：`def file_split_name_and_extension(file_path: str) -> tuple[str, str]`
- **位置**：`xapktoapk.py:121`
- **可见性**：module-level
- **参数**：`file_path: str`
- **返回值**：`(name_without_ext, ext)` 元组
- **抛出**：无
- **副作用**：无
- **调用**：被 `main()` 调用（行 544）
- **调用了**：`os.path.splitext()` (行 122)
- **简要说明**：拆文件名和扩展名

---

## `determine_split_type_by_apk_file_name(apk_file_name, xapk_package_name)` (行 126)

- **签名**：`def determine_split_type_by_apk_file_name(apk_file_name: str, xapk_package_name: str) -> Optional[str]`
- **位置**：`xapktoapk.py:126`
- **可见性**：module-level
- **参数**：
  - `apk_file_name: str` —— 单个 APK 的文件名（如 `config.arm64_v8a.apk`）
  - `xapk_package_name: str` —— manifest.json 里的 `package_name`
- **返回值**：四个常量之一 —— `const_split_apk_type_main` / `_arch` / `_dpi` / `_locale`，失败时 `None`
- **抛出**：内部 try/except 吞掉所有异常，返回 `None`
- **副作用**：无
- **调用**：被 `main()` 调用（行 577）
- **调用了**：`os.path.splitext()` (行 132), `str()` (行 134)
- **简要说明**：根据文件名判定 split 类型

判定规则（行 129-142）：

| 文件名 | 判定结果 |
|--------|----------|
| `<xapk_package_name>.apk` 或 `base.apk` | `main` |
| `config.<X>.apk` 且 `<X>` 以 `dpi` 结尾 | `dpi` |
| `config.<X>.apk` 且 `<X>` ∈ 架构白名单 | `arch` |
| `config.<X>.apk` 其他 | `locale` |
| 其余文件 | `locale`（兜底） |

---

## `get_apks_of_type(target_apks, type)` (行 148)

- **签名**：`def get_apks_of_type(target_apks: dict, type: str) -> list[dict]`
- **位置**：`xapktoapk.py:148`
- **可见性**：module-level
- **参数**：
  - `target_apks: dict` —— 全部 APK 字典（来自 `main`）
  - `type: str` —— split 类型
- **返回值**：匹配类型的 APK 属性字典列表
- **抛出**：无
- **副作用**：无
- **调用**：被 `main()` 调用（行 597, 598, 599），被 `get_main_apk()` 调用（行 158）
- **调用了**：无（纯 dict 操作）
- **简要说明**：按 split 类型过滤

---

## `get_main_apk(target_apks)` (行 157)

- **签名**：`def get_main_apk(target_apks: dict) -> dict`
- **位置**：`xapktoapk.py:157`
- **可见性**：module-level
- **参数**：`target_apks: dict`
- **返回值**：main APK 的属性字典（取列表首元素）
- **抛出**：`IndexError` 当没有 main APK（但理论上 xapk 必有 main）
- **副作用**：无
- **调用**：被 `main()` 调用（行 596）
- **调用了**：`get_apks_of_type()` (行 158 → 148)
- **简要说明**：取 main APK

---

## `get_do_not_compress_lines(config_file_lines)` (行 161)

- **签名**：`def get_do_not_compress_lines(config_file_lines: list[str]) -> tuple[list[str], int, int]`
- **位置**：`xapktoapk.py:161`
- **可见性**：module-level
- **参数**：`config_file_lines: list[str]` —— apktool.yml 的全部行
- **返回值**：`(do_not_compress_lines_sorted, index_start, index_end)` 三元组
- **抛出**：无
- **副作用**：无
- **调用**：被 `parse_apktool_config()` 调用（行 188）
- **调用了**：`enumerate()` (行 168), `startswith()` (行 169, 173, 175)
- **简要说明**：解析 `doNotCompress:` 块

解析状态机（行 165-180）：
- 起始：`doNotCompress:` 行被识别为 `opened=True`，记录 `index_start = 当前索引+1`
- 中间：以 `- ` 开头的行收集到 `result`
- 结束：第一个不以 `- ` 开头的行（且在块内）作为 `index_end = 当前索引-1`

---

## `parse_apktool_config(config_file_path)` (行 183)

- **签名**：`def parse_apktool_config(config_file_path: str) -> dict`
- **位置**：`xapktoapk.py:183`
- **可见性**：module-level
- **参数**：`config_file_path: str` —— apktool.yml 绝对路径
- **返回值**：
  ```python
  {
      'lines_all': [...],
      'lines_do_not_compress': [...],
      'lines_do_not_compress_index_start': int,
      'lines_do_not_compress_index_end': int,
  }
  ```
- **抛出**：文件 IO 异常
- **副作用**：读文件
- **调用**：被 `insert_new_lines_do_not_compress()` 调用（行 200），被 `merge_apk_arch()` 调用（行 235），被 `merge_apk_assets()` 调用（行 309）
- **调用了**：`open()` (行 185), `file.readlines()` (行 186), `get_do_not_compress_lines()` (行 188 → 161)
- **简要说明**：读 apktool.yml，返回结构化 dict

---

## `insert_new_lines_do_not_compress(config_file_path, lines_to_insert)` (行 199)

- **签名**：`def insert_new_lines_do_not_compress(config_file_path: str, lines_to_insert: list[str]) -> None`
- **位置**：`xapktoapk.py:199`
- **可见性**：module-level
- **参数**：
  - `config_file_path: str` —— 目标 apktool.yml 路径
  - `lines_to_insert: list[str]` —— 要插入的 `- xxx` 行
- **返回值**：None
- **抛出**：文件 IO 异常
- **副作用**：原地修改 apktool.yml
- **调用**：被 `merge_apk_arch()` 调用（行 236），被 `merge_apk_assets()` 调用（行 310）
- **调用了**：`parse_apktool_config()` (行 200 → 183), `set()` (行 203), `sort()` (行 207, 215 切片赋值), `open(w)` (行 217), `file.writelines()` (行 218)
- **简要说明**：把新行合并到 apktool.yml 的 doNotCompress 块

---

## `merge_apk_arch(dir_apk_main, dir_apk_arch)` (行 221)

- **签名**：`def merge_apk_arch(dir_apk_main: str, dir_apk_arch: str) -> None`
- **位置**：`xapktoapk.py:221`
- **可见性**：module-level
- **参数**：
  - `dir_apk_main: str` —— main APK 解包目录
  - `dir_apk_arch: str` —— arch APK 解包目录
- **返回值**：None
- **抛出**：可能 `os.mkdir` 失败
- **副作用**：在 main 下建 `lib/`，把 arch 的 `lib/<ABI>/` 拷过来；合并 apktool.yml
- **调用**：被 `main()` 调用（行 602）
- **调用了**：`os.path.join()` (行 222, 223, 232, 233), `os.path.exists()` (行 224), `os.mkdir()` (行 225), `os.listdir()` (行 227), `shutil.copytree()` (行 230), `parse_apktool_config()` (行 235 → 183), `insert_new_lines_do_not_compress()` (行 236 → 199)
- **简要说明**：合并 arch 分片到 main

---

## `merge_apk_resources(dir_apk_main, dir_apk_with_resources)` (行 239)

- **签名**：`def merge_apk_resources(dir_apk_main: str, dir_apk_with_resources: str) -> None`
- **位置**：`xapktoapk.py:239`
- **可见性**：module-level
- **参数**：
  - `dir_apk_main: str`
  - `dir_apk_with_resources: str` —— dpi 或 locale APK 解包目录
- **返回值**：None
- **抛出**：可能 IO 异常
- **副作用**：把分片的 `res/` 拷到 main，跳过 `values/public.xml` 和冲突
- **调用**：被 `main()` 调用（行 605, 607）
- **调用了**：`os.path.join()` (行 240, 241, 248, 252, 256), `os.walk()` (行 246, 288), `os.path.exists()` (行 249, 268), `os.mkdir()` (行 250, 269), `endswith()` (行 253), `os.path.abspath()` (行 267), `os.path.dirname()` (行 267), `shutil.copy()` (行 271)
- **简要说明**：合并 dpi/locale 分片的 res 到 main

合并规则（行 261-265）：
- 目标已存在 + 路径以 `drawable` 开头 → 跳过（**bug**：注释 `# todo handle merge xmls ?`）
- 目标已存在 + 其他路径 → 跳过（不覆盖）
- 目标不存在 → `os.makedirs` + `shutil.copy`

---

## `merge_apk_assets(dir_apk_main, dir_apk_with_asset_pack)` (行 274)

- **签名**：`def merge_apk_assets(dir_apk_main: str, dir_apk_with_asset_pack: str) -> None`
- **位置**：`xapktoapk.py:274`
- **可见性**：module-level
- **参数**：
  - `dir_apk_main: str`
  - `dir_apk_with_asset_pack: str` —— locale APK 解包目录（locale 才可能有 assetpack）
- **返回值**：None（如果分片无 `assets/assetpack/`，提前 return 行 281）
- **抛出**：可能 IO 异常
- **副作用**：建 `assets/assetpack/` 目录，拷贝文件；合并 apktool.yml
- **调用**：被 `main()` 调用（行 608）
- **调用了**：`os.path.join()` (行 275, 276, 277, 278, 290, 294, 296, 302), `os.path.exists()` (行 280, 282, 284, 303), `os.mkdir()` (行 283, 285, 304), `os.walk()` (行 288), `shutil.copy()` (行 305), `parse_apktool_config()` (行 309 → 183), `insert_new_lines_do_not_compress()` (行 310 → 199)
- **简要说明**：合并 locale 分片的 assets/assetpack 到 main

---

## `unpack_apk(path_dir_tmp, apk_file, number_current, number_total)` (行 313)

- **签名**：`def unpack_apk(path_dir_tmp: str, apk_file: str, number_current: int, number_total: int) -> None`
- **位置**：`xapktoapk.py:313`
- **可见性**：module-level
- **参数**：
  - `path_dir_tmp: str` —— 临时目录
  - `apk_file: str` —— 单个 APK 文件名
  - `number_current: int` —— 当前进度
  - `number_total: int` —— 总数（用于打印）
- **返回值**：None
- **抛出**：`Exception("failed to unpack %s" % apk_file)` 当 RC != 0 或 Windows 路径下 stderr 非空
- **副作用**：`chdir(path_dir_tmp)`；执行 `apktool d -s <apk_file>`；删除原 apk 文件
- **调用**：被 `main()` 调用（行 594）
- **调用了**：`print()` (行 314), `os.chdir()` (行 315), `get_executable_in_path()` (行 316 → 104), `execute_command_subprocess()` (行 318 → 76), `get_path_to_batch()` (行 322 → 107), `Popen()` (行 323), `p.communicate()` (行 324), `os.remove()` (行 327)
- **简要说明**：用 apktool 解包单个 APK

---

## `pack_apk(path_dir_tmp, main_apk_dir)` (行 330)

- **签名**：`def pack_apk(path_dir_tmp: str, main_apk_dir: str) -> None`
- **位置**：`xapktoapk.py:330`
- **可见性**：module-level
- **参数**：
  - `path_dir_tmp: str`
  - `main_apk_dir: str` —— main APK 的解包目录名
- **返回值**：None
- **抛出**：`Exception("failed to pack apk")` 或 `"result apk not found"`
- **副作用**：`chdir(path_dir_tmp)`；执行 `apktool b <main_apk_dir>`；拷贝产物到 `<tmp>/target.apk`
- **调用**：被 `build_single_apk()` 调用（行 471）
- **调用了**：`print()` (行 331), `os.chdir()` (行 332), `get_executable_in_path()` (行 333 → 104), `execute_command_subprocess()` (行 335 → 76), `get_path_to_batch()` (行 339 → 107), `Popen()` (行 340), `p.communicate()` (行 341), `os.path.exists()` (行 345), `os.path.join()` (行 344, 348), `os.path.basename()` (行 344), `os.remove()` (行 350), `shutil.copy()` (行 352)
- **简要说明**：用 apktool 重打包 main APK

产物路径：`<tmp>/<main_apk_dir>/dist/<basename>.apk` → 拷到 `<tmp>/target.apk`（行 344-352）

---

## `zipalign_apk(path_dir_tmp)` (行 355)

- **签名**：`def zipalign_apk(path_dir_tmp: str) -> None`
- **位置**：`xapktoapk.py:355`
- **可见性**：module-level
- **参数**：`path_dir_tmp: str`
- **返回值**：None
- **抛出**：`Exception("failed to zipalign apk")` 或 `"result apk not found"`
- **副作用**：`chdir(path_dir_tmp)`；执行 `zipalign -p -f 4 target.apk aligned_target.apk`；原子替换
- **调用**：被 `build_single_apk()` 调用（行 472）
- **调用了**：`print()` (行 356), `os.chdir()` (行 357), `os.path.join()` (行 359, 364), `os.path.exists()` (行 360, 365, 371), `os.remove()` (行 366, 374), `execute_command_subprocess()` (行 368 → 76), `shutil.move()` (行 375)
- **简要说明**：4 字节对齐 zip 条目

---

## `sign_apk(path_dir_tmp, sign_config)` (行 378)

- **签名**：`def sign_apk(path_dir_tmp: str, sign_config: dict) -> None`
- **位置**：`xapktoapk.py:378`
- **可见性**：module-level
- **参数**：
  - `path_dir_tmp: str`
  - `sign_config: dict` —— `load_sign_properties` 返回的字典
- **返回值**：None
- **抛出**：`Exception("result apk not found")` 或 `"failed to sign apk file"`
- **副作用**：`chdir(path_dir_tmp)`；执行 `apksigner sign --ks <ks> --ks-pass pass:<pw> --ks-key-alias <alias> --key-pass pass:<pw> target.apk`
- **调用**：被 `build_single_apk()` 调用（行 474）
- **调用了**：`os.path.join()` (行 379), `os.path.exists()` (行 380), `print()` (行 383), `os.chdir()` (行 384), `check_if_executable_exists_in_path()` (行 385 → 100), `execute_command_subprocess()` (行 386 → 76), `os.path.expanduser()` (行 386, 390), `get_path_to_batch()` (行 390 → 107), `Popen()` (行 391), `p.communicate()` (行 392)
- **简要说明**：用 apksigner 给 APK 签名

---

## `delete_file_if_exists(path_to_file)` (行 397)

- **签名**：`def delete_file_if_exists(path_to_file: str) -> None`
- **位置**：`xapktoapk.py:397`
- **可见性**：module-level
- **参数**：`path_to_file: str`
- **返回值**：None
- **抛出**：无（`os.remove` 失败时可能抛）
- **副作用**：若文件存在则删除
- **调用**：被 `delete_signature_related_files()` 调用（行 405, 406, 407）
- **调用了**：`os.path.exists()` (行 398), `os.remove()` (行 399)
- **简要说明**：安全的 `os.remove`

注：注释掉的 `unknown/stamp-cert-sha256` 与 `original/stamp-cert-sha256` 删除逻辑（行 403-404），apktool 新版本不再生成这些文件。

---

## `delete_signature_related_files(path_to_main_apk)` (行 402)

- **签名**：`def delete_signature_related_files(path_to_main_apk: str) -> None`
- **位置**：`xapktoapk.py:402`
- **可见性**：module-level
- **参数**：`path_to_main_apk: str`
- **返回值**：None
- **抛出**：无（依赖 `delete_file_if_exists` 兜底）
- **副作用**：删除 `original/META-INF/` 下的三个签名文件
- **调用**：被 `main()` 调用（行 610）
- **调用了**：`delete_file_if_exists()` (行 405, 406, 407 → 397), `os.path.join()` (行 405, 406, 407)
- **简要说明**：删签名残留，准备重新签名

---

## `update_main_manifest_file(path_main_apk)` (行 410)

- **签名**：`def update_main_manifest_file(path_main_apk: str) -> None`
- **位置**：`xapktoapk.py:410`
- **可见性**：module-level
- **参数**：`path_main_apk: str`
- **返回值**：None
- **抛出**：文件 IO 异常
- **副作用**：原地修改 `AndroidManifest.xml`
- **调用**：被 `main()` 调用（行 611）
- **调用了**：`os.path.join()` (行 411), `open(r)` (行 424), `file.read()` (行 425), `str.replace()` (行 428), `open(w)` (行 430), `file.write()` (行 431)
- **简要说明**：字符串硬编码替换去 split 标记

替换规则（行 414-422）：
| from | to |
|------|-----|
| `<meta-data android:name="com.google.firebase.messaging.default_notification_icon" android:resource="@null"/>` | `""` |
| `android:isSplitRequired="true" ` | `""` |
| `android:requiredSplitTypes="base__abi,base__density" ` | `""` |
| `android:splitTypes="" ` | `""` |
| `android:value="STAMP_TYPE_DISTRIBUTION_APK"` | `android:value="STAMP_TYPE_STANDALONE_APK"` |
| `<meta-data android:name="com.android.vending.splits.required" android:value="true"/>` | `""` |
| `<meta-data android:name="com.android.vending.splits" android:resource="@xml/splits0"/>` | `""` |

---

## `load_sign_properties()` (行 434)

- **签名**：`def load_sign_properties() -> Optional[dict]`
- **位置**：`xapktoapk.py:434`
- **可见性**：module-level
- **参数**：无
- **返回值**：properties 字典 或 `None`（签名未启用 / 配置无效）
- **抛出**：无
- **副作用**：可能读 cwd 或 ~/ 下的 properties 文件
- **调用**：被 `main()` 调用（行 534）
- **调用了**：`os.path.abspath()` (行 435, 437), `os.path.join()` (行 435, 437), `os.getcwd()` (行 435), `os.path.exists()` (行 436, 438, 462), `os.path.expanduser()` (行 437, 461), `open(r)` (行 442), `sign_config_file.readlines()` (行 443), `line.strip()` (行 447), `line.replace()` (行 447), `line.startswith()` (行 448), `line.split()` (行 450), `len()` (行 451), `properties.keys()` (行 457, 459), `properties[key].lower()` (行 457), `os.path.isdir()` (行 462)
- **简要说明**：加载签名配置

返回条件（必须全部满足）：
- properties 文件存在
- `sign.enabled=true`
- 4 个字段（keystore file / password / alias / key password）齐全
- keystore 文件存在且不是目录
- 所有密码非空

---

## `build_single_apk(path_to_tmp_dir, path_to_main_apk_dir, should_sign_apk, sign_config)` (行 470)

- **签名**：`def build_single_apk(path_to_tmp_dir: str, path_to_main_apk_dir: str, should_sign_apk: bool, sign_config: Optional[dict]) -> None`
- **位置**：`xapktoapk.py:470`
- **可见性**：module-level
- **参数**：
  - `path_to_tmp_dir: str`
  - `path_to_main_apk_dir: str`
  - `should_sign_apk: bool`
  - `sign_config: Optional[dict]`
- **返回值**：None
- **抛出**：异常来自 `pack_apk` / `zipalign_apk` / `sign_apk`
- **副作用**：顺序调用 pack → zipalign → sign
- **调用**：被 `main()` 调用（行 613）
- **调用了**：`pack_apk()` (行 471 → 330), `zipalign_apk()` (行 472 → 355), `sign_apk()` (行 474 → 378), `print()` (行 476)
- **简要说明**：高层 pack + zipalign + sign 编排

---

## `copy_single_apk_to_working_dir(path_to_tmp_dir, path_to_working_dir, target_name)` (行 479)

- **签名**：`def copy_single_apk_to_working_dir(path_to_tmp_dir: str, path_to_working_dir: str, target_name: str) -> None`
- **位置**：`xapktoapk.py:479`
- **可见性**：module-level
- **参数**：
  - `path_to_tmp_dir: str`
  - `path_to_working_dir: str`
  - `target_name: str` —— 不含扩展名的目标文件名
- **返回值**：None
- **抛出**：`Exception("result apk file not found")`
- **副作用**：把 `<tmp>/target.apk` 拷到 `<working_dir>/<target_name>.apk`
- **调用**：被 `main()` 调用（行 614）
- **调用了**：`os.path.join()` (行 480, 484), `os.path.exists()` (行 481, 485), `os.path.isdir()` (行 481, 486), `shutil.rmtree()` (行 487), `os.remove()` (行 489), `shutil.copy()` (行 491)
- **简要说明**：拷产物到工作目录

---

## `prioritize_dpi_apk_list_rev_sort(apks_dpi)` (行 494)

- **签名**：`def prioritize_dpi_apk_list_rev_sort(apks_dpi: list[dict]) -> list[dict]`
- **位置**：`xapktoapk.py:494`
- **可见性**：module-level
- **参数**：`apks_dpi: list[dict]`
- **返回值**：按 `apk_file_name` 字典序倒排
- **抛出**：无
- **副作用**：无
- **调用**：被 `prioritize_dpi_apk_list()` 调用（行 512）
- **调用了**：`sorted()` (行 495), `lambda`
- **简要说明**：DPI 字典序倒排（兜底排序）

---

## `prioritize_dpi_apk_list(apks_dpi)` (行 499)

- **签名**：`def prioritize_dpi_apk_list(apks_dpi: list[dict]) -> list[dict]`
- **位置**：`xapktoapk.py:499`
- **可见性**：module-level
- **参数**：`apks_dpi: list[dict]`
- **返回值**：按 `xxxhdpi → xxhdpi → xhdpi → hdpi → mdpi → ldpi → nodpi → tvdpi` 优先级排序；剩余按字典序倒排
- **抛出**：无
- **副作用**：无
- **调用**：被 `main()` 调用（行 603）
- **调用了**：`dict()` (行 502), `apks_dpi_map.keys()` (行 508, 511), `del()` (行 510), `len()` (行 511), `prioritize_dpi_apk_list_rev_sort()` (行 512 → 494)
- **简要说明**：DPI 优先级排序

排序逻辑：先按白名单顺序逐个取出（从 `apks_dpi_map` 删除），剩余值用字典序倒排补到末尾。

---

## `main()` (行 519)

- **签名**：`def main() -> None`
- **位置**：`xapktoapk.py:519`
- **可见性**：module-level（脚本入口）
- **参数**：无
- **返回值**：None
- **抛出**：`exit(-1)` / `exit(-2)` / `Exception`（来自各子函数）
- **副作用**：完整流水线 + stdout 进度打印 + 临时目录创建/清理
- **调用**：由 `if __name__ == '__main__'` 调用（行 622-623）
- **调用了**：见下
- **简要说明**：顶层编排

**直接调用的函数**（行 520-617，按调用顺序）：
1. `check_sys_args()` (520)
2. `print_help()` (521)
3. `check_if_executable_exists_in_path("apktool")` (525)
4. `get_path_to_batch("apktool")` (525)
5. `check_if_executable_exists_in_path("zipalign")` (530)
6. `load_sign_properties()` (534)
7. `check_if_executable_exists_in_path("apksigner")` (538)
8. `get_path_to_batch("apksigner")` (538)
9. `get_param_xapk_file_name()` (542)
10. `get_param_xapk_abs_path()` (543)
11. `file_split_name_and_extension()` (544)
12. `create_tmp_dir(cwd)` (549)
13. `determine_split_type_by_apk_file_name()` (577, 在循环中)
14. `unpack_apk()` (594, 在循环中)
15. `get_main_apk()` (596)
16. `get_apks_of_type()` (597, 598, 599)
17. `merge_apk_arch()` (602, 在循环中)
18. `prioritize_dpi_apk_list()` (603)
19. `merge_apk_resources()` (605, 607, 在循环中)
20. `merge_apk_assets()` (608, 在循环中)
21. `delete_signature_related_files()` (610)
22. `update_main_manifest_file()` (611)
23. `build_single_apk()` (613)
24. `copy_single_apk_to_working_dir()` (614)

`main` 内调用的标准库：`sys.exit`、`os.system`（间接）、`os.path.*`、`shutil.copy/rmtree`、`zipfile.ZipFile.extractall`、`json.load`

---

## 函数调用关系图（简版）

```mermaid
flowchart LR
    main[main 行 519]
    main --> A1[check_sys_args]
    main --> A2[print_help]
    main --> A3[load_sign_properties]
    main --> A4[get_param_xapk_file_name]
    main --> A5[get_param_xapk_abs_path]
    main --> A6[file_split_name_and_extension]
    main --> A7[create_tmp_dir]
    main --> A8[determine_split_type_by_apk_file_name]
    main --> A9[unpack_apk]
    main --> A10[get_main_apk]
    main --> A11[get_apks_of_type]
    main --> A12[merge_apk_arch]
    main --> A13[prioritize_dpi_apk_list]
    main --> A14[merge_apk_resources]
    main --> A15[merge_apk_assets]
    main --> A16[delete_signature_related_files]
    main --> A17[update_main_manifest_file]
    main --> A18[build_single_apk]
    main --> A19[copy_single_apk_to_working_dir]
    main --> B1[check_if_executable_exists_in_path]
    main --> B2[get_path_to_batch]

    A4 --> C1[get_param_xapk_file_name again]
    A5 --> A4
    A7 --> B3[create_or_recreate_dir]
    A10 --> A11
    A11 --> C2[dict filter]
    A12 --> D1[parse_apktool_config]
    A12 --> D2[insert_new_lines_do_not_compress]
    A14 --> C3[os walk + shutil.copy]
    A15 --> C4[os walk + shutil.copy]
    A15 --> D1
    A15 --> D2
    A16 --> B4[delete_file_if_exists]
    A17 --> C5[open r/w]
    A18 --> E1[pack_apk]
    A18 --> E2[zipalign_apk]
    A18 --> E3[sign_apk]
    A19 --> C6[shutil.copy]

    A9 --> B1
    A9 --> B2
    A9 --> F1[execute_command_subprocess]
    A9 --> F2[Popen]
    B3 --> B5[is_windows]
    B3 --> B6[windows_hide_file]
    B6 --> F1

    A1 --> A4
    D1 --> D3[get_do_not_compress_lines]
    D2 --> D1
    D2 --> C7[set + sort]

    A13 --> D4[prioritize_dpi_apk_list_rev_sort]
    E1 --> B1
    E1 --> B2
    E1 --> F1
    E1 --> F2
    E2 --> F1
    E3 --> B1
    E3 --> F1
    E3 --> F2
```