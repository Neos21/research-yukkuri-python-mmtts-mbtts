# -*- coding: utf8 -*-
# mecab_aquestalk2.py
# mbtts 0.97
# 2010/08/18
# copyright(c) takayan
# http://neu101.seesaa.net/

import platform
import os
from array import array
import ctypes
from ctypes import *
import mb_converter
import mbtts_var

##### クラス #####

# aquestalk用の音素に変換するクラス
# aquestalkが解釈できる文字列を生成するまでの処理を担当する

class AquesTalk2(mb_converter.Conv):
	"""aquestalk2用の音素ファイルを生成するためのクラス
	"""

	name = u'aquestalk2'

	engine_type = 'aquestalk2'

	##### コンストラクタ #####
	def __init__(self,phont_name,dic_name):

		if not mbtts_var.AQUESTALK2_PATH:
			raise Exception(u"AquesTalk2 のDLLが見つかりません")

		# プラットフォームに合わせた DLL の読み込み
		try:
			ps = platform.system()
			if ps == "Linux" or ps == "Darwin":
				d = cdll.LoadLibrary(mbtts_var.AQUESTALK2_PATH)

			elif ps == "Windows":
				d = windll.LoadLibrary(mbtts_var.AQUESTALK2_PATH)

			else:
				raise Exception(u"対応していないプラットフォームです")
		except:
			raise Exception(u"dllをロードできません。")

		# 音声データ生成メソッド
		self.aques_synthe = d.AquesTalk2_Synthe
		self.aques_synthe.argtypes = [ctypes.c_char_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p]
		self.aques_synthe.restype = ctypes.c_void_p

		# 音声データ解放メソッド
		self.aques_free = d.AquesTalk2_FreeWave
		self.aques_free.argtypes = [ctypes.c_void_p]
		self.aques_free.restype = None

		# 声種データを読み込む
		self.phont_data = 0
		if phont_name:
			path = os.path.join( mbtts_var.PHONT_DIR, phont_name + ".phont" )
			if os.path.exists(path):
				f = open(path,"rb")
				self.phont_data = f.read()
				f.close()

		# 基底クラスのコンストラクタを呼び出す
		mb_converter.Conv.__init__(self,"aquestalk2",dic_name,"aquestalk2")


	##### デストラクタ #####
	def __del__(self):
		pass


	### 音素データ ###

	# 仮名文字をアルファベットに変換するテーブル
	convert_table = {
		u'ア':u'あ',
		u'あ':u'あ',
		u'イ':u'い',
		u'い':u'い',
		u'ウ':u'う',
		u'う':u'う',
		u'エ':u'え',
		u'え':u'え',
		u'オ':u'お',
		u'お':u'お',
		u'カ':u'か',
		u'か':u'か',
		u'キ':u'き',
		u'き':u'き',
		u'ク':u'く',
		u'く':u'く',
		u'ケ':u'け',
		u'け':u'け',
		u'コ':u'こ',
		u'こ':u'こ',
		u'サ':u'さ',
		u'さ':u'さ',
		u'シ':u'し',
		u'し':u'し',
		u'ス':u'す',
		u'す':u'す',
		u'セ':u'せ',
		u'せ':u'せ',
		u'ソ':u'そ',
		u'そ':u'そ',
		u'タ':u'た',
		u'た':u'た',
		u'チ':u'ち',
		u'ち':u'ち',
		u'ツ':u'つ',
		u'つ':u'つ',
		u'テ':u'て',
		u'て':u'て',
		u'ト':u'と',
		u'と':u'と',
		u'ナ':u'な',
		u'な':u'な',
		u'ニ':u'に',
		u'に':u'に',
		u'ヌ':u'ぬ',
		u'ぬ':u'ぬ',
		u'ネ':u'ね',
		u'ね':u'ね',
		u'ノ':u'の',
		u'の':u'の',
		u'ハ':u'は',
		u'は':u'は',
		u'ヒ':u'ひ',
		u'ひ':u'ひ',
		u'フ':u'ふ',
		u'ふ':u'ふ',
		u'ヘ':u'へ',
		u'へ':u'へ',
		u'ホ':u'ほ',
		u'ほ':u'ほ',
		u'マ':u'ま',
		u'ま':u'ま',
		u'ミ':u'み',
		u'み':u'み',
		u'ム':u'む',
		u'む':u'む',
		u'メ':u'め',
		u'め':u'め',
		u'モ':u'も',
		u'も':u'も',
		u'ヤ':u'や',
		u'や':u'や',
		u'ユ':u'ゆ',
		u'ゆ':u'ゆ',
		u'ヨ':u'よ',
		u'よ':u'よ',
		u'ラ':u'ら',
		u'ら':u'ら',
		u'リ':u'り',
		u'り':u'り',
		u'ル':u'る',
		u'る':u'る',
		u'レ':u'れ',
		u'れ':u'れ',
		u'ロ':u'ろ',
		u'ろ':u'ろ',
		u'ワ':u'わ',
		u'わ':u'わ',
		u'ヮ':u'ゎ',
		u'ゎ':u'ゎ',
		u'ヰ':u'ゐ',
		u'ゐ':u'ゐ',
		u'ヱ':u'ゑ',
		u'ゑ':u'ゑ',
		u'ヲ':u'を',
		u'を':u'を',
		u'ガ':u'が',
		u'が':u'が',
		u'ギ':u'ぎ',
		u'ぎ':u'ぎ',
		u'グ':u'ぐ',
		u'ぐ':u'ぐ',
		u'ゲ':u'げ',
		u'げ':u'げ',
		u'ゴ':u'ご',
		u'ご':u'ご',
		u'ザ':u'ざ',
		u'ざ':u'ざ',
		u'ジ':u'じ',
		u'じ':u'じ',
		u'ズ':u'ず',
		u'ず':u'ず',
		u'ゼ':u'ぜ',
		u'ぜ':u'ぜ',
		u'ゾ':u'ぞ',
		u'ぞ':u'ぞ',
		u'ダ':u'だ',
		u'だ':u'だ',
		u'ヂ':u'ぢ',
		u'ぢ':u'ぢ',
		u'ヅ':u'づ',
		u'づ':u'づ',
		u'デ':u'で',
		u'で':u'で',
		u'ド':u'ど',
		u'ど':u'ど',
		u'バ':u'ば',
		u'ば':u'ば',
		u'ビ':u'び',
		u'び':u'び',
		u'ブ':u'ぶ',
		u'ぶ':u'ぶ',
		u'ベ':u'べ',
		u'べ':u'べ',
		u'ボ':u'ぼ',
		u'ぼ':u'ぼ',
		u'パ':u'ぱ',
		u'ぱ':u'ぱ',
		u'ピ':u'ぴ',
		u'ぴ':u'ぴ',
		u'プ':u'ぷ',
		u'ぷ':u'ぷ',
		u'ペ':u'ぺ',
		u'ぺ':u'ぺ',
		u'ポ':u'ぽ',
		u'ぽ':u'ぽ',
		u'ん':u'ん',
		u'ン':u'ん',
		u'ぁ':u'ぁ',
		u'ァ':u'ぁ',
		u'ぃ':u'ぃ',
		u'ィ':u'ぃ',
		u'ぅ':u'ぅ',
		u'ゥ':u'ぅ',
		u'ぇ':u'ぇ',
		u'ェ':u'ぇ',
		u'ぉ':u'ぉ',
		u'ォ':u'ぉ',
		u'ゎ':u'ゎ',
		u'ヮ':u'ゎ',
		u'ゃ':u'ゃ',
		u'ャ':u'ゃ',
		u'ゅ':u'ゅ',
		u'ュ':u'ゅ',
		u'ょ':u'ょ',
		u'ョ':u'ょ',
		u'ヴ':u'ヴ',
		u'っ':u'っ',
		u'ッ':u'っ',
		u'。':u'。',
		u'？':u'？',
		u'ー':u'ー',
		u'、':u'、',
		u',':u',',
		u';,':u';',
		u'/':u'/',
		u'+':u'+',
#		u'!':u'！',
	}


	##### Phoneme_aquestalk メソッド定義 #####

	# テキストを音声ファイルに変換する
	def make_sound_file( self, text, filename, volume ):

		# 読み上げ速度
		if self.rate >= 1.0:
			speed = self.rate * 37.5
		else:
			speed = self.rate * 100
		speed = int(speed)

		text = text.encode('shift-jis')
		size = ctypes.c_int()
		data = self.aques_synthe(text,speed,ctypes.byref(size),self.phont_data)

		if data != None:
			byte_ary = array('B')

			for i in range(size.value):
			    byte = ctypes.c_ubyte.from_address(data+i).value
			    byte_ary.append(byte)

			self.aques_free(data)

			for i in range(byte_ary[40]/2):
				val = int( byte_ary[i+44] * volume )
				if val > 32767:
					val =  32767
				elif val < -32768:
					val = -32768
				byte_ary[i+44] = val

			fp = open(filename, "wb")
			byte_ary.tofile(fp)
			fp.close()


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
		if s == u'':
			return []

		# 空白文字ならば、「。」にして返す
		if s == u' ' or s == u'　':
			return [u'。']

		# 仮名文字列を正規化する（簡易処理）
		string = u''
		for ch in s:
			if ch in self.convert_table:
				string = string + self.convert_table[ch]

		return string


	# 単字詳細読みの音素変換処理
	def _execute_spell(self,string):
		"""Unicode文字列を音素データに変換する
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
		string = self.convert(string)

		return [string]


	# 音素変換処理
	def execute(self,s,spell):
		"""Unicode文字列を音素データに変換する
		戻り値は文字列の配列
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
		temp = u''
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
		temp = u''
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
		temp = u''
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

			# 解析結果より音素行を作成する
			if nodes:
				temp = self.make_ph_string( nodes )

				# 今での結果に連結
				result.append(temp)

		return result


	# 音素を出力する
	def make_ph_string( self, nodes ):

		# node( 音素リスト, 品詞, アクセント, ソース )

		# アクセントを考慮した音素データリストを作成
		# print "nodes:",nodes
		phonemes = self.accented_phonemes_list( nodes )

		if mbtts_var.DEBUG:
			self.log.writeln(u'処理後:')
			#self.log.dump_phonemes( phonemes )

		# それを文字列にする
		result = u''
		for ph in phonemes:
			if ph[0] != u'_':
				ch = ph[0]
			else:
				ch = u'。'

			result = result + ch

		if mbtts_var.DEBUG:
			self.log.writeln(u'変換結果:' + result )

		return result


