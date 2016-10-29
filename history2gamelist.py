#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
history2gamelist.py
MAMEの各種データベースから、
EmulationStationのgamelist.xmlを生成して、
リストにあるROMイメージだけをまとめます。

アーケードエミュレータは複数ありますが、Wikiで推奨されている
lr-mame2003 (RPi2, 3推奨)
lr-fba-next (RPi2, 3推奨)
mame4all (RPiZero, 1推奨)
に対応しています。しかし、RPiのバージョンによらずmame4allを推奨します。
理由は後述します。

■用意するもの
0) 十分なHDD容量
このスクリプトと同じディレクトリに、
対応するROMイメージ群と画像（スクショ）のコピーを作ります。
2)のROMイメージ群と3)の画像群から必要なぶんだけをコピーするので、
必要な容量は予測できると思います。2GBもあれば十分です。

1) gamelist.xml作成に必要なファイル
このスクリプトと同じディレクトリに以下のファイルを置いてください。

ファイル名：
　history.dat
　mameinfo.dat
　mame_jp.lst
　lr-mame2003.tsv
　lr-fba-next.tsv
　Mame4all.tsv

ファイル入手先：
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
　RPi動作確認済みのタイトルを抽出するために使用します。
　また、ROMの親子関係の確認にも使います。
　下記３種類のCompatibility Listのスプレッドシートを保存する
　　ファイル→形式を指定してダウンロード→タブ区切りの値(.tsv、現在のシート)
　ファイル名は以下の通りにリネームしてください。
　lr-mame2003 → lr-mame2003.tsv
　lr-fba-next → lr-fba-next.tsv
　mame4all    → Mame4all.tsv

2) 以下の.DATを使ってclrmameproなどでリビルドしたROMイメージを収めたフォルダ
　DATファイルは以下参照
　https://github.com/RetroPie/RetroPie-Setup/wiki/Managing-ROMs

3) ROMに対応する画像イメージ群を収めたフォルダ(スクショ推奨)
　ROMイメージを格納するzipファイルに対応する画像ファイルが無い場合は、
　画像なしとして扱います。

■実行方法
pythonが必要です。
MacやLinuxであれば最初から入っていますが、
Windowsであればpython2.7をインストールしてください。

コマンドラインから以下のコマンドを入力してください。
> python history2gamelist.py <rompath> <imagepath> <emulator> <piver>

<rompath>
  clrmameproで以下の.DATを使ってリビルドしたROMイメージを収めたフォルダ
<imagepath>
  ROMに対応する画像イメージ群を収めたフォルダ
<emulator>
  対応エミュレータ。"lr-mame2003", "lr-fba-next", "mame4all" のいずれか。
  "mame4all" 推奨。""（ダブルクォーテーション）は入力しない。
<piver>
  Raspberry Piのバージョン。"0", "1", "2", "3" のいずれか。
  "0"と"1"は同じものとして扱う。""（ダブルクォーテーション）は入力しない。

実行例：
>python history2gamelist.py X:\MAME037b5\ X:\MAME\snap\ mame4all 2
...
roms = 1660 / 2199 (日本語DBのあるROM / 全てのROM)

gamelist.xmlの生成とROM、画像をまとめました。
以下のファイルをRetroPieの所定のフォルダに転送してください。
mame4all\gamelist.xml
  -> /home/pi/.emulationstation/gamelists/mame-mame4all/gamelist.xml
mame4all\image\
  -> /home/pi/.emulationstation/downloaded_images/mame-mame4all
mame4all\zip\
  -> /home/pi/RetroPie/roms/mame-mame4all

>

実行後に生成されたファイル群は、
RetroPieの所定の位置に配置してください。


コメント：
各アーケードエミュレータに対し、Wikiでは
lr-mame2003, lr-fba-next をRPi2, 3推奨
mame4all をRPiZero, 1推奨
としていますが、
Compatibility Listで動作確認済みとなっているタイトル数は、
RPi2のmame4allに集中しており、他のRPiやエミュレータでは
動作確認すらまともに行われていないようです。

※参考：Compatibility Listで挙げられているタイトルと、
"OK"(=動作確認済み)となっている数の比較 (2016/10)

                    RPi1        RPi2        RPi3
lr-mame2003       0/4720    327/4720    390/4720
lr-fba-next       3/4150    152/4150    261/4150
mame4all        146/2270   1854/2270    142/2270
"""
import re, sys, os, shutil, codecs, glob
import xml.sax.saxutils as saxutils

Roms = {}
Roms['lr-mame2003'] = {
	'compati': u'lr-mame2003.tsv',
	'zippath': u'/home/pi/RetroPie/roms/mame-libretro',
	'imgpath': u'/home/pi/.emulationstation/downloaded_images/mame-libretro',
	'glipath': u'/home/pi/.emulationstation/gamelists/mame-libretro',
	}
Roms['lr-fba-next'] = {
	'compati': u'lr-fba-next.tsv',
	'zippath': u'/home/pi/RetroPie/roms/fba',
	'imgpath': u'/home/pi/.emulationstation/downloaded_images/fba',
	'glipath': u'/home/pi/.emulationstation/gamelists/fba',
	}
Roms['mame4all']    = {
	'compati': u'Mame4all.tsv',
	'zippath': u'/home/pi/RetroPie/roms/mame-mame4all',
	'imgpath': u'/home/pi/.emulationstation/downloaded_images/mame-mame4all',
	'glipath': u'/home/pi/.emulationstation/gamelists/mame-mame4all',
	}

NeedFiles = [
	u'history.dat',
	u'mameinfo.dat',
	u'mame_jp.lst',
	Roms['lr-mame2003']['compati'],
	Roms['lr-fba-next']['compati'],
	Roms['mame4all']['compati'],
]

PiVersion = [
	u'0',
	u'1',
	u'2',
	u'3',
]


def loadHistoryDat(filepath):
	
	historydict = {}
	
	f = codecs.open(filepath, 'r', 'utf-8')
	buffer = u''
	for line in f:
		l = line.strip() + u'\n'
		if l.startswith(u'#'):
			continue
		if l.startswith(u'$info='):
			buffer = l
			continue
		if buffer == u'':
			continue
		buffer += l
		if l.startswith(u'$end') is not True:
			continue
		buffer = buffer.strip()
		
		key = u''
		data = {
			'title': u'',
			'release': u'',
			'developer': u'',
			'publisher': u'',
			'systemboard': u'',
			'cpu': u'',
			'soundchip': u'',
			'screen': u'',
			'genre': u'',
			'controller': u'',
			'supportversion': u'',
			'comment': u''
			}
		
		m = re.search(u'^\$info=(.+)$', buffer, re.MULTILINE)
		if m is None:
			continue
		keys = m.group(1).split(',')
		
		m = re.search(u'^\$bio\n(.+)\n', buffer, re.MULTILINE)
		if m is None:
			continue
		data['title'] = m.group(1)
		
		if data['release'] == u'':
			m = re.search(u'^発売年：([0-9]{4})\.([0-9]{2})\.([0-9]{2})$', buffer, re.MULTILINE)
			if m is not None:
				data['release'] = m.group(1) + m.group(2) + m.group(3)
		if data['release'] == u'':
			m = re.search(u'^発売年：([0-9]{4})\.([0-9]{2})$', buffer, re.MULTILINE)
			if m is not None:
				data['release'] = m.group(1) + m.group(2) + u'01'
		if data['release'] == u'':
			m = re.search(u'^発売年：([0-9]{4})$', buffer, re.MULTILINE)
			if m is not None:
				data['release'] = m.group(1) + u'0101'
		
		if data['developer'] == u'' and data['publisher'] == u'':
			m = re.search(u'^(海外)?開発／発売元：(.+)$', buffer, re.MULTILINE)
			if m is not None:
				data['developer'] = m.group(2)
				data['publisher'] = m.group(2)
		if data['developer'] == u'' and data['publisher'] == u'':
			m = re.search(u'(海外)?開発元：(.+)　(国内)?発売元：(.+)', buffer, re.MULTILINE)
			if m is not None:
				data['developer'] = m.group(2)
				data['publisher'] = m.group(4)
		
		m = re.search(u'^システムボード：(.+)$', buffer, re.MULTILINE)
		if m is not None:
			data['systemboard'] = m.group(1)
		
		m = re.search(u'^CPU構成\[([^]]+)\]$', buffer, re.MULTILINE)
		if m is not None:
			data['cpu'] = m.group(1)
		
		m = re.search(u'^音源チップ\[([^]]+)\]$', buffer, re.MULTILINE)
		if m is not None:
			data['soundchip'] = m.group(1)
		
		m = re.search(u'^画面構成\[([^]]+)\]$', buffer, re.MULTILINE)
		if m is not None:
			data['screen'] = m.group(1)
		
		m = re.search(u'^ジャンル：(.+)$', buffer, re.MULTILINE)
		if m is not None:
			data['genre'] = m.group(1)
		
		m = re.search(u'^コントローラ：(.+)$', buffer, re.MULTILINE)
		if m is not None:
			data['controller'] = m.group(1)
		
		m = re.search(u'^サポートバージョン：(.+)$', buffer, re.MULTILINE)
		if m is not None:
			data['supportversion'] = m.group(1)
		
		m = re.search(u'(.+)\n\$end', buffer, re.MULTILINE)
		if m is not None:
			data['comment'] = m.group(1).strip()
		
		for key in keys:
			historydict[key] = data
		
	f.close()
	
	return historydict
	


def loadMameinfoDat(filepath):
	
	mameinfodict = {}
	
	f = codecs.open(filepath, 'r', 'utf-8')
	buffer = u''
	for line in f:
		l = line.strip() + u'\n'
		if l.startswith(u'#'):
			continue
		if l.startswith(u'$info='):
			buffer = l
			continue
		if buffer == u'':
			continue
		buffer += l
		if l.startswith(u'$end') is not True:
			continue
		buffer = buffer.strip()
		
		m = re.search(u'^\$info=(.+)$', buffer, re.MULTILINE)
		if m is None:
			continue
		key = m.group(1)
		
		spos = buffer.find('$mame\n')
		if spos == -1:
			continue
		spos += len('$mame\n')
		epos = buffer.find('\n$end', spos)
		if epos == -1:
			continue
		
		info = buffer[spos:epos]
		info = info.replace('\n\n', '\n')
		info = info.replace('\n\n', '\n')
		
		mameinfodict[key] = info
	
	f.close()
	
	return mameinfodict
	


def loadMame_jplst(filepath):
	
	mamejplstdict = {}
	
	f = codecs.open(filepath, 'r', 'cp932')
	for line in f:
		rows = line.split(u'\t')
		gameid = rows[0].strip()
		gametitle = rows[1].strip()
		mamejplstdict[gameid] = gametitle
	
	f.close()
	
	return mamejplstdict
	


"""
Compatibility List から得られるステータスは現時点では以下のいずれか。
	OK
	Has Issues
	Doesn't Work
	Untested
"""
def loadCompatibilityList(filepath, piver):
	
	compatilistdict = {}
	
	f = codecs.open(filepath, 'r', 'utf-8')
	buffer = u''
	
	f.readline()
	head = f.readline()
	
	statusrowindex = -1
	headrows = head.split(u'\t')
	for i in range(len(headrows)):
		if headrows[i] == u'Rpi 1 Status' and (piver == PiVersion[0] or piver == PiVersion[1]):
			statusrowindex = i
			break
		if headrows[i] == u'Rpi 2 Status' and piver == PiVersion[2]:
			statusrowindex = i
			break
		if headrows[i] == u'Rpi 3 Status' and piver == PiVersion[3]:
			statusrowindex = i
			break
	
	if statusrowindex == -1:
		print u'もしかするとCompatibility List のフォーマットが変わっているのかもしれません。'
		return None
	
	parentindex = -1
	for i in range(len(headrows)):
		if headrows[i] == u'Parent':
			parentindex = i
			break
	
	if parentindex == -1:
		print u'もしかするとCompatibility List のフォーマットが変わっているのかもしれません。'
		return None
	
	for line in f:
		rows = line.split(u'\t')
		key = rows[0].strip() # stripしないと死ぬ
		title = rows[1]
		status = rows[statusrowindex]
		parent = rows[parentindex]
		compatilistdict[key] = {'title': title, 'status': status, 'parent': parent}
		
	
	return compatilistdict
	


def loadRomFileList(romdir):
	
	romdict = {}
	
	romdir = romdir.rstrip('\\') + u'\\'
	
	for r in glob.glob(romdir + u'*.zip'):
		filename = os.path.basename(r)
		gameid, ext = os.path.splitext(filename)
		romfullpath = r
		
		romdict[gameid] = romfullpath
	
	return romdict
	


def loadImageFileList(imagedir):
	
	imagedict = {}
	
	imagedir = imagedir.rstrip('\\') + u'\\'
	
	for r in glob.glob(imagedir + u'*'):
		filename = os.path.basename(r)
		gameid, ext = os.path.splitext(filename)
		
		if os.path.isfile(imagedir + gameid + u'.png') is True:
			imagefullpath = imagedir + gameid + u'.png'
		elif os.path.isfile(imagedir + gameid + u'.jpg') is True:
			imagefullpath = imagedir + gameid + u'.jpg'
		else:
			continue
		
		imagedict[gameid] = imagefullpath
	
	return imagedict
	


def createGamelistXml(mergedlist):
	
	gamelistxml  = u''
	gamelistxml += u'<?xml version="1.0"?>\n'
	gamelistxml += u'<gameList>\n'
	for m in mergedlist:
		gamelistxml += u'\t<game>\n'
		if m['rpzip'] != u'':
			gamelistxml += u'\t\t<path>' + saxutils.escape(m['rpzip']) + u'</path>\n'
		gamelistxml += u'\t\t<name>' + saxutils.escape(m['title']) + u'</name>\n'
		if m['desc'] != u'':
			gamelistxml += '\t\t<desc>' + saxutils.escape(m['desc']) + u'</desc>\n'
		if m['rpimage'] != u'':
			gamelistxml += u'\t\t<image>' + saxutils.escape(m['rpimage']) + u'</image>\n'
		gamelistxml += u'\t\t<releasedate>' + saxutils.escape(m['release']) + u'T000000</releasedate>\n'
		if m['developer'] != u'':
			gamelistxml += u'\t\t<developer>' + saxutils.escape(m['developer']) + u'</developer>\n'
		gamelistxml += u'\t\t<publisher>' + saxutils.escape(m['publisher']) + u'</publisher>\n'
		gamelistxml += u'\t\t<genre>' + saxutils.escape(m['genre']) + u'</genre>\n'
		gamelistxml += u'\t\t<players />\n'
		gamelistxml += u'\t</game>\n'
	
	gamelistxml += '</gameList>\n'
	
	return gamelistxml
	


def usage(errmsg=u''):
	
	print u'usage:'
	print u'> python ' + __file__ + ' <rompath> <imagepath> <emulator> <piver>'
	print u''
	print u'  <rompath>'
	print u'    clrmameproで以下の.DATを使ってリビルドしたROMイメージを収めたフォルダ'
	print u'  <imagepath>'
	print u'    ROMに対応する画像イメージ群を収めたフォルダ'
	print u'  <emulator>'
	print u'    対応エミュレータ。"lr-mame2003", "lr-fba-next", "mame4all" のいずれか。'
	print u'  <piver>'
	print u'    Raspberry Piのバージョン。"0", "1", "2", "3" のいずれか。'
	print u''
	
	if errmsg != u'':
		print u'error:'
		print errmsg
	
	return
	


def main():
	
	sys.stdout = codecs.getwriter("cp932")(sys.stdout)
	
	argvs = sys.argv
	argc = len(argvs)
	
	hasError = False
	for f in NeedFiles:
		if os.path.isfile(f) is False:
			hasError = True
			print f + u' が見つかりません。'
	if hasError:
		return
	
	if argc != 5:
		usage()
		return
	
	rompath = argvs[1]
	imagepath = argvs[2]
	emulator = argvs[3]
	piver = argvs[4]
	
	errmsg = u''
	if os.path.isdir(rompath) is False:
		errmsg += u'* ' + rompath + u' はフォルダではありません。\n'
	if os.path.isdir(imagepath) is False:
		errmsg += u'* ' + imagepath + u' はフォルダではありません。\n'
	if Roms.has_key(emulator) is False:
		errmsg += u'* ' + emulator + u' には対応エミュレータを指定してください。\n'
	elif os.path.isdir(emulator):
		errmsg += u'* フォルダ ' + emulator + u' がすでにあります。削除してください。'
	if piver not in PiVersion:
		errmsg += u'* Raspberry Piのバージョンは "0", "1", "2", "3"のいずれかで指定してください。\n'
	
	if errmsg != u'':
		usage(errmsg)
		return
	
	historydict = loadHistoryDat('history.dat')
	mameinfodict = loadMameinfoDat('mameinfo.dat')
	mamejplstdict = loadMame_jplst('mame_jp.lst')
	compatilistdict = loadCompatibilityList(Roms[emulator]['compati'], piver)
	if compatilistdict is None:
		return
	romdict = loadRomFileList(rompath)
	imagedict = loadImageFileList(imagepath)
	
	
	# 取得した情報をまとめる
	count = 0
	mergedlist = []
	for gameid in sorted(romdict.keys()):
		if compatilistdict.has_key(gameid) is False:
			continue
		if compatilistdict[gameid]['status'] != u'OK':
			continue
		parentid = compatilistdict[gameid]['parent']
		
		m = {}
		m['gameid'] = gameid
		m['zip'] = romdict[gameid]
		m['rpzip'] = Roms[emulator]['zippath'] + u'/' + os.path.basename(romdict[gameid])
		
		m['parentid'] = parentid
		if parentid != u'' and romdict.has_key(parentid) is False:
			# 親ROMが見つからない
			continue
		
		if parentid != u'':
			m['parentzip'] = romdict[parentid]
			m['rpparentzip'] = Roms[emulator]['zippath'] + u'/' + os.path.basename(romdict[parentid])
		else:
			m['parentzip'] = u''
			m['rpparentzip'] = u''
		
		if imagedict.has_key(gameid):
			m['image'] = imagedict[gameid]
			m['rpimage'] = Roms[emulator]['imgpath'] + u'/' + os.path.basename(imagedict[gameid])
		elif imagedict.has_key(parentid):
			m['image'] = imagedict[parentid]
			m['rpimage'] = Roms[emulator]['imgpath'] + u'/' + os.path.basename(imagedict[parentid])
		else:
			m['image'] = u''
			m['rpimage'] = u''
		
		if mamejplstdict.has_key(gameid):
			m['title'] = mamejplstdict[gameid]
		elif historydict.has_key(gameid):
			m['title'] = historydict[gameid]['title'] 
		else:
			m['title'] = compatilistdict[gameid]['title']
		
		if historydict.has_key(gameid):
			id = gameid
		elif historydict.has_key(parentid):
			id = parentid
		else:
			continue
		
		m['release']   = historydict[id]['release']
		m['developer'] = historydict[id]['developer']
		m['publisher'] = historydict[id]['publisher']
		m['genre']     = historydict[id]['genre']
		m['desc']      = historydict[id]['comment']+'\n\n'
		if mameinfodict.has_key(id):
			m['desc'] += mameinfodict[id]
		m['desc']      = m['desc'].rstrip()
		mergedlist.append(m)
		"""
		print '----'
		print u"%d" % (count+1)
		print m['gameid']
		print m['zip']
		print m['rpzip']
		print m['parentzip']
		print m['rpparentzip']
		print m['parentid']
		print m['image']
		print m['rpimage']
		print m['title']
		print m['release']
		print m['developer']
		print m['publisher']
		print m['genre']
		print m['desc']
		"""
		count += 1
	
	xmltext = createGamelistXml(mergedlist)
	
	os.mkdir(emulator)
	f = codecs.open(emulator + u'\\gamelist.xml', 'w', 'utf-8')
	f.write(xmltext)
	f.close()
	
	os.mkdir(emulator + u'\\zip')
	os.mkdir(emulator + u'\\image')
	
	i = 0
	for m in mergedlist:
		print '[%5d/%5d] copy %s -> %s' % (i+1, len(mergedlist), m['zip'], emulator + u'\\zip')
		if m['parentzip'] != u'' and os.path.isfile(emulator + u'\\zip\\' + os.path.basename(m['parentzip'])) is False:
			print '              copy %s -> %s' % (m['parentzip'], emulator + u'\\zip')
			shutil.copy(m['parentzip'], emulator + u'\\zip')
		shutil.copy(m['zip'], emulator + u'\\zip')
		if m['image'] != u'':
			print '              copy %s -> %s' % (m['image'], emulator + u'\\image')
			shutil.copy(m['image'], emulator + u'\\image')
		i += 1
	
	print u''
	print u'roms = %d / %d (日本語DBのあるROM / 全てのROM)' % (count, len(romdict.keys()))
	print u''
	print u'gamelist.xmlの生成とROM、画像をまとめました。'
	print u'以下のファイルをRetroPieの所定のフォルダに転送してください。'
	print u'' + emulator + u'\\gamelist.xml'
	print u'  -> ' + Roms[emulator]['glipath'] + u'/gamelist.xml'
	print u'' + emulator + u'\\image\\'
	print u'  -> ' + Roms[emulator]['imgpath']
	print u'' + emulator + u'\\zip\\'
	print u'  -> ' + Roms[emulator]['zippath']
	
	return
	


if __name__ == "__main__":
	main()
