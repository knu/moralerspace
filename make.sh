#!/usr/bin/env bash

set -euo pipefail

# スクリプトファイルがある場所に移動する
cd "$(dirname "$0")"

# 並列ビルドの前に、固定したバージョンの合成元を取得する
python3 font_sources.py

# ini から VERSION を取得
version=$(python3 -c 'import configparser; config = configparser.ConfigParser(); config.read("build.ini"); print(config["DEFAULT"]["VERSION"])')

font_name=$(python3 -c 'import configparser; config = configparser.ConfigParser(); config.read("build.ini"); print(config["DEFAULT"]["FONT_NAME"])')

# 各ファイルを置くフォルダを作成
mkdir -p "./release_files/"

# ビルドフォルダを削除
rm -rf ./build

# 並列処理
option=(
  ""
  "--half-width"
  "--jpdoc"
  "--half-width --jpdoc"
  "--nerd-font-mono"
  "--half-width --nerd-font-mono"
  "--jpdoc --nerd-font-mono"
  "--half-width --jpdoc --nerd-font-mono"
)
output_folder=(
  "-"
  "HW-"
  "JPDOC-"
  "HWJPDOC-"
  "NFM-"
  "HWNFM-"
  "JPDOCNFM-"
  "HWJPDOCNFM-"
)

# 配列を並列処理しやすい形式に変換
function run_build() {
  local -a build_options=()
  if [[ -n "$1" ]]; then
    read -r -a build_options <<<"$1"
  fi
  local output_prefix="$2"
  echo "fontforge script start. option: \"$1\""
  python3 ./fontforge_script.py --do-not-delete-build-dir "${build_options[@]}" &&
    echo "fonttools script start. option: \"$output_prefix\"" &&
    python3 fonttools_script.py "$output_prefix"
}
export -f run_build

# parallelコマンドで並列実行
parallel -j 4 --halt soon,fail=1 --link run_build ::: "${option[@]}" ::: "${output_folder[@]}"

# ファイル移動
timestamp=$(date +%Y%m%d%H%M%S)
move_dir="./release_files/build_$timestamp"

for variant in "" HW JPDOC HWJPDOC NFM HWNFM JPDOCNFM HWJPDOCNFM; do
  folder_path="$move_dir/${font_name}${variant}_$version"
  mkdir -p "$folder_path"
  for family in Neon Argon Xenon Radon Krypton; do
    for style in Regular Bold Italic BoldItalic; do
      mv "./build/${font_name}${family}${variant}-${style}.ttf" "$folder_path/"
    done
  done
done

cp source_fonts/versions.ini "$move_dir/source-versions.ini"

echo "Finish build."
