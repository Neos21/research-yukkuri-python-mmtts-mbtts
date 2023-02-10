# -*- coding: utf8 -*-
# mbtts_variable.py
# mbtts 0.95
# 2010/03/25
# copyright(c) takayan
# http://neu101.seesaa.net/

import platform
import os
import sys
import ConfigParser

import mb_jp1
import mb_jp2
import mb_jp3

import mecab_ipadic
import mecab_unidic


##### 変数 #####

# デバッグ
DEBUG = 0

# パッケージ名
PACKAGE_NAME = 'mbtts'

# 設定ファイル保存先
CONFIG_DIR = None

# 設定ファイル名
CONFIG_NAME = "config.txt"

#ログファイル名
LOGFILE_NAME = "log.txt"

# ユーザ簡易辞書名
USERDIC_NAME = "userdic.txt"

# 自動読み上げ対象ファイル名
DEFAULT_TEXT = 'text.txt'

# 挨拶文字列
MESSAGE_TEXT = u'世界のみなさん、こんにちは'

# アクセントを有効にするかのフラグ
ACCENT_FLAG = 1

# 記号を読むかどうかのフラグ
READING_SYMBOL_FLAG = 0

# mbrola実行ファイルの名前
MBROLA_NAME = 'mbrola'


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
	CONFIG_DIR = os.path.join( os.environ['HOMEDRIVE']
		+ os.environ['HOMEPATH'], '.' + PACKAGE_NAME )

	# mbrola実行ファイルの名前
	MBROLA_NAME = 'mbrola.exe'

elif ps == "Linux":
	pp = platform.platform()
	if pp.find("Ubuntu") != -1:

		# MeCab 文字コード
		MECAB_CHARSET = 'euc-jp'

		# システム文字コード（入出力標準文字コード）
		SYSTEM_CHARSET = 'utf8'

		# テキストファイル標準文字コード
		TEXT_CHARSET = 'utf8'

		# 設定ディレクトリ
		CONFIG_DIR = os.path.join( os.environ['HOME'], '.' + PACKAGE_NAME )

elif ps == "Darwin":

	# MeCab 文字コード
	MECAB_CHARSET = 'utf8'

	# システム文字コード（入出力標準文字コード）
	SYSTEM_CHARSET = 'utf8'

	# テキストファイル標準文字コード
	TEXT_CHARSET = 'utf8'

	# 設定ディレクトリ
	CONFIG_DIR = os.path.join( os.environ['HOME'], '.' + PACKAGE_NAME )

	# mbrola実行ファイルの名前
	MBROLA_NAME = 'mbrola-darwin-ppc'



# 設定ディレクトリが決まっていないときは、仮にHOMEとする。
stop = False
if not CONFIG_DIR:
	try:
		CONFIG_DIR = os.path.join( os.environ['HOME'], '.' + PACKAGE_NAME )
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
	if not os.path.exists( os.path.join( CONFIG_DIR, CONFIG_NAME ) ):
		stop = True


# 使用できる辞書の一覧
DICS = {
	mecab_ipadic.IpaDic.name:mecab_ipadic.IpaDic,
	mecab_unidic.UniDic.name:mecab_unidic.UniDic,
}

# 標準で使用する辞書の名前
DIC_NAME = mecab_unidic.UniDic.name

# 使用できるデータベースの一覧
DATABASES = {
	mb_jp1.JP1.name:mb_jp1.JP1,
	mb_jp2.JP2.name:mb_jp2.JP2,
	mb_jp3.JP3.name:mb_jp3.JP3,
}

# 標準の音素データベースファイル名
DATABASE_NAME = mb_jp2.JP2.name

# 音素データベースのディレクトリ
DATABASE_DIR = CONFIG_DIR

# MBROLA実行ファイルが置いてあるパス
if os.path.exists( os.path.join( CONFIG_DIR, MBROLA_NAME ) ):
	MBROLA_PATH = os.path.join( CONFIG_DIR, MBROLA_NAME )
else:
	MBROLA_PATH = MBROLA_NAME

# ユーザ指定のMeCab辞書フォルダ
MECAB_DIC_BASE = ''

# 設定ファイル
CONFIG_PATH = os.path.join( CONFIG_DIR, CONFIG_NAME )


# 設定ファイルが存在するときはその値を優先する
if os.path.exists( CONFIG_PATH ):
	parser = ConfigParser.RawConfigParser()
	parser.read( CONFIG_PATH )

	section = PACKAGE_NAME
	if parser.has_section( section ):

		options = parser.items( section )

		if parser.has_option( section, 'mecab_dic_base' ):
			MECAB_DIC_BASE = parser.get( section, 'mecab_dic_base' )
			MECAB_DIC_BASE = unicode( MECAB_DIC_BASE, 'utf8' )

		if parser.has_option( section, 'mecab_charset' ):
			MECAB_CHARSET = parser.get( section, 'mecab_charset' )

		if parser.has_option( section, 'system_charset' ):
			SYSTEM_CHARSET = parser.get( section, 'system_charset' )

		if parser.has_option( section, 'text_charset' ):
			TEXT_CHARSET = parser.get( section, 'text_charset' )

		if parser.has_option( section, 'default_file' ):
			DEFAULT_TEXT = parser.get( section, 'default_file' )
			DEFAULT_TEXT = unicode( DEFAULT_TEXT, 'utf8' )

		if parser.has_option( section, 'message_text' ):
			MESSAGE_TEXT = parser.get( section, 'message_text' )
			MESSAGE_TEXT = unicode( MESSAGE_TEXT, 'utf8' )

		if parser.has_option( section, 'dic_name' ):
			DIC_NAME = parser.get( section, 'dic_name' )
			DIC_NAME = unicode( DIC_NAME, 'utf8' )

		if parser.has_option( section, 'database_name' ):
			DATABASE_NAME = parser.get( section, 'database_name' )
			DATABASE_NAME = unicode( DATABASE_NAME, 'utf8' )

		if parser.has_option( section, 'logfile_name' ):
			LOGFILE_NAME = parser.get( section, 'logfile_name' )
			LOGFILE_NAME = unicode( LOGFILE_NAME, 'utf8' )

		if parser.has_option( section, 'userdic_name' ):
			USERDIC_NAME = parser.get( section, 'userdic_name' )
			USERDIC_NAME = unicode( USERDIC_NAME, 'utf8' )

		if parser.has_option( section, 'debug' ):
			DEBUG = parser.getint( section, 'debug' )

		if parser.has_option( section, 'accent_flag' ):
			ACCENT_FLAG = parser.getint( section, 'accent_flag' )

		if parser.has_option( section, 'reading_symbol_flag' ):
			READING_SYMBOL_FLAG = parser.getint( section, 'reading_symbol_flag' )


# 存在しなければ、現在の設定を書き込む
else:
	parser = ConfigParser.RawConfigParser()

	section = PACKAGE_NAME
	parser.add_section(section)
	parser.set( section, 'mecab_dic_base', MECAB_DIC_BASE.encode('utf8') )
	parser.set( section, 'mecab_charset', MECAB_CHARSET.encode('utf8') )
	parser.set( section, 'system_charset', SYSTEM_CHARSET.encode('utf8') )
	parser.set( section, 'text_charset', TEXT_CHARSET.encode('utf8') )
	parser.set( section, 'default_file', DEFAULT_TEXT.encode('utf8') )
	parser.set( section, 'message_text', MESSAGE_TEXT.encode('utf8') )
	parser.set( section, 'dic_name', DIC_NAME.encode('utf8') )
	parser.set( section, 'database_name', DATABASE_NAME.encode('utf8') )
	parser.set( section, 'logfile_name', LOGFILE_NAME.encode('utf8') )
	parser.set( section, 'userdic_name', USERDIC_NAME.encode('utf8') )
	parser.set( section, 'debug', str(DEBUG) )
	parser.set( section, 'accent_flag', str(ACCENT_FLAG) )
	parser.set( section, 'reading_symbol_flag', str(READING_SYMBOL_FLAG) )

	# 設定ファイルを作る
	f = open( CONFIG_PATH, 'w')
	parser.write(f)
	f.close()


# 設定内容を踏まえての変数設定

# ユーザ簡易辞書パス
USER_DIC = os.path.join( CONFIG_DIR, USERDIC_NAME )

# ログファイルパス
LOGFILE = os.path.join( CONFIG_DIR, LOGFILE_NAME )

# 仮設定のときは終了
if stop:
	print u'未対応のシステムです。'
	print u'仮の設定を ' + CONFIG_PATH  + u' に書き込みました。'
	print u'このファイルをシステムにあわせて書き換えて、もう一度起動してみてください。'
	print sys.exit(-3)
	
