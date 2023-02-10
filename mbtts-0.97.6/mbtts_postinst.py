#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import sys
import platform

# 初期簡易辞書
data="""takayan,たかやん
[Ff]irefox,ファイヤーフォックス
[Rr]uby,ルビー
[Pp]ython,パイソン
[Dd]elphi,デルファイ
[Ll]inux,リナックス
[Ww]indowsVISTA,ウィンドウズヴィスタ
[Ww]indows7,ウィンドウズセブン
[Ww]indowsXP,ウィンドウズエックスピー
[Ww]indows,ウィンドウズ
[Jj]ava[Ss]cript,ジャバスクリプト
[Pp]erl,パール
VISTA,ヴィスタ
[Uu]buntu,ウブントゥ
[Cc]\\+\\+,シープラスプラス
[Yy]ahoo,ヤフー
i[Pp]od,アイポッド
[Tt]ouch,タッチ
MeCab,メカブ
mecab,メカブ
([^kmcn])m/s,\\1メートル毎秒
ドット[Cc]om,ドットコム
([A-Za-z])\\.([A-Za-z]),\\1ドット\\2
([A-Za-z])\\.([　 \\n]),\\1ピリオド\\2
四人,よにん
四年,よねん
四円,よえん
([^十百千万億一二三四五六七八九])一日([^中]),\\1ついたち\\2
([^十百千万億一二三四五六七八九])一日$,\\1ついたち
([^十百千万億一二三四五六七八九])一人,\\1ひとり
^一人,ひとり
一日中,いちにちじゅう
^一日([^中]),ついたち\\1
\\(日\\),日曜日　
\\(月\\),月曜日　
\\(火\\),火曜日　
\\(水\\),水曜日　
\\(木\\),木曜日　
\\(金\\),金曜日　
\\(土\\),土曜日　
（日）,日曜日　
（月）,月曜日　
（火）,火曜日　
（水）,水曜日　
（木）,木曜日　
（金）,金曜日　
（土）,土曜日　
"""

if sys.argv[1] == '-install':
	ps = platform.system()
	if ps == "Windows":
		path = os.path.join( os.environ['HOMEDRIVE'] + os.environ['HOMEPATH'], '.mbtts')
		if not os.path.exists( path ):
			os.mkdir(path)
		path = os.path.join( path, 'userdic.txt' )
		if not os.path.exists( path ):
			fp = open(path,'w')
			fp.write(data)
			fp.close()
