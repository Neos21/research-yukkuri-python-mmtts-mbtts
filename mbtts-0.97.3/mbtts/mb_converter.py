# -*- coding: utf8 -*-
# mb_converter.py
# mbtts 0.97
# 2010/08/19
# copyright(c) takayan
# http://neu101.seesaa.net/

import os
import re
import platform
import subprocess

import mbtts_var
import tankanji

##### クラス #####

# PHOファイルを生成する処理を担当する基底クラス
# 特定のデータベースを利用するスクリプトを書くときは、
# このクラスを継承し、この基底クラスのコンストラクタを呼び出す。
# このとき、name変数にデータベース名をつける。
# そして、mbtts_var.pyのDATABASESに、nameとクラスの対を追加する。

class Conv:
	"""音素ファイルデータベースを操作する基底クラス
	"""

	##### コンストラクタ #####
	def __init__(self,database_name,dic_name,engine_type):

		# ログファイルを作る
		self.log = None
		if mbtts_var.DEBUG:
			self.log = Log(mbtts_var.LOGFILE)

		# 標準音量比率
		self.volume = 1.0

		# 標準読み上げ速度比率
		self.rate = 1.0

		# 標準ピッチ比率
		self.pitch = 1.0

		# 読み上げエンジンの種類
		self.engine_type = engine_type

		# 記号を読むかどうかのフラグ
		self.reading_symbol_mode = mbtts_var.READING_SYMBOL_FLAG

		# アクセントを有効にするか
		self.accent_mode = mbtts_var.ACCENT_FLAG

		# データベースの名前の確認
		if database_name == "":
			raise Exception(u"データベースの名前が指定されていません")

		# aquestalk2 に対する処理
		if engine_type == "aquestalk2":
			pass

		# mbrola に対する処理
		elif engine_type == "mbrola":

			# データベースのパスを生成
			self.database = os.path.join( mbtts_var.DATABASE_DIR, database_name, database_name )

			# データベースの存在確認
			if not os.path.exists( self.database ):
				raise Exception(u"指定のデータベース " + database_name + u" が存在しません")

		# 不明なエンジン
		else:
			raise Exception(u"未対応な読み上げエンジンです")


		# MeCab辞書の設定
		dic_name = dic_name.lower()
		if dic_name in mbtts_var.DICS:
			try:
				self.dic = mbtts_var.DICS[dic_name]()
			except:
				# Unidicがインストールされていないときの対処
				self.dic = mbtts_var.DICS[u'ipadic']()

			self.mecab = self.dic.mecab
			self.mecab_dic_name = self.dic.mecab_dic_name
		else:
			raise Exception(u"MeCab辞書 " + dic_name + u" には未対応です")

		# 簡易辞書
		self.userdic = mbtts_var.USER_DIC					# 簡易辞書の場所
		if not os.path.isfile(self.userdic):
			self.userdic = os.path.dirname(__file__) + '\\' + self.userdic
		self.dic_enable = self.load_userdic()


	##### デストラクタ #####
	def __del__(self):
		pass

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

	# 必読記号の読み
	symbol_yomi = {
		u'_':u'アンダーバー',
		u':':u'コロン',
		u'：':u'コロン',
		u';':u'セミコロン',
		u'；':u'セミコロン',
		u'/':u'スラッシュ',
		u'／':u'スラッシュ',
		u'％':u'パーセント',
		u'%':u'パーセント',
		u'+':u'プラス',
		u'-':u'マイナス',
		u'÷':u'ワル',
		u'×':u'カケル',
		u'＋':u'プラス',
		u'－':u'マイナス',
		u'=':u'イコール',
		u'＝':u'イコール',
		u'>':u'だいなり',
		u'＞':u'だいなり',
		u'<':u'しょうなり',
		u'＜':u'しょうなり',
	}

	# 任意の記号の読み
	symbol2_yomi = {
		u'"':u'二重引用符',
		u"'":u'引用符',
		u'(':u'かっこ',
		u'（':u'かっこ',
		u')':u'かっことじ',
		u'）':u'かっことじ',
		u'[':u'かぎかっこ',
		u'「':u'かぎかっこ',
		u']':u'かぎかっことじ',
		u'」':u'かぎかっことじ',
		u'・':u'なかてん',
	}


	# aquestalk2 で wavファイルを作成する
	def aquestalk2_wave( self, string, filename, volume ):
		""" stringを元に音声ファイルを生成する。
		"""

		self.make_sound_file( string, filename, volume )


	# wavファイルを作成する
	def wave_generate( self, phofile, filename, volume ):
		"""PHOファイルを元に音声ファイルを生成する。
		"""

		if not mbtts_var.MBROLA_PATH:
			return

		# システムによって処理を切り替える
		ps = platform.system()
		if ps == "Linux":
			# mbrolaによりphoファイルをwavファイルに変換する
			subprocess.call( [
				mbtts_var.MBROLA_PATH,
				"-e","-v",str(volume),
				self.database, phofile, filename ] )

		elif ps == "Windows":
			# mbrolaによりphoファイルをwavファイルに変換する
			res = subprocess.call( [
				mbtts_var.MBROLA_PATH,
				"-e","-v",str(volume),
				self.database, phofile, filename ] )

		elif ps == "Darwin":
			# mbrolaによりphoファイルをwavファイルに変換する
			res = subprocess.call( [
				mbtts_var.MBROLA_PATH,
				"-e","-v",str(volume),
				self.database, phofile, filename ] )



	# 仮名文字列を音素記号に変換する。
	def convert(self,s):
		"""変換本体メソッド
		"""

		if mbtts_var.DEBUG:
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

		if mbtts_var.DEBUG:
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
			elif ch == ':' or ch == 'X' or ch == 'Q':
				temp.append( ch )
				keep = []
			else:
				keep.append(ch)
		phonemes = temp

		if mbtts_var.DEBUG:
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


	# アクセントを考慮した音素データリストを作成
	def accented_phonemes_list( self, nodes ):

		phonemes = []
		prev_accent = ''
		prev_noun   = False
		for node in nodes:

			if mbtts_var.DEBUG:
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

				# 中高型・尾高型
				else:
					for m in data[0]:
						phonemes.append( [m,0,0] )
					for n in data[1:int(accent)]:
						for m in n:
							phonemes.append( [m,0,1] )
					for n in data[int(accent):]:
						for m in n:
							phonemes.append( [m,0,0] )

			# ノードにアクセントがない場合
			else:
				for n in data:
					for m in n:
						phonemes.append( [m,0,0] )

		# 以上、各ノードに対する処理

		if mbtts_var.DEBUG:
			self.log.writeln(u'アクセント処理後:')
			#self.log.dump_phonemes( phonemes )

		return phonemes

	kana = {
		u"" : (u"",u"ア",u"イ",u"ウ",u"エ",u"オ"),
		u"k": (u"",u"カ",u"キ",u"ク",u"ケ",u"コ"),
		u"s": (u"",u"サ",u"シ",u"ス",u"セ",u"ソ"),
		u"t": (u"",u"タ",u"チ",u"ツ",u"テ",u"ト"),
		u"n": (u"",u"ナ",u"ニ",u"ヌ",u"ネ",u"ノ"),
		u"h": (u"",u"ハ",u"ヒ",u"フ",u"ヘ",u"ホ"),
		u"m": (u"",u"マ",u"ミ",u"ム",u"メ",u"モ"),
 		u"y": (u"",u"ヤ",u"イ",u"ユ",u"エ",u"ヨ"),
		u"r": (u"",u"ラ",u"リ",u"ル",u"レ",u"ロ"),
		u"w": (u"",u"ワ",u"ウィ",u"ウ",u"ウェ",u"ヲ"),
		u"g": (u"",u"ガ",u"ギ",u"グ",u"ゲ",u"ゴ"),
		u"z": (u"",u"ザ",u"ジ",u"ズ",u"ゼ",u"ゾ"),
		u"d": (u"",u"ダ",u"ヂ",u"ヅ",u"デ",u"ド"),
		u"b": (u"",u"バ",u"ビ",u"ブ",u"ベ",u"ボ"),
		u"p": (u"",u"パ",u"ピ",u"プ",u"ペ",u"ポ"),

		u"ky":(u"",u"キャ",u"キュ",u"キュ",u"キェ",u"キョ"),
		u"sy":(u"",u"シャ",u"シィ",u"シュ",u"シェ",u"ショ"),
		u"ty":(u"",u"チャ",u"チィ",u"チュ",u"チェ",u"チョ"),
		u"ny":(u"",u"ニャ",u"ニィ",u"ニュ",u"ニェ",u"ニョ"),
		u"hy":(u"",u"ヒャ",u"ヒィ",u"ヒュ",u"ヒェ",u"ヒョ"),
		u"my":(u"",u"ミャ",u"ミィ",u"ミュ",u"ミェ",u"ミョ"),
		u"ry":(u"",u"リャ",u"リィ",u"リュ",u"リェ",u"リョ"),
		u"gy":(u"",u"ギャ",u"ギィ",u"ギュ",u"ギェ",u"ギョ"),
		u"zy":(u"",u"ジャ",u"ジィ",u"ジュ",u"ジェ",u"ジョ"),
		u"dy":(u"",u"ヂャ",u"ヂィ",u"ヂュ",u"ヂェ",u"ヂョ"),
		u"by":(u"",u"ビャ",u"ビィ",u"ビュ",u"ビェ",u"ビョ"),
		u"py":(u"",u"ピャ",u"ピィ",u"ピュ",u"ピェ",u"ピョ"),

		u"j": (u"",u"ジャ",u"ジ",u"ジュ",u"ジェ",u"ジョ"),
		u"f": (u"",u"ファ",u"フィ",u"フ",u"フェ",u"フォ"),

		u"ts":(u"",u"ツァ",u"ツィ",u"ツ",u"ツェ",u"ツォ"),
		u"kw":(u"",u"クヮ",u"クィ",u"クゥ",u"クェ",u"クォ"),
		u"gw":(u"",u"グヮ",u"グィ",u"グゥ",u"グェ",u"グォ"),

		u"sh":(u"",u"シャ",u"シ",u"シュ",u"シェ",u"ショ"),
		u"ch":(u"",u"チャ",u"チ",u"チュ",u"チェ",u"チョ"),
		u"zh":(u"",u"ジャ",u"ジィ",u"ジュ",u"ジェ",u"ジョ"),

		u"c": (u"",u"カ",u"キ",u"ク",u"ケ",u"コ"),
	}

	matsubi = {
		u"k":u"ック",u"s":u"ス",u"t":u"ット",u"r":u"ル",u"l":u"ル",u"w":u"ウ",
		u"g":u"ッグ",u"z":u"",u"d":u"ッド",u"b":u"ッブ",u"p":u"ップ",u"m":u"ム",u"x":u"ックス",
		u"tch":u"ッチ",u"ck":u"ック",u"ch":u"ック",u"st":u"スト",u"sm":u"ズム",u"sh":u"ッシュ",
		u"th":u"ス",u"ry":u"リー",u"ly":u"リー",u"my":u"ミー",u"ty":u"ティー",u"ky":u"キー",
		u"sy":u"シー",u"xy":u"クシー",u"ng":u"ング",u"ll":u"ル",u"rt":u"ート",u"lf":u"ルフ",
		u"ld":u"ルド",u"gg":u"ッグ",
	}

	shiin = {
		u"b":u"ブ",u"c":u"ク",u"d":u"ド",u"f":u"フ",u"g":u"グ",u"h":u"フ",u"j":u"ジュ",u"k":u"ク",
		u"l":u"ル",u"m":u"ム",u"n":u"ヌ",u"p":u"プ",u"q":u"ク",u"r":u"ル",u"s":u"ス",
		u"t":u"ト",u"v":u"ブ",u"w":u"ウ",u"x":u"クス",u"y":u"イ",u"z":u"ズ",
	}

	v = {
		u"" :0,
		u"a":1,
		u"i":2,
		u"u":3,
		u"e":4,
		u"o":5,
	}


	def deromanize_pure( self, match ):
		"""アルファベットからなる文字列を仮名文字に変換する
		"""

		s = match.group()

		if s.upper() == s or len(s) == 1:
			return s.lower()

		s = s.lower()

		consonant , vowel, hatsu, choon = u"", u"", u"", u""

		result = u""
		while len(s):
			ch = s[0]
			s = s[1:]
			if ch in u"aiueo":
				vowel = ch
				if ( len(s) > 1 and s[0] == u"h" ) and not ( len(s) > 1 and s[1] in u"yaiueo" ):
					choon = u"ー"
					s = s[1:]
			elif ( len(s) == 0 and ch == "m" ):
				consonant = consonant + ch
				break
			elif ( ch == "n" or ch == "m" ) and ( len(s) == 0 or not s[0] in u"yaiueo" ):
				hatsu = u"ン"
			else:
				consonant = consonant + ch
				continue

			sokuon = u""
			while len(consonant) >= 2:
				if consonant[0] == consonant[1] or ( len(consonant) >= 3 and consonant[0:3] == u"tch" ):
					sokuon = u"ッ"
					consonant = consonant[1:]
				else:
					break

			if consonant in self.kana:
				temp = self.kana[consonant][self.v[vowel]]
			else:
				temp = u''
				for c in consonant:
					temp = temp + self.shiin[c]

				temp = temp + self.kana[u""][self.v[vowel]]

				if len(consonant) > 2:
					if consonant[-2:] in self.kana:
						temp = u''
						for c in consonant[:-2]:
							temp = temp + self.shiin[c]
						temp = temp + self.kana[consonant[-2:]][self.v[vowel]]
					else:
						if consonant[-1:] in self.kana:
							temp = u''
							for c in consonant[:-1]:
								temp = temp + self.shiin[c]
							temp = temp + self.kana[consonant[-1:]][self.v[vowel]]
				elif len(consonant) > 1:
					if consonant[-1:] in self.kana:
						temp = u''
						for c in consonant[:-1]:
							temp = temp + self.shiin[c]
						temp = temp + self.kana[consonant[-1:]][self.v[vowel]]

			result = result + sokuon + temp + choon + hatsu

			consonant , vowel, hatsu = u"", u"", u""

		return result + ( self.matsubi[consonant] if consonant in self.matsubi else consonant )


	def deromanize( self, s ):
		"""文字列中のアルファベットを仮名文字に変換する
		"""

		p = re.compile(u'[a-zA-Z]+')
		return p.sub( self.deromanize_pure, s )


	# 一と千の桁用
	numRead0 = {
		u"0":u"",
		u"1":u"一",
		u"2":u"二",
		u"3":u"三",
		u"4":u"四",
		u"5":u"五",
		u"6":u"六",
		u"7":u"七",
		u"8":u"八",
		u"9":u"九",
	}

	# それ以外の桁
	numRead1 = {
		u"0":u"",
		u"1":u"",
		u"2":u"二",
		u"3":u"三",
		u"4":u"四",
		u"5":u"五",
		u"6":u"六",
		u"7":u"七",
		u"8":u"八",
		u"9":u"九",
	}

	# 各桁の辞書のリスト
	numRead = [numRead0,numRead1,numRead1,numRead0]

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
	}

	numClass0 = {
		0:u'',
		1:u'十',
		2:u'百',
		3:u'千'
	}

	numClass1 = {
		0 : u"",
		1 : u"万",
		2 : u"億",
		3 : u"兆",
		4 : u"ケー",
		5 : u"垓"
	}

	numYomiHosei = {
		u"三百":u"サンビャク",
		u"六百":u"ロッピャク",
		u"八百":u"ハッピャク",
		u"一千":u"イッセン",
		u"三千":u"サンゼン",
		u"八千":u"ハッセン",
	}

	zen2han = {
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
		u'，':u',',
		u'．':u'.',
	}


	# 数値を表す文字列かどうかを調べる
	# 真のときは否定できないとき、数値区切りの可能性も残る 111,222,333
	def check_single_number(self,s):
		""" 数値を表す文字列かどうかを調べる
		"""

		# 数字だけからなる文字列ならば、真
		m = re.match( "\d+$", s )
		if m != None and m.group():
			return True

		# コンマを含まないとき、
		if s.count(u',') == 0:

			# ドットが一つ以外ならば、当然偽
			if s.count(u'.') != 1:
				return False

			# ドットで区切ってみる
			nums = s.split(u'.')

			# 整数部が一桁の0以外の0で始まる数のときは小数点数ではない
			if nums[0] != u"0":
				if len(nums[0]) > 1 and nums[0][0] == u"0":
					return False

			# 小数点数
			return True

		# コンマが含まれなければ、当然偽
		if s.count(u',') == 0:
			return False

		# コンマで区切ってみる
		nums = s.split(u',')

		# 末尾を抜き取る
		last_num = nums.pop()

		# 末尾項目以外に小数点があればコンマは区切り記号
		flag = False
		for num in nums:
			if num.count(u'.'):
				return False

		# 最後の項目に小数点が複数あると数値区切り
		if last_num.count(u'.') > 1:
			return False

		# 最後の項目に小数点があるとき、整数部が３桁でなければ数値区切り
		if last_num.count(u'.') == 1:
			i = last_num.split(u'.')
			if len(i[0]) != 3:
				return False

		# 最後の項目に小数点がないときは、３桁でなければ数値区切り
		if last_num.count(u'.') == 0:
			if len(last_num) != 3:
				return False

		# 先頭項目を抜き取る
		first_num = nums.pop(0)

		# 先頭の項目が４桁以上ならば、数値区切り
		if len(first_num) > 3:
				return False

		# 先頭、末尾以外の項目が３桁でないならば、数値区切り
		for num in nums:
			if len(num) != 3:
				return False

		# 数値区切りのコンマの可能性も残るがここでは判断できない
		return True


	# ドットが数値区切りとして使われているかチェック
	# 区切られる数値にはコンマが含まれないとする
	def check_dot_list(self,s):
		"""数値からなるドットリストかどうかを確認するメソッド
		"""

		# ドットが含まれなければ、当然偽
		if s.count(u'.') == 0:
			return False

		# ドットで区切ってみる
		nums = s.split(u'.')

		# 項目にコンマが含まれれば、ドット区切りではない
		flag = False
		for num in nums:
			if num.count(u','):
				return False

		# ただの小数点数の可能性もあるが、それはここでは判断できない
		return True


	# 小数点を含むかもしれない数値を日本語にする
	# コンマは正常であるとし確認せずに削除する
	def convert_number(self,s):
		"""数値を日本語に変換するメソッド
		"""

		if s == None or s == "":
			return u""

		if s == u"0":
			return u"ゼロ"

		# コンマを削除
		s = re.sub(u",", u"", s)

		# 結果格納変数
		result = u""

		# 小数点がなければ、
		if s.count(u'.') == 0:
			# 整数として変換
			result = self.convert_integer( s )

		# 小数点があれば、
		else:
			# ドットで区切ってみる
			nums = s.split(u'.')

			# 整数部
			if nums[0] == u"" or  nums[0] == u"0":
				result = u"レイ"
			else:
				result = self.convert_integer( nums[0] )

			# 小数部が複数あるときも、とりあえず変換
			for num in nums[1:]:

				# 小数点
				result = result + u"テン"

				# 小数部
				if num != u"":
					# 一桁ずつ読む
					for ch in num:
						result = result + self.numRead2[ch]

		return result


	# 整数を日本語にする
	# コンマは正常であるとし確認せずに削除する
	def convert_integer(self,source):
		"""整数を日本語に変換するメソッド
		"""

		# 念のため、排除
		if source == None or source == "":
			return u""

		# ゼロ
		if source == u"0":
			return u"ゼロ"

		# コンマを削除
		s = re.sub(u",", u"", source)

		# 結果格納変数
		result = u""
	
		# 最上位が０ならば一桁ずつ読む
		if len(s) > 1 and s[0] == u"0":
			for ch in s:
				result = result + self.numRead2[ch]
			return result

		# 「千」のための辞書の置き換え
		self.numRead[3] = self.numRead1 if len(source) == 4 else self.numRead0

		# 四桁毎の変換
		nums = []
		s = s[::-1]
		while len(s) > 3:
			temp = u''
			for i in range(4):
				if s[i] != u'0':
					temp = self.numRead[i][s[i]] + self.numClass0[i] + temp
			nums.append( temp )
			s = s[4:]

		# 残りの桁の変換
		temp = u''
		for i in range(len(s)):
			if len(s) > i and s[i] != u'0':
				temp = self.numRead[i][s[i]] + self.numClass0[i] + temp
		if temp:
			nums.append( temp )

		# 桁が大きすぎるときは変換せずに返す
		if len(nums) > len(self.numClass1):
			return source

		# 億、兆などを挿入する
		result = u''
		for i in range(len(nums)):
			if nums[i] != u'':
				result = nums[i] + self.numClass1[i] + result

		# 読みの補正
		for t, h in self.numYomiHosei.items():
			s = s.replace( t, h )

		return result


	# sub の変換関数
	def convert_pure_numstring(self,match):
		"""数値だけからなる文字列を日本語に変換するメソッド
		"""

		# マッチした文字列
		s = match.group()

		# 全角数字を半角数字に変換する
		for z, h in self.zen2han.items():
			s = s.replace( z, h )

		# 単一の数値（単一数値とみなせるものはすべて）
		if self.check_single_number( s ):
			result = self.convert_number(s)

		# ドットを数値区切りにした数値リスト
		elif self.check_dot_list( s ):
			nums = s.split(u".")
			result = u""
			for num in nums[:-1]:
				result = result + self.convert_integer(num) + u" ドット "
			result = result + self.convert_integer(nums[-1])

		# コンマを数値区切りにした数値リスト
		else:
			nums = s.split(u",")
			result = u""
			for num in nums[:-1]:
				result = result + self.convert_number(num) + u" コンマ "
			result = result + self.convert_number(nums[-1])

		return result


	# 文字列中の数値を日本語に変換する
	def convert_numstring(self,s):
		"""数値を日本語に変換するメソッド
		"""

		p = re.compile(u'[0-9０-９\.．][0-9０-９\.\,．，]*[0-9０-９]|[0-9０-９][0-9０-９\.\,．，]*[0-9０-９\.．]|[0-9０-９]')
		return p.sub( self.convert_pure_numstring, s )


	# 簡易辞書を読み込む
	def load_userdic(self):
		"""ユーザー辞書を読み込むメソッド
		"""
		# 辞書のソート用比較関数（長いものから先に調べるようにする）
		def length_comp(a):
			"""比較関数
			"""
			a = a.split(',')
			if a == []:
				return 0
			return -len(a[0])

		# 辞書がなければそのまま帰る
		if not os.path.exists( self.userdic ):
			return False

		f = open( self.userdic, 'r')
		self.userDic = []
		for line in f:
			self.userDic.append(unicode(line.strip(),'utf8'))
		self.userDic.sort( key=length_comp )
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
	def execute(self,s,spell):
		"""Unicode文字列をPHOデータに変換する
		"""

		# 単字詳細読みの音素変換処理
		if spell:
			return self._execute_spell(s)

		if mbtts_var.DEBUG:
			self.log.writeln(u"対象文字列:")
			self.log.writeln(s)
			self.log.writeln()

		# 簡易辞書を使ってカナ表記に置き換える
		if self.dic_enable:
			s = self.convert_using_userdic(s)

		if mbtts_var.DEBUG:
			self.log.writeln(u'簡易辞書変換後:')
			self.log.writeln(s)
			self.log.writeln()

#		for c in s:
#			print "char:%(ch)s = %(data)04x" % {"ch":c,"data":ord(c)}

		# 英字をローマ字読みに変換
		s = self.deromanize(s)

		# アルファベットを変換
		temp = ''
		for c in s:
			if c in self.alphabet_yomi:
				c = self.alphabet_yomi[c]
			temp = temp + c
		s = temp

		if mbtts_var.DEBUG:
			self.log.writeln(u'アルファベット変換後:')
			self.log.writeln(s)
			self.log.writeln()

		# 必読記号を変換
		temp = ''
		for c in s:
			if c in self.symbol_yomi:
				c = self.symbol_yomi[c]
			temp = temp + c
		s = temp

		if mbtts_var.DEBUG:
			self.log.writeln(u'必読記号変換後:')
			self.log.writeln(s)
			self.log.writeln()

		# 無視記号を無視、必要ならば変換
		temp = ''
		if self.reading_symbol_mode:
			for c in s:
				if c in self.symbol2_yomi:
					c = self.symbol2_yomi[c]
				temp = temp + c
		else:
			for c in s:
				if c in self.symbol2_yomi:
					c = u'　'
				temp = temp + c
		s = temp

		if mbtts_var.DEBUG:
			self.log.writeln(u'無視記号変換後:')
			self.log.writeln(s)
			self.log.writeln()

		# 文字列中の数値を日本語に変換
		s = self.convert_numstring(s)

		# 文字列をMeCabで処理できるエンコードに変換する
		s = s.encode(mbtts_var.MECAB_CHARSET)

		# MeCabで変換する
		node = self.mecab.parseToNode(s)
		node = node.next

		# mecab の解析結果をもとに各要素を変換
		result = []
		while node:

			# 入物用意
			nodes = []

			# 句点もしくは終端文字までを集めて、変換する。
			while node:
				try:
					# nodeから情報を分析する
					( string, category, accent_type ) = self.dic.analyze( node )

				# 分析できなければ、終端文字とみなしてループを脱出する。
				except:
					node = None
					break

				# 仮名文字を音素リストに変換する
				data = self.convert(string)

				# 入物に入れる
				nodes.append( (
						data,
						category,
						accent_type,
						unicode(node.surface,mbtts_var.MECAB_CHARSET)
					 ) )

				# 句点だったらループ脱出
				if  category == u'句点':
					node = node.next
					break

				# 次のノードへ
				node = node.next

			if mbtts_var.DEBUG:
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

			# 解析結果よりmbrola用の音素行を作成する
			if nodes:
				temp = self.make_pho_lines( nodes )

				# 今での結果に連結
				result.extend(temp)

		return result


	# 単字詳細読みの音素変換処理
	def _execute_spell(self,string):
		"""Unicode文字列をPHOデータに変換する
		"""

		if mbtts_var.DEBUG:
			self.log.writeln(u"対象文字列:")
			self.log.writeln(s)
			self.log.writeln()

		# 単字詳細読み辞書を使ってカナ表記に置き換える
		string = tankanji.convert(string)

		if mbtts_var.DEBUG:
			self.log.writeln(u'単漢字詳細読み変換後:')
			self.log.writeln(string)
			self.log.writeln()

		# 変換
		data = self.convert(string)

		# 渡すために入物に入れる
		nodes = [ ( data, None, None, string ) ]

		# 解析結果よりmbrola用の音素行を作成する
		result = []
		if nodes:
			result = self.make_pho_lines( nodes )

		return result


	# アクセントのモードを設定する
	def set_accent_mode(self,mode):
		if mode == 1:
			self.text_charset = 1
		else:
			self.text_charset = 0


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
			self.reading_symbol_mode = 1
		else:
			self.reading_symbol_mode = 0


# ログ出力用クラス
class Log:
	def __init__(self,name):

		self.fp = None
		try:
			self.fp = open(name,'w')
		except:
			raise Exception(u"おそらく、ログファイルが既に開かれています。"
							+ u"閉じてからやり直してみてください。")
	def __del__(self):
		if self.fp:
			self.fp.close()

	def write(self,data=""):
		data = data.encode(mbtts_var.SYSTEM_CHARSET)
		if self.fp:
			self.fp.write(data)
		print data,

	def writeln(self,data=""):
		data = data.encode(mbtts_var.SYSTEM_CHARSET)
		if self.fp:
			self.fp.write(data)
			self.fp.write('\n')
		print data

	def dump_phonemes(self,phonemes):
		for i in phonemes:
			self.writeln( str(i[0]) + '\t'  + str(i[1]) + '\t'  + str(i[2]) )
		self.writeln()

