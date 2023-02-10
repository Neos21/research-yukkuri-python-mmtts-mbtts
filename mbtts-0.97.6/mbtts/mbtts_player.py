# -*- coding: utf8 -*-
# mbtts_player.py
# mbtts 0.97
# 2010/08/25
# copyright(c) takayan
# http://neu101.seesaa.net/


import mbtts_var
import mb_aquestalk2
import mb_openjtalk
import pygame.mixer
import Queue
from threading import Thread
import time
import tempfile
import os
import re
import platform
import sys
if platform.system() == "Windows":
	import winsound


# MBTTSplayerクラス
class MBTTSplayer:
	"""TTSを管理するクラス。
	コンストラクタに渡す文字列によってデータベースと使用する変換辞書を指定する。
	発音や音声ファイル生成のメソッドが定義されている。
	"""

	# 音声合成エンジン名抽出
	def get_engine_voice(self,s):
		"""
		"""

		# mbrola の音声を得る
		def select_voice_mbrola(name):
			"""
			"""

			# データベース名が指定されていないときは、標準を用いる
			if name == None:
				name = mbtts_var.DEFAULT_DATABASE

			name = name.lower()
			if name in mbtts_var.DATABASES:
				return ( mbtts_var.DATABASES[name], u"mbrola", name )

			return ( None, u"mbrola", None )

		# aquestalk2 の音声を得る
		def select_voice_aquestalk2(name):
			"""
			"""

			# 声種が指定されていないときは、標準を用いる
			if name == None:
				return ( mb_aquestalk2.AquesTalk2, u"aquestalk2", None )

			# 声種が指定されているときは、それが使えるか調べる
			else:
				if name in mbtts_var.PHONTS:
					return ( mb_aquestalk2.AquesTalk2, u"aquestalk2", name )

			return ( None, u"aquestalk2", None )

		# openjtalk の音声を得る
		def select_voice_openjtalk(name):
			"""
			"""

			# 声種が指定されていないときは、標準を用いる
			if name == None:
				return ( mb_openjtalk.OpenJTalk, u"openjtalk", None )

			if name in mbtts_var.OPENJTALK_VOICES:
				return ( mb_openjtalk.OpenJTalk, u"openjtalk", name )

			return ( None, u"openjtalk", None )


		engines = {
			"mbrola"     : select_voice_mbrola,
			"aquestalk2" : select_voice_aquestalk2,
			"openjtalk"  : select_voice_openjtalk,
		}

		s = s.lower()
		s = re.sub( u'\(default\)', '', s )
		if s in engines:
			return engines[s](None)

		# ドット記法にマッチできれば
		m = re.match( "(.+?)\.(.+)$", s )
		if m:
			engine = m.group(1)
			if engine in engines:
					return engines[engine](m.group(2))

			return ( None, None, None )

		# 音声合成エンジンの指定がない場合
		else:
			for func in engines.values():
				( meth, engine, voice ) = func(s)
				if meth:
					return ( meth, engine, voice )

		# どの可能性もない場合
		return ( None, None, None )


	##### コンストラクタ #####
	def __init__(self,database_name=mbtts_var.DEFAULT_VOICE,dic_name=mbtts_var.DIC_NAME):
		"""
		"""

		# 声種名の初期化（MBROLAには関係ないけど）
		self.phont = None

		# 文字列からメソッド、エンジン、声データベースを獲得
		( meth, engine, voice ) = self.get_engine_voice(database_name)
		if not meth:
			# 標準の音声もためしてみる
			if database_name != mbtts_var.DEFAULT_VOICE:
				raise Exception( u"音声 " + database_name + u" にできませんでした")
				( meth, engine, voice ) = self.get_engine_voice(mbtts_var.DEFAULT_VOICE)
				print u"音声 " + database_name + u" にできませんでした。代わりに標準音声にします。"

			if not meth:
				raise Exception( u"音声 " + database_name + u" にできませんでした")


		# 変換器を獲得
		self.converter = meth( voice, dic_name )

		# 辞書の名前
		self.dic_name = dic_name

		# 記号を読むかどうかのフラグ
		self.reading_symbol_mode = mbtts_var.READING_SYMBOL_FLAG

		# アクセントを有効
		self.accent_mode = mbtts_var.ACCENT_FLAG

		# 入力テキストの標準文字コード
		self.text_charset = mbtts_var.TEXT_CHARSET

		# 標準音量比率
		self.volume = 1.0

		# 標準読み上げ速度比率
		self.rate = 1.0

		# 標準ピッチ比率
		self.pitch = 1.0

		# スレッド配列
		self.threads = []

		# キューロック
		self.queue_lock = False

		# キュー用のスレッド
		self.queue_thread = None

		# 再生開始時コールバック
		self._start  = None

		# 再生終了時コールバック
		self._finish = None

		# 読み上げエンジンの種類
		self.engine_type = self.converter.engine_type

		# mixer初期化
		pygame.mixer.quit()
		if self.converter.freq:
			pygame.mixer.init(frequency=self.converter.freq)

		# Queueの作成
		self.string_queue = Queue.Queue()


	##### デストラクタ #####
	def __del__(self):
		pass


	##### メソッド定義 #####


	# テキストからPHOファイルを作成する
	def text_to_pho(self,string,filename):
		"""テキストからPHOファイルを作成する。
		文字列とファイル名の文字コードはUnicode
		"""

		if string == '':
			return False

		# ファイル名をシステム向けに変換する
		filename = filename.encode(mbtts_var.SYSTEM_CHARSET)

		# PHOファイルを作成する
		return self._text_to_pho(string,filename,0)


	# テキストからPHOファイルを作成する
	def _text_to_pho(self,string,filename,spell):
		"""テキストからPHOファイルを作成する。
		文字列の文字コードはUnicode
		ファイル名はシステム名
		"""

		if string == '':
			return False

		# 音素変換インスタンスにパラメータを与える
		self.converter.set_accent_mode( self.accent_mode )					# アクセントの有無設定
		self.converter.set_reading_symbol( self.reading_symbol_mode )		# 記号読みの設定
		self.converter.set_rate( self.rate )								# レートの設定
		self.converter.set_pitch( self.pitch )								# ピッチの設定

		# テキストから音素リストを生成
		ps = self.converter.execute(string,spell)

		if ps == []:
			return False

		# 書き込み用ファイルを開く
		phofile = open( filename, 'w')

		# 音素リストを出力
		wave = "";
		for ph in ps:
			phofile.write(ph+'\n')

		# 音素ファイルを閉じる
		phofile.close()

		return True


	# テキストリストからPHOファイルを作成する
	def lines_to_pho(self,lines,filename):
		"""テキストリストからPHOファイルを作成する。
		文字列もファイル名もUnicodeでエンコードされているとする。
		ファイル名は'.pho'が既に付加されているとみなす
		"""

		# 書き込み用にPHOファイルを開く
		if filename == sys.stdout:
			phofile = sys.stdout
		else:
			# ファイル名をシステム向けに変換する
			filename = filename.encode(mbtts_var.SYSTEM_CHARSET)

			# 書き込み用ファイルを開く
			phofile = open( filename, 'w')

		# 音素変換クラス生成
		self.converter.set_accent_mode( self.accent_mode )					# アクセントの有無設定
		self.converter.set_reading_symbol( self.reading_symbol_mode )		# 記号読みの設定
		self.converter.set_rate( self.rate )								# レートの設定
		self.converter.set_pitch( self.pitch )								# ピッチの設定

		# 各入力に対して
		for line in lines:

			# テキストから音素リストを生成
			ps = self.converter.execute(line,0)
			if ps == []:
				return

			# 音素リストを出力
			wave = "";
			for ph in ps:
				phofile.write(ph+'\n')

		# 音素ファイルを閉じる
		phofile.close()


	# テキストを音声ファイルに変換する
	def speak_to_file(self,string,filename):
		self._speak_to_file(string,filename,0)

	# テキストを一文字ずつ読み上げた音声ファイルに変換する
	def speak_spell_to_file(self,string,filename):
		self._speak_to_file(string,filename,1)

	# テキストを音声ファイルに変換する
	def _speak_to_file(self,string,filename,spell):
		"""テキストを音声ファイルに変換する。
		文字列もファイル名もUnicodeでエンコードされているとする。
		ファイル名は'.wav'が既に付加されているとする。
		"""

		ps = platform.system()
		if ps != "Linux" and ps != "Windows" and ps != "Darwin" :
			raise Exception(u"このシステムには対応していません")

		# 入力文字列から余白を削除
		string = string.strip()

		# 音声合成エンジンに合わせて音声ファイル生成の処理を行う

		# mbrola 向けの処理
		if self.engine_type == "mbrola":

			# PHO用の一時ファイルを作成
			file = tempfile.mkstemp('.pho')	
			file_obj = os.fdopen(file[0], 'w')
			file_obj.write('a')
			file_obj.close()
			phofile = file[1]

			# 一時phoファイルを作成する
			ret = self._text_to_pho(string,phofile,spell)

			# wavファイルを作成する
			self.converter.wave_generate( phofile, filename, self.volume )

			# 一時ファイルを削除
			if os.path.exists(phofile):
				os.remove(phofile)

		# aquestalk2 向けの処理
		elif self.engine_type == "aquestalk2":

			if string == '':
				return False

			# 音素変換インスタンスにパラメータを与える
			self.converter.set_accent_mode( self.accent_mode )					# アクセントの有無設定
			self.converter.set_reading_symbol( self.reading_symbol_mode )		# 記号読みの設定
			self.converter.set_rate( self.rate )								# レートの設定
			self.converter.set_pitch( self.pitch )								# ピッチの設定

			# テキストから音素リストを生成
			lines = self.converter.execute(string,spell)

			# 解析結果を一つの文字列にする
			if lines == []:
				return False
			text = u''
			for s in lines:
				text = text + s + u'。'

			# wavファイルを作成する
			self.converter.wave_generate( text, filename, self.volume )

		# openjtalk 向けの処理
		elif self.engine_type == "openjtalk":

			# テキスト用の一時ファイルを作成
			file = tempfile.mkstemp('.txt')
			file_obj = os.fdopen(file[0], 'w')
			file_obj.write('a')
			file_obj.close()
			textfile = file[1]

			# テキストファイルを作成する
			f = open( textfile, 'w' )
			f.write(string.encode(mbtts_var.OPENJTALK_CHARSET))
			f.close()

			# wavファイルを作成する
			self.converter.wave_generate( textfile, filename, self.volume )

			# 一時ファイルを削除
			if os.path.exists(textfile):
				os.remove(textfile)

		# 未対応なエンジン
		else:
			raise Exception( self.engine_type + u"は対応していないエンジンです。")


	# テキストのリストを音声ファイルに変換する
	def speak_lines_to_file(self,lines,filename):
		"""テキストリストを音声ファイルに変換する。
		文字列もファイル名もUnicodeでエンコードされているとする。
		またファイル名は'.wav'が既に付加されているとする。
		"""

		ps = platform.system()
		if ps != "Linux" and ps != "Windows" and ps != "Darwin" :
			raise Exception(u"このシステムには対応していません")

		# 音声合成エンジンに合わせて音声ファイル生成の処理を行う

		# mbrola 向けの処理
		if self.engine_type == "mbrola":

			# PHO用の一時ファイルを作成
			file = tempfile.mkstemp('.pho')
			file_obj = os.fdopen(file[0], 'w')
			file_obj.write('a')
			file_obj.close()
			phofile = file[1]

			# phoファイルを作成する
			self.lines_to_pho(lines,phofile)

			# wavファイルを作成する
			self.converter.wave_generate( phofile, filename, self.volume )

			# 一時ファイルを削除
			if os.path.exists(phofile):
				os.remove(phofile)

		# aquestalk2 向けの処理
		elif self.engine_type == "aquestalk2":

			if string == u'':
				return False

			# 音素変換インスタンスにパラメータを与える
			self.converter.set_accent_mode( self.accent_mode )					# アクセントの有無設定
			self.converter.set_reading_symbol( self.reading_symbol_mode )		# 記号読みの設定
			self.converter.set_rate( self.rate )								# レートの設定
			self.converter.set_pitch( self.pitch )								# ピッチの設定

			# テキストから音素リストを生成
			lines = self.converter.execute(string,spell)

			# 解析結果を一つの文字列にする
			if lines == []:
				return False
			text = u''
			for s in lines:
				text = text + s + u'。'

			# wavファイルを作成する
			self.converter.wave_generate( text, filename, self.volume )

		# openjtalk 向けの処理
		elif self.engine_type == "openjtalk":

			# テキスト用の一時ファイルを作成
			file = tempfile.mkstemp('.txt')
			file_obj = os.fdopen(file[0], 'w')
			file_obj.write('a')
			file_obj.close()
			textfile = file[1]

			# テキストファイルを作成する
			f = open( textfile, 'w' )
			for line in lines:
				f.write(line.encode(mbtts_var.OPENJTALK_CHARSET)+'\n')
			f.close()

			# wavファイルを作成する
			self.converter.wave_generate( textfile, filename, self.volume )

			# 一時ファイルを削除
			if os.path.exists(textfile):
				os.remove(textfile)

		# 未対応なエンジン
		else:
			raise Exception( self.engine_type + u"は対応していないエンジンです。")


	def simple_speak(self,string):
		"""単純にテキストを発音する
		文字列はUnicodeでエンコードされているとする。
		"""

		# wav用の一時ファイルを作成
		file = tempfile.mkstemp('.wav')
		file_obj = os.fdopen(file[0], 'w')
		file_obj.write('a')
		file_obj.close()
		wavfile = file[1]

		# 文字列から一時的なwavファイルを作成
		self._speak_to_file( string, wavfile, 0 )

		# 発音
		if os.path.exists(wavfile):

#			pygame.mixer.quit()
#			if self.converter.freq:
#				pygame.mixer.init(frequency=self.converter.freq)

			channel = pygame.mixer.Sound( wavfile ).play()

			# 再生完了まで待つ
			while channel.get_busy():
				pass

			# 一時ファイルを削除
			os.remove(wavfile)


	# ファイル全体を読み上げる
	def speak_file(self,filename,charset=None):

		filename = filename.encode(mbtts_var.SYSTEM_CHARSET)

		if not os.path.exists(filename):
			return None

		if charset == None:
			charset = self.text_charset

		f = open( filename, 'r')
		for l in f:
			try:
				l = unicode( l, charset )
			except:
				raise Exception(u"エンコードエラーです。ファイルの文字コードを確認してください。")
			self.simple_speak(l)
		f.close()

		return False


	def set_dic(self,name):
		"""変換に使う辞書を設定する
		"""
		self.dic_name = name


	def set_volume(self,val):
		"""音量を設定する
		範囲は0<=val<=1.0
		"""

		if val < 0.0:
			raise Exception(u"音量比率を0.0より小さくすることはできません")

		if val > 1.0:
			raise Exception(u"音量比率を1.0より大きくすることはできません")

		self.volume = val


	def set_rate(self,val):
		"""読み上げ速度を設定する
		範囲は rate > 0
		"""

		if val < 0.2:
			raise Exception(u"速度比率を0.2より小さくすることはできません")

		if val > 8.0:
			raise Exception(u"速度比率を8.0より大きくすることはできません")

		self.rate = val


	def set_pitch(self,val):
		"""読み上げピッチを設定する
		範囲は[0.2,8.0]
		"""
		if val <= 0:
			raise Exception(u"ピッチ比率を0.2より小さくすることはできません")
		if val > 8.0:
			raise Exception(u"ピッチ比率を8.0より大きくすることはできません")

		self.pitch = val


	# アクセントのモードを設定する
	def set_accent_mode(self,mode):
		if mode == 1:
			self.accent_mode = 1
		else:
			self.accent_mode = 0


	# 記号の読みをするかどうかを設定する
	def set_reading_mode(self,mode):
		"""記号の読みをするかどうかを設定する
		"""

		if mode == 1:
			self.reading_symbol_mode = 1
		else:
			self.reading_symbol_mode = 0


	# テキストの文字コードを設定する
	def set_text_charset(self,set):
		self.text_charset = set.encode(mbtts_var.SYSTEM_CHARSET)


	# 全ての発音が終了するまで待つ
	def until_finishing(self):
		"""全ての発音が終了するまで待つ。
		"""
		for t in self.threads:
			t.join()
		self.threads = []


	# 再生中かどうか
	def is_speaking(self):
		"""再生中かどうかを調べる。
		"""
		for t in self.threads:
			if t.isAlive():
				return True
		return False


	# 一時停止
	def pause(self):
		"""全ての発音を一時停止する。
		"""
		pygame.mixer.pause()


	# 再開
	def resume(self):
		"""一時停止された発音を再開する。
		"""
		pygame.mixer.unpause()


	# 全ての発音を終了させる
	def stop(self):
		"""全ての発音を終了させる。
		"""
#		while True:
#			try:
#				( obj, string, spell, timing, start, finish, speaker ) = self.string_queue.get(True,1)
#				print "削除：",string
#			except Queue.Empty:
#				break

#		self.string_queue = None
#		print "削除：",self.string_queue
#		self.queue_thread = None
		self.string_queue = Queue.Queue()
		pygame.mixer.stop()
		self.threads = []


	# コールバックとともに普通に読み上げる
	def speak_with_callback(self,string,start,finish,timing=1):
		"""普通に読み上げる
		"""
		return self._speak(string,0,0,timing,start,finish)


	# コールバックとともに一文字ずつ読み上げる
	def speak_spell_with_callback(self,string,start,finish,timing=1):
		"""一文字ずつ読み上げる
		"""
		return self._speak(string,1,0,timing,start,finish)


	# 普通に読み上げる
	def speak(self,string,sync=1,timing=1):
		"""普通に読み上げる
		"""
		return self._speak(string,0,sync,timing,None,None)


	# 一文字ずつ読み上げる
	def speak_spell(self,string,sync=1,timing=1):
		"""一文字ずつ読み上げる
		"""
		return self._speak(string,1,sync,timing,None,None)


	# テキストを音声で即出力する
	#
	# spell  : 0 ... 文字列として発音する
	#	       1 ... 一文字ずつ発音する
	# 省略時は0
	#
	# sync: 0 ... asynchronous	非同期（再生終了を待たずに戻る）
	#	    1 ... synchronous	同期　（再生終了まで待つ）
	# 省略時は1
	#
	# timing : 0 ... 待って発声する	現在発声中の音声を続ける	01
	#	       1 ... 今すぐ発声する	現在発生中の音声を止める	10
	#	       2 ... 今すぐ発声する	現在発生中の音声も続ける	11
	# 省略時は1

	def _speak(self,string,spell,sync,timing,start=None,finish=None):
		"""文字列を指定の方法により発音する。
		"""

		# スレッドクラス
		class _speak_thread:
			def __call__(self,obj,string,spell,queue,start,finish,speaker):

				# キュー再生の場合の処理
				if queue:
					count = 0

					# ループ
					while True:
						count = count + 1
						obj.queue_lock = True
						try:
							( obj, string, spell, timing, start, finish, speaker ) = obj.string_queue.get(True,1)
						# 獲得できなければ終了
						except Queue.Empty:
							obj.queue_thread = None
#							print "スレッド終了",self
							obj.queue_lock = False
							return
						obj.queue_lock = False

						# 他の再生が完了するまで待つ
						while pygame.mixer.get_busy():
							pass

						# 一時ファイルを作成
						wavfile = tempfile.mkstemp('.wav')
						wavfile_obj = os.fdopen(wavfile[0], 'w')
						wavfile_obj.write('a')
						wavfile_obj.close()
						name = wavfile[1]

						# 開始時のコールバック関数を実行
						if start:
							start()

						# 音声ファイル作成
						obj._speak_to_file( string, name, spell )

						# 音声ファイル再生
#						pygame.mixer.quit()
#						if obj.converter.freq:
#							pygame.mixer.init(frequency=obj.converter.freq)
						channel = pygame.mixer.Sound(name).play()
						speaker.channel = channel

						# 再生完了まで待つ
						while channel.get_busy():
							pass

						# 音声ファイルの削除
						os.remove( name )

						# 終了時のコールバック関数を実行
						if finish:
							finish()

				# キュー再生ではない場合の処理
				else:
					# 一時ファイルを作成
					wavfile = tempfile.mkstemp('1.wav')
					wavfile_obj = os.fdopen(wavfile[0], 'w')
					wavfile_obj.write('a')
					wavfile_obj.close()
					name = wavfile[1]

					# 開始時のコールバック関数を実行
					if start:
						start()

					# 音声ファイル作成
					obj._speak_to_file( string, name, spell )

					# 音声ファイル再生
#					pygame.mixer.quit()
#					if obj.converter.freq:
#						pygame.mixer.init(frequency=obj.converter.freq)
					channel = pygame.mixer.Sound( name ).play()
					speaker.channel = channel

					# 再生完了まで待つ
					while channel.get_busy():
						pass

					# 音声ファイルの削除
					os.remove( name )

					# 終了時のコールバック関数を実行
					if finish:
						finish()

		# 文字列がなければ、処理をせずに戻る
		string = string.strip()
		if string=='':
			return

		# スレッド変数初期化
		th = None
		speaker = None

		# キューにためて発声
		if timing == 0:
#			print "キューに登録：",self.string_queue,string

			while self.queue_lock:
				time.sleep(0.01)
#			self.queue_lock = True

			# キューに登録
			speaker = Speaker()
			self.string_queue.put( ( self, string, spell, True, start, finish, speaker ) )

			# キュー用スレッドが作成されていないとき
			if self.queue_thread == None:
#				print "スレッド作成:", string
				sp = _speak_thread()
				speaker = Speaker()
				th = Thread( name=None, target=sp, args=( self, string, spell, True, start, finish, speaker ) )
				th.start()
				self.threads.append(th)
				self.queue_thread = th
#			self.queue_lock = False

		# 即発声
		else:
			# 全音を止めて発声
			if timing == 1:
				pygame.mixer.stop()
				self.threads = []

			# 全音に重ねて発声
			else:
				# 完了したスレッドを配列から除去
				temp = []
				for t in self.threads:
					if not t.isAlive():
						temp.append(t)
				for t in temp:
					self.threads.remove(t)

		# キュー再生ではない場合は、一度切りのスレッドを作成し実行する
		if timing != 0:

			# スレッドを作成し、開始
#			print "スレッド作成:", string
			sp = _speak_thread()
			speaker = Speaker()
			th = Thread( name=None, target=sp, args=( self, string, spell, False, start, finish, speaker ) )
			th.start()
			self.threads.append(th)

		# 同期指定ならば終了するまで待つ
		if sync == 1 and th != None:
			self.threads.remove(th)
			th.join()
			th = None
			speaker = None

		return speaker

	
# 非同期話者クラス
class Speaker:
	def __init__(self):
		self.th = None
		self.channel = None

	def stop(self):
		if self.channel:
			self.channel.stop()

	def pause(self):
		if self.channel:
			self.channel.pause()

	def resume(self):
		if self.channel:
			self.channel.unpause()

	def is_speaking(self):
		if self.channel:
			return self.channel.get_busy()
		else:
			return False

	def until_finishing(self):
		if self.channel:
			while self.channel.get_busy():
				pass
