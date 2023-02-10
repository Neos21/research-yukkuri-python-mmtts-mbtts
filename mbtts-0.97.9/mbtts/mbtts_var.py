# -*- coding: utf8 -*-
# mbtts_variable.py
# mbtts 0.97.9
# 2011/05/04
# copyright(c) takayan
# http://neu101.seesaa.net/

import platform
import os
import re
import sys
import ConfigParser
import tarfile
import zipfile
import shutil
from ctypes import *

import mb_jp1
import mb_jp2
import mb_jp3
import mb_aquestalk2

import mecab_ipadic
import mecab_unidic


##### 内部関数 #####

def exists(name):
	ps = platform.system()
	if ps == "Windows":
		s = ';'
	else:
		s = ':'
	list = os.environ['PATH'].split(s)
	for i in list:
		if os.path.exists( os.path.join( i, name ) ):
			return True
	return False


def extract_targz(d,n):
	p = os.path.join(d,n) + '.tar.gz'
	if os.path.exists(p):
		print n + u'.tar.gz を展開中...'
		f = tarfile.open(p)
		f.extractall(d)
		f.close()
		os.remove(p)


def extract_zip(d,n):
	p = os.path.join( d, n ) + '.zip'
	if os.path.exists(p):
		print n + u'.zip を展開中...'
		z = zipfile.ZipFile(p)
		z.extractall(d)
		z.close()
		os.remove(p)


##### 不変定数 #####


# パッケージ名
PACKAGE_NAME = 'mbtts'

# 設定ファイル名
CONFIG_NAME = "config.txt"

# 使用できる辞書の一覧
DICS = {
	mecab_ipadic.IpaDic.name:mecab_ipadic.IpaDic,
	mecab_unidic.UniDic.name:mecab_unidic.UniDic,
}


##### プラットフォーム非依存定数 #####

# デバッグ
DEBUG = 0

# アクセントを有効にするかのフラグ
ACCENT_FLAG = 1

# 記号を読むかどうかのフラグ
READING_SYMBOL_FLAG = 0

#ログファイル名
LOGFILE_NAME = "log.txt"

# ユーザ簡易辞書名
USERDIC_NAME = "userdic.txt"

# 自動読み上げ対象ファイル名
DEFAULT_TEXT = 'text.txt'

# 挨拶文字列
MESSAGE_TEXT = u'世界のみなさん、こんにちは'

# openjtalk 関連フォルダ名
OPENJTALK_DIR_NAME = 'open_jtalk'

# openjtalkの音声格納フォルダー名
OPENJTALK_VOICES_DIR_NAME = 'voices'

# openjtalkの辞書バージョン
DEFAULT_OPENJTALK_DIC_VER = '1.03'
OPENJTALK_DIC_VER = DEFAULT_OPENJTALK_DIC_VER

# openjtalk内部のmecabの文字セット
DEFAULT_OPENJTALK_CHARSET = 'UTF-8'
OPENJTALK_CHARSET = DEFAULT_OPENJTALK_CHARSET

# aqurstalk2 関連フォルダ名
AQUESTALK2_DIR_NAME = 'aquestalk2'

# 音素データベースのディレクトリ名
PHONT_DIR_NAME = 'phont'

# ユーザ指定のMeCab辞書フォルダ
MECAB_DIC_BASE = ''

# 標準で使用するmecab辞書の名前
DIC_NAME = mecab_unidic.UniDic.name

# 標準の音声名
DEFAULT_VOICE = u'MBROLA.' + mb_jp1.JP1.name

# 標準のMBLORA音素データベースファイル名
DEFAULT_DATABASE = mb_jp2.JP2.name

# OPEN JTALKの標準パラメータ
OPENJTALK_A  = 0.075
OPENJTALK_G  = 0
OPENJTALK_U  = 0.5
OPENJTALK_Z  = 1600
OPENJTALK_JM = 1.0
OPENJTALK_JF = 1.0
OPENJTALK_JL = 1.0

##### プラットフォーム依存定数 #####

## 省略時の値 ##

# 設定ファイル保存先(省略時の値)
CONFIG_DIR_PATH = None

# mbrola実行ファイルの名前
MBROLA_NAME = 'mbrola'

# aquestalk2 dll ファイルの名前
AQUESTALK2_NAME = 'libAquesTalk2Eva.so.2.1'

# openjtalk 実行ファイルの名前
OPENJTALK_NAME = 'open_jtalk'

# 文字コードの設定
ps = platform.system()
if ps == "Windows":

	# MeCab 文字コード
	MECAB_CHARSET = 'sjis'

	# システム文字コード（入出力標準文字コード）
	SYSTEM_CHARSET = 'sjis'

	# テキストファイル標準文字コード
	TEXT_CHARSET = 'sjis'

	# 設定ディレクトリ
	CONFIG_DIR_PATH = os.path.join( os.environ['HOMEDRIVE'] + os.environ['HOMEPATH'], '.' + PACKAGE_NAME )

	# mbrola実行ファイルの名前
	MBROLA_NAME = 'mbrola.exe'

	# aquestalk2 dll ファイルの名前
	AQUESTALK2_NAME = 'AquesTalk2.dll'

	# openjtalk実行ファイルの名前
	OPENJTALK_NAME = 'open_jtalk.exe'


elif ps == "Linux":

	# ビット数
	bit = platform.architecture()[0]
	if bit == '32bit':
		bit = 32
	elif bit == '64bit':
		bit = 64
	else:
		print u'システムのビット数が ' +  bit + u' です。'
		print u'このシステムには対応していません。'
		print platform.platform()
		sys.exit(-1)

	pp = platform.platform()
	if pp.find("Ubuntu") != -1:

		# MeCab 文字コード
		MECAB_CHARSET = 'euc-jp'

		# システム文字コード（入出力標準文字コード）
		SYSTEM_CHARSET = 'utf8'

		# テキストファイル標準文字コード
		TEXT_CHARSET = 'utf8'

		# 設定ディレクトリ
		CONFIG_DIR_PATH = os.path.join( os.environ['HOME'], '.' + PACKAGE_NAME )


elif ps == "Darwin":

	# MeCab 文字コード
	MECAB_CHARSET = 'utf8'

	# システム文字コード（入出力標準文字コード）
	SYSTEM_CHARSET = 'utf8'

	# テキストファイル標準文字コード
	TEXT_CHARSET = 'utf8'

	# 設定ディレクトリ
	CONFIG_DIR_PATH = os.path.join( os.environ['HOME'], '.' + PACKAGE_NAME )

	# mbrola実行ファイルの名前
	MBROLA_NAME = 'mbrola-darwin-ppc'

	# aquestalk2 dll ファイルの名前
	AQUESTALK2_NAME = 'AquesTalk2'


# 設定ディレクトリが決まっていないときは、仮にHOMEとする。
stop = False
if not CONFIG_DIR_PATH:
	try:
		CONFIG_DIR_PATH = os.path.join( os.environ['HOME'], '.' + PACKAGE_NAME )
	except:
		print u'環境変数HOMEが定義されていないシステムです。'
		print u'このシステムには対応していません。'
		print platform.platform()
		sys.exit(-1)

	# MeCab 文字コード
	MECAB_CHARSET = 'euc-jp'

	# システム文字コード（入出力標準文字コード）
	SYSTEM_CHARSET = 'utf8'

	# テキストファイル標準文字コード
	TEXT_CHARSET = 'utf8'

	# 設定ファイルが存在しなければ、作って終わるようにする
	if not os.path.exists( os.path.join( CONFIG_DIR_PATH, CONFIG_NAME ) ):
		stop = True


##### 設定ファイルから読み込み #####

# 設定ファイルの位置
CONFIG_PATH = os.path.join( CONFIG_DIR_PATH, CONFIG_NAME )

# 設定ファイルが存在するときはその値を優先する
if os.path.exists( CONFIG_PATH ):
	parser = ConfigParser.RawConfigParser()
	parser.read( CONFIG_PATH )

	section = PACKAGE_NAME
	if parser.has_section( section ):

#		options = parser.items( section )

		if parser.has_option( section, 'debug' ):
			DEBUG = parser.getint( section, 'debug' )

		if parser.has_option( section, 'accent_flag' ):
			ACCENT_FLAG = parser.getint( section, 'accent_flag' )

		if parser.has_option( section, 'reading_symbol_flag' ):
			READING_SYMBOL_FLAG = parser.getint( section, 'reading_symbol_flag' )

		if parser.has_option( section, 'mecab_charset' ):
			MECAB_CHARSET = parser.get( section, 'mecab_charset' )

		if parser.has_option( section, 'system_charset' ):
			SYSTEM_CHARSET = parser.get( section, 'system_charset' )

		if parser.has_option( section, 'text_charset' ):
			TEXT_CHARSET = parser.get( section, 'text_charset' )

		if parser.has_option( section, 'logfile_name' ):
			LOGFILE_NAME = parser.get( section, 'logfile_name' )
			LOGFILE_NAME = unicode( LOGFILE_NAME, 'utf8' )

		if parser.has_option( section, 'userdic_name' ):
			USERDIC_NAME = parser.get( section, 'userdic_name' )
			USERDIC_NAME = unicode( USERDIC_NAME, 'utf8' )

		if parser.has_option( section, 'default_file' ):
			DEFAULT_TEXT = parser.get( section, 'default_file' )
			DEFAULT_TEXT = unicode( DEFAULT_TEXT, 'utf8' )

		if parser.has_option( section, 'message_text' ):
			MESSAGE_TEXT = parser.get( section, 'message_text' )
			MESSAGE_TEXT = unicode( MESSAGE_TEXT, 'utf8' )

		if parser.has_option( section, 'openjtalk_dir_name' ):
			OPENJTALK_DIR_NAME = parser.get( section, 'openjtalk_dir_name' )
			OPENJTALK_DIR_NAME = unicode( OPENJTALK_DIR_NAME, 'utf8' )

		if parser.has_option( section, 'openjtalk_voices_dir_name' ):
			OPENJTALK_VOICES_DIR_NAME = parser.get( section, 'openjtalk_voices_dir_name' )
			OPENJTALK_VOICES_DIR_NAME = unicode( OPENJTALK_VOICES_DIR_NAME, 'utf8' )

		if parser.has_option( section, 'openjtalk_dic_ver' ):
			OPENJTALK_DIC_VER = parser.get( section, 'openjtalk_dic_ver' )
			OPENJTALK_DIC_VER = unicode( OPENJTALK_DIC_VER, 'utf8' )

		if parser.has_option( section, 'openjtalk_charset' ):
			OPENJTALK_CHARSET = parser.get( section, 'openjtalk_charset' )
			OPENJTALK_CHARSET = unicode( OPENJTALK_CHARSET, 'utf8' ).upper()
			if OPENJTALK_CHARSET != u'SHIFT_JIS' and OPENJTALK_CHARSET != u'EUC-JP':
				OPENJTALK_CHARSET = DEFAULT_OPENJTALK_CHARSET

		if parser.has_option( section, 'phont_dir_name' ):
			PHONT_DIR_NAME = parser.get( section, 'phont_dir_name' )
			PHONT_DIR_NAME = unicode( PHONT_DIR_NAME, 'utf8' )

		if parser.has_option( section, 'mecab_dic_base' ):
			MECAB_DIC_BASE = parser.get( section, 'mecab_dic_base' )
			MECAB_DIC_BASE = unicode( MECAB_DIC_BASE, 'utf8' )

		if parser.has_option( section, 'dic_name' ):
			DIC_NAME = parser.get( section, 'dic_name' )
			DIC_NAME = unicode( DIC_NAME, 'utf8' )

		if parser.has_option( section, 'default_voice' ):
			DEFAULT_VOICE = parser.get( section, 'default_voice' )
			DEFAULT_VOICE = unicode( DEFAULT_VOICE, 'utf8' )

		if parser.has_option( section, 'default_database' ):
			DEFAULT_DATABASE = parser.get( section, 'default_database' )
			DEFAULT_DATABASE = unicode( DEFAULT_DATABASE, 'utf8' )

		if parser.has_option( section, 'mbrola_name' ):
			MBROLA_NAME = parser.get( section, 'mbrola_name' )
			MBROLA_NAME = unicode( MBROLA_NAME, 'utf8' )

		if parser.has_option( section, 'aquestalk2_dir_name' ):
			AQUESTALK2_DIR_NAME = parser.get( section, 'aquestalk2_dir_name' )
			AQUESTALK2_DIR_NAME = unicode( AQUESTALK2_DIR_NAME, 'utf8' )

		if parser.has_option( section, 'aquestalk2_name' ):
			AQUESTALK2_NAME = parser.get( section, 'aquestalk2_name' )
			AQUESTALK2_NAME = unicode( AQUESTALK2_NAME, 'utf8' )

		if parser.has_option( section, 'openjtalk_name' ):
			OPENJTALK_NAME = parser.get( section, 'openjtalk_name' )
			OPENJTALK_NAME = unicode( OPENJTALK_NAME, 'utf8' )

		if parser.has_option( section, 'openjtalk_a' ):
			OPENJTALK_A = parser.getfloat( section, 'openjtalk_a' )

		if parser.has_option( section, 'openjtalk_g' ):
			OPENJTALK_G = parser.getint( section, 'openjtalk_g' )

		if parser.has_option( section, 'openjtalk_u' ):
			OPENJTALK_U = parser.getfloat( section, 'openjtalk_u' )

		if parser.has_option( section, 'openjtalk_z' ):
			OPENJTALK_Z = parser.getint( section, 'openjtalk_z' )

		if parser.has_option( section, 'openjtalk_jm' ):
			OPENJTALK_JM = parser.getfloat( section, 'openjtalk_jm' )

		if parser.has_option( section, 'openjtalk_jf' ):
			OPENJTALK_JF = parser.getfloat( section, 'openjtalk_jf' )

		if parser.has_option( section, 'openjtalk_jl' ):
			OPENJTALK_JL = parser.getfloat( section, 'openjtalk_jl' )


#### 定数を元に作成する定数 ####

# MBROLA音素データベースのディレクトリのパス
DATABASE_DIR_PATH = CONFIG_DIR_PATH

# OPENJTALK関連ディレクトリのパス(実在は不問)
if os.path.exists( os.path.join( CONFIG_DIR_PATH, OPENJTALK_DIR_NAME ) ):
	OPENJTALK_DIR_PATH = os.path.join( CONFIG_DIR_PATH, OPENJTALK_DIR_NAME )
else:
	OPENJTALK_DIR_PATH = CONFIG_DIR_PATH

# AQUESTALK2関連ディレクトリのパス(実在は不問)
if AQUESTALK2_DIR_NAME:
	AQUESTALK2_DIR_PATH = os.path.join( CONFIG_DIR_PATH, AQUESTALK2_DIR_NAME )
else:
	AQUESTALK2_DIR_PATH = CONFIG_DIR_PATH

# AquesTalk2 の声種ファイルの格納ディレクトリのパス(実在は不問)
if AQUESTALK2_DIR_PATH:
	PHONT_DIR_PATH = os.path.join( AQUESTALK2_DIR_PATH, PHONT_DIR_NAME )
else:
	PHONT_DIR_PATH = None

# MBROLA実行ファイルのパス
# 無ければ None
if os.path.exists( os.path.join( CONFIG_DIR_PATH, MBROLA_NAME ) ):
	MBROLA_PATH = os.path.join( CONFIG_DIR_PATH, MBROLA_NAME )
else:
	MBROLA_PATH = MBROLA_NAME if exists(MBROLA_NAME) else None

# AQUESTALK2 DLLファイルのパス
# 無ければ None
if os.path.exists( os.path.join( AQUESTALK2_DIR_PATH, AQUESTALK2_NAME ) ):
	AQUESTALK2_PATH = os.path.join( AQUESTALK2_DIR_PATH, AQUESTALK2_NAME )
else:
	try:
		cdll.LoadLibrary(AQUESTALK2_NAME)
		AQUESTALK2_PATH = AQUESTALK2_NAME
	except OSError:
		AQUESTALK2_PATH = None

# OPENJTALK実行ファイルのパス
if OPENJTALK_DIR_PATH != None and os.path.exists( os.path.join( OPENJTALK_DIR_PATH, OPENJTALK_NAME ) ):
	OPENJTALK_PATH = os.path.join( OPENJTALK_DIR_PATH, OPENJTALK_NAME )
else:
	OPENJTALK_PATH = OPENJTALK_NAME if exists(OPENJTALK_NAME) else None

# 処理できるMBROLAデータベースの一覧
DATABASES = {
	mb_jp1.JP1.name:mb_jp1.JP1,
	mb_jp2.JP2.name:mb_jp2.JP2,
	mb_jp3.JP3.name:mb_jp3.JP3,
}

# アーカイブがあれば展開する
if DATABASES:
	for i in os.listdir(DATABASE_DIR_PATH):
		m = re.match('(jp[123].*)\.zip$',i)
		if m:
			extract_zip(DATABASE_DIR_PATH,m.group(1))

# aquestalk2 のルートに置かれた声種アーカイブは音声フォルダに移す
if AQUESTALK2_DIR_PATH:
	if os.path.exists(AQUESTALK2_DIR_PATH):
		for i in os.listdir(AQUESTALK2_DIR_PATH):
			if re.match('(aq_.+)\.zip$',i):
				if not os.path.exists(PHONT_DIR_PATH):
					os.mkdir(PHONT_DIR_PATH)
				shutil.move(os.path.join(AQUESTALK2_DIR_PATH,i),os.path.join(PHONT_DIR_PATH,i))


# 使用できるaquestalk2声種の一覧
PHONTS = []
if os.path.exists(PHONT_DIR_PATH):
	for i in os.listdir(PHONT_DIR_PATH):
		m = re.match( '(aq_.+)\.zip$', i )
		if m:
			extract_zip(PHONT_DIR_PATH,m.group(1))

	for i in os.listdir(PHONT_DIR_PATH):
		m = re.match( '(.+)\.phont$', i )
		if m:
			PHONTS.append(m.group(1).lower())

# openjtalkの音声ディレクトリのパス
if OPENJTALK_DIR_PATH:
	OPENJTALK_VOICES_PATH = os.path.join( OPENJTALK_DIR_PATH, OPENJTALK_VOICES_DIR_NAME )
else:
	OPENJTALK_VOICES_PATH = None

# OPENJTALK のルートに置かれた音声アーカイブは音声フォルダに移す
if OPENJTALK_DIR_PATH:
	if os.path.exists(OPENJTALK_DIR_PATH):
		for i in os.listdir(OPENJTALK_DIR_PATH):
			if re.match('hts_voice_.*\.tar\.gz$',i):
				if not os.path.exists(OPENJTALK_VOICES_PATH):
					os.mkdir(OPENJTALK_VOICES_PATH)
				shutil.move(os.path.join(OPENJTALK_DIR_PATH,i),os.path.join(OPENJTALK_VOICES_PATH,i))

# openjtalk の音声フォルダーの一覧
# tar.gz ファイルのみのときは展開する。展開済みのときは何もしない。
OPENJTALK_VOICES = []
if OPENJTALK_VOICES_PATH:
	if os.path.exists(OPENJTALK_VOICES_PATH):
		for i in os.listdir(OPENJTALK_VOICES_PATH):
			if os.path.exists(os.path.join(OPENJTALK_VOICES_PATH,i)):
				m = re.match('(.+)\.tar\.gz$',i)
				if m:
					extract_targz(OPENJTALK_VOICES_PATH,m.group(1))

		for i in os.listdir(OPENJTALK_VOICES_PATH):
			if os.path.exists(os.path.join(OPENJTALK_VOICES_PATH,i)):
				if not re.search('\.tar\.gz$',i):
#					print u'Open JTalkの音声リストに ',i,u'を追加しました。'
					OPENJTALK_VOICES.append(i)

# ユーザ簡易辞書パス
USER_DIC_PATH = os.path.join( CONFIG_DIR_PATH, USERDIC_NAME )

# ログファイルパス
LOGFILE_PATH = os.path.join( CONFIG_DIR_PATH, LOGFILE_NAME )

# openjtalkの辞書フォルダー名
if not OPENJTALK_DIC_VER:
	OPENJTALK_DIC_VER = DEFAULT_OPENJTALK_DIC_VER

charset = u'utf_8'
if OPENJTALK_CHARSET:
	if OPENJTALK_CHARSET == 'SHIFT_JIS':
		charset = u'shift_jis'
	elif OPENJTALK_CHARSET == 'EUC-JP':
		charset = u'euc_jp'

# 辞書の名前
OPENJTALK_DIC_NAME = u'open_jtalk_dic_' + charset + u'-' + OPENJTALK_DIC_VER

# openjtalkの辞書のパス
OPENJTALK_DIC_PATH = None
if OPENJTALK_DIR_PATH:
	if os.path.exists( os.path.join( OPENJTALK_DIR_PATH, OPENJTALK_DIC_NAME + '.tar.gz' ) ):
		extract_targz(OPENJTALK_DIR_PATH,OPENJTALK_DIC_NAME)
	if os.path.exists( os.path.join( OPENJTALK_DIR_PATH, OPENJTALK_DIC_NAME ) ):
		OPENJTALK_DIC_PATH = os.path.join( OPENJTALK_DIR_PATH, OPENJTALK_DIC_NAME )



#### 現在の設定を書き込む ####

parser = ConfigParser.RawConfigParser()

section = PACKAGE_NAME
parser.add_section(section)
parser.set( section, 'debug', str(DEBUG) )
parser.set( section, 'accent_flag', str(ACCENT_FLAG) )
parser.set( section, 'reading_symbol_flag', str(READING_SYMBOL_FLAG) )
parser.set( section, 'mecab_charset', MECAB_CHARSET.encode('utf8') )
parser.set( section, 'system_charset', SYSTEM_CHARSET.encode('utf8') )
parser.set( section, 'text_charset', TEXT_CHARSET.encode('utf8') )
parser.set( section, 'logfile_name', LOGFILE_NAME.encode('utf8') )
parser.set( section, 'userdic_name', USERDIC_NAME.encode('utf8') )
parser.set( section, 'default_file', DEFAULT_TEXT.encode('utf8') )
parser.set( section, 'message_text', MESSAGE_TEXT.encode('utf8') )
parser.set( section, 'openjtalk_dir_name', OPENJTALK_DIR_NAME.encode('utf8') )
parser.set( section, 'openjtalk_voices_dir_name', OPENJTALK_VOICES_DIR_NAME.encode('utf8') )
parser.set( section, 'openjtalk_dic_ver', OPENJTALK_DIC_VER.encode('utf8') )
parser.set( section, 'openjtalk_charset', OPENJTALK_CHARSET.encode('utf8') )
parser.set( section, 'phont_dir_name', PHONT_DIR_NAME.encode('utf8') )
parser.set( section, 'mecab_dic_base', MECAB_DIC_BASE.encode('utf8') )
parser.set( section, 'dic_name', DIC_NAME.encode('utf8') )
parser.set( section, 'default_voice', DEFAULT_VOICE.encode('utf8') )
parser.set( section, 'default_database', DEFAULT_DATABASE.encode('utf8') )
parser.set( section, 'mbrola_name', MBROLA_NAME.encode('utf8') )
parser.set( section, 'aquestalk2_dir_name', AQUESTALK2_DIR_NAME.encode('utf8') )
parser.set( section, 'aquestalk2_name', AQUESTALK2_NAME.encode('utf8') )
parser.set( section, 'openjtalk_name', OPENJTALK_NAME.encode('utf8') )

parser.set( section, 'openjtalk_a',  str(OPENJTALK_A ) )
parser.set( section, 'openjtalk_g',  str(OPENJTALK_G ) )
parser.set( section, 'openjtalk_u',  str(OPENJTALK_U ) )
parser.set( section, 'openjtalk_z',  str(OPENJTALK_Z ) )
parser.set( section, 'openjtalk_jm', str(OPENJTALK_JM) )
parser.set( section, 'openjtalk_jf', str(OPENJTALK_JF) )
parser.set( section, 'openjtalk_jl', str(OPENJTALK_JL) )

# 設定ファイルを作る
f = open( CONFIG_PATH, 'w')
parser.write(f)
f.close()


#### 仮設定のときはメッセージを出力して終了 ####
if stop:
	print u'未対応のシステムです。'
	print u'仮の設定を ' + CONFIG_PATH  + u' に書き込みました。'
	print u'このファイルをシステムにあわせて書き換えて、もう一度起動してみてください。'
	sys.exit(-3)

