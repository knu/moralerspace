#!/usr/bin/env bash

set -euo pipefail

# スクリプトファイルがある場所に移動する
cd "$(dirname "$0")"

# ini から VERSION を取得
version=$(python3 -c 'import configparser; config = configparser.ConfigParser(); config.read("build.ini"); print(config["DEFAULT"]["VERSION"])')

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
)
output_folder=(
  "-"
  "HW-"
  "JPDOC-"
  "HWJPDOC-"
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
parallel -j -1 --halt soon,fail=1 --link run_build ::: "${option[@]}" ::: "${output_folder[@]}"

# ファイル移動
declare -A move_file_src_dest=(
  ["MoralerspaceNeon-*.ttf"]="Moralerspace_$version"
  ["MoralerspaceArgon-*.ttf"]="Moralerspace_$version"
  ["MoralerspaceXenon-*.ttf"]="Moralerspace_$version"
  ["MoralerspaceRadon-*.ttf"]="Moralerspace_$version"
  ["MoralerspaceKrypton-*.ttf"]="Moralerspace_$version"

  ["MoralerspaceNeonHW-*.ttf"]="MoralerspaceHW_$version"
  ["MoralerspaceArgonHW-*.ttf"]="MoralerspaceHW_$version"
  ["MoralerspaceXenonHW-*.ttf"]="MoralerspaceHW_$version"
  ["MoralerspaceRadonHW-*.ttf"]="MoralerspaceHW_$version"
  ["MoralerspaceKryptonHW-*.ttf"]="MoralerspaceHW_$version"

  ["MoralerspaceNeonJPDOC-*.ttf"]="MoralerspaceJPDOC_$version"
  ["MoralerspaceArgonJPDOC-*.ttf"]="MoralerspaceJPDOC_$version"
  ["MoralerspaceXenonJPDOC-*.ttf"]="MoralerspaceJPDOC_$version"
  ["MoralerspaceRadonJPDOC-*.ttf"]="MoralerspaceJPDOC_$version"
  ["MoralerspaceKryptonJPDOC-*.ttf"]="MoralerspaceJPDOC_$version"

  ["MoralerspaceNeonHWJPDOC-*.ttf"]="MoralerspaceHWJPDOC_$version"
  ["MoralerspaceArgonHWJPDOC-*.ttf"]="MoralerspaceHWJPDOC_$version"
  ["MoralerspaceXenonHWJPDOC-*.ttf"]="MoralerspaceHWJPDOC_$version"
  ["MoralerspaceRadonHWJPDOC-*.ttf"]="MoralerspaceHWJPDOC_$version"
  ["MoralerspaceKryptonHWJPDOC-*.ttf"]="MoralerspaceHWJPDOC_$version"
)

timestamp=$(date +%Y%m%d%H%M%S)
move_dir="./release_files/build_$timestamp"

for ttf in "${!move_file_src_dest[@]}"; do
  folder_path="$move_dir/${move_file_src_dest[$ttf]}"
  mkdir -p "$folder_path"
  find "./build/" -name "$ttf" -exec mv -t "$folder_path" {} \;
done

echo "Finish build."
