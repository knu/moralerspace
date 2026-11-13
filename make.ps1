# スクリプトファイルがある場所に移動する
Set-Location -Path $PSScriptRoot
$ErrorActionPreference = "Stop"
$settings = python -c 'import configparser, json; config = configparser.ConfigParser(); config.read("build.ini"); print(json.dumps(dict(config["DEFAULT"])))' | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw "Cannot read build.ini" }
$version = $settings.version
$font_name = $settings.font_name
# 各ファイルを置くフォルダを作成
New-Item -ItemType Directory -Force -Path ".\release_files\"
# ビルドフォルダを削除
Remove-Item -Path .\build -Recurse -Force

$option_and_output_folder = @(
    @("", "-"), # ビルド 通常版
    @("--half-width", "HW-"), # ビルド 1:2幅版
    @("--jpdoc", "JPDOC-"), # ビルド JPDOC版
    @("--half-width --jpdoc", "HWJPDOC-"), # ビルド 1:2幅 JPDOC版
    @("--nerd-font-mono", "NFM-"),
    @("--half-width --nerd-font-mono", "HWNFM-"),
    @("--jpdoc --nerd-font-mono", "JPDOCNFM-"),
    @("--half-width --jpdoc --nerd-font-mono", "HWJPDOCNFM-")
)

$option_and_output_folder | Foreach-Object -ThrottleLimit 4 -Parallel {
    Write-Host "fontforge script start. option: `"$($_[0])`""
    Invoke-Expression "& `"C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe`" .\fontforge_script.py --do-not-delete-build-dir $($_[0])" `
        && Write-Host "fonttools script start. option: `"$($_[1])`"" `
        && python fonttools_script.py $_[1]
}

$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$move_dir = ".\release_files\build_$timestamp"

$variants = @("", "HW", "JPDOC", "HWJPDOC", "NFM", "HWNFM", "JPDOCNFM", "HWJPDOCNFM")
foreach ($variant in $variants) {
    $folder_path = "$move_dir\${font_name}${variant}_$version"
    New-Item -ItemType Directory -Force -Path $folder_path
    foreach ($family in @("Neon", "Argon", "Xenon", "Radon", "Krypton")) {
        foreach ($style in @("Regular", "Bold", "Italic", "BoldItalic")) {
            Move-Item -Path ".\build\${font_name}${family}${variant}-${style}.ttf" -Destination $folder_path
        }
    }
}
