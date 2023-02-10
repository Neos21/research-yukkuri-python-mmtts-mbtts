#!/usr/bin/env python
# -*- coding: utf8 -*-
# mbtts.py
# mbtts 0.95
# 2010/03/25
# copyright(c) takayan
# http://neu101.seesaa.net/
"""コマンドラインからMBROLAを使って日本語文字列を音声に変換するスクリプトです。
スイッチもいくつか用意しています。
詳しくは --help でご確認ください。
"""

from optparse import OptionParser
import sys
import os

import mbtts


def main():
	"""コマンドライン処理をする関数です。
	"""


	### オプションの設定 ###

	dics = u'無し'
	if mbtts.mbtts_var.DICS:
		dics = u",".join(mbtts.mbtts_var.DICS.keys())

	databases = u'無し'
	if mbtts.mbtts_var.DATABASES:
		databases = u",".join(mbtts.mbtts_var.DATABASES.keys())

	usage = (u"\t%prog [options] 文字列１ 文字列２...\n\n"
	+ u"\t日本語文字列を音声に変換します。"
	+ u"\n\n\t使用可能な音素データベース：" + databases
	+ u"\n\t使用可能なMeCab辞書：" + dics
	)

	parser = OptionParser(usage=usage)
	parser.add_option( "-b", "--database",         dest="database",
		help=u"使用するデータベースを指定します。省略時：" + mbtts.mbtts_var.DATABASE_NAME )

	if mbtts.mbtts_var.DICS:
		temp = u"（" + u",".join(mbtts.mbtts_var.DICS.keys()) + u"）"
	parser.add_option( "-d", "--dic-name",     dest="dic_name",
		help=u"使用する辞書を指定します" + temp + u"省略時：" + mbtts.mbtts_var.DIC_NAME )

	parser.add_option( "-i", "--use-stdin",    action="store_true",   dest="enable_stdin",
		help=u"標準入力を読み上げます。" )

	parser.add_option( "-f", "--input-file",         dest="filename",
		help=u"読み上げるテキストファイルを指定します。" )

	parser.add_option( "-t", "--text-charset",  dest="text_charset",
		help=u"テキストファイルの文字コードを指定します。省略時：" + mbtts.mbtts_var.TEXT_CHARSET )

	parser.add_option( "-o", "--output-phofile",         dest="output_phofile",
		help=u"出力する音素リストファイルを指定します。" )

	parser.add_option( "-u", "--output-to-stdout",    action="store_true",   dest="stdout_mode",
		help=u"標準出力に音素リストファイルを指定します。" )

	parser.add_option( "-w", "--output-wavfile",      dest="output_wavfile",
		help=u"音声をファイルにのみ出力します。" )

	parser.add_option( "-r", "--rate-ratio",         dest="rate",
		help=u"読み上げ速度の比率を指定します（0.2～8.0）" )
	parser.add_option( "-v", "--volume-ratio",       dest="volume",
		help=u"読み上げ音量の比率を指定します（0.0～1.0）" )
	parser.add_option( "-p", "--pitch-ratio",        dest="pitch",
		help=u"読み上げピッチの比率を指定します（0.2～8.0）" )

	default_string =u"（標準設定）"
	str1 = ""
	str2 = default_string
	if mbtts.mbtts_var.ACCENT_FLAG:
		str1,str2 = str2,str1
	parser.add_option( "--accent-on",          action="store_true",   dest="accent_mode",
		help=u"アクセント読み上げをオンにします" + str1 )
	parser.add_option( "-a", "--accent-off",   action="store_false",  dest="accent_mode",
		help=u"アクセント読み上げをオフにします" + str2 )

	str1 = ""
	str2 = default_string
	if mbtts.mbtts_var.READING_SYMBOL_FLAG:
		str1,str2 = str2,str1
	parser.add_option( "-s", "--symbol-on",    action="store_true",   dest="symbol_mode",
		help=u"記号読み上げをオンにします" + str1 )
	parser.add_option( "--symbol-off",         action="store_false",  dest="symbol_mode",
		help=u"記号読み上げをオフにします" + str2 )

	parser.add_option( "--debug", action="store_true", dest="debug",
		help=u"処理内容を画面とファイルに出力します" )

	(options, args) = parser.parse_args()

	### インスタンス生成

	# まずインスタンス生成前に必要なパラメータを解釈する

	# ログを残す
	if options.debug:
		mbtts.mbtts_var.DEBUG = 1		# 定数書換

	# データベース
	database_name = mbtts.mbtts_var.DATABASE_NAME
	if options.database:
		database_name = options.database

	# MeCab辞書
	dic_name = mbtts.mbtts_var.DIC_NAME
	if options.dic_name:
		dic_name = unicode( options.dic_name, mbtts.mbtts_var.SYSTEM_CHARSET )

	# TTSインスタンス生成
	try:
		tts = mbtts.create(database_name,dic_name)
	except Exception,message:
		sys.stderr.write( ( u"エラー：" + message[0]) .encode(mbtts.mbtts_var.SYSTEM_CHARSET) )
		sys.exit()

		
	### パラメータから値を決定

	# 入力テキストの文字コード設定
	if options.text_charset:
		mbtts.mbtts_var.TEXT_CHARSET = options.text_charset		# 定数書換
		tts.set_text_charset( options.text_charset )

	if options.rate:
		tts.set_rate( float(options.rate) )

	if options.volume:
		tts.set_volume( float(options.volume) )

	if options.pitch:
		tts.set_pitch( float(options.pitch) )

	accent_mode = mbtts.mbtts_var.ACCENT_FLAG
	if options.accent_mode != None:
		accent_mode = options.accent_mode
		tts.set_accent_mode( options.accent_mode )

	symbol_mode = mbtts.mbtts_var.READING_SYMBOL_FLAG
	if options.symbol_mode != None:
		symbol_mode = options.symbol_mode
		tts.set_reading_mode( symbol_mode )


	# 音声出力
	quiet = None

	# pho出力先が指定されていたら音素ファイルを出力する
	output_pho = False
	if options.stdout_mode != None and  options.output_phofile:
		sys.stderr.write( u"音素リストの出力先にファイルと標準出力を同時に指定できません。\n"
			.encode( mbtts.mbtts_var.SYSTEM_CHARSET ) )
		sys.exit()

	elif options.stdout_mode != None:
		if options.stdout_mode == True:
			output_pho = True
			quiet = True

	elif options.output_phofile:
		output_pho = True
		quiet = True


	# 音声ファイルの出力先が指定されているときの処理
	output_wav = False
	if options.output_wavfile:
		output_wav = True
		quiet = True


	### パラメータに応じた処理 ###

	# 音素リスト配列
	lines = []
	# 標準入力からの読み込みが指定されていたら
	if options.enable_stdin != None:

		if options.filename:
			sys.stderr.write( u"標準入力とファイルを同時に入力にすることはできません\n"
								.encode( mbtts.mbtts_var.SYSTEM_CHARSET ) )
			sys.exit()
		else:
			for l in sys.stdin:
				if not quiet:
					tts.speak(l)
				lines.append(l)

	# そうではなく、ファイルからの読み込み、もしくは文字列が指定されていたら
	elif options.filename or len(args) > 0:

		if options.filename and not os.path.exists(options.filename):
			sys.stderr.write( ( u"エラー：指定されたファイル " + options.filename + u" が見つかりません。\n")
				.encode( mbtts.mbtts_var.SYSTEM_CHARSET ) )
			sys.exit()

		# 文字列が指定されていたら
		if len(args) > 0:
			for l in args:
				l = unicode( l, mbtts.mbtts_var.SYSTEM_CHARSET )
				if not quiet:
					tts.speak(l)
				lines.append(l)

		# ファイルが指定されていたら
		if  options.filename:
			f = open( options.filename, 'r')
			for l in f:
				try:
					l = unicode( l, mbtts.mbtts_var.TEXT_CHARSET )
				except:
					sys.stderr.write( (u"エンコードエラーです。ファイル " + options.filename +u" の文字コードを確認してください。\n")
								.encode( mbtts.mbtts_var.SYSTEM_CHARSET ) )
					sys.exit()
				if not quiet:
					tts.speak(l)
				lines.append(l)
			f.close()

	# そうでもなく、標準指定のテキストファイルが存在していたら
	elif os.path.exists(mbtts.mbtts_var.DEFAULT_TEXT):
		f = open(mbtts.mbtts_var.DEFAULT_TEXT, 'r')
		for l in f:
			try:
				l = unicode( l, mbtts.mbtts_var.TEXT_CHARSET )
			except:
				sys.stderr.write( (u"エンコードエラーです。ファイル " + options.filename +u" の文字コードを確認してください。\n")
							.encode( mbtts.mbtts_var.SYSTEM_CHARSET ) )
				sys.exit()
			if not quiet:
				tts.speak(l)
			lines.append(l)
		f.close()

	# そうでもなく、挨拶の文字列が指定されていたら
	elif mbtts.mbtts_var.MESSAGE_TEXT != '':
		if not quiet:
			tts.speak(mbtts.mbtts_var.MESSAGE_TEXT)
		lines.append(mbtts.mbtts_var.MESSAGE_TEXT)


	# PHO 出力指定
	if output_pho:
		if options.output_phofile:
			tts.lines_to_pho( lines, options.output_phofile )
		else:
			tts.lines_to_pho( lines, sys.stdout )

	# WAV 出力指定
	if output_wav:
		tts.speak_lines_to_file( lines, options.output_wavfile )


if __name__ == '__main__':
	main()
