# -*- coding: utf8 -*-
# mb_converter.py
# mbtts 0.95
# 2010/03/25
# copyright(c) takayan
# http://neu101.seesaa.net/


import mbtts_var
import mbtts_player

def create(database_name=mbtts_var.DATABASE_NAME,dic_name=mbtts_var.DIC_NAME):
	"""mbtts オブジェクトを返します。
	"""
	tts = mbtts_player.MBTTSplayer(database_name,dic_name)
	return tts

__all__ = ['mbtts_player','mbtts_var']
