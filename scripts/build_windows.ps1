$ErrorActionPreference = "Stop"

# Корень проекта независимо от того, откуда запущен скрипт
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$Python = ".\.venv\Scripts\python.exe"
$FFmpegDir = ".\src\ymd_gui\resources\ffmpeg\windows"
$FFmpeg = Join-Path $FFmpegDir "ffmpeg.exe"
$Icon = ".\src\ymd_gui\resources\icons\app.ico"

$BuildRoot = ".\build\windows"
$ReleaseRoot = ".\dist"


# ------------------------------------------------------------
# Проверки
# ------------------------------------------------------------

if (-not (Test-Path $Python)) {
    throw "Не найден Python виртуального окружения: $Python"
}

if (-not (Test-Path $FFmpeg)) {
    throw "Не найден bundled FFmpeg: $FFmpeg"
}

if (-not (Test-Path $Icon)) {
    throw "Не найдена иконка приложения: $Icon"
}


# ------------------------------------------------------------
# Версия
# ------------------------------------------------------------

$Version = (
    & $Python -c "from ymd_gui import __version__; print(__version__)"
).Trim()

if (-not $Version) {
    throw "Не удалось определить версию приложения"
}

# Windows resource version требует 4 числовых компонента
$WindowsVersion = "$Version.0"

$PortableName = "YandexMusicDownloader-$Version-Windows-x64"
$PortableDir = Join-Path $ReleaseRoot $PortableName
$ZipPath = Join-Path $ReleaseRoot "$PortableName.zip"


Write-Host ""
Write-Host "============================================"
Write-Host " Yandex Music Downloader $Version"
Write-Host " Windows x64 portable build"
Write-Host "============================================"
Write-Host ""


# ------------------------------------------------------------
# Очистка старой сборки
# ------------------------------------------------------------

if (Test-Path $BuildRoot) {
    Write-Host "Cleaning old Windows build..."
    Remove-Item $BuildRoot -Recurse -Force
}

New-Item `
    -ItemType Directory `
    -Force `
    -Path $BuildRoot |
    Out-Null


# ------------------------------------------------------------
# Nuitka
# ------------------------------------------------------------

Write-Host "Building standalone application..."

$NuitkaArgs = @(
    "--mode=standalone"
    "--plugin-enable=pyside6"
    "--windows-console-mode=disable"

    "--windows-icon-from-ico=$Icon"

    "--output-dir=$BuildRoot"
    "--output-filename=YandexMusicDownloader.exe"

    "--product-name=Yandex Music Downloader"
    "--file-description=Yandex Music Downloader"
    "--product-version=$WindowsVersion"
    "--file-version=$WindowsVersion"

    ".\src\ymd_gui\main.py"
)

& $Python -m nuitka @NuitkaArgs

if ($LASTEXITCODE -ne 0) {
    throw "Nuitka build failed with exit code $LASTEXITCODE"
}


# ------------------------------------------------------------
# Находим *.dist
# ------------------------------------------------------------

$Dist = Get-ChildItem `
    $BuildRoot `
    -Directory `
    -Filter "*.dist" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($null -eq $Dist) {
    throw "Не найдена Nuitka .dist директория"
}

$Executable = Join-Path `
    $Dist.FullName `
    "YandexMusicDownloader.exe"

if (-not (Test-Path $Executable)) {
    throw "Не найден YandexMusicDownloader.exe в .dist"
}


# ------------------------------------------------------------
# Bundled FFmpeg
# ------------------------------------------------------------

Write-Host "Adding bundled FFmpeg..."

$FFmpegTarget = Join-Path `
    $Dist.FullName `
    "resources\ffmpeg\windows"

New-Item `
    -ItemType Directory `
    -Force `
    -Path $FFmpegTarget |
    Out-Null

Copy-Item `
    $FFmpeg `
    (Join-Path $FFmpegTarget "ffmpeg.exe") `
    -Force

Get-ChildItem `
    $FFmpegDir `
    -Filter "*.dll" |
    Copy-Item `
        -Destination $FFmpegTarget `
        -Force


# ------------------------------------------------------------
# Portable directory
# ------------------------------------------------------------

Write-Host "Creating portable directory..."

New-Item `
    -ItemType Directory `
    -Force `
    -Path $ReleaseRoot |
    Out-Null

if (Test-Path $PortableDir) {
    Remove-Item `
        $PortableDir `
        -Recurse `
        -Force
}

New-Item `
    -ItemType Directory `
    -Force `
    -Path $PortableDir |
    Out-Null

Copy-Item `
    (Join-Path $Dist.FullName "*") `
    $PortableDir `
    -Recurse `
    -Force


# ------------------------------------------------------------
# Release documentation
# ------------------------------------------------------------

Write-Host "Adding release documentation..."

$PackagingRoot = ".\packaging\windows"

$ReadmeTemplate = Join-Path `
    $PackagingRoot `
    "README.txt"

$ThirdPartyNotices = Join-Path `
    $PackagingRoot `
    "THIRD_PARTY_NOTICES.txt"

$ThirdPartyLicenses = Join-Path `
    $PackagingRoot `
    "THIRD_PARTY_LICENSES.txt"

if (-not (Test-Path $ReadmeTemplate)) {
    throw "Не найден release README.txt"
}

if (-not (Test-Path $ThirdPartyNotices)) {
    throw "Не найден THIRD_PARTY_NOTICES.txt"
}

if (-not (Test-Path $ThirdPartyLicenses)) {
    throw "Не найден THIRD_PARTY_LICENSES.txt"
}


# Подставляем текущую версию
$ReadmeContent = Get-Content `
    $ReadmeTemplate `
    -Raw `
    -Encoding UTF8

$ReadmeContent = $ReadmeContent.Replace(
    "@VERSION@",
    $Version
)

Set-Content `
    (Join-Path $PortableDir "README.txt") `
    $ReadmeContent `
    -Encoding UTF8


Copy-Item `
    ".\LICENSE" `
    (Join-Path $PortableDir "LICENSE") `
    -Force


Copy-Item `
    $ThirdPartyLicenses `
    (Join-Path $PortableDir "THIRD_PARTY_LICENSES.txt") `
    -Force


Copy-Item `
    $ThirdPartyNotices `
    (Join-Path $PortableDir "THIRD_PARTY_NOTICES.txt") `
    -Force


# ------------------------------------------------------------
# Portable ZIP
# ------------------------------------------------------------

Write-Host "Creating ZIP archive..."

if (Test-Path $ZipPath) {
    Remove-Item `
        $ZipPath `
        -Force
}

Compress-Archive `
    -Path $PortableDir `
    -DestinationPath $ZipPath `
    -CompressionLevel Optimal


# ------------------------------------------------------------
# Результат
# ------------------------------------------------------------

$ZipInfo = Get-Item $ZipPath
$ZipSizeMB = [math]::Round(
    $ZipInfo.Length / 1MB,
    1
)

Write-Host ""
Write-Host "============================================"
Write-Host " BUILD COMPLETE"
Write-Host "============================================"
Write-Host ""
Write-Host "Portable directory:"
Write-Host $PortableDir
Write-Host ""
Write-Host "Portable ZIP:"
Write-Host $ZipPath
Write-Host ""
Write-Host "ZIP size: $ZipSizeMB MB"
Write-Host ""
