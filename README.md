## はじめに
MAMEの各種データベースからEmulationStationの `gamelist.xml` を生成して、所有しているROMイメージ群から、動作確認リストにあるROMイメージだけをまとめます。  

アーケードエミュレータは複数ありますが、Wikiで推奨されている４種類のエミュレータ向けのデータベースを作成できます。  

`lr-mame2003`  
`mame4all`  
`lr-fbalpha`  
`pifba`  


## 用意するもの
### 0) 十分なHDD容量  
このスクリプトを実行すると、このスクリプトと同じディレクトリに、対応するROMイメージ群と画像（スクショ）のコピーを作ります。2)のROMイメージ群と3)の画像群から必要なぶんだけをコピーするので、必要な容量は予測できると思いますが、2GBもあれば十分です。  

### 1) gamelist.xml作成に必要なファイル  
このスクリプトと同じディレクトリに以下のファイルを置いてください。一つでも欠けていると動作しません。  

`history.dat`  
`mameinfo.dat`  
`mame_jp.lst`  
`lr-fbalpha.tsv`  
`lr-mame2003.tsv`  
`Mame4all.tsv`  
`pifba.tsv`  

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
geocities.jpは2019年3月閉鎖予定

・RPi動作チェック済のスプレッドシート(Compatibility List)  
https://github.com/RetroPie/RetroPie-Setup/wiki/Arcade  
RPi動作確認済みタイトルの抽出とROMの親子関係の確認に使います。  
下記３種類のCompatibility Listのスプレッドシートを保存してください。  
ファイル → 形式を指定してダウンロード → タブ区切りの値(.tsv、現在のシート)  
ファイル名は以下の通りにリネームしてください。

`mame4all    → Mame4all.tsv`  
`lr-mame2003 → lr-mame2003.tsv`  
`pifba       → pifba.tsv`  
`lr-fbalpha  → lr-fbalpha.tsv`  

### 2) clrmameproなどでリビルドしたROMイメージ(*.zip)を収めたフォルダ  
DATファイルは以下から探す。エミュレータごとにリビルドに必要な.DATファイルは異なります。clrmameproの使い方は各自調べてください。  

https://github.com/RetroPie/RetroPie-Setup/wiki/MAME  
https://github.com/RetroPie/RetroPie-Setup/wiki/FinalBurn-Alpha  

### 3) ROMに対応する画像イメージ群を収めたフォルダ(スクショ推奨)  
ROMイメージを格納するzipファイルに対応する画像ファイルが無い場合は、画像なしとして扱います。この画像はEmulationStationの画面上で表示されます。拡張子は.png、.jpg、.jpegの順で検索します。  


## 実行方法
Python 3.7.x が必要です。前バージョンのスクリプトは 2.7.x 用でしたが、3.7.x でないとエラーが出ます。Windowsであれば Python 3.7.x をインストールしてください。  
https://www.python.org/downloads/  

コマンドラインから以下のコマンドを入力してください。  
`> python history2gamelist.py <rompath> <imagepath> <emulator> <piver>`  
  
`<rompath>`  
  RetroPieのWikiから手に入る.DATファイルを使って、clrmameproでリビルドしたROMイメージ(*.zip)を収めたフォルダ  
`<imagepath>`  
  ROMに対応する画像イメージ群(*.png, *.jpg, *.jpeg)を収めたフォルダ  
`<emulator>`  
  対応エミュレータ。`"mame4all"`, `"lr-mame2003"`, `"lr-fbalpha"`, `"pifba"` のいずれか。  
  （ダブルクォーテーションは入力しない）  
`<piver>`  
  Raspberry Piのバージョン。`"0"`, `"1"`, `"2"`, `"3"` のいずれか。  
  （ダブルクォーテーションは入力しない）  
  Compatibility Listでは、RPi0とRPi1と同一ハードとみなされているので`"0"`を入れても`"1"`と同じ結果になる。  
  
実行例：  
`>python history2gamelist.py X:\MAME037b5\ X:\MAME\snap\ mame4all 2`  
`...`  
`roms = 1660 / 2199 (日本語DBのあるROM / 全てのROM)`  
  
`gamelist.xmlの生成とROM、画像をまとめました。`  
`以下のファイルをRetroPieの所定のフォルダに転送してください。`  
`mame4all\gamelist.xml`  
  `-> /home/pi/.emulationstation/gamelists/mame-mame4all/gamelist.xml`  
`mame4all\image\*`  
  `-> /home/pi/.emulationstation/downloaded_images/mame-mame4all`  
`mame4all\zip\*`  
  `-> /home/pi/RetroPie/roms/mame-mame4all`  
  
`>`  

実行後に生成されたファイル群は、RetroPieの所定の位置に配置してください。  

## 参考  
Compatibility Listで挙がっているタイトルの数と、そのうちOK（動作確認済み）となっているタイトル数  
2018/11/25調べ  

`_______________RPi0/1__________RPi2__________RPi3`  
`lr-fbalpha____17/4896______198/4896_____1051/4896`  
`lr-mame2003___56/4720______514/4720_____2676/4720`  
`Mame4all_____225/2271_____1850/2271______339/2271`  
`pifba________111/ 684______274/ 684_______80/ 684`  

手持ちのRPiのバージョンにあわせてエミュレータを選びましょう。  
