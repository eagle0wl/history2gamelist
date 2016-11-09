## はじめに
MAMEの各種データベースからEmulationStationの `gamelist.xml` を生成して、リストにあるROMイメージだけをまとめます。  
アーケードエミュレータは複数ありますが、Wikiで推奨されている  
* `lr-mame2003`
* `lr-fba-next`
* `mame4all`

に対応しています。Wikiによると、RPi2or3では `lr-mame2003` か `lr-fba-next` 、RPi0or1では `mame4all` を使うことが推奨されています。  
しかし、**私はRPiのバージョンによらず `mame4all` を使うべきであると考えます。**理由は後述。  

## 用意するもの
### 0) 十分なHDD容量  
このスクリプトと同じディレクトリに、対応するROMイメージ群と画像（スクショ）のコピーを作ります。2)のROMイメージ群と3)の画像群から必要なぶんだけをコピーするので、必要な容量は予測できると思いますが、2GBもあれば十分だと思います。  

### 1) gamelist.xml作成に必要なファイル  
このスクリプトと同じディレクトリに以下のファイルを置いてください。一つでも欠けていると動作しません。  
`history.dat`  
`mameinfo.dat`  
`mame_jp.lst`  
`lr-mame2003.tsv`  
`lr-fba-next.tsv`  
`Mame4all.tsv`  

上記ファイルの入手先は以下の通り。  
・history.dat+(v0.178) UTF-8版  
history.dat  
http://www.e2j.net/downloads.html  

・mameinfo.dat UTF-8版  
mameinfo.dat  
http://www.e2j.net/downloads.html  

・mame_jp.lst  
MAME32 Plus! 0.146r5027用 Japanese Game List  
http://www.geocities.jp/mamelistjp/  
※文字コードはShift-JISのままにしてください。  

・RPi動作チェック済のスプレッドシート(Compatibility List)  
https://github.com/RetroPie/RetroPie-Setup/wiki/Managing-ROMs  
RPi動作確認済みタイトルの抽出とROMの親子関係の確認に使います。  
下記３種類のCompatibility Listのスプレッドシートを保存してください。  
ファイル → 形式を指定してダウンロード → タブ区切りの値(.tsv、現在のシート)

ファイル名は以下の通りにリネームしてください。  
`lr-mame2003 → lr-mame2003.tsv`  
`lr-fba-next → lr-fba-next.tsv`  
`mame4all    → Mame4all.tsv`  

### 2) 以下の.DATを使ってclrmameproなどでリビルドしたROMイメージを収めたフォルダ  
DATファイルは以下参照  
https://github.com/RetroPie/RetroPie-Setup/wiki/Managing-ROMs  
clrmameproはここでは解説しません。  

### 3) ROMに対応する画像イメージ群を収めたフォルダ(スクショ推奨)  
ROMイメージを格納するzipファイルに対応する画像ファイルが無い場合は、画像なしとして扱います。拡張子は.pngと.jpgがある場合は.pngを優先します。.jpegは認識しません。


##実行方法
pythonが必要です。MacやLinuxであれば最初から入っていますが、WindowsであればPython2.7をインストールしてください。  

コマンドラインから以下のコマンドを入力してください。  
`> python history2gamelist.py <rompath> <imagepath> <emulator> <piver>`  
  
`<rompath>`  
  clrmameproで以下の.DATを使ってリビルドしたROMイメージを収めたフォルダ  
`<imagepath>`  
  ROMに対応する画像イメージ群を収めたフォルダ  
`<emulator>`  
  対応エミュレータ。`"lr-mame2003"`, `"lr-fba-next"`, `"mame4all"` のいずれか。  
  `"mame4all"` 推奨。""（ダブルクォーテーション）は入力しない。  
`<piver>`  
  Raspberry Piのバージョン。`"0"`, `"1"`, `"2"`, `"3"` のいずれか。""（ダブルクォーテーション）は入力しない。  
  Compatibility ListではRPi0はRPi1と同一ハードとみなされているので`"0"`を入れても`"1"`と同じ結果になる。  
  
実行例：  
`>python history2gamelist.py X:\MAME037b5\ X:\MAME\snap\ mame4all 2`  
`...`  
`roms = 1660 / 2199 (日本語DBのあるROM / 全てのROM)`  
  
`gamelist.xmlの生成とROM、画像をまとめました。`  
`以下のファイルをRetroPieの所定のフォルダに転送してください。`  
`mame4all\gamelist.xml`  
  `-> /home/pi/.emulationstation/gamelists/mame-mame4all/gamelist.xml`  
`mame4all\image\`  
  `-> /home/pi/.emulationstation/downloaded_images/mame-mame4all`  
`mame4all\zip\`  
  `-> /home/pi/RetroPie/roms/mame-mame4all`  
  
`>`  

実行後に生成されたファイル群は、RetroPieの所定の位置に転送してください。　　

##本家Wikiに関する私見
RetroPieのWikiによると、RPi2or3では `lr-mame2003` か `lr-fba-next` 、RPi0or1では `mame4all `を使うことが推奨されています。しかしながら、Compatibility Listで動作確認済みとなっているタイトル数は、RPi2の `mame4all` に集中しており、RPi0,1,3や他のエミュレータでは動作確認すらまともに行われていないようです。 RPi2で動くものはRPi3でも動くと思うので神経質になる必要はないと思いますが、現時点でのCompatibility ListはRPi0とRPi1を同一ハードとみなしています。私はRPi0とRPi1を所有していませんが明らかに違うハードだと思いますし、ROMの動作率も違うと思います。RPi0をにメイン基板にして液晶パネルやハウジングを用意して、オリジナルの携帯ゲーム機を作りたいというのであれば、動作リストが極端に少ないので自分でROMの動作確認をするしかないと思います。 

※参考：Compatibility Listで挙げられているタイトルと、"OK"(=動作確認済み)となっている数の比較 (2016年10月調べ)  
  
`lr-mame2003 (4720タイトル)`  
`  RPi1 = 0`  
`  RPi2 = 327`  
`  RPi3 = 390`  
`lr-fba-next (4150タイトル)`  
`  RPi1 = 3`  
`  RPi2 = 152`  
`  RPi3 = 261`  
`mame4all (2270タイトル)`  
`  RPi1 = 146`  
`  RPi2 = 1854`  
`  RPi3 = 142`  
