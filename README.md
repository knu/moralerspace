# Moralerspace

Moralerspace は、欧文フォント [Monaspace](https://github.com/githubnext/monaspace) と日本語フォント [IBM Plex Sans JP](https://github.com/IBM/plex) などを合成したプログラミング向けフォントです。

```
  ∧＿＿∧
 (  ・∀・) マターリしようよ
 (       )
 ｜  ｜  ｜
 (＿＿)＿_)
```

## インストール

リリースページよりzipファイルをダウンロードし、展開したttfファイルを各OSごとの方法でインストールしてください。

[🆕 **ダウンロードはこちら**](https://github.com/yuru7/moralerspace/releases/latest)

※「Assets」内の zip ファイルをダウンロードしてご利用ください。

> 💡 その他、公開中のプログラミングフォント
>
> - 日本語文字に源柔ゴシック、英数字部分に Hack を使った [**白源 (はくげん／HackGen)**](https://github.com/yuru7/HackGen)
> - 日本語文字に IBM Plex Sans JP、英数字部分に IBM Plex Mono を使った [**PlemolJP (プレモル ジェイピー)**](https://github.com/yuru7/PlemolJP)
> - 日本語文字にBIZ UDゴシック、英数字部分に JetBrains Mono を使った [**UDEV Gothic**](https://github.com/yuru7/udev-gothic)

## 特徴

以下のような特徴があります。

- Texture healing システムを搭載した、GitHub 製 [Monaspace](https://github.com/githubnext/monaspace) 由来の英数字
- 文字の懐が広く読みやすい IBM 製 [IBM Plex Sans JP](https://github.com/IBM/plex) 由来の日本語文字
  - Xenon系統には[源ノ明朝JP](https://github.com/adobe-fonts/source-han-serif)を使用
  - Radon 系統には [キウイ丸 (Kiwi-Maru)](https://github.com/Kiwi-KawagotoKajiru/Kiwi-Maru) をベースに、足りないグリフを IBM Plex Sans JP で補完
  - Krypton 系統には [Stick](https://github.com/fontworks-fonts/Stick) をベースに、足りないグリフを IBM Plex Sans JP で補完
- 罫線素片などの一部半角記号は、 [Hack](https://github.com/source-foundry/Hack) より追加合成
- Nerd Fontsを標準搭載。無印は2.0と同じSymbols Nerd Fontの大きなアイコンを使用し、1セル内に収めるNFM版も用意
- 文字幅比率が 半角3:全角5、ゆとりのある半角英数字
  - 半角1:全角2 幅のバリエーションもあり
- バグの原因になりがちな全角スペースが可視化される

合成元のバージョンはMonaspace NF v1.400、IBM Plex Sans JP 3.0.0、源ノ明朝JP 2.003、Symbols Nerd Font 3.4.0です。

![sample](https://github.com/yuru7/moralerspace/assets/13458509/21d90d22-0178-4c41-a28c-7b15b7b17ecf)

## バリエーション

| 種類                                                     | 説明                                                                                                                           | 命名パターン                 |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| 通常版 (半角3:全角5 幅)                                  | 半角5文字と全角3文字が同等の幅になっているバリエーション。半角英数字が合成元オリジナルのサイズで広く表示されるため読みやすい。 | `Moralerspace*-*.ttf`        |
| 半角1:全角2 幅                                           | 半角2文字と全角1文字が同等の幅になっているバリエーション。半角幅と全角幅を倍の幅で表示させたい方はこちら。                     | `Moralerspace*HW-*.ttf`      |
| 通常版 (半角3:全角5 幅) & 日本語文書で頻出する記号が全角 | 通常版に対し、日本語文書で頻出する記号類 ( `← ↓ ↑ → □ ■ …` など) を全角幅にしたバリエーション。                                | `Moralerspace*JPDOC-*.ttf`   |
| 半角1:全角2 幅 & 日本語文書で頻出する記号が全角          | 半角 1:2 幅版に対し、日本語文書で頻出する記号類 ( `← ↓ ↑ → □ ■ …` など) を全角幅にしたバリエーション。                         | `Moralerspace*HWJPDOC-*.ttf` |

罫線は通常版/HW版では半角幅、JPDOC/HWJPDOC版では全角幅です。ターミナルのEast Asian Ambiguous文字幅設定に合わせて選択してください。JPDOC版では `↔ ⇐ ∴ ∵ ∽ ≒ ≦ ≧` も全角幅になります。

各バリエーションに、無印とNFM版があります。どちらもNerd Fontsを含み、通常アイコンの送り幅は英数字1文字分です。

- 無印は互換性のため、2.0の通常アイコンのサイズ・配置を維持します。輪郭は1セルより広い場合があるため、ラベルなどを続ける場合はアイコンの後ろに空白を入れてください。セルからはみ出す部分の描画は端末によって異なります。
- NFM版は縦横比を保ち、通常アイコンを1セルの幅と行高に収めて中央寄せします。例えばファイル名は`MoralerspaceArgonHWNFM-Regular.ttf`、表示名は`Moralerspace Argon HW NFM`です。

Powerlineの区切り・半円は両版で共通のセル用配置です。NFMの有無で欧文・日本語・罫線の輪郭や字幅は変わりません。

## ビルド

ビルドに使用するツール、ランタイム

- fontforge: `20230101` \[[Windows](https://fontforge.org/en-US/downloads/windows/)\] \[[Linux](https://fontforge.org/en-US/downloads/gnulinux/)\]
- Python: `>=3.8`

### Windows (PowerShell)

```sh
# 必要パッケージのインストール
pip install -r requirements.txt
# FontForge付属Pythonにも同じ依存をインストール
& "C:\Program Files (x86)\FontForgeBuilds\bin\ffpython.exe" -m pip install -r requirements.txt
# ビルド
.\make.ps1
```

### Linux

```sh
docker build -t font/moralerspace .
docker run -it --rm -v $PWD:/workspace font/moralerspace:latest
```

ビルドスクリプトは無印80本とNFM版80本を生成します。FontForgeスクリプト単体でNFM版を生成する場合は`--nerd-font-mono`を指定してください。

生成フォントの回帰チェックは、fontToolsとHarfBuzz CLI (`hb-shape`) がある環境で実行できます。出力先の `build_<日時>` を指定してください。

```sh
python3 tests/test_generated_fonts.py release_files/build_YYYYMMDDhhmmss
```

## ライセンス

SIL Open Font License, Version 1.1 が適用され、個人・商用問わず利用可能です。

ソースフォントのライセンスも同様に SIL Open Font License, Version 1.1 が適用されています。詳しくは `source_fonts` ディレクトリに含まれる LICENSE ファイルを参照してください。
