# Moralerspace Community Edition

Moralerspace は、欧文フォント [Monaspace](https://github.com/githubnext/monaspace) と日本語フォント [IBM Plex Sans JP](https://github.com/IBM/plex) などを合成したプログラミング向けフォントです。

このリポジトリは[yuru7/moralerspace](https://github.com/yuru7/moralerspace)のCommunity Editionです。フォントの表示名は引き続き`Moralerspace`です。v3.0.0での変更は[CHANGELOG.md](CHANGELOG.md)を参照してください。

```
  ∧＿＿∧
 (  ・∀・) マターリしようよ
 (       )
 ｜  ｜  ｜
 (＿＿)＿_)
```

## インストール

### Homebrew

[knu/knu](https://github.com/knu/homebrew-knu)のcaskからインストールできます。例えば、半角1:全角2幅のHW版は次のとおりです。

```sh
brew tap knu/knu
brew install --cask knu/knu/font-moralerspace-ce-hw
```

以下のcask名に`knu/knu/`を付けて指定してください。各caskには5書体×4スタイルの20本が含まれます。

| 種類 | 無印 | NFM版 |
| --- | --- | --- |
| 通常幅 (半角3:全角5) | `font-moralerspace-ce` | `font-moralerspace-ce-nfm` |
| HW (半角1:全角2) | `font-moralerspace-ce-hw` | `font-moralerspace-ce-hw-nfm` |
| JPDOC | `font-moralerspace-ce-jpdoc` | `font-moralerspace-ce-jpdoc-nfm` |
| HW JPDOC | `font-moralerspace-ce-hw-jpdoc` | `font-moralerspace-ce-hw-jpdoc-nfm` |

従来の公式caskから移行する場合は、対応する旧caskを先にアンインストールしてください。無印版は内部のフォント名が同じため、同じ種類の公式版とは共存できません。例えばHW版の移行は次のとおりです。

```sh
brew uninstall --cask font-moralerspace-hw
brew install --cask knu/knu/font-moralerspace-ce-hw
```

### ZIPからインストール

[リリースページ](https://github.com/knu/moralerspace/releases/latest)のAssetsから、使用するバリエーションのZIPをダウンロードしてください。展開したTTFファイルを各OSの方法でインストールします。例えばHW版は`MoralerspaceHW_v3.0.0.zip`、HW NFM版は`MoralerspaceHWNFM_v3.0.0.zip`です。

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

合成元のバージョンはMonaspace NF v1.400、IBM Plex Sans JP 3.0.0、源ノ明朝JP 2.003、Symbols Nerd Font 3.5.1です。

![v3.0.0のNeon、Argon、Xenon、Radon、Kryptonの欧文・日本語サンプル](https://github.com/user-attachments/assets/2764e589-7de3-4e90-b0d0-d7dd38467d66)

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

下図はArgonの通常アイコンの比較です。青い枠が1文字分、右の灰色の枠が隣のセルです。どちらも送り幅は1セルですが、無印の輪郭は隣のセルにはみ出す場合があります。

![Argonの無印とNFM版のNerd Fontアイコンを1セルの枠で比較](https://github.com/user-attachments/assets/b23c41ab-a75f-4bb5-87c7-64e2daaf6b8d)

## ビルド

ビルドに使用するツール、ランタイム

- fontforge: `20230101` \[[Windows](https://fontforge.org/en-US/downloads/windows/)\] \[[Linux](https://fontforge.org/en-US/downloads/gnulinux/)\]
- Python: `>=3.8`

Dockerのビルド環境はUbuntu 26.04、FontForge 20230101、Python 3.14です。

合成元の取得バージョンは[source_fonts/versions.ini](source_fonts/versions.ini)で固定しています。ビルド時に`font_sources.py`が指定タグ/コミットの公式フォントとライセンスを取得し、Kiwi Maru/Stickの太字とKiwi Maruのヒント除去版を生成します。取得物と生成済みの合成元は`build_sources/`にキャッシュされ、同じ入力のビルドでは再利用されます。初回はネットワーク接続が必要です。

Renovateはこのファイルの更新PRを作成します。PRのバージョン変更は次のビルドに反映されるため、ビルド・回帰チェック・描画確認と、上記の合成元バージョン表記の更新を済ませてからマージしてください。Gitに含まれる従来の合成元TTF/OTFはビルドに使用しません。

### Windows (PowerShell 7以降)

```powershell
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
docker run --rm -v "$PWD:/workspace" font/moralerspace:latest
```

ビルドスクリプトは無印80本とNFM版80本を生成します。FontForgeスクリプト単体でNFM版を生成する場合は`--nerd-font-mono`を指定してください。

生成フォントの回帰チェックは、fontToolsとHarfBuzz CLI (`hb-shape`) がある環境で実行できます。出力先の `build_<日時>` を指定してください。

```sh
python3 tests/test_generated_fonts.py release_files/build_YYYYMMDDhhmmss
```

PRではPythonの単体テスト・lint・構文・設定チェックを実行します。フォントの版や合成処理に関係する変更では、Argon Regularの通常/HW×無印/NFMとXenon Regular、Radon Bold、Krypton Boldの計7本をビルドし、同じ回帰チェックを実行します。全160本のビルドはリリースタグ時と、Fontsワークフローを手動実行して`full`を選んだ場合に実行します。合成元とDockerビルドのキャッシュはCIで再利用します。

代表ビルドをローカルで実行する場合は、ビルド環境内で次を実行してください。出力先の`build/smoke`は空の状態で開始します。

```sh
python3 scripts/build_smoke_fonts.py
python3 tests/test_generated_fonts.py build/smoke --smoke
```

### README画像の再生成

画像は[scripts/generate_readme_images.py](scripts/generate_readme_images.py)で生成します。Python 3.11以上と、RAQMに対応したPillowが必要です。仮想環境に画像生成用の依存パッケージを入れ、ビルド済みフォントの出力先を指定してください。リリースの通常版とNFM版のZIPを、同じディレクトリ配下に展開したものも使用できます。

```sh
python3 -m venv .venv-images
.venv-images/bin/python3 -m pip install -r requirements-images.txt
.venv-images/bin/python3 scripts/generate_readme_images.py release_files/build_YYYYMMDDhhmmss
```

フォントをOSへインストールする必要はありません。スクリプトは`build.ini`のバージョンと入力フォントのバージョンを照合し、`assets/sample.png`と`assets/nerd-font-width.png`を更新します。異なるバージョンや同名フォントの重複がある場合は停止します。

生成したPNGはGitに含めません。[画像保管用issue](https://github.com/knu/moralerspace/issues/1)へ添付し、取得した画像URLにREADMEの参照先を更新してください。

## リリース

`build.ini`の`VERSION`を更新し、[CHANGELOG.md](CHANGELOG.md)に対応するバージョンの節を手で記録してcommitします。例えば`v3.0.0`タグには`## 3.0.0`の節が必要です。

バージョンタグをpushすると、GitHub ActionsがUbuntu 26.04のコンテナで全160本をビルドし、回帰チェック後に8種類のZIPをGitHub Releaseのassetsへ公開します。本文はCHANGELOGの該当節から切り出します。タグと`VERSION`が一致しない場合や、変更履歴がない場合は公開しません。

## ライセンス

SIL Open Font License, Version 1.1 が適用され、個人・商用問わず利用可能です。

ソースフォントのライセンスも同様に SIL Open Font License, Version 1.1 が適用されています。詳しくは `source_fonts` ディレクトリに含まれる LICENSE ファイルを参照してください。
