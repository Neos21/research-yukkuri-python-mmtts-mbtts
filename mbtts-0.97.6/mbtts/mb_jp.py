# -*- coding: utf8 -*-
# mecab_jp.py
# mbtts 0.97
# 2010/08/25
# copyright(c) takayan
# http://neu101.seesaa.net/

import os
import platform
import subprocess
import mb_converter
import mbtts_var
import tankanji


##### クラス #####

# JP 関連の共通メソッドを定義するクラス

class JP(mb_converter.Conv):

	engine_type = u'mbrola'

	freq = 22050

	##### データ#####

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


	##### メソッド定義 #####

	# wavファイルを作成する
	def wave_generate( self, phofile, filename, volume ):
		"""PHOファイルを元に音声ファイルを生成する。
		"""

		if not mbtts_var.MBROLA_PATH:
			return

		command  = mbtts_var.MBROLA_PATH
		command += ' -e -v ' + str(volume)
		command += ' ' + self.database
		command += ' ' + phofile
		command += ' ' + filename
		command = command.encode(mbtts_var.SYSTEM_CHARSET)
		os.system( command )


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
