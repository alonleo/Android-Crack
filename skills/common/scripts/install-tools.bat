@echo off
setlocal EnableDelayedExpansion
REM ============================================================================
REM install-tools.bat - 下载所有 Android 逆向工具项目 (Windows)
REM ============================================================================
REM 说明:
REM   - 读取同目录 tools-source-registry.txt，逐个 git clone 到
REM     tools\crack-intergration-tools\source-projects\<目标目录>\
REM   - 不改系统环境、不污染 PATH；仅克隆源码项目。
REM   - 现有 Hermes 官方 install.sh 与本脚本无关（本脚本不修改它）。
REM   - dex2jar / FixStackmaps 为已内置非 git 项目，不参与克隆。
REM
REM 用法:
REM   install-tools.bat [-force] [-full] [-only 名称] [-list] [-yes]
REM
REM 依赖: 需先安装 Git for Windows（git.exe 必须在 PATH 中）
REM ============================================================================

set "FORCE=0"
set "FULL=0"
set "DO_LIST=0"
set "ASSUME_YES=0"
set "ONLY="

REM ---- 参数解析 ----
:parse_args
if "%~1"=="" goto end_parse_args
if /i "%~1"=="-force"  (set "FORCE=1" & shift & goto parse_args)
if /i "%~1"=="-full"   (set "FULL=1" & shift & goto parse_args)
if /i "%~1"=="-list"   (set "DO_LIST=1" & shift & goto parse_args)
if /i "%~1"=="-yes"    (set "ASSUME_YES=1" & shift & goto parse_args)
if /i "%~1"=="-only"   (
    if not "%~2"=="" (set "ONLY=%~2" & shift & shift) else (echo 缺少 -only 参数值 & exit /b 1)
    goto parse_args
)
if /i "%~1"=="-h"      (goto usage)
if /i "%~1"=="--help"  (goto usage)
echo 未知选项: %~1
:usage
echo install-tools.bat - 下载 Android 逆向工具项目源码
echo.
echo 用法: %~nx0 [选项]
echo.
echo 选项:
echo   -list           列出 registry 中的工具清单(不下载)
echo   -force          已存在目录也重新克隆
echo   -full           完整克隆(默认浅克隆 --depth 1)
echo   -only ^<名称^>     只克隆指定工具(registry 第 1 列名字)
echo   -yes            跳过开始前的确认提示
echo   -h, --help      显示帮助
exit /b 0
:end_parse_args

REM ---- 定位本脚本目录 ----
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "REGISTRY=%SCRIPT_DIR%\tools-source-registry.txt"
set "SRC_DIR=%SCRIPT_DIR%\tools\crack-intergration-tools\source-projects"

if not exist "%REGISTRY%" (
    echo [ERROR] 找不到工具来源清单: %REGISTRY%
    echo 请确认 tools-source-registry.txt 与脚本在同一目录。
    exit /b 1
)

REM ---- 依赖检查 ----
where git >nul 2>nul
if errorlevel 1 (
    echo [ERROR] 未找到 git,请先安装 Git for Windows 并加入 PATH。
    exit /b 1
)

REM ---- 浅克隆参数 ----
set "DEPTH=--depth 1"
if "%FULL%"=="1" set "DEPTH="

REM ---- 收集 tool 名称(registry 第 1 列)----
REM eol=# 跳过 # 注释行；tokens=1,2,* delims=| 拆分(%%a=name %%b=url %%c=desc)
set /a COUNT=0
for /f "usebackq eol=# tokens=1,2,* delims=|" %%a in ("%REGISTRY%") do (
    set "TOOL_NAME_!COUNT!=%%a"
    set "TOOL_URL_!COUNT!=%%b"
    set "TOOL_DESC_!COUNT!=%%c"
    set /a COUNT+=1
)

if "%DO_LIST%"=="1" (
    echo 共 !COUNT! 个工具项目(registry: %REGISTRY%)
    echo.
    set /a i=0
    :list_loop
    if !i! GEQ %COUNT% goto list_done
    for /f "delims=" %%n in ("!TOOL_NAME_!i!!") do (
        for /f "delims=" %%u in ("!TOOL_URL_!i!!") do (
            echo   %%n  (%%u^)
        )
    )
    set /a i+=1
    goto list_loop
    :list_done
    echo.
    echo 非 git 项目(已内置,不参与克隆):
    echo   dex2jar      发布版 jar(source-projects\dex2jar\)
    echo   FixStackmaps 单个 Java 源文件(source-projects\FixStackmaps\)
    exit /b 0
)

REM ---- 确认 ----
echo 将下载 !COUNT! 个工具项目到: %SRC_DIR%
if "%FORCE%"=="1" echo   模式: --force(已存在也重拉)
if "%FULL%"=="1" (echo   克隆: 完整历史) else (echo   克隆: 浅克隆)
if not "%ONLY%"=="" echo   仅: %ONLY%
echo.
if not "%ASSUME_YES%"=="1" (
    set /p ans=继续? [y/N]
    if /i not "!ans!"=="y" (
        if /i not "!ans!"=="yes" (
            echo 已取消。
            exit /b 0
        )
    )
)

REM ---- 执行克隆 ----
set /a done_ok=0
set /a done_fail=0
set /a done_skip=0
set "FAILED_NAMES="

set /a idx=0
:clone_loop
if !idx! GEQ %COUNT% goto clone_done

set "name=!TOOL_NAME_!idx!!"
set "url=!TOOL_URL_!idx!!"

REM -only 过滤
if not "%ONLY%"=="" (
    if /i not "!name!"=="%ONLY%" (
        set /a idx+=1
        goto clone_loop
    )
)

set "target=%SRC_DIR%\!name!"
set "skip_this=0"

REM 已存在判断
if exist "!target!\.git" set "skip_this=1"
if exist "!target!" if not exist "!target!\.git" set "skip_this=1"

if "!skip_this!"=="1" (
    if not "%FORCE%"=="1" (
        echo [跳过] !name! 已存在 - !target!
        set /a done_skip+=1
        set /a idx+=1
        goto clone_loop
    ) else (
        if exist "!target!" rd /s /q "!target!"
    )
)

echo [克隆] !name!  -  !url!
git clone %DEPTH% "!url!" "!target!"
if errorlevel 1 (
    echo [失败] !name!
    if exist "!target!" rd /s /q "!target!"
    set /a done_fail+=1
    set "FAILED_NAMES=!FAILED_NAMES! !name!"
) else (
    echo [完成] !name!
    set /a done_ok+=1
)
set /a idx+=1
goto clone_loop
:clone_done

echo.
echo ============================================
echo  完成
echo  新增/重拉成功: !done_ok!
if !done_skip! GTR 0 echo  已存在跳过: !done_skip!
if !done_fail! GTR 0 (
    echo  失败: !done_fail! ^(!FAILED_NAMES!^)
    echo.
    echo  以下工具克隆失败,可单独重试:
    echo    %~nx0 -only ^<名称^>
    exit /b 1
)
echo  全部就绪
exit /b 0