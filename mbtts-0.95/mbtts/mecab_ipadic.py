# -*- coding: utf8 -*-
# mecab_ipadic.py
# mbtts 0.95
# 2010/03/25
# copyright(c) takayan
# http://neu101.seesaa.net/

import platform
import os

import mbtts_var
import mecab_dic


# UniDic設定クラス
# コンストラクタで辞書の場所を設定する
class IpaDic(mecab_dic.MecabDic):

	# 辞書名
	name = u"ipadic"

	# コンストラクタ
	def __init__(self):
	
		# 辞書ディレクトリの初期化
		mecab_dic_dir = ''

		# 辞書ディレクトリが指定されているときはそこ
		if mbtts_var.MECAB_DIC_BASE:

			mecab_dic_dir = self.dic_dir_path(mbtts_var.MECAB_DIC_BASE,self.name)

		# 指定されていないときはありそうなところにする
		else:

			# プラットフォームで辞書の場所が違う
			ps = platform.system()

			# Windowsの場合の処理
			if ps == "Windows":

				# MeCabパッケージが標準の位置にインストールされているとする
				if os.path.isdir("C:\\Program Files\MeCab\\dic"):
					mecab_dic_dir = 'C:\\progra~1\\MeCab\\dic\\ipadic'

			# Linuxの場合の処理
			elif ps == "Linux":

				# Ubuntuの場合の処理
				pp = platform.platform()
				if pp.find("Ubuntu")!=-1:

					# debパッケージからのインストールされたの場合
					if os.path.isdir("/var/lib/mecab/dic/"):

						mecab_dic_dir = self.dic_dir_path('/var/lib/mecab/dic',self.name)

					# ソースからインストールした場合はそのパスを次に記述しておく
					else:
						mecab_dic_dir = ''

				# Ubuntu以外のディストリビューションは今のところ対応していない
				else:
					raise Exception(u"このLinuxディストリビューションへの対応は不明です。\n"
							+ u"スクリプトを修正してから利用してください。" )

			# Darwin
			elif ps == "Darwin":
				mecab_dic_dir = self.dic_dir_path('/usr/local/lib/mecab/dic',self.name)

			# Windows と Linux 以外のプラットフォームには今のところ対応していない
			else:
				raise Exception(u"このシステムには対応していません")

		# 基底クラスのコンストラクタ
		mecab_dic.MecabDic.__init__( self, self.name.lower(), mecab_dic_dir )


	# MeCabの結果nodeから音素作りに必要な情報を解析する
	def analyze( self, node ):

		# 文字コードをUnicodeに変換
		f = unicode( node.feature, mbtts_var.MECAB_CHARSET )

		# 項目に分割
		f = f.split(',')

		# 終端文字
		if f[0] == u'BOS/EOS':
			raise Exception( u'terminateor' )

		# 読み仮名を獲得
		if len(f)>8:
			s = f[8]

		# 読み仮名がなければ、漢字であろうが表層文字そのものにする
		else:
			s = unicode( node.surface, mbtts_var.MECAB_CHARSET )

		if f[0] == u'記号' and f[1] == u'句点':
			return ( s, f[1], None )
		else:
			return ( s, f[0], None )
