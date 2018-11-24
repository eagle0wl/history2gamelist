#!/usr/bin/env python
"""
history2gamelist.py
by eagle0wl (masm0wl@hotmail.com)
https://github.com/eagle0wl/

MAMEの各種データベースからEmulationStationのgamelist.xmlを生成して、
所有しているROMイメージ群から、
動作確認リストにあるROMイメージだけをまとめます。

アーケードエミュレータは複数ありますが、
Wikiで推奨されている４種類のエミュレータ向けのデータベースを作成できます。

lr-mame2003
mame4all
lr-fbalpha
pifba


■用意するもの
0) 十分なHDD容量
このスクリプトを実行すると、このスクリプトと同じディレクトリに、
対応するROMイメージ群と画像（スクショ）のコピーを作ります。
2)のROMイメージ群と3)の画像群から必要なぶんだけをコピーするので、
必要な容量は予測できると思いますが、2GBもあれば十分です。

1) gamelist.xml作成に必要なファイル
このスクリプトと同じディレクトリに以下のファイルを置いてください。

ファイル名：
　history.dat
　mameinfo.dat
　mame_jp.lst
　lr-fbalpha.tsv
　lr-mame2003.tsv
　Mame4all.tsv
　pifba.tsv

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
・RPi動作チェック済のスプレッドシート（Compatibility List参照）
　https://github.com/RetroPie/RetroPie-Setup/wiki/Arcade
　RPi動作確認済みのタイトルを抽出するために使用します。
　また、ROMの親子関係の確認にも使います。
　下記４種類のCompatibility Listのスプレッドシートを保存する
　　ファイル→形式を指定してダウンロード→タブ区切りの値(.tsv、現在のシート)
　ファイル名は以下の通りにリネームしてください。
　mame4all    → Mame4all.tsv
　lr-mame2003 → lr-mame2003.tsv
　pifba       → pifba.tsv
　lr-fbalpha  → lr-fbalpha.tsv

2) clrmameproなどでリビルドしたROMイメージ(*.zip)を収めたフォルダ
　DATファイルは以下から探す。エミュレータごとにリビルドに必要な.DATファイルは異なります。
　clrmameproの使い方は各自調べてください。
　https://github.com/RetroPie/RetroPie-Setup/wiki/MAME
　https://github.com/RetroPie/RetroPie-Setup/wiki/FinalBurn-Alpha

3) ROMに対応する画像イメージ群を収めたフォルダ(スクショ推奨)
　ROMイメージを格納するzipファイルに対応する画像ファイルが無い場合は、
　画像なしとして扱います。
　この画像はEmulationStationの画面上で表示されます。

■実行方法
Python 3.7.x が必要です。
前バージョンのスクリプトは 2.7.x 用でしたが、3.7.x でないとエラーが出ます。
Windowsであれば Python 3.7.x をインストールしてください。
https://www.python.org/downloads/

コマンドラインから以下のコマンドを入力してください。

> python history2gamelist.py <rompath> <imagepath> <emulator> <piver>

  <rompath>
    RetroPieのWikiから手に入る.DATファイルを使って、
    clrmameproでリビルドしたROMイメージ(*.zip)を収めたフォルダ
  <imagepath>
    ROMに対応する画像イメージ群(*.png, *.jpg, *.jpeg)を収めたフォルダ
  <emulator>
    対応エミュレータ。
    "mame4all", "lr-mame2003", "lr-fbalpha", "pifba" のいずれか。
    （ダブルクォーテーションは入力しない）
  <piver>
    Raspberry Piのバージョン。"0", "1", "2", "3" のいずれか。
    （ダブルクォーテーションは入力しない）

実行例：
> python history2gamelist.py X:\MAME037b5\ X:\MAME\snap\ mame4all 2
...
roms = 1660 / 2199 (日本語DBのあるROM / 全てのROM)

gamelist.xmlの生成と、ROMイメージとスクリーンショットのまとめが終わりました。
以下のファイルをRetroPieの所定のフォルダに転送してください。

mame4all\gamelist.xml
  -> /home/pi/.emulationstation/gamelists/mame-mame4all/gamelist.xml
mame4all\image\*
  -> /home/pi/.emulationstation/downloaded_images/mame-mame4all
mame4all\zip\*
  -> /home/pi/RetroPie/roms/mame-mame4all

>

実行後に生成されたファイル群は、
RetroPieの所定の位置に配置してください。

コメント：
Compatibility Listで挙がっているタイトルの数と、
そのうちOK（動作確認済み）となっているタイトル数
2018/11/25調べ

               RPi0/1          RPi2          RPi3
lr-fbalpha    17/4896      198/4896     1051/4896
lr-mame2003   56/4720      514/4720     2676/4720
Mame4all     225/2271     1850/2271      339/2271
pifba        111/ 684      274/ 684       80/ 684


"""
import re, sys, os, shutil, codecs, glob
import xml.sax.saxutils as saxutils

Roms = {}
Roms['lr-mame2003'] = {
	'compati': 'lr-mame2003.tsv',
	'zippath': '/home/pi/RetroPie/roms/mame-libretro',
	'imgpath': '/home/pi/.emulationstation/downloaded_images/mame-libretro',
	'glipath': '/home/pi/.emulationstation/gamelists/mame-libretro',
	}
Roms['mame4all']    = {
	'compati': 'Mame4all.tsv',
	'zippath': '/home/pi/RetroPie/roms/mame-mame4all',
	'imgpath': '/home/pi/.emulationstation/downloaded_images/mame-mame4all',
	'glipath': '/home/pi/.emulationstation/gamelists/mame-mame4all',
	}
Roms['lr-fbalpha'] = {
	'compati': 'lr-fbalpha.tsv',
	'zippath': '/home/pi/RetroPie/roms/fba',
	'imgpath': '/home/pi/.emulationstation/downloaded_images/fba',
	'glipath': '/home/pi/.emulationstation/gamelists/fba',
	}
Roms['pifba'] = {
	'compati': 'pifba.tsv',
	'zippath': '/home/pi/RetroPie/roms/fba',
	'imgpath': '/home/pi/.emulationstation/downloaded_images/fba',
	'glipath': '/home/pi/.emulationstation/gamelists/fba',
	}

NeedFiles = [
	'history.dat',
	'mameinfo.dat',
	'mame_jp.lst',
	Roms['mame4all']['compati'],
	Roms['lr-mame2003']['compati'],
	Roms['lr-fbalpha']['compati'],
	Roms['pifba']['compati'],
	]

PiVersion = [
	'0',
	'1',
	'2',
	'3',
	]


# history.dat
def loadHistoryDat(filepath):
	
	historydict = {}
	
	f = codecs.open(filepath, 'r', 'utf-8')
	buffer = ''
	for line in f:
		l = line.strip() + '\n'
		if l.startswith('#'):
			continue
		if l.startswith('$info='):
			buffer = l
			continue
		if buffer == '':
			continue
		buffer += l
		if l.startswith('$end') is not True:
			continue
		buffer = buffer.strip()
		
		key = ''
		data = {
			'title': '',
			'release': '',
			'developer': '',
			'publisher': '',
			'systemboard': '',
			'cpu': '',
			'soundchip': '',
			'screen': '',
			'genre': '',
			'controller': '',
			'supportversion': '',
			'comment': ''
			}
		
		m = re.search('^\$info=(.+)$', buffer, re.MULTILINE)
		if m is None:
			continue
		keys = m.group(1).split(',')
		
		m = re.search('^\$bio\n(.+)\n', buffer, re.MULTILINE)
		if m is None:
			continue
		data['title'] = m.group(1)
		
		if data['release'] == '':
			m = re.search('^発売年：([0-9]{4})\.([0-9]{2})\.([0-9]{2})$', buffer, re.MULTILINE)
			if m is not None:
				data['release'] = m.group(1) + m.group(2) + m.group(3)
		if data['release'] == '':
			m = re.search('^発売年：([0-9]{4})\.([0-9]{2})$', buffer, re.MULTILINE)
			if m is not None:
				data['release'] = m.group(1) + m.group(2) + '01'
		if data['release'] == '':
			m = re.search('^発売年：([0-9]{4})$', buffer, re.MULTILINE)
			if m is not None:
				data['release'] = m.group(1) + '0101'
		
		if data['developer'] == '' and data['publisher'] == '':
			m = re.search('^(海外)?開発／発売元：(.+)$', buffer, re.MULTILINE)
			if m is not None:
				data['developer'] = m.group(2)
				data['publisher'] = m.group(2)
		if data['developer'] == '' and data['publisher'] == '':
			m = re.search('(海外)?開発元：(.+)　(国内)?発売元：(.+)', buffer, re.MULTILINE)
			if m is not None:
				data['developer'] = m.group(2)
				data['publisher'] = m.group(4)
		
		m = re.search('^システムボード：(.+)$', buffer, re.MULTILINE)
		if m is not None:
			data['systemboard'] = m.group(1)
		
		m = re.search('^CPU構成\[([^]]+)\]$', buffer, re.MULTILINE)
		if m is not None:
			data['cpu'] = m.group(1)
		
		m = re.search('^音源チップ\[([^]]+)\]$', buffer, re.MULTILINE)
		if m is not None:
			data['soundchip'] = m.group(1)
		
		m = re.search('^画面構成\[([^]]+)\]$', buffer, re.MULTILINE)
		if m is not None:
			data['screen'] = m.group(1)
		
		m = re.search('^ジャンル：(.+)$', buffer, re.MULTILINE)
		if m is not None:
			data['genre'] = m.group(1)
		
		m = re.search('^コントローラ：(.+)$', buffer, re.MULTILINE)
		if m is not None:
			data['controller'] = m.group(1)
		
		m = re.search('^サポートバージョン：(.+)$', buffer, re.MULTILINE)
		if m is not None:
			data['supportversion'] = m.group(1)
		
		m = re.search('(.+)\n\$end', buffer, re.MULTILINE)
		if m is not None:
			data['comment'] = m.group(1).strip()
		
		for key in keys:
			historydict[key] = data
		
	f.close()
	
	return historydict
	


# mameinfo.dat
def loadMameinfoDat(filepath):
	
	mameinfodict = {}
	
	f = codecs.open(filepath, 'r', 'utf-8')
	buffer = ''
	for line in f:
		l = line.strip() + '\n'
		if l.startswith('#'):
			continue
		if l.startswith('$info='):
			buffer = l
			continue
		if buffer == '':
			continue
		buffer += l
		if l.startswith('$end') is not True:
			continue
		buffer = buffer.strip()
		
		m = re.search('^\$info=(.+)$', buffer, re.MULTILINE)
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
		rows = line.split('\t')
		gameid = rows[0].strip()
		gametitle = rows[1].strip()
		mamejplstdict[gameid] = gametitle
	
	f.close()
	
	return mamejplstdict
	


# Compatibility List から得られるステータスは現時点では以下のいずれか。
# "OK", "Has Issues", "Doesn't Work", "Untested", (空欄)
def loadCompatibilityList(filepath, piver):
	
	compatilistdict = {}
	
	f = codecs.open(filepath, 'r', 'utf-8')
	buffer = ''
	
	f.readline()
	head = f.readline()
	
	statusrowindex = -1
	headrows = head.split('\t')
	for i in range(len(headrows)):
		if headrows[i] == 'Rpi 1 Status' and (piver == PiVersion[0] or piver == PiVersion[1]):
			statusrowindex = i
			break
		if headrows[i] == 'Rpi 2 Status' and piver == PiVersion[2]:
			statusrowindex = i
			break
		if headrows[i] == 'Rpi 3 Status' and piver == PiVersion[3]:
			statusrowindex = i
			break
	
	if statusrowindex == -1:
		print('Compatibility Listのフォーマットが変わっているかもしれません。')
		return None
	
	parentindex = -1
	for i in range(len(headrows)):
		if headrows[i] == 'Parent':
			parentindex = i
			break
	
	if parentindex == -1:
		print('Compatibility List のフォーマットが変わっているかもしれません。')
		return None
	
	for line in f:
		rows = line.split('\t')
		key = rows[0].strip() # stripしないと死ぬ
		title = rows[1].strip()
		status = rows[statusrowindex].strip()
		parent = rows[parentindex].strip()
		compatilistdict[key] = {'title': title, 'status': status, 'parent': parent}
		
	
	return compatilistdict
	


def loadRomFileList(romdir):
	
	romdict = {}
	
	romdir = romdir.rstrip('\\') + '\\'
	
	for r in glob.glob(romdir + '*.zip'):
		filename = os.path.basename(r)
		gameid, ext = os.path.splitext(filename)
		romfullpath = r
		
		romdict[gameid] = romfullpath
	
	return romdict
	


def loadImageFileList(imagedir):
	
	imagedict = {}
	
	imagedir = imagedir.rstrip('\\') + '\\'
	
	for r in glob.glob(imagedir + '*'):
		filename = os.path.basename(r)
		gameid, ext = os.path.splitext(filename)
		
		if os.path.isfile(imagedir + gameid + '.png') is True:
			imagefullpath = imagedir + gameid + '.png'
		elif os.path.isfile(imagedir + gameid + '.jpg') is True:
			imagefullpath = imagedir + gameid + '.jpg'
		elif os.path.isfile(imagedir + gameid + '.jpeg') is True:
			imagefullpath = imagedir + gameid + '.jpeg'
		else:
			continue
		
		imagedict[gameid] = imagefullpath
	
	return imagedict
	


def createGamelistXml(mergedlist):
	
	gamelistxml  = ''
	gamelistxml += '<?xml version="1.0"?>\n'
	gamelistxml += '<gameList>\n'
	for m in mergedlist:
		gamelistxml += '\t<game>\n'
		if m['rpzip'] != '':
			gamelistxml += '\t\t<path>' + saxutils.escape(m['rpzip']) + '</path>\n'
		gamelistxml += '\t\t<name>' + saxutils.escape(m['title']) + '</name>\n'
		if m['desc'] != '':
			gamelistxml += '\t\t<desc>' + saxutils.escape(m['desc']) + '</desc>\n'
		if m['rpimage'] != '':
			gamelistxml += '\t\t<image>' + saxutils.escape(m['rpimage']) + '</image>\n'
		gamelistxml += '\t\t<releasedate>' + saxutils.escape(m['release']) + 'T000000</releasedate>\n'
		if m['developer'] != '':
			gamelistxml += '\t\t<developer>' + saxutils.escape(m['developer']) + '</developer>\n'
		gamelistxml += '\t\t<publisher>' + saxutils.escape(m['publisher']) + '</publisher>\n'
		gamelistxml += '\t\t<genre>' + saxutils.escape(m['genre']) + '</genre>\n'
		gamelistxml += '\t\t<players />\n'
		gamelistxml += '\t</game>\n'
	
	gamelistxml += '</gameList>\n'
	
	return gamelistxml
	


def usage(errmsg=''):
	
	print('  usage:')
	print('  > python ' + __file__ + ' <rompath> <imagepath> <emulator> <piver>')
	print('  ')
	print('    <rompath>')
	print('      RetroPieのWikiから手に入る.DATファイルを使って、')
	print('      clrmameproでリビルドしたROMイメージ(*.zip)を収めたフォルダ')
	print('    <imagepath>')
	print('      ROMに対応する画像イメージ群(*.png, *.jpg, *.jpeg)を収めたフォルダ')
	print('    <emulator>')
	print('      対応エミュレータ。')
	print('      "mame4all", "lr-mame2003", "lr-fbalpha", "pifba" のいずれか。')
	print('      （ダブルクォーテーションは入力しない）')
	print('    <piver>')
	print('      Raspberry Piのバージョン。"0", "1", "2", "3" のいずれか。')
	print('      （ダブルクォーテーションは入力しない）')
	print('  ')
	print('  example:')
	print('  > python ' + __file__ + ' X:\MAME037b5\ X:\MAME\snap\ mame4all 2')
	
	if errmsg != '':
		print('error:')
		print(errmsg)
	
	return
	


def main():
	
	argvs = sys.argv
	argc = len(argvs)
	
	hasError = False
	for f in NeedFiles:
		if os.path.isfile(f) is False:
			hasError = True
			print(f + ' が見つかりません。')
	if hasError:
		return
	
	if argc != 5:
		usage()
		return
	
	rompath = argvs[1]
	imagepath = argvs[2]
	emulator = argvs[3]
	piver = argvs[4]
	
	errmsg = ''
	if os.path.isdir(rompath) is False:
		errmsg += '* ' + rompath + u' はフォルダではありません。\n'
	if os.path.isdir(imagepath) is False:
		errmsg += '* ' + imagepath + u' はフォルダではありません。\n'
	if emulator in Roms is False:
		errmsg += '* ' + emulator + u' には対応エミュレータを指定してください。\n'
	elif os.path.isdir(emulator):
		errmsg += '* フォルダ ' + emulator + u' がすでにあります。削除してください。'
	if piver not in PiVersion:
		errmsg += '* Raspberry Piのバージョンは "0", "1", "2", "3"のいずれかで指定してください。\n'
	
	if errmsg != '':
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
		if (gameid in compatilistdict) is False:
			continue
		if compatilistdict[gameid]['status'] != 'OK':
			continue
		parentid = compatilistdict[gameid]['parent']
		
		m = {}
		m['gameid'] = gameid
		m['zip'] = romdict[gameid]
		m['rpzip'] = Roms[emulator]['zippath'] + '/' + os.path.basename(romdict[gameid])
		
		m['parentid'] = parentid
		if parentid != '' and ((parentid in romdict) is False):
			# 親ROMが見つからない
			continue
		
		if parentid != '':
			m['parentzip'] = romdict[parentid]
			m['rpparentzip'] = Roms[emulator]['zippath'] + '/' + os.path.basename(romdict[parentid])
		else:
			m['parentzip'] = ''
			m['rpparentzip'] = ''
		
		if gameid in imagedict:
			m['image'] = imagedict[gameid]
			m['rpimage'] = Roms[emulator]['imgpath'] + '/' + os.path.basename(imagedict[gameid])
		elif parentid in imagedict:
			m['image'] = imagedict[parentid]
			m['rpimage'] = Roms[emulator]['imgpath'] + '/' + os.path.basename(imagedict[parentid])
		else:
			m['image'] = ''
			m['rpimage'] = ''
		
		if gameid in mamejplstdict:
			m['title'] = mamejplstdict[gameid]
		elif gameid in historydict:
			m['title'] = historydict[gameid]['title'] 
		else:
			m['title'] = compatilistdict[gameid]['title']
		
		if gameid in historydict:
			id = gameid
		elif parentid in historydict:
			id = parentid
		else:
			continue
		
		m['release']   = historydict[id]['release']
		m['developer'] = historydict[id]['developer']
		m['publisher'] = historydict[id]['publisher']
		m['genre']     = historydict[id]['genre']
		m['desc']      = historydict[id]['comment'] + '\n\n'
		if id in mameinfodict:
			m['desc'] += mameinfodict[id]
		m['desc']      = m['desc'].rstrip()
		mergedlist.append(m)
		"""
		print('----')
		print("%d" % (count+1))
		print(m['gameid'])
		print(m['zip'])
		print(m['rpzip'])
		print(m['parentzip'])
		print(m['rpparentzip'])
		print(m['parentid'])
		print(m['image'])
		print(m['rpimage'])
		print(m['title'])
		print(m['release'])
		print(m['developer'])
		print(m['publisher'])
		print(m['genre'])
		print(m['desc'])
		"""
		count += 1
	
	xmltext = createGamelistXml(mergedlist)
	
	os.mkdir(emulator)
	f = codecs.open(emulator + '\\gamelist.xml', 'w', 'utf-8')
	f.write(xmltext)
	f.close()
	
	os.mkdir(emulator + '\\zip')
	os.mkdir(emulator + '\\image')
	
	i = 0
	for m in mergedlist:
		print('[%5d/%5d] copy %s -> %s' % (i+1, len(mergedlist), m['zip'], emulator + '\\zip'))
		
		if m['parentzip'] != '':
			if os.path.isfile(emulator + '\\zip\\' + os.path.basename(m['parentzip'])) is False:
				print('              copy %s -> %s' % (m['parentzip'], emulator + '\\zip'))
				shutil.copy(m['parentzip'], emulator + '\\zip')
		
		shutil.copy(m['zip'], emulator + '\\zip')
		
		if m['image'] != '':
			print('              copy %s -> %s' % (m['image'], emulator + '\\image'))
			shutil.copy(m['image'], emulator + '\\image')
		i += 1
	
	print('')
	print('roms = %d / %d (日本語DBのあるROM / 全てのROM)' % (count, len(romdict.keys())))
	print('')
	print('gamelist.xmlの生成と、ROMイメージとスクリーンショットのまとめが終わりました。')
	print('以下のファイルをRetroPieの所定のフォルダに転送してください。')
	print('' + emulator + '\\gamelist.xml')
	print('  -> ' + Roms[emulator]['glipath'] + '/gamelist.xml')
	print( '' + emulator + '\\image\\*')
	print('  -> ' + Roms[emulator]['imgpath'])
	print('' + emulator + '\\zip\\*')
	print('  -> ' + Roms[emulator]['zippath'])
	
	return
	


if __name__ == "__main__":
	main()


