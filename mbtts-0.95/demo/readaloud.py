#!/usr/bin/env python
# -*- coding: utf8 -*-
import mbtts
import time
import sys
import os
tts = mbtts.create('jp3')
tts.speak(u'こんにちは')
tts.until_finishing()
if not os.path.exists(u'text.txt'):
	tts.speak(u'''このスクリプトは同じフォルダに text.txt
	ファイルがあると、そのファイルを音読します。
	''')
	sys.exit()
tts.speak(u'それでは音読を始めます')
time.sleep(2)
tts.set_text_charset('utf8')
try:
	tts.speak_file(u'text.txt')
	tts.speak(u'おしまいです。')
except Exception, message:
	tts.speak(u'エラーが発生しました。')
	tts.speak(message[0])
