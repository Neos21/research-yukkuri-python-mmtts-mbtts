# -*- coding: utf8 -*-
# mecab_openjtalk.py
# mbtts 0.97
# 2010/08/25
# copyright(c) takayan
# http://neu101.seesaa.net/

from array import array
import platform
import os
import mb_converter
import mbtts_var
import tankanji


##### クラス #####

# openjtalk 関連メソッドを定義するクラス

class OpenJTalk(mb_converter.Conv):
	"""openjtalk用の音素ファイルを生成するためのクラス
	"""

	name = u'openjtalk'

	engine_type = u'openjtalk'

	freq = 16000


	##### コンストラクタ #####
	def __init__(self,phont_name,dic_name):

		self.phont_name = phont_name

		# 基底クラスのコンストラクタを呼び出す
		mb_converter.Conv.__init__(self,"openjtalk",dic_name,"openjtalk")


	##### デストラクタ #####
	def __del__(self):
		pass


	##### メソッド定義 #####

	# wavファイルを作成する
	def wave_generate( self, textfile, file, volume ):
		"""PHOファイルを元に音声ファイルを生成する。
		"""

		if self.phont_name:
			voice = os.path.join(mbtts_var.OPENJTALK_VOICES_PATH,self.phont_name)
		else:
			voice = os.path.join(mbtts_var.OPENJTALK_VOICES_PATH,mbtts_var.OPENJTALK_VOICES[0])

		if not os.path.exists(voice):
			raise Exception(u"Open JTalk用の音声設定ファイルが見つかりません。")

		dic = mbtts_var.OPENJTALK_DIC_PATH
		if not dic or not os.path.exists(dic):
			raise Exception(u"Open JTalk用の辞書ファイルが見つかりません。")

		command = mbtts_var.OPENJTALK_PATH
		command += ' -td ' + os.path.join( voice, 'tree-dur.inf' )
		command += ' -tf ' + os.path.join( voice, 'tree-lf0.inf' )
		command += ' -tm ' + os.path.join( voice, 'tree-mgc.inf' )
		command += ' -md ' + os.path.join( voice, 'dur.pdf' )
		command += ' -mf ' + os.path.join( voice, 'lf0.pdf' )
		command += ' -mm ' + os.path.join( voice, 'mgc.pdf' )
		command += ' -df ' + os.path.join( voice, 'lf0.win1' )
		command += ' -df ' + os.path.join( voice, 'lf0.win2' )
		command += ' -df ' + os.path.join( voice, 'lf0.win3' )
		command += ' -dm ' + os.path.join( voice, 'mgc.win1' )
		command += ' -dm ' + os.path.join( voice, 'mgc.win2' )
		command += ' -dm ' + os.path.join( voice, 'mgc.win3' )
		command += ' -ef ' + os.path.join( voice, 'tree-gv-lf0.inf' )
		command += ' -em ' + os.path.join( voice, 'tree-gv-mgc.inf' )
		command += ' -cf ' + os.path.join( voice, 'gv-lf0.pdf' )
		command += ' -cm ' + os.path.join( voice, 'gv-mgc.pdf' )
		command += ' -k  ' + os.path.join( voice, 'gv-switch.inf' )
		command += ' -s  ' + str(self.freq)
		command += ' -x  ' + dic
		command += ' -a  ' + str(mbtts_var.OPENJTALK_A)
		command += ' -g  ' + str(mbtts_var.OPENJTALK_G)
		command += ' -u  ' + str(mbtts_var.OPENJTALK_U)
		command += ' -z  ' + str(mbtts_var.OPENJTALK_Z)
		command += ' -jm ' + str(mbtts_var.OPENJTALK_JM)
		command += ' -jf ' + str(mbtts_var.OPENJTALK_JF)
		command += ' -jl ' + str(mbtts_var.OPENJTALK_JL)
		command += ' -ow ' + file
		command += ' ' + textfile
		command = command.encode(mbtts_var.SYSTEM_CHARSET)
		os.system( command )
		if mbtts_var.DEBUG:
			print "command:" + command

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

		return [s]
