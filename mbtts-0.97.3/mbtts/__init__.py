# -*- coding: utf8 -*-
# mb_converter.py
# mbtts 0.97
# 2010/08/18
# copyright(c) takayan
# http://neu101.seesaa.net/

import mbtts_var
import mbtts_player
import os
import re
import ctypes.util
import ctypes
from ctypes import *

def create(database_name=mbtts_var.DEFAULT_VOICE,dic_name=mbtts_var.DIC_NAME):
	"""mbtts オブジェクトを返します。
	"""
	tts = mbtts_player.MBTTSplayer(database_name,dic_name)
	return tts

def default_database():
	"""標準データベース名を返します。
	"""
	return mbtts_var.DEFAULT_VOICE

def available_databases():
	"""利用可能なデータベースを返します。
	"""

	_temp = []

	if mbtts_var.MBROLA_PATH:
		for _name in mbtts_var.DATABASES:
			if os.path.exists( os.path.join( mbtts_var.DATABASE_DIR, _name, _name ) ):
				_temp.append( u'MBROLA.' + _name )
		if len(mbtts_var.DATABASES):
			_temp.append( u'MBROLA(default)' )

	if mbtts_var.AQUESTALK2_PATH:
		for _name in mbtts_var.PHONTS:
			_temp.append( u'AquesTalk2.' + _name )
		_temp.append( u'AquesTalk2(default)' )

	return sorted(_temp)


__all__ = ['mbtts_player','mbtts_var']
