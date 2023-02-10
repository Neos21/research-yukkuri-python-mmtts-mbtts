# -*- coding: utf8 -*-
# mb_converter.py
# mbtts 0.95
# 2010/03/25
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
	def __init__(self,database_name,dic_name):

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

		# 記号を読むかどうかのフラグ
		self.reading_symbol_mode = mbtts_var.READING_SYMBOL_FLAG

		# アクセントを有効にするか
		self.accent_mode = mbtts_var.ACCENT_FLAG

		# データベースの名前の確認
		if database_name == "":
			raise Exception(u"データベースの名前が指定されていません")

		# データベースのパスを生成
		self.database = os.path.join( mbtts_var.DATABASE_DIR, database_name, database_name )

		# データベースの存在確認
		if not os.path.exists( self.database ):
			raise Exception(u"指定のデータベース " + database_name + u" が存在しません")

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


	# wavファイルを作成する
	def wave_generate( self, phofile, filename, volume ):
		"""PHOファイルを元に音声ファイルを生成する。
		"""

		# システムによって処理を切り替える
		ps = platform.system()
		if ps == "Linux":
			#mbrolaによりphoファイルをwavファイルに変換する
			subprocess.call( [
				mbtts_var.MBROLA_PATH,
				"-e","-v",str(volume),
				self.database, phofile, filename ] )

		elif ps == "Windows":
			#mbrolaによりphoファイルをwavファイルに変換する
			res = subprocess.call( [
				mbtts_var.MBROLA_PATH,
				"-e","-v",str(volume),
				self.database, phofile, filename ] )

		elif ps == "Darwin":
			#mbrolaによりphoファイルをwavファイルに変換する
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
			self.log.dump_phonemes( phonemes )

		return phonemes



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
				while par!=[]:
					if par[0] != '0':
						flag = 1
						# 「1」以外は必ず読む、一番下の桁ならば何でも読む
						if par[0] != '1' or len(par) == 1:
							s.append( self.numRead[par[0]] )
						s.append( self.numClass1[repr(len(par))] )
					par.pop(0)

				# そこに0以外の数字があれば
				if flag == 1:
					num = int(len(i)/4)
					s.append( self.numClass2[repr(num)] )

			# 四桁より短くて一桁でなければ
			while len(i) > 1:
				if i[0] != '0':
					# 「1」以外は必ず読む、一番下の桁ならば何でも読む
					if i[0] != '1' or len(i) == 1:
						s.append( self.numRead[i[0]] )
					s.append( self.numClass1[repr(len(i))] )
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
			if r != None:
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

