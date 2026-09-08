<#
.SYNOPSIS
  Android 逆向工具链本地安装 — Windows PowerShell 版
.DESCRIPTION
  将 JDK / apktool / jadx / Android SDK / frida 安装到本项目目录下
  不污染系统环境。
.PARAMETER Force
  重新下载已存在的工具
.EXAMPLE
  .\tools\scripts\setup-local-tools.ps1
  .\tools\scripts\setup-local-tools.ps1 -Force
#>

param([switch]$Force)

$ErrorActionPreference = "Stop"
$REPO = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$ENV_DIR = Join-Path $REPO "tools\environments"
$TOOLS_BIN = Join-Path $ENV_DIR "bin"
$SDK_DIR = Join-Path $ENV_DIR "android-sdk"
$JDK_DIR = Join-Path $ENV_DIR "jdk"
$MANIFEST = Join-Path $ENV_DIR ".manifest"

# ── 清单函数 ──
function Manifest-Init {
  if (-not (Test-Path $MANIFEST)) { "# tool_id|status|verify_path|ts" | Out-File $MANIFEST -Encoding ASCII }
}
function Manifest-Check {
  param([string]$Id, [string]$VerifyPath)
  if (-not (Test-Path $VerifyPath)) { return $false }
  $line = Select-String "^${Id}\|ok\|" $MANIFEST -SimpleMatch -Quiet 2>$null
  return ($line -ne $null)
}
function Manifest-Mark {
  param([string]$Id, [string]$Status, [string]$VerifyPath)
  $ts = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
  $content = Get-Content $MANIFEST -Raw
  if ($content -match "(?m)^${Id}\|") {
    $content = $content -replace "(?m)^${Id}\|.*$", "${Id}|${Status}|${VerifyPath}|${ts}"
  } else {
    $content += "${Id}|${Status}|${VerifyPath}|${ts}`n"
  }
  $content | Out-File $MANIFEST -Encoding ASCII
}
function Manifest-Clear {
  param([string]$Id)
  $content = Get-Content $MANIFEST -Raw
  $content = $content -replace "(?m)^${Id}\|.*`n", ""
  $content | Out-File $MANIFEST -Encoding ASCII
}
function Manifest-Count {
  $ok = 0; $fail = 0
  Get-Content $MANIFEST | ForEach-Object {
    if ($_ -match "^(?!\#)([^|]+)\|(ok|fail)\|") {
      if ($matches[2] -eq "ok") { $ok++ } else { $fail++ }
    }
  }
  return $ok, $fail
}
function Check-Skip {
  param([string]$Id, [string]$VerifyPath, [string]$Label)
  if (Manifest-Check $Id $VerifyPath) { Write-Info "$Label 已完成（清单记录）"; return $true }
  if (Test-Path $VerifyPath) { Write-Info "$Label 已存在（补记清单）"; Manifest-Mark $Id "ok" $VerifyPath; return $true }
  return $false
}

# ── -Force 清理 ──
if ($Force) {
  Write-Host ""
  Write-Host "  --force 模式: 清除已有工具缓存" -ForegroundColor Yellow
  @(
    "$REPO\tools\crack-intergration-tools\execable\apktool.jar",
    "$ENV_DIR\jadx",
    "$SDK_DIR\build-tools",
    "$SDK_DIR\platform-tools",
    "$SDK_DIR\platforms",
    "$ENV_DIR\jdk",
    "$SDK_DIR\cmdline-tools",
    $MANIFEST
  ) | ForEach-Object {
    if (Test-Path $_) {
      Remove-Item $_ -Recurse -Force -ErrorAction SilentlyContinue
      Write-Host "  ✘  清除 $(Split-Path $_ -Leaf)" -ForegroundColor Red
    }
  }
  Write-Host ""
}

$StartTime = Get-Date

# ── 颜色（PowerShell 5+ 原生 ConsoleColor） ──
function Write-Info  { Write-Host "  ℹ " -NoNewline -ForegroundColor Blue;  Write-Host " $args" }
function Write-Ok    { Write-Host "  ✔ " -NoNewline -ForegroundColor Green; Write-Host " $args" }
function Write-Warn  { Write-Host "  ⚠ " -NoNewline -ForegroundColor Yellow; Write-Host " $args" }
function Write-Fail  { Write-Host "  ✘ " -NoNewline -ForegroundColor Red;   Write-Host " $args" }
function Write-Sep   { Write-Host "  ── $args ──" -ForegroundColor Cyan }

function Write-Header {
  param([string]$Text)
  $w = 52
  Write-Host ""
  Write-Host ("┌─" + ("─" * $w) + "─┐") -ForegroundColor Cyan
  Write-Host ("│  " + $Text.PadRight($w) + " │") -ForegroundColor Cyan
  Write-Host ("└─" + ("─" * $w) + "─┘") -ForegroundColor Cyan
}

function Format-Size {
  param([long]$Bytes)
  if ($Bytes -ge 1GB) { return "{0:N1} GB" -f ($Bytes / 1GB) }
  if ($Bytes -ge 1MB) { return "{0:N1} MB" -f ($Bytes / 1MB) }
  if ($Bytes -ge 1KB) { return "{0:N1} KB" -f ($Bytes / 1KB) }
  return "$Bytes B"
}

function Format-Duration {
  param([int]$Seconds)
  if ($Seconds -ge 3600) { return "{0}h{1}m" -f ($Seconds/3600), (($Seconds%3600)/60) }
  if ($Seconds -ge 60)   { return "{0}m{1}s" -f ($Seconds/60), ($Seconds%60) }
  return "${Seconds}s"
}

# ── 带进度条下载 ──
function Download-File {
  param([string]$Url, [string]$OutFile, [string]$Label)
  if ((Test-Path $OutFile) -and ((Get-Item $OutFile).Length -gt 0) -and -not $Force) {
    $sz = (Get-Item $OutFile).Length
    Write-Info "$Label 已存在 ($(Format-Size $sz))"
    return $true
  }
  Write-Sep "下载 $Label"
  try {
    $wc = New-Object System.Net.WebClient
    $wc.DownloadFileAsync($Url, $OutFile)
    # 等待下载并显示文件名
    while ($wc.IsBusy) {
      Start-Sleep -Milliseconds 200
      if (Test-Path $OutFile) {
        $sz = (Get-Item $OutFile).Length
        Write-Progress -Activity "下载 $Label" -Status "$(Format-Size $sz)" -PercentComplete -1
      }
    }
    Write-Progress -Activity "下载 $Label" -Completed
    $sz = (Get-Item $OutFile).Length
    Write-Ok "$Label → $(Format-Size $sz)"
    return $true
  } catch {
    Write-Fail "$Label 下载失败: $_"
    return $false
  }
}

# ── 解压 .zip ──
function Extract-Zip {
  param([string]$Archive, [string]$DestDir, [string]$Label)
  Write-Sep "解压 $Label"
  try {
    Expand-Archive -Path $Archive -DestinationPath $DestDir -Force
    Write-Ok "$Label 解压完成"
  } catch {
    Write-Fail "$Label 解压失败: $_"
  }
}

# ══════════════════════════════════
#  依赖检查
# ══════════════════════════════════
$missing = @()
if (-not (Get-Command python3 -ErrorAction SilentlyContinue) -and
    -not (Get-Command python -ErrorAction SilentlyContinue)) {
  $missing += "python3（请安装 Python 3）"
}
if ($missing.Count -gt 0) {
  Write-Fail "缺少: $($missing -join ', ')"
  exit 1
}

# 确定 Python 路径
$PY = if (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { "python" }

Clear-Host
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║   Android 逆向工具链 · 本地一键安装    ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host "  工作区: $REPO"
Write-Host ""

New-Item -ItemType Directory -Force -Path $TOOLS_BIN, $SDK_DIR, $JDK_DIR | Out-Null
Manifest-Init

# ══════════════════════════════════
#  1/6  JDK
# ══════════════════════════════════
Write-Header "1/6  Eclipse Temurin JDK 21"
$JDK_JAVA = "$JDK_DIR\jdk-21\bin\java.exe"
if (Check-Skip "jdk" $JDK_JAVA "JDK 21") {
  # 设置已有 JDK 的环境变量
  if (Test-Path $JDK_JAVA) {
    $env:JAVA_HOME = "$JDK_DIR\jdk-21"
    $env:Path = "$JDK_DIR\jdk-21\bin;$env:Path"
  }
} else {
  # 也检查其他版本目录
  $foundJdk = $false
  Get-ChildItem $JDK_DIR -Directory | ForEach-Object {
    $javaExe = Join-Path $_.FullName "bin\java.exe"
    if (Test-Path $javaExe) {
      Write-Info "本地 JDK 已就绪 → $($_.Name)"
      $foundJdk = $true
      Manifest-Mark "jdk" "ok" $javaExe
      $env:JAVA_HOME = $_.FullName
      $env:Path = "$($_.FullName)\bin;$env:Path"
    }
  }

  if (-not $foundJdk) {
    $t0 = Get-Date
    $jd = Download-File `
      -Url "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse" `
      -OutFile "$env:TEMP\jdk.zip" `
      -Label "Temurin JDK 21 (windows/x64)"
    if ($jd) {
      Extract-Zip -Archive "$env:TEMP\jdk.zip" -DestDir $JDK_DIR -Label "JDK 21"

      Get-ChildItem $JDK_DIR -Directory | ForEach-Object {
        $javaExe = Join-Path $_.FullName "bin\java.exe"
        if (Test-Path $javaExe -and $_.Name -ne "jdk-21") {
          $target = Join-Path $JDK_DIR "jdk-21"
          if (Test-Path $target) { Remove-Item $target -Recurse -Force }
          Rename-Item $_.FullName $target
        }
      }
      Remove-Item "$env:TEMP\jdk.zip" -Force -ErrorAction SilentlyContinue

      if (Test-Path $JDK_JAVA) {
        Manifest-Mark "jdk" "ok" $JDK_JAVA
        $elapsed = [int]((Get-Date) - $t0).TotalSeconds
        Write-Ok "JDK 21 ($(Format-Duration $elapsed))"
        $env:JAVA_HOME = "$JDK_DIR\jdk-21"
        $env:Path = "$JDK_DIR\jdk-21\bin;$env:Path"
      } else {
        Manifest-Mark "jdk" "fail" $JDK_JAVA
        Write-Fail "JDK 安装失败"
      }
    }
  }
}

# ══════════════════════════════════
#  2/6  apktool
# ══════════════════════════════════
Write-Header "2/6  apktool"
$apkPath = "$REPO\tools\crack-intergration-tools\execable\apktool.jar"
if (-not (Check-Skip "apktool" $apkPath "apktool")) {
  if (Download-File -Url "https://github.com/iBotPeaches/Apktool/releases/download/v2.11.1/apktool_2.11.1.jar" -OutFile $apkPath -Label "apktool_2.11.1.jar") {
    Manifest-Mark "apktool" "ok" $apkPath
  } else { Manifest-Mark "apktool" "fail" $apkPath }
}

# ══════════════════════════════════
#  3/6  jadx 反编译器
# ══════════════════════════════════
Write-Header "3/6  jadx 反编译器"
$JADX_DIR = Join-Path $ENV_DIR "jadx"
$JADX_BAT = "$JADX_DIR\bin\jadx.bat"
if (Check-Skip "jadx" $JADX_BAT "jadx") {
  # 已存在
} else {
  $t0 = Get-Date
  New-Item -ItemType Directory -Force -Path $JADX_DIR | Out-Null
  $ok = Download-File `
    -Url "https://github.com/skylot/jadx/releases/download/v1.5.1/jadx-1.5.1.zip" `
    -OutFile "$env:TEMP\jadx.zip" `
    -Label "jadx-1.5.1.zip"
  if ($ok) {
    Extract-Zip -Archive "$env:TEMP\jadx.zip" -DestDir $JADX_DIR -Label "jadx"
    Remove-Item "$env:TEMP\jadx.zip" -Force -ErrorAction SilentlyContinue
    if (Test-Path $JADX_BAT) {
      Manifest-Mark "jadx" "ok" $JADX_BAT
      $elapsed = [int]((Get-Date) - $t0).TotalSeconds
      Write-Ok "jadx ($(Format-Duration $elapsed))"
    } else {
      Manifest-Mark "jadx" "fail" $JADX_BAT
    }
  }
}
}

# ══════════════════════════════════
#  4/6  Android SDK cmdline-tools
# ══════════════════════════════════
Write-Header "4/6  Android SDK 命令行工具"
$CLT_DIR = Join-Path $SDK_DIR "cmdline-tools\latest"
$SDKMGR = "$CLT_DIR\bin\sdkmanager.bat"
if (Check-Skip "cmdline-tools" $SDKMGR "cmdline-tools") {
  # 已存在
} else {
  $t0 = Get-Date
  New-Item -ItemType Directory -Force -Path "$SDK_DIR\cmdline-tools" | Out-Null
  $ok = Download-File `
    -Url "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" `
    -OutFile "$env:TEMP\cmdline-tools.zip" `
    -Label "cmdline-tools.zip"
  if ($ok) {
    Extract-Zip -Archive "$env:TEMP\cmdline-tools.zip" -DestDir "$SDK_DIR\cmdline-tools" -Label "cmdline-tools"

    # 整理为 cmdline-tools/latest/ 结构
    $inner = Join-Path $SDK_DIR "cmdline-tools\cmdline-tools"
    if (Test-Path $inner) {
      New-Item -ItemType Directory -Force -Path "$SDK_DIR\cmdline-tools\latest" | Out-Null
      Get-ChildItem $inner | Move-Item -Destination "$SDK_DIR\cmdline-tools\latest\" -Force
      Remove-Item $inner -Recurse -Force
    }

    Remove-Item "$env:TEMP\cmdline-tools.zip" -Force -ErrorAction SilentlyContinue

    if (Test-Path $SDKMGR) {
      Manifest-Mark "cmdline-tools" "ok" $SDKMGR
      $elapsed = [int]((Get-Date) - $t0).TotalSeconds
      Write-Ok "cmdline-tools ($(Format-Duration $elapsed))"
    } else {
      Manifest-Mark "cmdline-tools" "fail" $SDKMGR
    }
  }
}

# ══════════════════════════════════
#  5/6  SDK 组件
# ══════════════════════════════════
Write-Header "5/6  Android SDK 组件（耗时较长）"
$env:ANDROID_HOME = $SDK_DIR

$components = @(
  @{ Id = "sdk-build-tools-35"; Name = "build-tools;35.0.0"; Path = "$SDK_DIR\build-tools\35.0.0" }
  @{ Id = "sdk-platform-tools"; Name = "platform-tools";     Path = "$SDK_DIR\platform-tools" }
  @{ Id = "sdk-platform-35";    Name = "platforms;android-35"; Path = "$SDK_DIR\platforms\android-35" }
)

$needInstall = @()
foreach ($comp in $components) {
  if (Check-Skip $comp.Id $comp.Path $comp.Name) {
    # 已安装
  } elseif ((Test-Path $comp.Path) -and ((Get-ChildItem $comp.Path).Count -gt 0)) {
    Manifest-Mark $comp.Id "ok" $comp.Path
    Write-Info "$($comp.Name) 已安装（补记清单）"
  } else {
    $needInstall += $comp.Name
  }
}

if ($needInstall.Count -eq 0) {
  Write-Info "全部 SDK 组件已就绪"
} else {
  Write-Info "需要安装: $($needInstall -join ', ')"
  Write-Sep "sdkmanager 开始下载（网络慢可能需数分钟）"

  $sdkmanager = Join-Path $CLT_DIR "bin\sdkmanager.bat"
  if (Test-Path $sdkmanager) {
    $sdkmanagerDir = Split-Path (Split-Path $sdkmanager) -Parent

    # 用本地 JDK 的 java 运行 sdkmanager
    $javaExe = if ($env:JAVA_HOME) { "$env:JAVA_HOME\bin\java.exe" } else { "java.exe" }

    # sdkmanager 接受 license
    $needInstall | ForEach-Object {
      Write-Host "    $_"
    }

    # 管道 yes 给 sdkmanager
    $yesString = "y`r`n" * 10
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $javaExe
    $psi.Arguments = "-jar `"$sdkmanagerDir\lib\sdkmanager-2.0.0.jar`" --sdkRoot=`"$SDK_DIR`" $($needInstall -join ' ')"
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $p = [System.Diagnostics.Process]::Start($psi)
    $p.StandardInput.Write($yesString)
    $p.StandardInput.Close()
    $out = $p.StandardOutput.ReadToEnd()
    $err = $p.StandardError.ReadToEnd()
    $p.WaitForExit()

    if ($out) { Write-Host $out -ForegroundColor Yellow }
    if ($err) { Write-Host $err -ForegroundColor DarkYellow }

    foreach ($comp in $components) {
      if ((Test-Path $comp.Path) -and ((Get-ChildItem $comp.Path).Count -gt 0)) {
        Manifest-Mark $comp.Id "ok" $comp.Path
        Write-Ok "$($comp.Name) 安装完成"
      } else {
        Manifest-Mark $comp.Id "fail" $comp.Path
        Write-Fail "$($comp.Name) 安装失败"
      }
    }
  } else {
    Write-Fail "sdkmanager.bat 不存在于 $sdkmanager"
    Write-Warn "可手动下载 Android Studio 或在项目外安装 SDK"
  }
}

# ══════════════════════════════════
#  6/6  frida
# ══════════════════════════════════
Write-Header "6/6  frida 动态插桩"
$fridaPath = (Get-Command frida -ErrorAction SilentlyContinue).Source
if (Check-Skip "frida" $fridaPath "frida") {
  # 已安装
} else {
  $fridaVersion = & frida --version 2>$null
  if ($LASTEXITCODE -eq 0) {
    Manifest-Mark "frida" "ok" (Get-Command frida).Source
    Write-Ok "frida v$fridaVersion 已安装"
  } else {
    Write-Sep "pip install frida-tools"
    try {
      & $PY -m pip install frida-tools 2>&1 | ForEach-Object {
        if ($_ -match "Downloading") { Write-Host "  ⏬  $_" }
        elseif ($_ -match "Successfully") { Write-Host "  ✅  $_" -ForegroundColor Green }
      }
      $ver = & frida --version 2>$null
      $fp = (Get-Command frida -ErrorAction SilentlyContinue).Source
      if ($LASTEXITCODE -eq 0) {
        Manifest-Mark "frida" "ok" $fp
        Write-Ok "frida v$ver"
      } else {
        Manifest-Mark "frida" "fail" ""
        Write-Warn "frida 安装失败，可手动: pip install frida-tools"
      }
    } catch {
      Manifest-Mark "frida" "fail" ""
      Write-Warn "pip install 失败: $_"
    }
  }
}

# ══════════════════════════════════
#  验证
# ══════════════════════════════════
Write-Header "验证所有工具"

# 清单统计
$okCount, $failCount = Manifest-Count
Write-Host ""
Write-Host "  下载清单: $MANIFEST" -ForegroundColor Cyan
Write-Host ("  状态: " + $okCount + " 完成") -NoNewline -ForegroundColor Green
if ($failCount -gt 0) { Write-Host ("  " + $failCount + " 失败") -NoNewline -ForegroundColor Red }
Write-Host ""
Write-Host ""

$errors = 0
$tools = @("java", "keytool", "apktool", "jadx", "aapt2", "apksigner", "zipalign", "adb", "frida")
# 在 Windows 上，aapt2/apksigner/zipalign/adb 在 build-tools/platform-tools 目录下
# 它们可能不在 PATH 中，但 env.sh 会处理
foreach ($name in $tools) {
  $path = Get-Command $name -ErrorAction SilentlyContinue
  if ($path) {
    Write-Host ("  " + $name.PadRight(12)) -NoNewline -ForegroundColor Green
    Write-Host " $($path.Source)"
  } else {
    # Windows 上可能没有 .exe 在 PATH 但文件存在
    $possible = @(
      "$SDK_DIR\build-tools\35.0.0\$name.exe",
      "$SDK_DIR\build-tools\35.0.0\$name",
      "$SDK_DIR\platform-tools\$name.exe",
      "$SDK_DIR\platform-tools\$name"
    )
    $found = $false
    foreach ($p in $possible) {
      if (Test-Path $p) { Write-Host ("  " + $name.PadRight(12)) -NoNewline -ForegroundColor Green; Write-Host " $p"; $found = $true; break }
    }
    if (-not $found) {
      Write-Host ("  " + $name.PadRight(12)) -NoNewline -ForegroundColor Red
      Write-Host " 未找到" -ForegroundColor Red
      $errors++
    }
  }
}

$elapsed = [int]((Get-Date) - $StartTime).TotalSeconds
Write-Host ""
Write-Host "════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "  总耗时: $(Format-Duration $elapsed)"
if ($errors -eq 0) { Write-Host "  全部就绪 ✓" -ForegroundColor Green }
else { Write-Host "  $errors 个工具未找到" -ForegroundColor Red }
Write-Host "════════════════════════════════════════" -ForegroundColor Magenta
Write-Host ""
Write-Host "  安装位置:"
Write-Host "    tools\environments\jdk\"
Write-Host "    tools\crack-intergration-tools\execable\apktool.jar"
Write-Host "    tools\environments\jadx\"
Write-Host "    tools\environments\android-sdk\"
Write-Host "    tools\environments\bin\  (wrapper 脚本)"
Write-Host ""
Write-Host "  使用:"
Write-Host "    bash tools\scripts\crack.sh apks\<你的APK>"
Write-Host "    （Windows 需在 Git Bash / WSL 下运行 crack.sh）"
