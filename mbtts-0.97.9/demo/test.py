#!/usr/bin/env python
# -*- coding: utf8 -*-
import mbtts
print u'利用可能音声リスト：'
list = mbtts.available_databases()
for i in list: print(i)
tts = mbtts.create('jp1')
tts.speak(u'検索した結果、以下の八件が該当します。どれかについてアブストラクトを表示しますか？',1,0)
tts = mbtts.create('jp2')
tts.speak(u'おはようございます。暗証番号をどうぞ。',1,0)
tts.speak(u'こんにちは、中島です。',1,0)
tts = mbtts.create('jp3')
tts.speak(u'あらゆる現実を、全て自分の方へねじ曲げたのだ。',1,0)
