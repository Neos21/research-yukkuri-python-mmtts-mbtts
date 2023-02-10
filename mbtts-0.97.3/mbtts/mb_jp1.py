# -*- coding: utf8 -*-
# mecab_jp1.py
# mbtts 0.97
# 2010/08/18
# copyright(c) takayan
# http://neu101.seesaa.net/

import os
import mb_converter
import mbtts_var


##### クラス #####

# jp1用の音素に変換するクラス
# PHOを生成するまでの処理を担当する

class JP1(mb_converter.Conv):
	"""JP1/JP3用の音素ファイルを生成するためのクラス
	"""

	name = u'jp1'

	##### コンストラクタ #####
	def __init__(self,database_name,dic_name):

		self.acc_diff       =  20		# アクセントのピッチ差
		self.ques_diff      =  20		# 疑問語尾のピッチ差
		self.finish_rest    = 100		# 終了後の休止時間
		self.default_pt     = 160		# 標準のピッチ jp1
		self.default_po     =  50		# 標準のピッチ位置
		self.default_ms     = 150		# 標準の音素の母音発音時間
		self.default_scale  = 0.8		# 標準の音素の読み上げ速度補正(母音長150の調整値)

		# 基底クラスのコンストラクタを呼び出す
		mb_converter.Conv.__init__(self,"jp1",dic_name,"mbrola")


	##### デストラクタ #####
	def __del__(self):
		pass


	### JP3 音素データ ###

	# 母音長表
	phone_duration_vowel = {
	# 母音
		'a'   :  150,
		'i'   :  150,
		'u'   :  150,
		'e'   :  150,
		'o'   :  150,
	# 促音記号
	    'Q'   :  150,
	# 撥音記号
		'N'   :  150,
	# ポーズ(終止)
		'_'   :  150,
		','   :  100,
	}


	# 子音長表
	phone_duration_consonant= {
		'b'  :  50,
		't'  :  50,
		'd'  :  50,
		'k'  :  20,
		'g'  :  50,
#		'G'  :  50,
		's'  :  50,
		'S'  :  50,
		'm'  :  50,
		'n'  :  50,
		'w'  :  50,
		'j'  :  50,
		'rr' :  50,
		'tS' :  50,
		'dZ' :  50,
		'h'  :  50,
		'p'  :  50,
		'ts' :  50,
#		'f'  :  50,
		'v'  :  50,
		'N'  :  50,
		'z'  :  50,
	}


	# 仮名文字をアルファベットに変換するテーブル
	convert_table = {
		u'ア':['a'],
		u'あ':['a'],
		u'イ':['i'],
		u'い':['i'],
		u'ウ':['u'],
		u'う':['u'],
		u'エ':['e'],
		u'え':['e'],
		u'オ':['o'],
		u'お':['o'],
		u'カ':['k','a'],
		u'か':['k','a'],
		u'キ':['k','i'],
		u'き':['k','i'],
		u'ク':['k','u'],
		u'く':['k','u'],
		u'ケ':['k','e'],
		u'け':['k','e'],
		u'コ':['k','o'],
		u'こ':['k','o'],
		u'サ':['s','a'],
		u'さ':['s','a'],
		u'シ':['S','i'],
		u'し':['S','i'],
		u'ス':['s','u'],
		u'す':['s','u'],
		u'セ':['s','e'],
		u'せ':['s','e'],
		u'ソ':['s','o'],
		u'そ':['s','o'],
		u'タ':['t','a'],
		u'た':['t','a'],
		u'チ':['tS','i'],
		u'ち':['tS','i'],
		u'ツ':['ts','u'],
		u'つ':['ts','u'],
		u'テ':['t','e'],
		u'て':['t','e'],
		u'ト':['t','o'],
		u'と':['t','o'],
		u'ナ':['n','a'],
		u'な':['n','a'],
		u'ニ':['n','i'],#
		u'に':['n','i'],#
		u'ヌ':['n','u'],
		u'ぬ':['n','u'],
		u'ネ':['n','e'],
		u'ね':['n','e'],
		u'ノ':['n','o'],
		u'の':['n','o'],
		u'ハ':['h','a'],
		u'は':['h','a'],
		u'ヒ':['h','i'],#
		u'ひ':['h','i'],#
		u'フ':['h','u'],#
		u'ふ':['h','u'],#
		u'ヘ':['h','e'],
		u'へ':['h','e'],
		u'ホ':['h','o'],
		u'ほ':['h','o'],
		u'マ':['m','a'],
		u'ま':['m','a'],
		u'ミ':['m','i'],
		u'み':['m','i'],
		u'ム':['m','u'],
		u'む':['m','u'],
		u'メ':['m','e'],
		u'め':['m','e'],
		u'モ':['m','o'],
		u'も':['m','o'],
		u'ヤ':['j','a'],
		u'や':['j','a'],
		u'ユ':['j','u'],
		u'ゆ':['j','u'],
		u'ヨ':['j','o'],
		u'よ':['j','o'],
		u'ラ':['rr','a'],#
		u'ら':['rr','a'],#
		u'リ':['rr','i'],#
		u'り':['rr','i'],#
		u'ル':['rr','u'],#
		u'る':['rr','u'],#
		u'レ':['rr','e'],#
		u'れ':['rr','e'],#
		u'ロ':['rr','o'],#
		u'ろ':['rr','o'],#
		u'ワ':['w','a'],
		u'わ':['w','a'],
		u'ヮ':['w','a'],
		u'ゎ':['w','a'],
		u'ヰ':['w','i'],
		u'ゐ':['w','i'],
		u'ヱ':['w','e'],
		u'ゑ':['w','e'],
		u'ヲ':['o'],
		u'を':['o'],
		u'ガ':['g','a'],
		u'が':['g','a'],
		u'ギ':['g','i'],
		u'ぎ':['g','i'],
		u'グ':['g','u'],
		u'ぐ':['g','u'],
		u'ゲ':['g','e'],
		u'げ':['g','e'],
		u'ゴ':['g','o'],
		u'ご':['g','o'],
		u'ザ':['z','a'],
		u'ざ':['z','a'],
		u'ジ':['dZ','i'],#
		u'じ':['dZ','i'],#
		u'ズ':['z','u'],
		u'ず':['z','u'],
		u'ゼ':['z','e'],
		u'ぜ':['z','e'],
		u'ゾ':['z','o'],
		u'ぞ':['z','o'],
		u'ダ':['d','a'],
		u'だ':['d','a'],
		u'ヂ':['dZ','i'],#
		u'ぢ':['dZ','i'],#
		u'ヅ':['z','u'],#
		u'づ':['z','u'],#
		u'デ':['d','e'],
		u'で':['d','e'],
		u'ド':['d','o'],
		u'ど':['d','o'],
		u'バ':['b','a'],
		u'ば':['b','a'],
		u'ビ':['b','i'],
		u'び':['b','i'],
		u'ブ':['b','u'],
		u'ぶ':['b','u'],
		u'ベ':['b','e'],
		u'べ':['b','e'],
		u'ボ':['b','o'],
		u'ぼ':['b','o'],
		u'パ':['p','a'],
		u'ぱ':['p','a'],
		u'ピ':['p','i'],
		u'ぴ':['p','i'],
		u'プ':['p','u'],
		u'ぷ':['p','u'],
		u'ペ':['p','e'],
		u'ぺ':['p','e'],
		u'ポ':['p','o'],
		u'ぽ':['p','o'],
		u'ヴ':['v','u'],
	}


	##### Phoneme_jp1/jp3メソッド定義 #####

	# 拗音ならば変換
	def yoon(self,string,boin):
		"""拗音付きの文字列を変換するメソッド
		"""

		if string != [] and ( boin == 'a' or boin == 'u' or boin == 'o' ):
			if len(string)>=2 and string[-1] == 'i':
				c = string[-2]
				if c == 'tS' or c == 'dZ' or c == 'S':
					string[-1] = boin
					return string
				else:
					string[-1] = 'j'
					string.append(boin)
					return string
			else:
				return ['j',boin]

		return []


	# 半拗音ならば変換
	def hanyoon(self,string,boin):
		"""半拗音付きの文字列を変換するメソッド
		"""

		# 要素が二つ以上
		if len(string) >= 2:
			c = string[-2]
			v = string[-1]

			# う゛ぁ va,vi,ve,vo<-vux[aieo]
			if v == 'u' and ( boin == 'a' or  boin == 'i'
				or  boin == 'e' or  boin == 'o' ) and ( c == 'v' ):
				string[-1] = boin
				return string

			# てぃ ti<-texi、でぃ di<-dexi
			elif v == 'e' and boin == 'i' and ( c == 't' or c == 'd' ):
				string[-1] = boin
				return string

			# じぇ Ze<-Zixe、ちぇ tSe<-tSixe
			elif v == 'i' and boin == 'e' and ( c == 'dZ' or c == 'tS' ):
				string[-1] = boin
				return string

		# 半拗音を使いながら、上記以外ならば母音と見なす
		string.append(boin)
		return string


	# 文字単位で変換
	# return (確定音列specified,未確定音列unspecified)
	def convert_symbol(self,s,carryover):
		"""文字単位で変換していくメソッド
		"""

		## 確定 ##
		# 句点
		if ( s == u'。' ) or ( s == u'.' ):
			carryover.append('.')
			return ( carryover, [] )

		# 読点
		elif ( s == u'、' ) or ( s == u'，' ) or ( s == u',' ):
			carryover.append(',')
			return ( carryover, [] )

		# 疑問符
		elif ( s == u'？' ) or ( s == u'?' ):
			carryover.append('?')
			return ( carryover, [] )

		# 感嘆符
		elif ( s == u'！' ) or ( s == u'!' ):
			carryover.append('!')
			return ( carryover, [] )

		# 長音記号
		elif ( s == u'ー' ):
			if carryover:
				last = carryover[-1] # 繰越があるということは繰越に要素は一つはある
				if last == 'a' or last == 'i' or last == 'u' or last == 'e' or last == 'o':
					carryover.append(':')
			return ( carryover, [] )

		# 撥音（次の文字次第で音が変わるが、それはすべてが終わってから確定させる）
		elif ( s == u'ン' ) or ( s == u'ん' ):
			carryover.append('X')
			return ( carryover, [] )


		## 未確定 ##
		# 半拗音記号（長音が続くことがあるので未確定）
		elif s in self.convert_hanyoon_table:
			unspecified = self.hanyoon(carryover,self.convert_hanyoon_table[s])
			return ( [], unspecified )

		# 拗音記号（長音が続くことがあるので未確定）
		elif s in self.convert_yoon_table:
			unspecified = self.yoon(carryover,self.convert_yoon_table[s])
			return ( [], unspecified )

		# 濁音記号。「う゛」のときのみ。それ以外は文字クリア（長音が続くことがあるので未確定）
		elif ( s == u'゛' ):
			if carryover != [] and carryover[-1] == 'u':
				unspecified = ['v','u']
				return ( [], unspecified )
			else:
				return ( [], [] )

		## 確定＆未確定 ##
		# 促音記号
		elif ( s == u'ッ' ) or ( s == u'っ' ):
			return ( carryover, ['Q'] )

		# 単文字（新しい音節が始まるので、前のものが確定になる）
		elif s in self.convert_table:
			unspecified = self.convert_table[s][:]
			return ( carryover, unspecified )

		## 不正な文字 ##
		# 繰越分を確定し、不正な文字は捨てる
		else:
			return ( carryover, [] )

		return ( carryover, [] )


	# pho形式で音素を出力する
	def make_pho_lines( self, nodes ):

		# node( 音素リスト, 品詞, アクセント, ソース )

		# 時間の調整
		scale = 1 / self.rate / self.default_scale

		# アクセントを考慮した音素データリストを作成
		phonemes = self.accented_phonemes_list( nodes )

		# 長音記号を前の母音に結びつける(jp1/jp3はダブらせる)
		prev = []
		temp = []
		for ph in phonemes:
			if ph[0] == ':':
				if prev:
					p = prev[0]
					if p == 'a' or p == 'i' or p == 'u' or p == 'e' or p == 'o':
						temp.append( prev )
						temp.append( [ p,  ph[1],   ph[2] ] )
					else:
						temp.append( prev )
					prev = []
			else:
				if prev:
					temp.append( prev )
				prev = ph

		if prev:
			temp.append( prev )
		phonemes = temp

		if mbtts_var.DEBUG:
			self.log.writeln(u'長音処理後:')
			self.log.dump_phonemes( phonemes )


		# 音素の長さを計算。母音は先立つ子音の長さを引いて調整する
		temp = []
		length = 0
		for ph in phonemes:
			d = 100
			if ph:
				# 句点の処理
				if ph[0] == '?' or  ph[0] == '!' or  ph[0] == '.'  or  ph[0] == ',':
					length = 0

				# 子音の処理
				if ph[0] in self.phone_duration_consonant:
					d = self.phone_duration_consonant[ph[0]]
					length = length + d

				# 母音の処理
				if ph[0] in self.phone_duration_vowel:
					d = self.phone_duration_vowel[ph[0]] - length
					length = 0

			temp.append( [ph[0],d,ph[2]] )
		phonemes = temp

		if mbtts_var.DEBUG:
			self.log.writeln(u'音長処理後:')
			self.log.dump_phonemes( phonemes )


		# 疑問文のときは、上がり調子にする
		if phonemes and len(phonemes)>2:
			if phonemes[-1][0] == '?':
				ph = phonemes[-2]
				phonemes[-2] = [ ph[0], ph[1]+self.default_ms, 4]

		if mbtts_var.DEBUG:
			self.log.writeln(u'疑問形処理後:')
			self.log.dump_phonemes( phonemes )


		result = []
		result.append( '_\t' + str(int(100*scale)) )

		# 要素の数だけ繰り返す
		for ph in phonemes:
			po = self.default_po			# 標準ピッチ位置
			pt = self.default_pt			# 標準音素ピッチ

			# 標準値を計算しておく
			pitch_temp = str(int((pt)*self.pitch))

			data = ph[0]

			if ph[1]:
				tm = ph[1]
			else:
				tm = self.default_ms

			if data == ',':  # コンマ補正
				data = '_'

			if data == 'X':  # 発音補正
				data = 'N'

			if data == 'Q':  # 促音補正
				data = '_'

			# 句点
			if data == '.' or data == '!' or data == '?':
				result.append( '_' + '\t' + str(int(tm*scale))
							+ '\t' + str(int(po)) + '\t' + pitch_temp )

			# 通常の音素
			else:
				# ピッチ上昇の処理
				if  ph[2] == 0:
					pitch_temp = str(int((pt)*self.pitch))

				# アクセントのある音節の上昇
				elif ph[2] == 1:
					pitch_temp = str(int((pt+self.acc_diff)*self.pitch))

				# 長母音の前半部のみの上昇
				elif ph[2] == 2:
					pitch_temp = str(int((pt+self.acc_diff)*self.pitch))
					po = po * 0.5

				# 長母音の後半部のみの上昇
				elif ph[2] == 3:
					pitch_temp = str(int((pt+self.acc_diff)*self.pitch))
					po = po * 1.5

				# 疑問文の上昇
				elif ph[2] == 4:
					pitch_temp = str(int((pt+self.ques_diff)*self.pitch))

				else:
					pitch_temp = str(int((pt)*self.pitch))

				result.append( data + '\t' + str(int(tm*scale))
								+ '\t' + str(int(po)) + '\t' + pitch_temp )

		result.append( '_\t' + str(int(self.finish_rest*scale)) )

		if mbtts_var.DEBUG:
			if result:
				self.log.writeln(u'変換結果:')
				for i in result:
					self.log.writeln(i)
				self.log.writeln()


		return result


