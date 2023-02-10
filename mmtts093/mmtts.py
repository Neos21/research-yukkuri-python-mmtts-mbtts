#!/usr/bin/env python
# -*- coding: utf8 -*-
# mmtts.py 0.93
# MBROLA JP2データベース専用の音声変換
# 2010/03/08
# copyright(c) takayan
# http://neu101.seesaa.net/

import os
import re
import sys
import MeCab
import tempfile
import platform
from optparse import OptionParser
if platform.system() == "Windows":
	import winsound
	import pho2wav


##### 変数 #####

# デバッグ
DEBUG = 0

# 文字コードの設定
ps = platform.system()
if ps == "Windows":

	# MeCab 文字コード
	mecab_charset = 'sjis'

	# システム文字コード（入出力標準文字コード）
	system_charset = 'sjis'

	# テキストファイル標準文字コード
	text_charset = 'sjis'

elif ps == "Linux":
	pp = platform.platform()
	if pp.find("Ubuntu") != -1:

		# MeCab 文字コード
		mecab_charset = 'euc-jp'
		#mecab_charset = 'utf8'

		# システム文字コード（入出力標準文字コード）
		system_charset = 'utf8'

		# テキストファイル標準文字コード
		text_charset = 'utf8'

try:
	mecab_charset + system_charset + text_charset
except:
	print u'未知のシステムのため文字コードの値が正しく設定されていません。\n適切に設定してから、もう一度やり直してください。'
	sys.exit()


# 自動読み上げ対象ファイル名
text = 'text.txt'

# 挨拶文字列
message = u'こんにちは'

# アクセントを有効にするかのフラグ
accent_mode = 1

# 記号を読むかどうかのフラグ
reading_symbol_mode = 0

# 使用する辞書の名前
dics = (
	u'ipadic',
	u'unidic',
)
default_dic = 1
dic_name = dics[default_dic]
#    辞書を追加するときは、ここに名前を追加し、コンストラクタにディレクトリを選択するif文を追加し、
#    txt2phoメソッド内に どの結果を使うかの処理を書き込む必要がある

# 音素データベースファイルの場所
database = 'jp2'

# 音素データベースが呼び出しディレクトリになければ、スクリプトのあるディレクトリを探す
if not os.path.isfile(database):
	database = os.path.dirname(__file__) + '\\' + database

# ログファイルの名前
logfile = "log.txt"


##### クラス #####

# jp2用の音素に変換するクラス
# PHOを生成するまでの処理を担当する
# 将来的には、基底クラスを用意して他の音素データベース向けクラスも作る

class Phenomen:
	"""JP2用の音素ファイルを生成するためのクラス
	"""

	##### コンストラクタ #####
	def __init__(self,name):
		global logfile,mecab_charset,reading_symbol_mode,accent_mode

		# ログファイルを作る
		if DEBUG:
			self.log = Log(logfile)

		# 標準音量比率
		self.volume = 1.0

		# 標準読み上げ速度比率
		self.rate = 1.0

		# 標準ピッチ比率
		self.pitch = 1.0

		self.userdic = 'userdic.txt'		# 簡易辞書の場所
		self.acc_diff       =  40		# アクセントのピッチ差
		self.ques_diff      =  40		# 疑問語尾のピッチ差
		self.finish_rest    = 100		# 終了後の休止時間
		self.default_pt     = 220		# 標準のピッチ
		self.default_po     =  50		# 標準のピッチ位置
		self.default_ms     = 150		# 標準の音素の母音発音時間
		self.default_scale  = 1.0		# 標準の音素の読み上げ速度補正(母音長150の値を調整するための値)

		self.flag_reading_symbol = reading_symbol_mode	# 記号を読むかどうかのフラグ

		self.use_accent = accent_mode				# アクセントを処理するかのフラグ

		# MeCab用辞書のパス
		ipadicdir = ''
		unidicdir   = ''
		ps = platform.system()
		if ps == "Windows":

			# MeCabパッケージが標準の位置にインストールされているとする
			if os.path.isdir("C:\\Program Files\MeCab\\dic"):
				ipadicdir = 'C:\\progra~1\\MeCab\\dic\\ipadic'
				unidicdir = 'C:\\progra~1\\MeCab\\dic\\unidic'

			# Unidicパッケージが標準の位置にインストールされているときは、よりそちらを優先する
			if os.path.isdir("C:\\Program Files\unidic\\dic"):
				unidicdir = 'C:\\progra~1\\unidic\\dic\\unidic-mecab'
				mecab_charset = 'utf8'

		elif ps == "Linux":
			pp = platform.platform()
			if pp.find("Ubuntu")!=-1:
				# debパッケージからのインストール
				if os.path.isdir("/var/lib/mecab/dic/"):
					if mecab_charset == 'utf8':
						ipadicdir = '/var/lib/mecab/dic/ipadic-utf8'
						unidicdir = '/var/lib/mecab/dic/unidic-utf8'
					else:
						ipadicdir = '/var/lib/mecab/dic/ipadic'
						unidicdir = '/var/lib/mecab/dic/unidic'
						mecab_charset = 'euc-jp'
				# ソースからインストールした場合はそのパスを次に記述しておく
				else:
					ipadicdir = ''
					unidicdir = ''
			else:
				sys.stderr.write( u"このlinuxディストリビューションへの対応は不明です。\nスクリプトを修正してから利用してください。\n"
															.encode( system_charset ) )
				sys.exit()
		else:
			sys.stderr.write( u"このシステムには対応していません\n".encode( system_charset ) )
			sys.exit()

		# パラメータを辞書名として登録する
		self.mecab_dic_name = name

		# 辞書ディレクトリの設定
		if self.mecab_dic_name == u'ipadic':
			mecab_dic_dir = ipadicdir
			self.use_accent = 0
		elif self.mecab_dic_name == u'unidic':
			mecab_dic_dir = unidicdir
			if not os.path.isdir(mecab_dic_dir):
				mecab_dic_dir = ipadicdir
				self.mecab_dic_name = u'ipadic'
				self.use_accent = 0
		else:
			sys.stderr.write( ( u'辞書 ' + self.mecab_dic_name + u' には現在対応していません。\n').encode( system_charset ) )
			sys.exit()

		# MeCab辞書の存在を確認する
		if not mecab_dic_dir:
			sys.stderr.write( (u'辞書 ' + self.mecab_dic_name + u' のパスが分かりません。\nスクリプトを修正してから利用してください。\n').encode( system_charset ) )
			sys.exit()
		if not os.path.isdir(mecab_dic_dir):
			sys.stderr.write( (u'辞書 ' + self.mecab_dic_name + u' が見つかりません。\n').encode( system_charset ) )
			sys.exit()

		# MeCabクラス初期化、辞書の指定
		self.mecab = MeCab.Tagger( " -d " + mecab_dic_dir )

		# 簡易辞書
		if not os.path.isfile(self.userdic):
			self.userdic = os.path.dirname(__file__) + '\\' + self.userdic
		self.dic_enable = self.load_userdic()

	##### デストラクタ #####
	def __del__(self):
		pass


	### JP2 音素データ ###

	# 母音長表
	phone_duration_vowel = {
	# 母音
		'a'   :  150,
		'i'   :  150,
		'u'   :  150,
		'e'   :  150,
		'o'   :  150,
	# 長母音
		'a:'  :  300,
		'i:'  :  300,
		'u:'  :  300,
		'e:'  :  300,
		'o:'  :  300,
	# 無声母音
		'i_0' :  150,
		'u_0' :  150,
	# 促音記号
	    'Q'   :  150,
	# 撥音記号
		'X'   :  150,
	# ポーズ(終止)
		'_'   :  150,
		','   :  100,
	}


	# 子音長表
	phone_duration_consonant= {
		'k'  : 100,
		's'  : 100,
		't'  :  50,
		'm'  :  50,
		'n'  :  50,
		'n1' :  50,
		'h'  :  50,
		'f'  :  50,
		'C'  :  50,
		'j'  :  50,
		'r'  :  50,
		'w'  :  50,
		'S'  : 100,
		'tS' : 100,
		'ts' : 100,
		'g'  :  50,
		'dz' :  50,
		'z'  : 100,
		'Z'  : 100,
		'dZ' : 100,
		'd'  :  50,
		'b'  :  50,
		'p'  :  50,
		'f'  :  50,
		'ts' :  50,
	}


	# 撥音対応表（後続の音素：本来の撥音記号）
	phone_N_map = {
		'a' : 'N:',
		'i' : 'N:',
		'u' : 'N:',
		'e' : 'N:',
		'o' : 'N:',
		'a:': 'N:',
		'i:': 'N:',
		'u:': 'N:',
		'e:': 'N:',
		'o:': 'N:',
		's' : 'N:',
		'h' : 'N:',
		'f' : 'N:',
		'S' : 'N:',
		'C' : 'N:',
		'w' : 'N:',
		'g' : 'G:',
		'k' : 'G:',
		't' : 'n:',
		'r' : 'n:',
		'dZ': 'n:',
		'dz': 'n:',
		'j' : 'N:',
		'ts': 'n:',
		'tS': 'n:',
		'd' : 'n:',
		'b' : 'm:',
		'p' : 'm:',
		'm' : 'm:',
		'n' : 'n:',
		'n1': 'n1:',
		'_' : 'N:',
		'!' : 'N:',
		'?' : 'N:',
		'.' : 'N:',
		',' : 'N:',
		'Q' : 'N:',
		'z' : 'N:',
		'Z' : 'N:',
	}


	# 文頭/撥音のあとに来たときに置き換える音の表
	phone_head_remap = {
		'Z' : 'dZ',
		'z' : 'dz',
	}

	# 仮名文字をアルファベットに変換するテーブル
	convert_table = {
		u'ア':['a'],
		u'あ':['a'],
		u'イ':['i'],
		u'い':['i'],
		u'ウ':['u'],
		u'う':['u'],
		u'エ':['e'],
		u'え':['e'],
		u'オ':['o'],
		u'お':['o'],
		u'カ':['k','a'],
		u'か':['k','a'],
		u'キ':['k','i'],
		u'き':['k','i'],
		u'ク':['k','u'],
		u'く':['k','u'],
		u'ケ':['k','e'],
		u'け':['k','e'],
		u'コ':['k','o'],
		u'こ':['k','o'],
		u'サ':['s','a'],
		u'さ':['s','a'],
		u'シ':['S','i'],
		u'し':['S','i'],
		u'ス':['s','u'],
		u'す':['s','u'],
		u'セ':['s','e'],
		u'せ':['s','e'],
		u'ソ':['s','o'],
		u'そ':['s','o'],
		u'タ':['t','a'],
		u'た':['t','a'],
		u'チ':['tS','i'],
		u'ち':['tS','i'],
		u'ツ':['ts','u'],
		u'つ':['ts','u'],
		u'テ':['t','e'],
		u'て':['t','e'],
		u'ト':['t','o'],
		u'と':['t','o'],
		u'ナ':['n','a'],
		u'な':['n','a'],
		u'ニ':['n1','i'],
		u'に':['n1','i'],
		u'ヌ':['n','u'],
		u'ぬ':['n','u'],
		u'ネ':['n','e'],
		u'ね':['n','e'],
		u'ノ':['n','o'],
		u'の':['n','o'],
		u'ハ':['h','a'],
		u'は':['h','a'],
		u'ヒ':['C','i'],
		u'ひ':['C','i'],
		u'フ':['f','u'],
		u'ふ':['f','u'],
		u'ヘ':['h','e'],
		u'へ':['h','e'],
		u'ホ':['h','o'],
		u'ほ':['h','o'],
		u'マ':['m','a'],
		u'ま':['m','a'],
		u'ミ':['m','i'],
		u'み':['m','i'],
		u'ム':['m','u'],
		u'む':['m','u'],
		u'メ':['m','e'],
		u'め':['m','e'],
		u'モ':['m','o'],
		u'も':['m','o'],
		u'ヤ':['j','a'],
		u'や':['j','a'],
		u'ユ':['j','u'],
		u'ゆ':['j','u'],
		u'ヨ':['j','o'],
		u'よ':['j','o'],
		u'ラ':['r','a'],
		u'ら':['r','a'],
		u'リ':['r','i'],
		u'り':['r','i'],
		u'ル':['r','u'],
		u'る':['r','u'],
		u'レ':['r','e'],
		u'れ':['r','e'],
		u'ロ':['r','o'],
		u'ろ':['r','o'],
		u'ワ':['w','a'],
		u'わ':['w','a'],
		u'ヮ':['w','a'],
		u'ゎ':['w','a'],
		u'ヰ':['w','i'],
		u'ゐ':['w','i'],
		u'ヱ':['w','e'],
		u'ゑ':['w','e'],
		u'ヲ':['w','o'],
		u'を':['w','o'],
		u'ガ':['g','a'],
		u'が':['g','a'],
		u'ギ':['g','i'],
		u'ぎ':['g','i'],
		u'グ':['g','u'],
		u'ぐ':['g','u'],
		u'ゲ':['g','e'],
		u'げ':['g','e'],
		u'ゴ':['g','o'],
		u'ご':['g','o'],
		u'ザ':['z','a'],
		u'ざ':['z','a'],
		u'ジ':['Z','i'],
		u'じ':['Z','i'],
		u'ズ':['z','u'],
		u'ず':['z','u'],
		u'ゼ':['z','e'],
		u'ぜ':['z','e'],
		u'ゾ':['z','o'],
		u'ぞ':['z','o'],
		u'ダ':['d','a'],
		u'だ':['d','a'],
		u'ヂ':['d','i'],
		u'ぢ':['d','i'],
		u'ヅ':['Z','u'],
		u'づ':['Z','u'],
		u'デ':['d','e'],
		u'で':['d','e'],
		u'ド':['d','o'],
		u'ど':['d','o'],
		u'バ':['b','a'],
		u'ば':['b','a'],
		u'ビ':['b','i'],
		u'び':['b','i'],
		u'ブ':['b','u'],
		u'ぶ':['b','u'],
		u'ベ':['b','e'],
		u'べ':['b','e'],
		u'ボ':['b','o'],
		u'ぼ':['b','o'],
		u'パ':['p','a'],
		u'ぱ':['p','a'],
		u'ピ':['p','i'],
		u'ぴ':['p','i'],
		u'プ':['p','u'],
		u'ぷ':['p','u'],
		u'ペ':['p','e'],
		u'ぺ':['p','e'],
		u'ポ':['p','o'],
		u'ぽ':['p','o'],
		u'ヴ':['v','u'],
	}

	# 仮名文字をアルファベットに変換するテーブル
	convert_hanyoon_table = {
		u'ァ':'a',
		u'ぁ':'a',
		u'ィ':'i',
		u'ぃ':'i',
		u'ゥ':'u',
		u'ぅ':'u',
		u'ェ':'e',
		u'ぇ':'e',
		u'ォ':'o',
		u'ぉ':'o',
	}

	# 仮名文字をアルファベットに変換するテーブル
	convert_yoon_table = {
		u'ャ':'a',
		u'ゃ':'a',
		u'ュ':'u',
		u'ゅ':'u',
		u'ョ':'o',
		u'ょ':'o',
	}

	# アルファベットの読み
	alphabet_yomi = {
		u'A':u'エー',
		u'B':u'ビー',
		u'C':u'シー',
		u'D':u'ディー',
		u'E':u'イー',
		u'F':u'エフ',
		u'G':u'ジー',
		u'H':u'エッチ',
		u'I':u'アイ',
		u'J':u'ジェー',
		u'K':u'ケー',
		u'L':u'エル',
		u'M':u'エム',
		u'N':u'エヌ',
		u'O':u'オー',
		u'P':u'ピー',
		u'Q':u'キュー',
		u'R':u'アール',
		u'S':u'エス',
		u'T':u'ティー',
		u'U':u'ユー',
		u'V':u'ヴイ',
		u'W':u'ダブリュー',
		u'X':u'エックス',
		u'Y':u'ワイ',
		u'Z':u'ゼット',
		u'a':u'エー',
		u'b':u'ビー',
		u'c':u'シー',
		u'd':u'ディー',
		u'e':u'イー',
		u'f':u'エフ',
		u'g':u'ジー',
		u'h':u'エッチ',
		u'i':u'アイ',
		u'j':u'ジェー',
		u'k':u'ケー',
		u'l':u'エル',
		u'm':u'エム',
		u'n':u'エヌ',
		u'o':u'オー',
		u'p':u'ピー',
		u'q':u'キュー',
		u'r':u'アール',
		u's':u'エス',
		u't':u'ティー',
		u'u':u'ユー',
		u'v':u'ヴイ',
		u'w':u'ダブリュー',
		u'x':u'エックス',
		u'y':u'ワイ',
		u'z':u'ゼット',
		u'Ａ':u'エー',
		u'Ｂ':u'ビー',
		u'Ｃ':u'シー',
		u'Ｄ':u'ディー',
		u'Ｅ':u'イー',
		u'Ｆ':u'エフ',
		u'Ｇ':u'ジー',
		u'Ｈ':u'エッチ',
		u'Ｉ':u'アイ',
		u'Ｊ':u'ジェー',
		u'Ｋ':u'ケー',
		u'Ｌ':u'エル',
		u'Ｍ':u'エム',
		u'Ｎ':u'エヌ',
		u'Ｏ':u'オー',
		u'Ｐ':u'ピー',
		u'Ｑ':u'キュー',
		u'Ｒ':u'アール',
		u'Ｓ':u'エス',
		u'Ｔ':u'ティー',
		u'Ｕ':u'ユー',
		u'Ｖ':u'ヴイ',
		u'Ｗ':u'ダブリュー',
		u'Ｘ':u'エックス',
		u'Ｙ':u'ワイ',
		u'Ｚ':u'ゼット',
		u'ａ':u'エー',
		u'ｂ':u'ビー',
		u'ｃ':u'シー',
		u'ｄ':u'ディー',
		u'ｅ':u'イー',
		u'ｆ':u'エフ',
		u'ｇ':u'ジー',
		u'ｈ':u'エッチ',
		u'ｉ':u'アイ',
		u'ｊ':u'ジェー',
		u'ｋ':u'ケー',
		u'ｌ':u'エル',
		u'ｍ':u'エム',
		u'ｎ':u'エヌ',
		u'ｏ':u'オー',
		u'ｐ':u'ピー',
		u'ｑ':u'キュー',
		u'ｒ':u'アール',
		u'ｓ':u'エス',
		u'ｔ':u'ティー',
		u'ｕ':u'ユー',
		u'ｖ':u'ヴイ',
		u'ｗ':u'ダブリュー',
		u'ｘ':u'エックス',
		u'ｙ':u'ワイ',
		u'ｚ':u'ゼット',
	}


	# 記号の読み
	symbol_yomi = {
		u'"':u'二重引用符',
		u"'":u'引用符',
		u'_':u'アンダーバー',
		u':':u'コロン',
		u'：':u'コロン',
		u';':u'セミコロン',
		u'；':u'セミコロン',
		u'/':u'スラッシュ',
		u'／':u'スラッシュ',
		u'％':u'パーセント',
		u'%':u'パーセント',
		u'>':u'だいなり',
		u'＞':u'だいなり',
		u'<':u'しょうなり',
		u'＜':u'しょうなり',
		u'(':u'かっこ',
		u'（':u'かっこ',
		u')':u'かっことじ',
		u'）':u'かっことじ',
		u'[':u'かぎかっこ',
		u'「':u'かぎかっこ',
		u']':u'かぎかっことじ',
		u'」':u'かぎかっことじ',
		u'・':u'なかてん',
		u'+':u'プラス',
		u'-':u'マイナス',
		u'÷':u'ワル',
		u'×':u'カケル',
		u'＋':u'プラス',
		u'－':u'マイナス',
		u'=':u'イコール',
		u'＝':u'イコール',
	}


	##### Phoneme_jp2メソッド定義 #####

   	# 拗音ならば変換
   	def yoon(self,string,boin):
		"""拗音付きの文字列を変換するメソッド
		"""

		if string != [] and ( boin == 'a' or boin == 'u' or boin == 'o' ):
			if len(string)>=2 and string[-1] == 'i':
				c = string[-2]
				if c == 'C' or c == 'Z' or c == 'S' or c == 'tS' or c == 'n1' :
					string[-1] = boin
					return string
				elif c == 'n':
					string[-2] = 'n1'
					string[-1] = boin
					return string
				else:
					string[-1] = 'j'
					string.append(boin)
					return string
			else:
				return ['j',boin]

		return []


	# 半拗音ならば変換
	def hanyoon(self,string,boin):
		"""半拗音付きの文字列を変換するメソッド
		"""

		# 要素が二つ以上
		if len(string) >= 2:
			c = string[-2]
			v = string[-1]

			# う゛ぁ va,vi,ve,vo<-vu、ふぁ fa,fi,fe,fo<-fu
			if v == 'u' and ( boin == 'a' or  boin == 'i' or  boin == 'e' or  boin == 'o' )  and ( c == 'f' or c == 'v' ):
				string[-1] = boin
				return string

			# てぃ ti<-te、でぃ di<-de
			elif v == 'e' and boin == 'i' and ( c == 't' or c == 'd' ):
				string[-1] = boin
				return string

			# じぇ Ze<-Zi、ちぇ tSe<-tSi
			elif v == 'i' and boin == 'e' and ( c == 'Z' or c == 'tS' ):
				string[-1] = boin
				return string

		# 半拗音を使いながら、上記以外ならば母音と見なす
		string.append(boin)
		return string


	# 文字単位で変換
	# return (確定音列specified,未確定音列unspecified)
	def convert_symbol(self,s,carryover):
		"""文字単位で変換していくメソッド
		"""

		## 確定 ##
		# 句点
		if ( s == u'。' ) or ( s == u'.' ):
			carryover.append('.')
			return ( carryover, [] )

		# 読点
		elif ( s == u'、' ) or ( s == u'，' ) or ( s == u',' ):
			carryover.append(',')
			return ( carryover, [] )

		# 疑問符
		elif ( s == u'？' ) or ( s == u'?' ):
			carryover.append('?')
			return ( carryover, [] )

		# 感嘆符
		elif ( s == u'！' ) or ( s == u'!' ):
			carryover.append('!')
			return ( carryover, [] )

		# 長音記号
		elif ( s == u'ー' ):
			if carryover:
				last = carryover[-1] # 繰越があるということは繰越に要素は一つはある
				if last == 'a' or last == 'i' or last == 'u' or last == 'e' or last == 'o':
					carryover[-1] = last + ':'
			return ( carryover, [] )

		# 撥音（次の文字次第で音が変わるが、それはすべてが終わってから確定させる）
		elif ( s == u'ン' ) or ( s == u'ん' ):
			carryover.append('X')
			return ( carryover, [] )

		# 促音記号
		elif ( s == u'ッ' ) or ( s == u'っ' ):
			carryover.append('Q')
			return ( carryover, [] )

		## 未確定 ##
		# 半拗音記号（長音が続くことがあるので未確定）
		elif self.convert_hanyoon_table.has_key(s):
			unspecified = self.hanyoon(carryover,self.convert_hanyoon_table[s])
			return ( [], unspecified )

		# 拗音記号（長音が続くことがあるので未確定）
		elif self.convert_yoon_table.has_key(s):
			unspecified = self.yoon(carryover,self.convert_yoon_table[s])
			return ( [], unspecified )

		# 濁音記号。「う゛」のときのみ。それ以外は文字クリア（長音が続くことがあるので未確定）
		elif ( s == u'゛' ):
			if carryover != [] and carryover[-1] == 'u':
				unspecified = ['v','u']
				return ( [], unspecified )
			else:
				return ( [], [] )

		## 確定＆未確定 ##
		# 単文字（新しい音節が始まるので、前のものが確定になる）
		elif self.convert_table.has_key(s):
			unspecified = self.convert_table[s][:]
			return ( carryover, unspecified )

		## 不正な文字 ##
		# 繰越分を確定し、不正な文字は捨てる
		else:
			return ( carryover, [] )

		return ( carryover, [] )


	# 仮名文字列を音素記号に変換する。
	def convert(self,s):
		"""変換本体メソッド
		"""

		if DEBUG:
			## log
			self.log.writeln(u'変換対象仮名文字:')
			self.log.writeln(s)
			self.log.writeln()

		# 語が空ならば何もせず終了
		if s == '':
			return []

		if s == u' ' or s == u'　':
			return [u' ']

		# 仮名文字列から音素の配列を作る
		phonemes    = []
		unspecified = []
		for ch in s:
			( specified, unspecified ) = self.convert_symbol(ch,unspecified)

			if specified:
				for ph in specified:
					phonemes.append(ph)

		if unspecified:
			for ph in unspecified:
				phonemes.append(ph)

		# 音素配列が空ならば終了
		if not phonemes:
			return []

		if DEBUG:
			## log
			self.log.writeln(u'仮名文字から音素配列に変換後:')
			for n in phonemes:
				self.log.write(n)
			self.log.writeln()
			self.log.writeln()

		# モーラ単位に分ける
		temp = []
		keep = []
		while phonemes:
			ch = phonemes.pop(0)
			if ch == '.' or ch == '!' or ch == '?'  or ch == ',':
				keep.append(ch)
				temp.append(keep)
				keep = []
			elif ch == 'a' or ch == 'i' or ch == 'u' or ch == 'e' or ch == 'o':
				keep.append(ch)
				temp.append(keep)
				keep = []
			elif ch == 'a:' or ch == 'i:' or ch == 'u:' or ch == 'e:' or ch == 'o:':
				keep.append(ch[0])
				temp.append(keep)
				temp.append(':')
				keep = []
			elif ch == 'X' or ch == 'Q':
				temp.append( ch )
				keep = []
			else:
				keep.append(ch)
		phonemes = temp

		if DEBUG:
			## log
			self.log.writeln(u'モーラ毎に分割後:')
			for n in phonemes:
				if n:
					self.log.write(u'[')
					for m in n:
						self.log.write(m)
					self.log.write(u']')
			self.log.writeln()
			self.log.writeln()

		return phonemes


	# pho形式で音素を出力する
	def make_pho_lines( self, nodes ):

		# node( 音素リスト, 品詞, アクセント, ソース )

		scale = 1 / rate / self.default_scale

		# アクセントを考慮した音素データリストを作成
		phonemes = []
		prev_accent = ''
		prev_noun   = False
		for node in nodes:

			if DEBUG:
				if node[3]:
					self.log.writeln(u"表層形　　：" + node[3])
				self.log.write(u"音素列　　：")
				for n in node[0]:
					for m in n:
						self.log.write(m)
				self.log.writeln()
				self.log.writeln(u"品詞　　　：" + node[1] )
				if node[2]:
					self.log.writeln(u"アクセント：" + node[2])
				if node[1] !=u'補助記号' and node[1] != u'句点':
					self.log.writeln(u"モーラ数　：" + str(len(node[0])))
				self.log.writeln()
				# 音素の情報　　（記号、長さ、高低、表層）


			# 音素データが空白の場合
			if node and node[0] and node[0][0]== u' ':
				phonemes.append(['_',0,0])
				prev_accent = ''
				prev_noun   = False
				continue

			# 補助記号は空白扱いにする
			if node[1] == u'補助記号':
				ch = ''
				if node[0] and node[0][0] and node[0][0][0]:
					ch = node[0][0][0]
				if ch == '?' or ch == '!' or ch =='.' or ch == ',':
					phonemes.append([ch,0,0])
				else:
					phonemes.append(['_',0,0])
				prev_accent = ''
				prev_noun   = False
				continue

			# 前のノードが平板アクセントの名詞ならば、そのあとの助詞は高音にする
			if ( node[1] == u'助詞' ) and prev_noun and prev_accent == '0':

				for n in node[0]:
					for m in n:
						phonemes.append( [m,0,1] )
				continue

			# 最初の要素が音素データ
			data = node[0]

			# アクセントの情報を付加する
			accent = node[2]
			prev_accent = accent
			prev_noun   = node[1]==u'名詞'
			if accent:

				# 平板型アクセント
				if accent == '0':
					for m in data[0]:
						phonemes.append( [m,0,0] )

					for n in data[1:]:
						for m in n:
							phonemes.append( [m,0,1] )

				# 頭高型アクセント
				elif accent == '1':
					for m in data[0]:
						phonemes.append( [m,0,1] )
					for n in data[1:]:
						for m in n:
							phonemes.append( [m,0,0] )

				# 中高型
				elif accent == '2':
					for m in data[0]:
						phonemes.append( [m,0,0] )
					for m in data[1]:
						phonemes.append( [m,0,1] )
					for n in data[2:]:
						for m in n:
							phonemes.append( [m,0,0] )

				# 尾高型
				else:
					for n in data[:int(accent)-1]:
						for m in n:
							phonemes.append( [m,0,0] )

					for n in data[int(accent)-1:]:
						for m in n:
							phonemes.append( [m,0,1] )

			# ノードにアクセントがない場合
			else:
				for n in data:
					for m in n:
						phonemes.append( [m,0,0] )

		# 以上、各ノードに対する処理

		if DEBUG:
			self.log.writeln(u'アクセント処理後:')
			self.log.dump_phonemes( phonemes )

		# 長音記号を前の母音に結びつける
		prev = []
		temp = []
		for ph in phonemes:
			if ph[0] == ':':
				if prev:
					p = prev[0]
					if p == 'a' or p == 'i' or p == 'u' or p == 'e' or p == 'o':
						if prev[2] == 1 and ph[2] == 0:
							temp.append( [ p + ':',  prev[1], 2 ] )
						elif prev[2] == 0 and ph[2] == 1:
							temp.append( [ p + ':',  prev[1], 3 ] )
						elif prev[2] == 1 and ph[2] == 1:
							temp.append( [ p + ':',  prev[1], 1 ] )
						elif prev[2] == 0 and ph[2] == 0:
							temp.append( [ p + ':',  prev[1], 0 ] )
					else:
						temp.append( prev )
					prev = []
			else:
				if prev:
					temp.append( prev )
				prev = ph

		if prev:
			temp.append( prev )
		phonemes = temp

		if DEBUG:
			self.log.writeln(u'長音処理後:')
			self.log.dump_phonemes( phonemes )

		# 音素の長さを計算。母音は先立つ子音の長さを引いて調整する
		temp = []
		length = 0
		for ph in phonemes:

			if ph:
				# 句点の処理
				if ph[0] == '?' or  ph[0] == '!' or  ph[0] == '.'  or  ph[0] == ',':
					d = 100
					length = 0

				# 子音の処理
				if self.phone_duration_consonant.has_key(ph[0]):
					d = self.phone_duration_consonant[ph[0]]
					length = length + d

				# 母音の処理
				if self.phone_duration_vowel.has_key(ph[0]):
					d = self.phone_duration_vowel[ph[0]] - length
					length = 0

			temp.append( [ph[0],d,ph[2]] )
		phonemes = temp

		if DEBUG:
			self.log.writeln(u'音長処理後:')
			self.log.dump_phonemes( phonemes )

		# 文頭及び撥音の直後の歯茎破裂音記号を歯茎破擦音に変換　Z->dZ, z->dz
		last = '_'
		t = []
		for ph in phonemes:
			if self.phone_head_remap.has_key(ph[0]) and ( last == ',' or last == '_' or last == 'Q' or last == 'X' ):
				t.append( [self.phone_head_remap[ph[0]],ph[1],ph[2]] )
			else:
				t.append( ph )
			last = ph[0]
		if not t:
			return []
		phonemes = t

		if DEBUG:
			self.log.writeln(u'歯茎破擦音処理後:')
			self.log.dump_phonemes( phonemes )

		# 撥音記号を本来の音素に変換する(逆順で処理)
		last = '_'
		t = []
		for ph in reversed(phonemes):
			p = ph[0]
			if p == 'X' and self.phone_N_map.has_key(last):
				p =  self.phone_N_map[last]
				t.append( [p,ph[1],ph[2]] )
			else:
				t.append(ph)
			last = p
		phonemes = t[::-1]

		if DEBUG:
			self.log.writeln(u'撥音記号処理後:')
			self.log.dump_phonemes( phonemes )

		# 疑問文のときは、上がり調子にする
		if phonemes and len(phonemes)>2:
			if phonemes[-1][0] == '?':
				ph = phonemes[-2]
				phonemes[-2] = [ ph[0], ph[1]+self.default_ms, 4]

		if DEBUG:
			self.log.writeln(u'疑問形処理後:')
			self.log.dump_phonemes( phonemes )

		# 未対応連続音の調整（a:i:,i:u:,u:u:,o:u:,vu:）->（a:_i:,i:_u:,u:_u:,o:_u:,vuu:）
		last = ''
		i = 0
		temp = []
		for ph in phonemes:
			ch = ph[0]
			if ch == 'i:' and last == 'a:':
				temp.append( ['_',0,0] )
			elif ch == 'u:' and ( last == 'i:' or last == 'u:' or last == 'o:' ):
				temp.append( ['_',0,0] )
			elif p == 'u:' and last == 'v':
				temp.append( ['u',self.default_ms,self.default_po,self.default_pt] )
			temp.append( ph )
			last = ch
		phonemes = temp

		if DEBUG:
			self.log.writeln(u'未対応連続音の補正:')
			self.log.dump_phonemes( phonemes )



		result = []
		result.append( '_\t' + str(int(100*scale)) )

		# 要素の数だけ繰り返す
		for ph in phonemes:
			po = self.default_po			# 標準ピッチ位置
			pt = self.default_pt			# 標準音素ピッチ

			# 標準値を計算しておく
			pitch_temp = str(int((pt)*pitch))


			data = ph[0]

			if data == 'X': # 変換できていない撥音記号があったら削除
				continue

			if ph[1]:
				tm = ph[1]
			else:
				tm = self.default_ms

			if data == ',':  # コンマを補正
				data = '_'

			elif data == 'Q':  # 促音記号を補正
				data = '_'

			# 句点のときはコメントを挿入（PYDで利用）
			if data == '.' or data == '!' or data == '?':
				result.append( '_' + '\t' + str(int(tm*scale)) + '\t' + str(int(po)) + '\t' + pitch_temp )
				result.append( ';kuten' )

			# 通常の音素
			else:
				# ピッチ上昇の処理
				if  ph[2] == 0:
					pitch_temp = str(int((pt)*pitch))

				# アクセントのある音節の上昇
				elif ph[2] == 1:
					pitch_temp = str(int((pt+self.acc_diff)*pitch))

				# 長母音の前半部のみの上昇
				elif ph[2] == 2:
					pitch_temp = str(int((pt+self.acc_diff)*pitch))
					po = po * 0.5

				# 長母音の後半部のみの上昇
				elif ph[2] == 3:
					pitch_temp = str(int((pt+self.acc_diff)*pitch))
					po = po * 1.5

				# 疑問文の上昇
				elif ph[2] == 4:
					pitch_temp = str(int((pt+self.ques_diff)*pitch))

				else:
					pitch_temp = str(int((pt)*pitch))

				result.append( data + '\t' + str(int(tm*scale)) + '\t' + str(int(po)) + '\t' + pitch_temp )

		result.append( '_\t' + str(int(self.finish_rest*scale)) )

		if DEBUG:
			if result:
				self.log.writeln(u'変換結果:')
				for i in result:
					self.log.writeln(i)
				self.log.writeln()


		return result

	# 数値用
	numRead = {
		u"0":u"ゼロ",
		u"1":u"一",
		u"2":u"二",
		u"3":u"三",
		u"4":u"四",
		u"5":u"五",
		u"6":u"六",
		u"7":u"七",
		u"8":u"八",
		u"9":u"九",
		u"０":u"ゼロ",
		u"１":u"一",
		u"２":u"二",
		u"３":u"三",
		u"４":u"四",
		u"５":u"五",
		u"６":u"六",
		u"７":u"七",
		u"８":u"八",
		u"９":u"九",
	}


	# 数字用
	numRead2 = {
		u"0":u"ゼロ",
		u"1":u"イチ",
		u"2":u"ニー",
		u"3":u"サン",
		u"4":u"ヨン",
		u"5":u"ゴー",
		u"6":u"ロク",
		u"7":u"ナナ",
		u"8":u"ハチ",
		u"9":u"キュウ",
		u"０":u"ゼロ",
		u"１":u"イチ",
		u"２":u"ニー",
		u"３":u"サン",
		u"４":u"ヨン",
		u"５":u"ゴー",
		u"６":u"ロク",
		u"７":u"ナナ",
		u"８":u"ハチ",
		u"９":u"キュウ",
	}

	numClass1 = {
		u"1" : u"",
		u"2" : u"十",
		u"3" : u"百",
		u"4" : u"千",
	}

	numClass2 = {
		u"0" : u"",
		u"1" : u"万",
		u"2" : u"億",
		u"3" : u"兆",
		u"4" : u"ケー",
	}

	numYomiHosei = {
		u"三百":u"サンビャク",
		u"六百":u"ロッピャク",
		u"八百":u"ハッピャク",
		u"三千":u"サンゼン",
		u"八千":u"ハッセン",
	}

	numzenhan = {
		u'０':u'0',
		u'１':u'1',
		u'２':u'2',
		u'３':u'3',
		u'４':u'4',
		u'５':u'5',
		u'６':u'6',
		u'７':u'7',
		u'８':u'8',
		u'９':u'9',
	}

	# 文字列中の数値を日本語に変換する
	def convert_numstring(self,string):
		"""数値を日本語に変換するメソッド
		"""

		number = re.compile( u'([0-9０-９]+,*[0-9,０-９]*)(\.[0-9０-９]*)?' )
		zeros  = re.compile( u'^[0０]+$' )
		comma  = re.compile( ',' );

		# 無限ループ、数値部分がなければ途中でリターン
		for n in range(100):

			# 数値文字列を検索
			val = number.search( string )
			if val == None:
				return string;

            # 全角数字を半角数字に変換する
			def zennum2hannum(string):
				if string == None:
					return None

				for k,v in self.numzenhan.items():
					string = string.replace( k, v )
				return string

			# 整数と小数
			i = val.group(1)
			r = val.group(2)
			i = zennum2hannum(i)
			r = zennum2hannum(r)

			# 格納配列初期化
			s = []

			# ゼロだけからなる数値はどれもゼロ
			if zeros.search( i ):
				i = '0'

			## 整数部の処理
			# 桁区切りの「,」があれば削除
			i = comma.sub( '', i )
			olen  = len(i)

			# 四桁より長い間
			while len(i) > 4:

				par = []
				par.append( i[0] )
				i = i[1::]
				while len(i)%4 != 0:
					par.append( i[0] )
					i = i[1:]

				flag = 0
				while par<>[]:
					if par[0] != '0':
						flag = 1
						# 「1」以外は必ず読む、一番下の桁ならば何でも読む
						if par[0] != '1' or len(par) == 1:
							s.append( self.numRead[par[0]] )
						s.append( self.numClass1[`len(par)`] )
					par.pop(0)

				# そこに0以外の数字があれば
				if flag == 1:
					num = int(len(i)/4)
					s.append( self.numClass2[`num`] )

			# 四桁より短くて一桁でなければ
			while len(i) > 1:
				if i[0] != '0':
					# 「1」以外は必ず読む、一番下の桁ならば何でも読む
					if i[0] != '1' or len(i) == 1:
						s.append( self.numRead[i[0]] )
					s.append( self.numClass1[`len(i)`] )
				i = i[1:]

			## 一の位の処理
			# 一の位がゼロならば
			if i[0] == '0':
				# 一桁ならば、
				if olen == 1:
					# 小数がなければ普通に読む
					if r == '':
						s.append( self.numRead[i[0]] )
						i = i[1::]
					 # 小数がある場合は「れい」と読む
					else:
						s.append( u"レイ" )
			# 一の位がゼロ以外ならば普通に読む
			else:
				s.append( self.numRead[i[0]] )
				i = i[1::]

			## 小数の処理
			# 小数点以下があれば読む
			if r <> None:
				s.append( u"テン" )
				r = r[1::]		# 小数点記号を捨てて
				for n in r:
					s.append( self.numRead2[n] )

			# 配列を連結する
			s = u''.join(s)

			# 数値読み補正
			for i in self.numYomiHosei:
				s = re.sub( i, self.numYomiHosei[i], s )

			# 文字列置換
			temp = ""
			if val.start(0) > 0:
				temp = string[0:val.start(0)]
			temp = temp + s
			if len(string)>val.end(0):
				temp = temp + string[val.end(0):]
			string = temp


	# 簡易辞書を読み込む
	def load_userdic(self):
		"""ユーザー辞書を読み込むメソッド
		"""
		# 辞書のソート用比較関数（長いものから先に調べるようにする）
		def length_comp(a,b):
			"""比較関数
			"""
			a = a.split(',')
			if a == []:
				return -1
			b = b.split(',')
			if b == []:
				return 1
			return len(b[0]) - len(a[0])

		# 辞書がなければそのまま帰る
		if not os.path.exists( self.userdic ):
			return False

		f = open( self.userdic, 'r')
		self.userDic = []
		for line in f:
			self.userDic.append(unicode(line.strip(),'utf8'))
		self.userDic.sort( length_comp )
		f.close()
		return True


	# 簡易辞書を使ってアルファベットなどをカナ表記に置き換える
	def convert_using_userdic(self,s):
		"""簡易辞書変換メソッド
		"""
		for line in self.userDic:
			word = line.split(',')
			if len( word ) == 2:
				s = re.compile( word[0] ).sub( word[1], s )
		return s


	# 音素変換処理
	def txt2pho(self,s):
		"""Unicode文字列をPHOデータに変換する
		"""

		if DEBUG:
			self.log.writeln(u"対象文字列:")
			self.log.writeln(s)
			self.log.writeln()

		# 簡易辞書を使ってカナ表記に置き換える
		if self.dic_enable:
			s = self.convert_using_userdic(s)

		if DEBUG:
			self.log.writeln(u'簡易辞書変換後:')
			self.log.writeln(s)
			self.log.writeln()

		# アルファベットを変換
		temp = ''
		for c in s:
			if self.alphabet_yomi.has_key(c):
				c = self.alphabet_yomi[c]
			temp = temp + c
		s = temp

		if DEBUG:
			self.log.writeln(u'アルファベット変換後:')
			self.log.writeln(s)
			self.log.writeln()

		# 記号を変換
		temp = ''
		if self.flag_reading_symbol:
			for c in s:
				if self.symbol_yomi.has_key(c):
					c = self.symbol_yomi[c]
				temp = temp + c
		else:
			for c in s:
				if self.symbol_yomi.has_key(c):
					c = u'　'
				temp = temp + c
		s = temp

		if DEBUG:
			self.log.writeln(u'記号変換後:')
			self.log.writeln(s)
			self.log.writeln()

		# 文字列中の数値を日本語に変換
		s = self.convert_numstring(s)

		# 文字列をMeCabで処理できるエンコードに変換する
		s = s.encode(mecab_charset)

		# MeCabで変換する
		node = self.mecab.parseToNode(s)
		node = node.next

		# feature リストを獲得
		def get_feature_list(feature):

			if not feature:
				return []

			# 文字コードをUnicodeに変換
			feature = unicode( feature, mecab_charset )

			t = feature.split(u',')

			# 文字列としての','の解釈を補正
			ttt = ''
			s = []
			for tt in t:
				if tt and tt[0] == u'"':
					ttt = tt[1:]
					tt  = ''
				elif ttt and tt and tt[-1] == u'"':
					ttt = ttt + u',' + tt[:-1]
					tt = ttt
					ttt = ''
				elif ttt:
					ttt = ttt + u',' + tt
					tt  = ''
				if tt:
					s.append(tt)

			return s

		# mecab の解析結果をもとに各要素を変換
		result = []
		while node:

			nodes = []

			# 句点もしくは終端文字までを集めて、変換する。
			while node:

				t = get_feature_list(node.feature)

				# Unidicに対しての処理
				if self.mecab_dic_name == u'unidic':

					if len(t)>9 and t[9]:
						s = t[9]
					else:
						s = unicode( node.surface, mecab_charset )

					if t[0] == u'BOS/EOS':
						node = None
						break

					if DEBUG:
						self.log.writeln(u"str    :" + u"'" + s + u"'")
						self.log.writeln(u"feature:" + unicode(node.feature,mecab_charset) )
						self.log.writeln(u"surface:" + unicode(node.surface,mecab_charset) )
						self.log.writeln()

					data = self.convert(s)

					if self.use_accent:

						if len(t) > 22:
							accent = t[22]
							accent = accent.split(u',')[0]
							if accent == u'*':
								accent = ''
						else:
							accent = ''

						nodes.append( ( data, t[0], accent, unicode(node.surface,mecab_charset) ) )
					else:
						nodes.append( ( data, t[0], None, unicode(node.surface,mecab_charset) ) )

				# ipadicに対しての処理
				elif self.mecab_dic_name == u'ipadic':

					if t[0] == u'BOS/EOS':
						node = None
						break
					if len(t)>8:
						s = t[8]
					else:
						s = unicode( node.surface, mecab_charset )

					if DEBUG:
						self.log.writeln(u"str    :" + u"'" + s + u"'")
						self.log.writeln(u"feature:" + unicode(node.feature,mecab_charset) )
						self.log.writeln(u"surface:" + unicode(node.surface,mecab_charset) )
						self.log.writeln()

					data = self.convert(s)

					nodes.append( ( data, t[0], None, unicode(node.surface,mecab_charset) ) )

				if  t[1] == u'句点':
					node = node.next
					break

				node = node.next

			if DEBUG:
				## log
				if nodes:
					self.log.writeln(u'変換結果:')

					for n in nodes:
						self.log.writeln(u"品詞：" + n[1] )

						if n[2]:
							accent = n[2]
							self.log.writeln(u"アクセント：" + accent)
						else:
							self.log.writeln(u"アクセント：情報なし")
						self.log.write(u"音素記号：")
						for l in n[0]:
							self.log.write(u'[')
							for m in l:
								self.log.write(m)
							self.log.write(u']')
						self.log.writeln()
						self.log.writeln()
					self.log.writeln()

			# 各音素のパラメータを設定する
			if nodes:
				temp = self.make_pho_lines( nodes )

				# 今での結果に連結
				result.extend(temp)

		return result


	# アクセントのモードを設定する
	def set_accent_mode(self,mode):
		if mode == 1:
			self.use_accent = 1
		else:
			self.use_accent = 0


	# ピッチを設定する
	def set_pitch(self,vol):
		"""音量を設定する
		範囲は[0.2,8.0]
		"""

		if vol < 0.2:
			vol = 0.2

		if vol > 8.0:
			vol = 8.0

		self.pitch = vol


	# 読み上げ速度を設定する
	def set_rate(self,val):
		"""読み上げ速度を設定する
		範囲は[0.2,8.0]
		"""

		if val < 0.2:
			val = 0.2

		if val > 8.0:
			val = 8.0

		self.rate = val


	# 記号読み上げの設定
	def set_reading_symbol(self,mode):

		if mode == 1:
			self.flag_reading_symbol = 1
		else:
			self.flag_reading_symbol = 0


# ログ出力用クラス
class Log:
	def __init__(self,name):
		self.fp = None
		try:
			self.fp = open(name,'w')
		except:
			sys.stderr.write( u"おそらく、ログファイルが既に開かれています。閉じてからやり直してみてください。\n"
												.encode( system_charset ) )
			sys.exit()

	def __del__(self):
		if self.fp:
			self.fp.close()

	def write(self,data=""):
		data = data.encode(system_charset)
		if self.fp:
			self.fp.write(data)
		print data,

	def writeln(self,data=""):
		data = data.encode(system_charset)
		if self.fp:
			self.fp.write(data)
			self.fp.write('\n')
		print data

	def dump_phonemes(self,phonemes):
		for i in phonemes:
			self.writeln( str(i[0]) + '\t'  + str(i[1]) + '\t'  + str(i[2]) )
		self.writeln()


##### クラス終了 #####




# 標準音量比率
volume = 1.0

# 標準読み上げ速度比率
rate = 1.0

# 標準ピッチ比率
pitch = 1.0




# テキストからPHOファイルを作成する
def makePHO(string,filename):
	"""テキストからPHOファイルを作成する。
	文字列もファイル名もUnicodeでエンコードされているとする。
	ファイル名は'.pho'が既に付加されているとみなす
	"""

	global accent_mode
	global dic_name
	global rate
	global pitch

	# 書き込み用にPHOファイルを開く
	phofile = open( filename, 'w')

	if string == '':
		return

	# 音素クラス生成
	phenomen = Phenomen( dic_name )
	phenomen.set_accent_mode( accent_mode )					# アクセントの有無設定
	phenomen.set_rate( rate )								# レートの設定
	phenomen.set_pitch( pitch )								# ピッチの設定
	phenomen.set_reading_symbol( reading_symbol_mode )		# 記号読みの設定

	ps = phenomen.txt2pho(string)
	if ps == []:
		return

	# 音素リストを出力
	wave = "";
	for ph in ps:
		phofile.write(ph+'\n')

	# 音素ファイルを閉じる
	phofile.close()


# テキストを音声ファイルに変換する
def makeWAV(string,filename):
	"""テキストを音声ファイルに変換する。
	文字列もファイル名もUnicodeでエンコードされているとする。
	ファイル名は'.wav'が既に付加されているとする。
	"""

	global volume

	ps = platform.system()
	if ps != "Linux" and ps != "Windows":
		sys.stderr.write( u"このシステムには対応していません\n".encode( system_charset ) )
		sys.exit()

	# 入力文字列から余白を削除
	string = string.strip()

	# PHO用の一時ファイルを作成
	file = tempfile.mkstemp('.pho')
	file_obj = os.fdopen(file[0], 'w')
	file_obj.close()
	phofile = file[1]

	# phoファイルを作成する
	makePHO(string,phofile)

	if ps == "Linux":
		#mbrolaによりphoファイルをwavファイルに変換する
		if volume > 1.0:
			volume = 1.0
		os.system( "mbrola -e -v " + str(volume) + " " + database + " " + phofile + " " + filename )
	elif ps == "Windows":
		#mbrolaによりphoファイルをwavファイルに変換する
		pho2wav.convert( database, phofile, filename, volume )

	# 一時ファイルを削除
	os.remove(phofile)


def speak(string):
	"""テキストを発音する
	文字列はUnicodeでエンコードされているとする。
	"""

	# wav用の一時ファイルを作成
	file = tempfile.mkstemp('.wav')
	file_obj = os.fdopen(file[0], 'w')
	file_obj.close()
	wavfile = file[1]

	# 文字列から一時的なwavファイルを作成
	makeWAV( string, wavfile )

	# 発音
	ps = platform.system()
	if ps == "Linux":
		os.system( "aplay -q " + wavfile )
	elif ps == "Windows":
		winsound.PlaySound( wavfile, winsound.SND_FILENAME)
	else:
		sys.stderr.write( u"このシステムには対応していません\n".encode( system_charset ) )
		sys.exit()


	# 一時ファイルを削除
	os.remove(wavfile)


def set_volume(vol):
	"""音量を設定する
	範囲は[0.2,8.0]
	"""

	global volume
	if vol < 0.2:
		vol = 0.2

	if vol > 8.0:
		vol = 8.0

	volume = vol


def set_rate(val):
	"""読み上げ速度を設定する
	範囲は[0.2,8.0]
	"""

	global rate
	if val < 0.2:
		val = 0.2

	if val > 8.0:
		val = 8.0

	rate = val


def set_pitch(val):
	"""読み上げピッチを設定する
	範囲は[0.2,8.0]
	"""
	global pitch
	if val < 0.2:
		val = 0.2

	if val > 8.0:
		val = 8.0

	pitch = val


# アクセントのモードを設定する
def set_accent_mode(mode):
	global accent_mode
	if mode == 1:
		accent_mode = 1
	else:
		accent_mode = 0


# 記号の読みをするかどうかを設定する
def set_reading_symbol(mode):
	"""記号の読みをするかどうかを設定する
	"""

	global reading_symbol_mode
	if mode == 1:
		reading_symbol_mode = 1
	else:
		reading_symbol_mode = 0


##### 単独利用処理 #####

def main():

	global accent_mode,reading_symbol_mode,dics,default_dic,dic_name,message,text_charset,system_charset

	### オプションの設定 ###

	usage = u"usage: %prog [options] 文字列１ 文字列２..."

	parser = OptionParser(usage=usage)

	parser.add_option( "-f", "--file",         dest="filename",
		help=u"読み上げるファイルを指定します（-iとの競合は不可）" )

	parser.add_option( "-r", "--rate",         dest="rate",
		help=u"読み上げ速度の比率を指定します（0.2～8.0）" )
	parser.add_option( "-v", "--volume",       dest="volume",
		help=u"読み上げ音量の比率を指定します（0.2～8.0）" )
	parser.add_option( "-p", "--pitch",        dest="pitch",
		help=u"読み上げピッチの比率を指定します（0.2～8.0）" )

	parser.add_option( "-t", "--text-charset",  dest="text_charset",
		help=u"テキストファイルの文字コードを指定します。標準:" + text_charset )

	default_string =u"（標準設定）"
	str1 = ""
	str2 = default_string
	if accent_mode:
		str1,str2 = str2,str1
	parser.add_option( "--accent-on",          action="store_true",   dest="accent_mode",
		help=u"アクセント読み上げをオンにします" + str1 )
	parser.add_option( "-a", "--accent-off",   action="store_false",  dest="accent_mode",
		help=u"アクセント読み上げをオフにします" + str2 )

	str1 = ""
	str2 = default_string
	if reading_symbol_mode:
		str1,str2 = str2,str1
	parser.add_option( "-s", "--symbol-on",    action="store_true",   dest="symbol_mode",
		help=u"記号読み上げをオンにします" + str1 )
	parser.add_option( "--symbol-off",         action="store_false",  dest="symbol_mode",
		help=u"記号読み上げをオフにします" + str2 )

	if dics:
		temp = u"（" + u",".join(dics) + u"）"
	parser.add_option( "-d", "--dic-name",     dest="dic_name",
		help=u"使用する辞書を指定します" + temp + u"標準は" + dics[default_dic] )

	parser.add_option( "-i", "--use-stdin",    action="store_true",   dest="enable_stdin",
		help=u"標準入力を読み上げます（-fとの競合は不可）" )
	(options, args) = parser.parse_args()


	### パラメータから値を決定

	if options.rate:
		set_rate( float(options.rate) )

	if options.volume:
		set_volume( float(options.volume) )

	if options.pitch:
		set_pitch( float(options.pitch) )

	if options.pitch:
		set_pitch( float(options.pitch) )

	if options.accent_mode != None:
		set_accent_mode( options.accent_mode )

	if options.symbol_mode != None:
		set_reading_symbol( options.symbol_mode )

	if options.text_charset:
		text_charset = options.text_charset


	if options.dic_name:
		dic_name = unicode( options.dic_name, system_charset )

	### パラメータに応じた処理 ###

	# 標準入力からの読み込みが指定されていたら
	if options.enable_stdin != None:

		if options.filename:
			sys.stderr.write( u"標準入力とファイルを同時に入力にすることはできません\n".encode( system_charset ) )
			sys.exit()
		else:
			for line in sys.stdin:
				speak(line)

	# そうではなく、ファイルからの読み込みが指定されていたら
	elif options.filename:
		if os.path.exists(options.filename):
			f = open( options.filename, 'r')
			for l in f:
				try:
					l = unicode( l, text_charset )
				except:
					sys.stderr.write( u"エンコードエラーです。ファイルの文字コードを確認してください。\n"
												.encode( system_charset ) )
					sys.exit()
				speak(l)
			f.close()

	# そうでもなく、文字列が指定されていたら
	elif len(args) > 0:
		for l in args:
			l = unicode( l, system_charset )
			speak(l)

	# そうでもなく、指定のテキストファイルが存在していたら
	elif os.path.exists(text):
		f = open(text, 'r')
		for l in f:
			try:
				l = unicode( l, text_charset )
			except:
				sys.stderr.write( u"エンコードエラーです。ファイルの文字コードを確認してください。\n"
												.encode( system_charset ) )
				sys.exit()

			speak(l)
		f.close()

	# そうでもなく、挨拶の文字列が指定されていたら
	elif message != '':
		speak(message)


if __name__ == '__main__':
	main()
