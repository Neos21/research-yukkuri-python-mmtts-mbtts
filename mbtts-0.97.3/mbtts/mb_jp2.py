# -*- coding: utf8 -*-
# mecab_jp2.py
# mbtts 0.97
# 2010/08/18
# copyright(c) takayan
# http://neu101.seesaa.net/

import os
import mbtts_var
import mb_converter

##### クラス #####

# jp2用の音素に変換するクラス
# PHOを生成するまでの処理を担当する

class JP2(mb_converter.Conv):
	"""JP2用の音素ファイルを生成するためのクラス
	"""

	name = u'jp2'

	##### コンストラクタ #####
	def __init__(self,database_name,dic_name):

		self.acc_diff       =  40		# アクセントのピッチ差
		self.ques_diff      =  40		# 疑問語尾のピッチ差
		self.finish_rest    = 100		# 終了後の休止時間
		self.default_pt     = 220		# 標準のピッチ
		self.default_po     =  50		# 標準のピッチ位置
		self.default_ms     = 150		# 標準の音素の母音発音時間
		self.default_scale  = 0.8		# 標準の音素の読み上げ速度補正(母音長150の調整値)

		# 基底クラスのコンストラクタを呼び出す
		mb_converter.Conv.__init__(self,"jp2",dic_name,"mbrola")


	##### デストラクタ #####
	def __del__(self):
		pass


	### JP2 音素データ ###

	# 母音長表
	phone_duration_vowel = {
	# 母音
		'a'   :  150,
		'i'   :  150,
		'u'   :  150,
		'e'   :  150,
		'o'   :  150,
	# 長母音
		'a:'  :  300,
		'i:'  :  300,
		'u:'  :  300,
		'e:'  :  300,
		'o:'  :  300,
	# 無声母音
		'i_0' :  150,
		'u_0' :  150,
	# 促音記号
	    'Q'   :  150,
	# 撥音記号
		'X'   :  150,
	# ポーズ(終止)
		'_'   :  150,
		','   :  100,
	}


	# 子音長表
	phone_duration_consonant= {
		'k'  :  50,
		's'  :  50,
		't'  :  50,
		'm'  :  50,
		'n'  :  50,
		'n1' :  50,
		'h'  :  50,
		'f'  :  50,
		'C'  :  50,
		'j'  :  50,
		'r'  :  50,
		'w'  :  50,
		'S'  :  50,
		'tS' :  50,
		'ts' :  50,
		'g'  :  50,
		'dz' :  50,
		'z'  :  50,
		'Z'  :  50,
		'dZ' :  50,
		'd'  :  50,
		'b'  :  50,
		'p'  :  50,
		'f'  :  50,
		'ts' :  50,
	}


	# 撥音対応表（後続の音素：本来の撥音記号）
	phone_N_map = {
		'a' : 'N:',
		'i' : 'N:',
		'u' : 'N:',
		'e' : 'N:',
		'o' : 'N:',
		'a:': 'N:',
		'i:': 'N:',
		'u:': 'N:',
		'e:': 'N:',
		'o:': 'N:',
		's' : 'N:',
		'h' : 'N:',
		'f' : 'N:',
		'S' : 'N:',
		'C' : 'N:',
		'w' : 'N:',
		'g' : 'G:',
		'k' : 'G:',
		't' : 'n:',
		'r' : 'n:',
		'dZ': 'n:',
		'dz': 'n:',
		'j' : 'N:',
		'ts': 'n:',
		'tS': 'n:',
		'd' : 'n:',
		'b' : 'm:',
		'p' : 'm:',
		'm' : 'm:',
		'n' : 'n:',
		'n1': 'n1:',
		'_' : 'N:',
		'!' : 'N:',
		'?' : 'N:',
		'.' : 'N:',
		',' : 'N:',
		'Q' : 'N:',
		'z' : 'N:',
		'Z' : 'N:',
	}


	# 文頭/撥音のあとに来たときに置き換える音の表
	phone_head_remap = {
		'Z' : 'dZ',
		'z' : 'dz',
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
		u'ニ':['n1','i'],
		u'に':['n1','i'],
		u'ヌ':['n','u'],
		u'ぬ':['n','u'],
		u'ネ':['n','e'],
		u'ね':['n','e'],
		u'ノ':['n','o'],
		u'の':['n','o'],
		u'ハ':['h','a'],
		u'は':['h','a'],
		u'ヒ':['C','i'],
		u'ひ':['C','i'],
		u'フ':['f','u'],
		u'ふ':['f','u'],
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
		u'ラ':['r','a'],
		u'ら':['r','a'],
		u'リ':['r','i'],
		u'り':['r','i'],
		u'ル':['r','u'],
		u'る':['r','u'],
		u'レ':['r','e'],
		u'れ':['r','e'],
		u'ロ':['r','o'],
		u'ろ':['r','o'],
		u'ワ':['w','a'],
		u'わ':['w','a'],
		u'ヮ':['w','a'],
		u'ゎ':['w','a'],
		u'ヰ':['w','i'],
		u'ゐ':['w','i'],
		u'ヱ':['w','e'],
		u'ゑ':['w','e'],
		u'ヲ':['w','o'],
		u'を':['w','o'],
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
		u'ジ':['Z','i'],
		u'じ':['Z','i'],
		u'ズ':['z','u'],
		u'ず':['z','u'],
		u'ゼ':['z','e'],
		u'ぜ':['z','e'],
		u'ゾ':['z','o'],
		u'ぞ':['z','o'],
		u'ダ':['d','a'],
		u'だ':['d','a'],
		u'ヂ':['d','i'],
		u'ぢ':['d','i'],
		u'ヅ':['Z','u'],
		u'づ':['Z','u'],
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


	##### Phoneme_jp2メソッド定義 #####

	# 拗音ならば変換
	def yoon(self,string,boin):
		"""拗音付きの文字列を変換するメソッド
		"""

		if string != [] and ( boin == 'a' or boin == 'u' or boin == 'o' ):
			if len(string)>=2 and string[-1] == 'i':
				c = string[-2]
				if c == 'C' or c == 'Z' or c == 'S' or c == 'tS' or c == 'n1' :
					string[-1] = boin
					return string
				elif c == 'n':
					string[-2] = 'n1'
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

			# う゛ぁ va,vi,ve,vo<-vu、ふぁ fa,fi,fe,fo<-fu
			if v == 'u' and ( boin == 'a' or  boin == 'i'
				or  boin == 'e' or  boin == 'o' ) and ( c == 'f' or c == 'v' ):
				string[-1] = boin
				return string

			# てぃ ti<-te、でぃ di<-de
			elif v == 'e' and boin == 'i' and ( c == 't' or c == 'd' ):
				string[-1] = boin
				return string

			# じぇ Ze<-Zi、ちぇ tSe<-tSi
			elif v == 'i' and boin == 'e' and ( c == 'Z' or c == 'tS' ):
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
			carryover.append('Q')
			return ( carryover, [] )

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

		# 長音記号を前の母音に結びつける
		prev = []
		temp = []
		for ph in phonemes:
			if ph[0] == ':':
				if prev:
					p = prev[0]
					if p == 'a' or p == 'i' or p == 'u' or p == 'e' or p == 'o':
						if prev[2] == 1 and ph[2] == 0:
							temp.append( [ p + ':',  prev[1], 2 ] )
						elif prev[2] == 0 and ph[2] == 1:
							temp.append( [ p + ':',  prev[1], 3 ] )
						elif prev[2] == 1 and ph[2] == 1:
							temp.append( [ p + ':',  prev[1], 1 ] )
						elif prev[2] == 0 and ph[2] == 0:
							temp.append( [ p + ':',  prev[1], 0 ] )
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


		# 文頭及び撥音の直後の歯茎破裂音記号を歯茎破擦音に変換　Z->dZ, z->dz
		last = '_'
		t = []
		for ph in phonemes:
			if ph[0] in self.phone_head_remap and ( last == ','
					or last == '_' or last == 'Q' or last == 'X' ):
				t.append( [self.phone_head_remap[ph[0]],ph[1],ph[2]] )
			else:
				t.append( ph )
			last = ph[0]
		if not t:
			return []
		phonemes = t

		if mbtts_var.DEBUG:
			self.log.writeln(u'歯茎破擦音処理後:')
			self.log.dump_phonemes( phonemes )

		# 撥音記号を本来の音素に変換する(逆順で処理)
		last = '_'
		t = []
		for ph in reversed(phonemes):
			p = ph[0]
			if p == 'X' and last in self.phone_N_map:
				p =  self.phone_N_map[last]
				t.append( [p,ph[1],ph[2]] )
			else:
				t.append(ph)
			last = p
		phonemes = t[::-1]

		if mbtts_var.DEBUG:
			self.log.writeln(u'撥音記号処理後:')
			self.log.dump_phonemes( phonemes )

		# 疑問文のときは、上がり調子にする
		if phonemes and len(phonemes)>2:
			if phonemes[-1][0] == '?':
				ph = phonemes[-2]
				phonemes[-2] = [ ph[0], ph[1]+self.default_ms, 4]

		if mbtts_var.DEBUG:
			self.log.writeln(u'疑問形処理後:')
			self.log.dump_phonemes( phonemes )

		# 未対応連続音の調整（a:i:,i:u:,u:u:,o:u:,vu:
		#					->（a:_i:,i:_u:,u:_u:,o:_u:,vuu:）
		last = ''
		i = 0
		temp = []
		for ph in phonemes:
			ch = ph[0]
			if ch == 'i:' and last == 'a:':
				temp.append( ['_',0,0] )
			elif ch == 'u:' and ( last == 'i:' or last == 'u:' or last == 'o:' ):
				temp.append( ['_',0,0] )
			elif p == 'u:' and last == 'v':
				temp.append( ['u',self.default_ms,self.default_po,self.default_pt] )
			temp.append( ph )
			last = ch
		phonemes = temp

		if mbtts_var.DEBUG:
			self.log.writeln(u'未対応連続音の補正:')
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

			if data == 'X': # 変換できていない撥音記号があったら削除
				continue

			if ph[1]:
				tm = ph[1]
			else:
				tm = self.default_ms

			if data == ',':  # コンマを補正
				data = '_'

			elif data == 'Q':  # 促音記号を補正
				data = '_'

			# 句点のときはコメントを挿入（PYDで利用）
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

