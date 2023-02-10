# -*- coding: utf8 -*-
# mecab_unidic.py
# mbtts 0.95
# 2010/03/25
# copyright(c) takayan
# http://neu101.seesaa.net/

import mecab_dic
import platform
import os

import mbtts_var


# UniDic設定クラス
# コンストラクタで辞書の場所を設定する
class UniDic(mecab_dic.MecabDic):

	# 辞書名
	name = u"unidic"

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
					mecab_dic_dir = 'C:\\progra~1\\MeCab\\dic\\unidic'

				# Unidicパッケージが標準の位置にインストールされているときは、よりそちらを優先する
				if os.path.isdir("C:\\Program Files\unidic\\dic"):
					mecab_dic_dir = 'C:\\progra~1\\unidic\\dic\\unidic-mecab'
					mbtts_var.MECAB_CHARSET = 'utf8'

			# Linuxの場合の処理
			elif ps == "Linux":

				# Ubuntuの場合の処理
				pp = platform.platform()
				if pp.find("Ubuntu")!=-1:

					# debパッケージからのインストールされた（可能性がある）場合
					if os.path.isdir("/var/lib/mecab/dic/"):

						mecab_dic_dir = self.dic_dir_path('/var/lib/mecab/dic',self.name)

					# ソースからインストールした場合はそのパスを次に記述しておく
					else:
						mecab_dic_dir = ''

				# Ubuntu以外のディストリビューションは今のところ対応していない
				else:
					raise Exception(u"""このLinuxディストリビューションへの対応は不明です。
							スクリプトを修正してから利用してください。
							""" )

			# Darwin
			elif ps == "Darwin":
				mecab_dic_dir = self.dic_dir_path('/usr/local/lib/mecab/dic',self.name)

			# Windows と Linux 以外のプラットフォームには今のところ対応していない
			else:
				raise Exception(u"このシステムには対応していません")

		# 基底クラスのコンストラクタ
		mecab_dic.MecabDic.__init__( self, self.name, mecab_dic_dir )


	# feature リストを作成
	def split_feature(self,f):

		if not f:
			return []

		# 文字コードをUnicodeに変換
		f = unicode( f, mbtts_var.MECAB_CHARSET )

		item = f.split(u',')

		# 文字列としての','の解釈を補正
		temp = ''
		res = []
		for i in item:
			if i and i[0] == u'"':
				temp = i[1:]
				i  = ''
			elif temp and i and i[-1] == u'"':
				temp = temp + u',' + i[:-1]
				i = temp
				temp = ''
			elif temp:
				temp = temp + u',' + i
				i  = ''
			if i:
				res.append(i)
		return res


	# MeCabの結果nodeから音素作りに必要な情報を解析する
	def analyze( self, node ):

		# 項目に分割
		f = self.split_feature(node.feature)

		# 読み仮名を獲得
		if len(f)>9 and f[9]:
			s = f[9]
		# 読み仮名がなければ、漢字であろうが表層文字そのものにする
		else:
			s = unicode( node.surface, mbtts_var.MECAB_CHARSET )


		# 終端文字
		if f[0] == u'BOS/EOS':
			raise Exception( u'terminateor' )

		# アクセント情報
		if len(f) > 22 and mbtts_var.ACCENT_FLAG:
			a = f[22]
			a = a.split(u',')[0]		# 第一候補のみ使う
			if a == u'*':
				a = ''
		else:
			a = ''

		# 解析結果
		if f[0] == u'補助記号' and f[1] == u'句点':
			return ( s, f[1], a )
		else:
			return ( s, f[0], a )
