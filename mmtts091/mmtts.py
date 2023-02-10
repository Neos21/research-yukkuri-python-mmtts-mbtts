# -*- coding: sjis -*-
#
# mmtts.py 0.91
#
# MBROLA JP2データベース専用の音声変換
#
# copyright(c) takayan
# http://neu101.seesaa.net/

import os
import re
import sys
import MeCab
import tempfile
import winsound
import pho2wav

##### 変数定義 #####

volume = 1.0				# 標準音量
rate   = 1.0		 		# 標準読み上げ速度
pitch  = 1.0				# ピッチ


##### 変数定義 #####

database = 'jp2'			# データベースファイルの場所
text     = 'text.txt'		# サンプル用のファイル名(SJIS)
message  = 'こんにちは'		# 挨拶文字列

if not os.path.isfile(database):
	database = os.path.dirname(__file__) + '\\' + database

# jp2用の音素に変換するクラス
class Phenomen:
	"""JP2用の音素ファイルを生成するためのクラス
	"""

	##### コンストラクタ #####
	def __init__(self):

		# ユーザー辞書の読み込み、辞書の有無を返す

		if not os.path.isfile(self.userdic):
			self.userdic = os.path.dirname(__file__) + '\\' + self.userdic

		self.dic = self.load_userdic()

		# MeCabクラス初期化
		self.mecab = MeCab.Tagger( "--eos-format=\n -F%pS%f[8] -U%M" )


	##### デストラクタ #####
	def __del__(self):
		pass

	##### 変数定義 #####
	userdic = 'userdic.txt'		# 辞書の場所


	### JP2 音素データ ###

	# 母音長表
	phoneDurVowel = {
	# 母音
		'a'   :  500,
		'i'   :  500,
		'u'   :  500,
		'e'   :  500,
		'o'   :  500,
	# 長母音
		'a:'  : 1000,
		'i:'  : 1000,	
		'u:'  : 1000,
		'e:'  : 1000,
		'o:'  : 1000,
	# 無声母音
		'i_0' :  500,
		'u_0' :  500,
	# 促音記号
	    'Q'   :  500,
	# 撥音記号
		'X'   :  500,
	# ポーズ(終止)
		'_'   :  500,
		','   :  200,
		';'   :  500,
	}


	# 子音長表
	phoneDurConsonant= {
		'k'  : 130,
		's'  : 100,
		't'  :  55,
		'm'  :  55,
		'n'  :  80,
		'n1' :  55,
		'h'  :  55,
		'f'  :  55,
		'C'  :  55,
		'j'  :  55,
		'r'  :  55,
		'w'  :  55,
		'S'  : 250,
		'tS' : 300,
		'ts' : 100,
		'g'  :  55,
		'dz' :  55,
		'z'  : 200,
		'Z'  : 200,
		'dZ' : 200,
		'd'  :  55,
		'b'  :  55,
		'p'  :  55,
		'f'  :  55,
		'ts' :  55,
	}

	# 撥音対応表（後続の音素：本来の撥音記号）
	phoneNMap = {
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
		',' : 'N:',
		'Q' : 'N:',
		'z' : 'N:',
		'Z' : 'N:',
	}

	# 文頭/撥音のあとに来たときに置き換える音の表
	phoneHeadRemap = {
		'Z' : 'dZ',
		'z' : 'dz',
	}

	# 仮名文字をアルファベットに変換するテーブル
	convert_table = {
		u'ア':'a',
		u'あ':'a',
		u'イ':'i',
		u'い':'i',
		u'ウ':'u',
		u'う':'u',
		u'エ':'e',
		u'え':'e',
		u'オ':'o',
		u'お':'o',
		u'カ':'k a',
		u'か':'k a',
		u'キ':'k i',
		u'き':'k i',
		u'ク':'k u',
		u'く':'k u',
		u'ケ':'k e',
		u'け':'k e',
		u'コ':'k o',
		u'こ':'k o',
		u'サ':'s a',
		u'さ':'s a',
		u'シ':'S i',
		u'し':'S i',
		u'ス':'s u',
		u'す':'s u',
		u'セ':'s e',
		u'せ':'s e',
		u'ソ':'s o',
		u'そ':'s o',
		u'タ':'t a',
		u'た':'t a',
		u'チ':'tS i',
		u'ち':'tS i',
		u'ツ':'ts u',
		u'つ':'ts u',
		u'テ':'t e',
		u'て':'t e',
		u'ト':'t o',
		u'と':'t o',
		u'ナ':'n a',
		u'な':'n a',
		u'ニ':'n1 i',
		u'に':'n1 i',
		u'ヌ':'n u',
		u'ぬ':'n u',
		u'ネ':'n e',
		u'ね':'n e',
		u'ノ':'n o',
		u'の':'n o',
		u'ハ':'h a',
		u'は':'h a',
		u'ヒ':"C i",
		u'ひ':"C i",
		u'フ':"f u",
		u'ふ':"f u",
		u'ヘ':'h e',
		u'へ':'h e',
		u'ホ':'h o',
		u'ほ':'h o',
		u'マ':'m a',
		u'ま':'m a',
		u'ミ':'m i',
		u'み':'m i',
		u'ム':'m u',
		u'む':'m u',
		u'メ':'m e',
		u'め':'m e',
		u'モ':'m o',
		u'も':'m o',
		u'ヤ':'j a',
		u'や':'j a',
		u'ユ':'j u',
		u'ゆ':'j u',
		u'ヨ':'j o',
		u'よ':'j o',
		u'ラ':'r a',
		u'ら':'r a',
		u'リ':'r i',
		u'り':'r i',
		u'ル':'r u',
		u'る':'r u',
		u'レ':'r e',
		u'れ':'r e',
		u'ロ':'r o',
		u'ろ':'r o',
		u'ワ':'w a',
		u'わ':'w a',
		u'ヮ':'w a',
		u'ゎ':'w a',
		u'ヰ':'w i',
		u'ゐ':'w i',
		u'ヱ':'w e',
		u'ゑ':'w e',
		u'ヲ':'w o',
		u'を':'w o',
		u'ガ':'g a',
		u'が':'g a',
		u'ギ':'g i',
		u'ぎ':'g i',
		u'グ':'g u',
		u'ぐ':'g u',
		u'ゲ':'g e',
		u'げ':'g e',
		u'ゴ':'g o',
		u'ご':'g o',
		u'ザ':'z a',
		u'ざ':'z a',
		u'ジ':'Z i',
		u'じ':'Z i',
		u'ズ':'z u',
		u'ず':'z u',
		u'ゼ':'z e',
		u'ぜ':'z e',
		u'ゾ':'z o',
		u'ぞ':'z o',
		u'ダ':'d a',
		u'だ':'d a',
		u'ヂ':'d i',
		u'ぢ':'d i',
		u'ヅ':'Z u',
		u'づ':'Z u',
		u'デ':'d e',
		u'で':'d e',
		u'ド':'d o',
		u'ど':'d o',
		u'バ':'b a',
		u'ば':'b a',
		u'ビ':'b i',
		u'び':'b i',
		u'ブ':'b u',
		u'ぶ':'b u',
		u'ベ':'b e',
		u'べ':'b e',
		u'ボ':'b o',
		u'ぼ':'b o',
		u'パ':'p a',
		u'ぱ':'p a',
		u'ピ':'p i',
		u'ぴ':'p i',
		u'プ':'p u',
		u'ぷ':'p u',
		u'ペ':'p e',
		u'ぺ':'p e',
		u'ポ':'p o',
		u'ぽ':'p o',
		u'ヴ':'v u',
	}

	# 仮名文字をアルファベットに変換するテーブル
	convert_hanyoon_table = {
		u'ァ':'a',
		u'ぁ':'a',
		u'ィ':'i',
		u'ぃ':'i',
		u'ゥ':'u',
		u'ぅ':'u',
		u'ェ':'e',
		u'ぇ':'e',
		u'ォ':'o',
		u'ぉ':'o',
	}

	# 仮名文字をアルファベットに変換するテーブル
	convert_yoon_table = {
		u'ャ':'a',
		u'ゃ':'a',
		u'ュ':'u',
		u'ゅ':'u',
		u'ョ':'o',
		u'ょ':'o',
	}


	##### Phoneme_jp2メソッド定義 #####

   	# 拗音ならば変換
   	def yoon(self,str,boin):
		"""拗音付きの文字列を変換するメソッド
		"""
		if str <>'' and ( boin == 'a' or boin == 'u' or  boin == 'o' ):
			if len(str)>=3 and str[-1] == 'i':
				if str == 'C i':
					result = "C " + boin
				elif str[-3] == 'Z':
					result = 'Z ' + boin
				elif str[-3] == 'S':
					result = str[0:-1] + boin
				elif str[-3] == 'n':
					result = str[0:-3] + ' n1 ' + boin
				elif len(str)>=4 and str[-4:-2] == 'n1':   # 'n1 i'
					result = str[0:-1] + boin
				else:
					result = str[0:-1] + 'j ' + boin
			else:
				result = 'j ' + boin

			return result
		return ''


	# 半拗音ならば変換
	def hanyoon(self,str,boin):
		"""半拗音付きの文字列を変換するメソッド
		"""

		# う゛ぁ va,vi,ve,vo<-vu
		if  str == 'v u' and ( boin == 'a' or  boin == 'i' or  boin == 'e' or  boin == 'o' ):
			result = 'v ' + boin

		# ふぁ fa,fi,fe,fo<-fu
		elif  str == 'f u' and ( boin == 'a' or  boin == 'i' or  boin == 'e' or  boin == 'o' ):
			result = 'f ' + boin

		# てぃ ti<-te
		elif boin == 'i' and str == 't e':
			result = 't i'

		# でぃ di<-de
		elif boin == 'i' and str == 'd e':
			result = 'd i'

		# じぇ Ze<-Zi
		elif boin == 'e' and str == 'Z i':
			result = 'Z e'

		# ちぇ tSe<-tSi
		elif boin == 'e' and str =='tS i':
			result = 'tS e'

		# 半拗音を使いながら、上記以外ならば母音と見なす
		else:
			if str <> '':
				result = str + ' ' + boin
			else:
				result = boin

	#	print "母音:",boin,"変換前:",str,"変換後:",result
		return result


	# 文字単位で変換
	# 確定したときだけ戻り値に値がある
	# 最後に取り残しがあるので、大域変数moraに直接アクセスする
	def convert_symbol(self,s,prev):
		"""文字単位で変換していくメソッド
		後続する拗音などは、あとから配慮する
		"""

		# 音節終端記号
		if ( s == u'。' ):
			return ( prev + ' ;' if prev else ';', '' )

		elif ( s == u'？' ) or ( s == u'?' ):
			return ( prev + ' _' if prev else '_', '' )

		elif ( s == u'！' ) or ( s == u'!' ):
			return ( prev + ' _' if prev else '_', '' )

		elif ( s == u'、' ) or ( s == u'，' ) or ( s == u',' ):
			return ( prev + ' ,' if prev else ',', '' )

		# 長音記号(音節終端)
		elif ( s == u'ー' ):
			return ( ( prev + ':') if prev else '' , '' ) 

		# 半拗音記号
		elif self.convert_hanyoon_table.has_key(s):
			return ( '', self.hanyoon(prev,self.convert_hanyoon_table[s]) )

		# 拗音記号
		elif self.convert_yoon_table.has_key(s):
			return ( '', self.yoon(prev,self.convert_yoon_table[s]) )

		# 促音記号
		elif ( s == u'ッ' ) or ( s == u'っ' ):
			return ( ( prev + ' Q' ) if prev else 'Q', '' )

		# 濁音文字。「う゛」のときのみ。それ以外は文字クリア
		elif ( s == u'゛' ):
			return ( '', 'v u' if prev == 'u' else '' )

		# 撥音。音節終了。次の文字次第で音が変わるが、それはすべてが終わってから
		elif ( s == u'ン' ) or ( s == u'ん' ):
			return ( ( prev + ' X' ) if prev else 'X', '' )

		# 単文字
		elif self.convert_table.has_key(s):
			return ( prev, self.convert_table[s] )

		# 不正な文字
		else:
			return (prev,'')

		return (prev,rest)


	# 仮名文字列を音素記号に変換する。
	def convert(self,s):
		"""変換本体メソッド
		"""

		# 語が空ならば何もしない
		if s == '':
			return []

		# 仮名文字列から音素の配列を作る
		rest = ''
		phonemes = []
		for ch in s:

			( phs, rest ) = self.convert_symbol(ch,rest)
			if phs <> '':
				phs = phs.split(" ")
				for ph in phs:
					phonemes.append(ph)

		if rest <> '':
			phs = rest.split(" ")
			for ph in phs:
				phonemes.append(ph)
			rest = ''
		if not phonemes:
			return []
		# とりあえず、音素配列完成 #

		# 禁止連続音の調整（a:i:,i:u:,u:u:,o:u:,vu:）
		last = ''
		i = 0
		while i < len(phonemes):
			ph = phonemes[i]
			if ph == 'i:' and last == 'a:':
				phonemes.insert( i, '_' )
				i += 1
			elif ph == 'u:' and ( last == 'i:' or last == 'u:' or last == 'o:' ):
				phonemes.insert( i, '_' )
				i += 1
			elif ph == 'u:' and last == 'v':
				phonemes.insert( i, 'u' )
				i += 1
			last = ph
			i += 1

		# 音素の長さを計算。母音は先立つ子音の長さを引いて調整する
		le = []
		length = 0
		for ph in phonemes:
			d = 50
			if ph <> '':
				if self.phoneDurConsonant.has_key(ph):
					d = self.phoneDurConsonant[ph]
					length = length + d
				if self.phoneDurVowel.has_key(ph):
					d = self.phoneDurVowel[ph] - length
					length = 0
			le.append(d)

		# 文頭及び撥音の直後の音素変換　Z->dZ, z->dz
		last = '_'
		t = []
		for ph in phonemes:
			if ph <> '' and self.phoneHeadRemap.has_key(ph) and ( last == ',' or last == '_' or last == 'Q' or last == 'X' ):
				t.append( self.phoneHeadRemap[ph] )
			else:
				t.append( ph )
			last = ph
		if not t:
			return []
		phonemes = t

		# 撥音記号を本来の音素に変換する
		last = '_'
		t = []
		for ph in reversed(phonemes):
			if ph == 'X' and self.phoneNMap.has_key(last):
				ph =  self.phoneNMap[last]
			t.append(ph)
			last = ph
		phonemes = t[::-1]

		# パラメータとともに出力する
		t = []
		global rate
		scale = 0.4 / rate
		t.append( '_\t300' )
		while len(phonemes)!=0:

			# ピッチの補正
			global pitch
			if pitch < 0.2:
				pitch = 0.2
			if pitch > 8.0:
				pitch = 8.0

			ms = 50
			pt = 225
			

			a = phonemes.pop(0)
			if a == 'X': # 変換できていない撥音記号があったら削除
				le.pop(0)
				continue
			if len(le)!=0:
				b = le.pop(0)
			else:
				b = 100

			if a == ',':  # コンマを補正
				a = '_'

			if a == 'Q':  # 促音記号を補正
				a = '_'

			if a == 'Q':  # 促音記号を補正
				a = '_'

			# 句点のときはコメントを挿入（PYDで利用）
			if a == ';':
				t.append( '_' + '\t' + str(int(b*scale)) )
				t.append( ';kuten' )

			# 無音のとき
			elif a == '_':
				t.append( a + '\t' + str(int(b*scale)) )

			# 通常の音素
			else:
				t.append( a + '\t' + str(int(b*scale)) + '\t' + str(ms) + '\t' + str(pt*pitch) )

		t.append( '_\t300' )

		return t

	# 数値用
	numRead = {
		u"0":u"ゼロ",
		u"1":u"一",
		u"2":u"二",
		u"3":u"三",
		u"4":u"四",
		u"5":u"五",
		u"6":u"六",
		u"7":u"七",
		u"8":u"八",
		u"9":u"九",
		u"０":u"ゼロ",
		u"１":u"一",
		u"２":u"二",
		u"３":u"三",
		u"４":u"四",
		u"５":u"五",
		u"６":u"六",
		u"７":u"七",
		u"８":u"八",
		u"９":u"九",
	}


	# 数字用
	numRead2 = {
		u"0":u"ゼロ",
		u"1":u"イチ",
		u"2":u"ニー",
		u"3":u"サン",
		u"4":u"ヨン",
		u"5":u"ゴー",
		u"6":u"ロク",
		u"7":u"ナナ",
		u"8":u"ハチ",
		u"9":u"キュウ",
		u"０":u"ゼロ",
		u"１":u"イチ",
		u"２":u"ニー",
		u"３":u"サン",
		u"４":u"ヨン",
		u"５":u"ゴー",
		u"６":u"ロク",
		u"７":u"ナナ",
		u"８":u"ハチ",
		u"９":u"キュウ",
	}

	numClass1 = {
		u"1" : u"",
		u"2" : u"十",
		u"3" : u"百",
		u"4" : u"千",
	}

	numClass2 = {
		u"0" : u"",
		u"1" : u"万",
		u"2" : u"億",
		u"3" : u"兆",
		u"4" : u"ケー",
	}

	numYomiHosei = {
		u"三百":u"サンビャク",
		u"六百":u"ロッピャク",
		u"八百":u"ハッピャク",
		u"三千":u"サンゼン",
		u"八千":u"ハッセン",
	}

	numzenhan = {
		u'０':u'0',
		u'１':u'1',
		u'２':u'2',
		u'３':u'3',
		u'４':u'4',
		u'５':u'5',
		u'６':u'6',
		u'７':u'7',
		u'８':u'8',
		u'９':u'9',
	}

	# 文字列中の数値を日本語に変換する
	def convert_numstring(self,str):
		"""数値を日本語に変換するメソッド
		"""

		number = re.compile( u'([0-9０-９]+,*[0-9,０-９]*)(\.[0-9０-９]*)?' )
		zeros  = re.compile( u'^[0０]+$' )
		comma  = re.compile( ',' );

		# 無限ループ、数値部分がなければ途中でリターン
		for n in range(100):

			# 数値文字列を検索
			val = number.search( str )
			if val == None:
				return str;

            # 全角数字を半角数字に変換する
			def zennum2hannum(str):
				if str == None:
					return None

				for k,v in self.numzenhan.items():
					str = str.replace( k, v )
				return str

			# 整数と小数
			i = val.group(1)
			r = val.group(2)
			i = zennum2hannum(i)
			r = zennum2hannum(r)

			# 格納配列初期化
			s = []

			# ゼロだけからなる数値はどれもゼロ
			if zeros.search( i ):
				i = '0'

			## 整数部の処理
			# 桁区切りの「,」があれば削除
			i = comma.sub( '', i )
			olen  = len(i)

			# 四桁より長い間
			while len(i) > 4:

				par = []
				par.append( i[0] )
				i = i[1::]
				while len(i)%4 != 0:
					par.append( i[0] )
					i = i[1:]

				flag = 0
				while par<>[]:
					if par[0] != '0':
						flag = 1
						# 「1」以外は必ず読む、一番下の桁ならば何でも読む
						if par[0] != '1' or len(par) == 1:
							s.append( self.numRead[par[0]] )
						s.append( self.numClass1[`len(par)`] )
					par.pop(0)

				# そこに0以外の数字があれば
				if flag == 1:
					num = int(len(i)/4)
					s.append( self.numClass2[`num`] )

			# 四桁より短くて一桁でなければ
			while len(i) > 1:
				if i[0] != '0':
					# 「1」以外は必ず読む、一番下の桁ならば何でも読む
					if i[0] != '1' or len(i) == 1:
						s.append( self.numRead[i[0]] )
					s.append( self.numClass1[`len(i)`] )
				i = i[1:]

			## 一の位の処理
			# 一の位がゼロならば
			if i[0] == '0':
				# 一桁ならば、
				if olen == 1:
					# 小数がなければ普通に読む
					if r == '':
						s.append( self.numRead[i[0]] )
						i = i[1::]
					 # 小数がある場合は「れい」と読む
					else:
						s.append( u"レイ" )
			# 一の位がゼロ以外ならば普通に読む
			else:
				s.append( self.numRead[i[0]] )
				i = i[1::]

			## 小数の処理
			# 小数点以下があれば読む
			if r <> None:
				s.append( u"テン" )
				r = r[1::]		# 小数点記号を捨てて
				for n in r:
					s.append( self.numRead2[n] )

			# 配列を連結する
			s = u''.join(s)

			# 数値読み補正
			for i in self.numYomiHosei:
				s = re.sub( i, self.numYomiHosei[i], s )

			# 文字列置換
			temp = ""
			if val.start(0) > 0:
				temp = str[0:val.start(0)]
			temp = temp + s
			if len(str)>val.end(0):
				temp = temp + str[val.end(0):]
			str = temp


	# 簡易辞書を読み込む
	def load_userdic(self):
		"""ユーザー辞書を読み込むメソッド
		"""
		# 辞書のソート用比較関数（長いものから先に調べるようにする）
		def length_comp(a,b):
			"""比較関数
			"""
			a = a.split(',')
			if a == []:
				return -1
			b = b.split(',')
			if b == []:
				return 1
			return len(b[0]) - len(a[0])

		# 辞書がなければそのまま帰る
		if not os.path.exists( self.userdic ):
			return False

		f = open( self.userdic, 'r')
		self.userDic = []
		for line in f:
			self.userDic.append(unicode(line.strip(),'sjis'))
		self.userDic.sort( length_comp )
		f.close()
		return True


	# 簡易辞書を使ってアルファベットなどをカナ表記に置き換える
	def convert_bydic(self,s):
		"""辞書変換メソッド
		"""
		for line in self.userDic:
			word = line.split(',')
			if len( word ) == 2:
				s = re.compile( word[0] ).sub( word[1], s )
		return s


	# 音素変換処理
	def txt2pho(self,s):
		"""sjis文字列をPHOデータに変換する
		"""

		# ユニコードに変換
		s = unicode(s,'sjis')

		# 簡易辞書を使ってアルファベットなどをカナ表記に置き換える
		if self.dic:
			s = self.convert_bydic(s)

		# 文字列中の数値を日本語に変換
		s = self.convert_numstring(s)

		# MeCabで漢字を仮名に変換
		s = s.encode('sjis')
		s = self.mecab.parse(s)
		s = unicode(s,'sjis')

		# 音素記号に変換
		t = self.convert(s)

		return t

	# end class #


# テキストからPHOファイルを作成する
def makePHO(str,filename):
	"""テキストからPHOファイルを作成する。
	文字列もファイル名もsjisでエンコードされているとする。
	ファイル名は'.pho'が既に付加されているとみなす
	"""

	# 書き込み用にPHOファイルを開く
	phofile = open( filename, 'w')

	# 入力文字列がなければ例外発生
	if str == '':
		return
		#raise Exception( '文字列がありません' )

	# 音素クラス生成
	phenomen = Phenomen()
	ps = phenomen.txt2pho(str)
	if ps == []:
		return
		# raise Exception( '変換後に文字列がありません' )

	# 音素リストを出力
	wave = "";
	for ph in ps:
		phofile.write(ph+'\n')

	# 音素ファイルを閉じる
	phofile.close()


# テキストを音声ファイルに変換する
def makeWAV(str,filename):
	"""テキストを音声ファイルに変換する。
	文字列もファイル名もsjisでエンコードされているとする。
	ファイル名は'.wav'が既に付加されているとみなす。
	"""

	global volume

	# 入力文字列から余白を削除
	str = str.strip()

	# PHO用の一時ファイルを作成
	file = tempfile.mkstemp('.pho')
	file_obj = os.fdopen(file[0], 'w')
	file_obj.close()
	phofile = file[1]

	# phoファイルを作成する
	makePHO(str,phofile)

	# mbrolaによりphoファイルをwavファイルに変換する
	pho2wav.convert( database, phofile, filename, volume )

	# 一時ファイルを削除
	os.remove(phofile)


def speak(str):
	"""テキストを発音する
	文字列はsjisでエンコードされているとする。
	"""

	# wav用の一時ファイルを作成
	file = tempfile.mkstemp('.wav')
	file_obj = os.fdopen(file[0], 'w')
	file_obj.close()
	wavfile = file[1]

	# 文字列から一時的なwavファイルを作成 
	makeWAV( str, wavfile )

	# 発音
	winsound.PlaySound( wavfile, winsound.SND_FILENAME)

	# 一時ファイルを削除
	os.remove(wavfile)


def set_volume(vol):
	"""音量を設定する
	範囲は[0.2,8.0]
	"""

	global volume
	if vol < 0.2:
		vol = 0.2

	if vol > 8.0:
		vol = 8.0

	volume = vol


def set_rate(val):
	"""読み上げ速度を設定する
	範囲は[0.2,8.0]
	"""

	global rate
	if val < 0.2:
		val = 0.2

	if val > 8.0:
		val = 8.0

	rate = val


def set_pitch(val):
	"""読み上げピッチを設定する
	範囲は[0.2,8.0]
	"""
	global pitch
	if val < 0.2:
		val = 0.2

	if val > 8.0:
		val = 8.0

	pitch = val


if __name__ == '__main__':
	argv = sys.argv
	argc = len(argv)

	set_rate  ( 1.0 )
	set_volume( 1.0 )
	set_pitch ( 1.2 )

	# エクスプローラから起動したとき、引数がないとき
	if argc == 1:
		# 標準のテキストファイルが用意されていれば読む
		if os.path.exists(text):
			for line in open(text, 'r'):
				speak( line )
		elif message != '':
			makePHO(message,'message.pho')
			speak(message)

	# 第一引数が '-' のときは標準入力を読み上げる。それ以降の引数は無視
	elif argv[1] == '-':
		print sys.stdin
		for line in sys.stdin:
			speak(line)

	# 第一引数が -f の時は第二引数をファイル名とみなしてそれを読み上げる。それ以降は無視 
	elif argv[1] == '-f' and argc >= 3:
		file = argv[2]
		for line in open(file, 'r'):
			speak( line )

	# それ以外のときは、引数をテキストとみなして読み上げる
	else:
		for word in argv[1:]:
			speak(word)
