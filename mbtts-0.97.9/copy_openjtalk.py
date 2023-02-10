#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import re
import sys
import platform
import shutil
import tarfile
import urllib
import ConfigParser

openjtalk_charset  = 'UTF-8'
config_dir         = '.mbtts'
config_name        = 'config.txt'
package_name       = 'mbtts'
openjtalk_win_name = 'open_jtalk.exe'
openjtalk_dir_name = 'open_jtalk'


if platform.system() == "Windows":
	dist = os.path.join( os.environ['HOMEDRIVE'] + os.environ['HOMEPATH'], config_dir )
else:
	dist = os.path.join(os.environ['HOME'], config_dir )

config_path = os.path.join( dist, config_name )

if os.path.exists( config_path ):
	parser = ConfigParser.RawConfigParser()
	parser.read( config_path )

	section = package_name
	if parser.has_section( section ):

		options = parser.items( section )

		if parser.has_option( section, 'openjtalk_dir_name' ):
			openjtalk_dir_name = parser.get( section, 'openjtalk_dir_name' )

		if parser.has_option( section, 'openjtalk_dic_name' ):
			openjtalk_dic_name = parser.get( section, 'openjtalk_dic_name' )

		if parser.has_option( section, 'openjtalk_name' ):
			openjtalk_win_name = parser.get( section, 'openjtalk_name' )

	# コピー先ディレクトリを作成する
	if not os.path.exists( dist ):
		os.mkdir(dist)
	dist = os.path.join( dist, openjtalk_dir_name)
	if not os.path.exists( dist ):
		os.mkdir(dist)

	for f in os.listdir('.'):
		# 話者データをコピー
		if re.match('hts_voice_.*\.tar\.gz$',f):
			try:
				shutil.copyfile(f,os.path.join(dist,f))
				print u'話者 ' + f + u' をコピーしました。'
			except:
				print u'話者 ' + f + u' のコピーに失敗しました。'

		# openjtalkの辞書のパス
		if re.match('open_jtalk_dic_.*\.tar\.gz$',f):
			try:
				shutil.copyfile(f,os.path.join(dist,f))
				print u'辞書 ' + f + u' をコピーしました。'
			except:
				print u'辞書 ' + f + u' のコピーに失敗しました。'


# Windows だけ open_jtalk.exe をコピー
if platform.system() == "Windows":
	try:
		shutil.copyfile(openjtalk_win_name,os.path.join( dist, openjtalk_win_name))
		print openjtalk_win_name + u' をコピーしました。'
	except:
		print openjtalk_win_name + u' のコピーに失敗しました。'

