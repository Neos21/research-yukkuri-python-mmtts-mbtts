# -*- coding: utf8 -*-
# mecab_dic.py
# mbtts 0.97
# 2010/08/18
# copyright(c) takayan
# http://neu101.seesaa.net/


import os
import mecab_mbtts

import mbtts_var

# MeCab辞書を追加する場合はここで定義されているMecabDicクラスを継承し、
# 他の辞書クラスに倣ってこのコンストラクタを呼び出すコードを書く。
# そのとき、name 変数に辞書の名前を与える。
# そして、mbtts_var.py の DICS にその名前とクラスの対を追加する。


# MeCab辞書基底クラス
class MecabDic:

	# コンストラクタ
	def __init__(self,dic_name,mecab_dic_dir):

		# 辞書名の確認
		if not dic_name:
			raise Exception(u'辞書名が指定されていません。')

		# MeCab辞書の存在を確認する
		if not mecab_dic_dir:
			raise Exception(u'辞書 ' + dic_name + u' のパスが分かりません。\n'
					+ u'スクリプトを修正してから利用してください。')

		# MeCab辞書のディレクトリを確認する
		if not os.path.isdir(mecab_dic_dir):
			raise Exception(u'辞書 ' + dic_name + u' が見つかりません。')

		# MeCabクラス初期化
		self.mecab = mecab_mbtts.Tagger( (" -d " + mecab_dic_dir).encode(mbtts_var.SYSTEM_CHARSET) )

		# MeCab辞書名
		self.mecab_dic_name = dic_name



	# 辞書の場所を設定する
	def dic_dir_path( self, base, name ):

		# 辞書フォルダのパス
		mecab_dic_dir = os.path.join( base, name )

		# 文字セット
		charset = mbtts_var.MECAB_CHARSET.lower()

		# 文字セットの表記のゆれを吸収
		if charset == 'shift_jis' or charset == 'sjis':
			charset = 'sjis'

		elif charset == 'utf-8' or charset == 'utf8':
			charset = 'utf8'

		elif charset == 'euc-jp' or charset == 'euc_jp' or charset == 'eucjp'  or charset == 'eucj':
			charset = 'eucj'

		with_cs = mecab_dic_dir + '-' + charset
		if os.path.isdir(with_cs):
			mecab_dic_dir = with_cs

		return mecab_dic_dir
