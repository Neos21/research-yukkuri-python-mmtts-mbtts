# -*- coding: sjis -*-
#
# mmtts.py 0.91
#
# MBROLA JP2�f�[�^�x�[�X��p�̉����ϊ�
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

##### �ϐ���` #####

volume = 1.0				# �W������
rate   = 1.0		 		# �W���ǂݏグ���x
pitch  = 1.0				# �s�b�`


##### �ϐ���` #####

database = 'jp2'			# �f�[�^�x�[�X�t�@�C���̏ꏊ
text     = 'text.txt'		# �T���v���p�̃t�@�C����(SJIS)
message  = '����ɂ���'		# ���A������

if not os.path.isfile(database):
	database = os.path.dirname(__file__) + '\\' + database

# jp2�p�̉��f�ɕϊ�����N���X
class Phenomen:
	"""JP2�p�̉��f�t�@�C���𐶐����邽�߂̃N���X
	"""

	##### �R���X�g���N�^ #####
	def __init__(self):

		# ���[�U�[�����̓ǂݍ��݁A�����̗L����Ԃ�

		if not os.path.isfile(self.userdic):
			self.userdic = os.path.dirname(__file__) + '\\' + self.userdic

		self.dic = self.load_userdic()

		# MeCab�N���X������
		self.mecab = MeCab.Tagger( "--eos-format=\n -F%pS%f[8] -U%M" )


	##### �f�X�g���N�^ #####
	def __del__(self):
		pass

	##### �ϐ���` #####
	userdic = 'userdic.txt'		# �����̏ꏊ


	### JP2 ���f�f�[�^ ###

	# �ꉹ���\
	phoneDurVowel = {
	# �ꉹ
		'a'   :  500,
		'i'   :  500,
		'u'   :  500,
		'e'   :  500,
		'o'   :  500,
	# ���ꉹ
		'a:'  : 1000,
		'i:'  : 1000,	
		'u:'  : 1000,
		'e:'  : 1000,
		'o:'  : 1000,
	# �����ꉹ
		'i_0' :  500,
		'u_0' :  500,
	# �����L��
	    'Q'   :  500,
	# �����L��
		'X'   :  500,
	# �|�[�Y(�I�~)
		'_'   :  500,
		','   :  200,
		';'   :  500,
	}


	# �q�����\
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

	# �����Ή��\�i�㑱�̉��f�F�{���̝����L���j
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

	# ����/�����̂��Ƃɗ����Ƃ��ɒu�������鉹�̕\
	phoneHeadRemap = {
		'Z' : 'dZ',
		'z' : 'dz',
	}

	# �����������A���t�@�x�b�g�ɕϊ�����e�[�u��
	convert_table = {
		u'�A':'a',
		u'��':'a',
		u'�C':'i',
		u'��':'i',
		u'�E':'u',
		u'��':'u',
		u'�G':'e',
		u'��':'e',
		u'�I':'o',
		u'��':'o',
		u'�J':'k a',
		u'��':'k a',
		u'�L':'k i',
		u'��':'k i',
		u'�N':'k u',
		u'��':'k u',
		u'�P':'k e',
		u'��':'k e',
		u'�R':'k o',
		u'��':'k o',
		u'�T':'s a',
		u'��':'s a',
		u'�V':'S i',
		u'��':'S i',
		u'�X':'s u',
		u'��':'s u',
		u'�Z':'s e',
		u'��':'s e',
		u'�\':'s o',
		u'��':'s o',
		u'�^':'t a',
		u'��':'t a',
		u'�`':'tS i',
		u'��':'tS i',
		u'�c':'ts u',
		u'��':'ts u',
		u'�e':'t e',
		u'��':'t e',
		u'�g':'t o',
		u'��':'t o',
		u'�i':'n a',
		u'��':'n a',
		u'�j':'n1 i',
		u'��':'n1 i',
		u'�k':'n u',
		u'��':'n u',
		u'�l':'n e',
		u'��':'n e',
		u'�m':'n o',
		u'��':'n o',
		u'�n':'h a',
		u'��':'h a',
		u'�q':"C i",
		u'��':"C i",
		u'�t':"f u",
		u'��':"f u",
		u'�w':'h e',
		u'��':'h e',
		u'�z':'h o',
		u'��':'h o',
		u'�}':'m a',
		u'��':'m a',
		u'�~':'m i',
		u'��':'m i',
		u'��':'m u',
		u'��':'m u',
		u'��':'m e',
		u'��':'m e',
		u'��':'m o',
		u'��':'m o',
		u'��':'j a',
		u'��':'j a',
		u'��':'j u',
		u'��':'j u',
		u'��':'j o',
		u'��':'j o',
		u'��':'r a',
		u'��':'r a',
		u'��':'r i',
		u'��':'r i',
		u'��':'r u',
		u'��':'r u',
		u'��':'r e',
		u'��':'r e',
		u'��':'r o',
		u'��':'r o',
		u'��':'w a',
		u'��':'w a',
		u'��':'w a',
		u'��':'w a',
		u'��':'w i',
		u'��':'w i',
		u'��':'w e',
		u'��':'w e',
		u'��':'w o',
		u'��':'w o',
		u'�K':'g a',
		u'��':'g a',
		u'�M':'g i',
		u'��':'g i',
		u'�O':'g u',
		u'��':'g u',
		u'�Q':'g e',
		u'��':'g e',
		u'�S':'g o',
		u'��':'g o',
		u'�U':'z a',
		u'��':'z a',
		u'�W':'Z i',
		u'��':'Z i',
		u'�Y':'z u',
		u'��':'z u',
		u'�[':'z e',
		u'��':'z e',
		u'�]':'z o',
		u'��':'z o',
		u'�_':'d a',
		u'��':'d a',
		u'�a':'d i',
		u'��':'d i',
		u'�d':'Z u',
		u'��':'Z u',
		u'�f':'d e',
		u'��':'d e',
		u'�h':'d o',
		u'��':'d o',
		u'�o':'b a',
		u'��':'b a',
		u'�r':'b i',
		u'��':'b i',
		u'�u':'b u',
		u'��':'b u',
		u'�x':'b e',
		u'��':'b e',
		u'�{':'b o',
		u'��':'b o',
		u'�p':'p a',
		u'��':'p a',
		u'�s':'p i',
		u'��':'p i',
		u'�v':'p u',
		u'��':'p u',
		u'�y':'p e',
		u'��':'p e',
		u'�|':'p o',
		u'��':'p o',
		u'��':'v u',
	}

	# �����������A���t�@�x�b�g�ɕϊ�����e�[�u��
	convert_hanyoon_table = {
		u'�@':'a',
		u'��':'a',
		u'�B':'i',
		u'��':'i',
		u'�D':'u',
		u'��':'u',
		u'�F':'e',
		u'��':'e',
		u'�H':'o',
		u'��':'o',
	}

	# �����������A���t�@�x�b�g�ɕϊ�����e�[�u��
	convert_yoon_table = {
		u'��':'a',
		u'��':'a',
		u'��':'u',
		u'��':'u',
		u'��':'o',
		u'��':'o',
	}


	##### Phoneme_jp2���\�b�h��` #####

   	# �X���Ȃ�Εϊ�
   	def yoon(self,str,boin):
		"""�X���t���̕������ϊ����郁�\�b�h
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


	# ���X���Ȃ�Εϊ�
	def hanyoon(self,str,boin):
		"""���X���t���̕������ϊ����郁�\�b�h
		"""

		# ���J�� va,vi,ve,vo<-vu
		if  str == 'v u' and ( boin == 'a' or  boin == 'i' or  boin == 'e' or  boin == 'o' ):
			result = 'v ' + boin

		# �ӂ� fa,fi,fe,fo<-fu
		elif  str == 'f u' and ( boin == 'a' or  boin == 'i' or  boin == 'e' or  boin == 'o' ):
			result = 'f ' + boin

		# �Ă� ti<-te
		elif boin == 'i' and str == 't e':
			result = 't i'

		# �ł� di<-de
		elif boin == 'i' and str == 'd e':
			result = 'd i'

		# ���� Ze<-Zi
		elif boin == 'e' and str == 'Z i':
			result = 'Z e'

		# ���� tSe<-tSi
		elif boin == 'e' and str =='tS i':
			result = 'tS e'

		# ���X�����g���Ȃ���A��L�ȊO�Ȃ�Εꉹ�ƌ��Ȃ�
		else:
			if str <> '':
				result = str + ' ' + boin
			else:
				result = boin

	#	print "�ꉹ:",boin,"�ϊ��O:",str,"�ϊ���:",result
		return result


	# �����P�ʂŕϊ�
	# �m�肵���Ƃ������߂�l�ɒl������
	# �Ō�Ɏ��c��������̂ŁA���ϐ�mora�ɒ��ڃA�N�Z�X����
	def convert_symbol(self,s,prev):
		"""�����P�ʂŕϊ����Ă������\�b�h
		�㑱����X���Ȃǂ́A���Ƃ���z������
		"""

		# ���ߏI�[�L��
		if ( s == u'�B' ):
			return ( prev + ' ;' if prev else ';', '' )

		elif ( s == u'�H' ) or ( s == u'?' ):
			return ( prev + ' _' if prev else '_', '' )

		elif ( s == u'�I' ) or ( s == u'!' ):
			return ( prev + ' _' if prev else '_', '' )

		elif ( s == u'�A' ) or ( s == u'�C' ) or ( s == u',' ):
			return ( prev + ' ,' if prev else ',', '' )

		# �����L��(���ߏI�[)
		elif ( s == u'�[' ):
			return ( ( prev + ':') if prev else '' , '' ) 

		# ���X���L��
		elif self.convert_hanyoon_table.has_key(s):
			return ( '', self.hanyoon(prev,self.convert_hanyoon_table[s]) )

		# �X���L��
		elif self.convert_yoon_table.has_key(s):
			return ( '', self.yoon(prev,self.convert_yoon_table[s]) )

		# �����L��
		elif ( s == u'�b' ) or ( s == u'��' ):
			return ( ( prev + ' Q' ) if prev else 'Q', '' )

		# ���������B�u���J�v�̂Ƃ��̂݁B����ȊO�͕����N���A
		elif ( s == u'�J' ):
			return ( '', 'v u' if prev == 'u' else '' )

		# �����B���ߏI���B���̕�������ŉ����ς�邪�A����͂��ׂĂ��I����Ă���
		elif ( s == u'��' ) or ( s == u'��' ):
			return ( ( prev + ' X' ) if prev else 'X', '' )

		# �P����
		elif self.convert_table.has_key(s):
			return ( prev, self.convert_table[s] )

		# �s���ȕ���
		else:
			return (prev,'')

		return (prev,rest)


	# ��������������f�L���ɕϊ�����B
	def convert(self,s):
		"""�ϊ��{�̃��\�b�h
		"""

		# �ꂪ��Ȃ�Ή������Ȃ�
		if s == '':
			return []

		# ���������񂩂特�f�̔z������
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
		# �Ƃ肠�����A���f�z�񊮐� #

		# �֎~�A�����̒����ia:i:,i:u:,u:u:,o:u:,vu:�j
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

		# ���f�̒������v�Z�B�ꉹ�͐旧�q���̒����������Ē�������
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

		# �����y�ѝ����̒���̉��f�ϊ��@Z->dZ, z->dz
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

		# �����L����{���̉��f�ɕϊ�����
		last = '_'
		t = []
		for ph in reversed(phonemes):
			if ph == 'X' and self.phoneNMap.has_key(last):
				ph =  self.phoneNMap[last]
			t.append(ph)
			last = ph
		phonemes = t[::-1]

		# �p�����[�^�ƂƂ��ɏo�͂���
		t = []
		global rate
		scale = 0.4 / rate
		t.append( '_\t300' )
		while len(phonemes)!=0:

			# �s�b�`�̕␳
			global pitch
			if pitch < 0.2:
				pitch = 0.2
			if pitch > 8.0:
				pitch = 8.0

			ms = 50
			pt = 225
			

			a = phonemes.pop(0)
			if a == 'X': # �ϊ��ł��Ă��Ȃ������L������������폜
				le.pop(0)
				continue
			if len(le)!=0:
				b = le.pop(0)
			else:
				b = 100

			if a == ',':  # �R���}��␳
				a = '_'

			if a == 'Q':  # �����L����␳
				a = '_'

			if a == 'Q':  # �����L����␳
				a = '_'

			# ��_�̂Ƃ��̓R�����g��}���iPYD�ŗ��p�j
			if a == ';':
				t.append( '_' + '\t' + str(int(b*scale)) )
				t.append( ';kuten' )

			# �����̂Ƃ�
			elif a == '_':
				t.append( a + '\t' + str(int(b*scale)) )

			# �ʏ�̉��f
			else:
				t.append( a + '\t' + str(int(b*scale)) + '\t' + str(ms) + '\t' + str(pt*pitch) )

		t.append( '_\t300' )

		return t

	# ���l�p
	numRead = {
		u"0":u"�[��",
		u"1":u"��",
		u"2":u"��",
		u"3":u"�O",
		u"4":u"�l",
		u"5":u"��",
		u"6":u"�Z",
		u"7":u"��",
		u"8":u"��",
		u"9":u"��",
		u"�O":u"�[��",
		u"�P":u"��",
		u"�Q":u"��",
		u"�R":u"�O",
		u"�S":u"�l",
		u"�T":u"��",
		u"�U":u"�Z",
		u"�V":u"��",
		u"�W":u"��",
		u"�X":u"��",
	}


	# �����p
	numRead2 = {
		u"0":u"�[��",
		u"1":u"�C�`",
		u"2":u"�j�[",
		u"3":u"�T��",
		u"4":u"����",
		u"5":u"�S�[",
		u"6":u"���N",
		u"7":u"�i�i",
		u"8":u"�n�`",
		u"9":u"�L���E",
		u"�O":u"�[��",
		u"�P":u"�C�`",
		u"�Q":u"�j�[",
		u"�R":u"�T��",
		u"�S":u"����",
		u"�T":u"�S�[",
		u"�U":u"���N",
		u"�V":u"�i�i",
		u"�W":u"�n�`",
		u"�X":u"�L���E",
	}

	numClass1 = {
		u"1" : u"",
		u"2" : u"�\",
		u"3" : u"�S",
		u"4" : u"��",
	}

	numClass2 = {
		u"0" : u"",
		u"1" : u"��",
		u"2" : u"��",
		u"3" : u"��",
		u"4" : u"�P�[",
	}

	numYomiHosei = {
		u"�O�S":u"�T���r���N",
		u"�Z�S":u"���b�s���N",
		u"���S":u"�n�b�s���N",
		u"�O��":u"�T���[��",
		u"����":u"�n�b�Z��",
	}

	numzenhan = {
		u'�O':u'0',
		u'�P':u'1',
		u'�Q':u'2',
		u'�R':u'3',
		u'�S':u'4',
		u'�T':u'5',
		u'�U':u'6',
		u'�V':u'7',
		u'�W':u'8',
		u'�X':u'9',
	}

	# �����񒆂̐��l����{��ɕϊ�����
	def convert_numstring(self,str):
		"""���l����{��ɕϊ����郁�\�b�h
		"""

		number = re.compile( u'([0-9�O-�X]+,*[0-9,�O-�X]*)(\.[0-9�O-�X]*)?' )
		zeros  = re.compile( u'^[0�O]+$' )
		comma  = re.compile( ',' );

		# �������[�v�A���l�������Ȃ���Γr���Ń��^�[��
		for n in range(100):

			# ���l�����������
			val = number.search( str )
			if val == None:
				return str;

            # �S�p�����𔼊p�����ɕϊ�����
			def zennum2hannum(str):
				if str == None:
					return None

				for k,v in self.numzenhan.items():
					str = str.replace( k, v )
				return str

			# �����Ə���
			i = val.group(1)
			r = val.group(2)
			i = zennum2hannum(i)
			r = zennum2hannum(r)

			# �i�[�z�񏉊���
			s = []

			# �[����������Ȃ鐔�l�͂ǂ���[��
			if zeros.search( i ):
				i = '0'

			## �������̏���
			# ����؂�́u,�v������΍폜
			i = comma.sub( '', i )
			olen  = len(i)

			# �l����蒷����
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
						# �u1�v�ȊO�͕K���ǂށA��ԉ��̌��Ȃ�Ή��ł��ǂ�
						if par[0] != '1' or len(par) == 1:
							s.append( self.numRead[par[0]] )
						s.append( self.numClass1[`len(par)`] )
					par.pop(0)

				# ������0�ȊO�̐����������
				if flag == 1:
					num = int(len(i)/4)
					s.append( self.numClass2[`num`] )

			# �l�����Z���Ĉꌅ�łȂ����
			while len(i) > 1:
				if i[0] != '0':
					# �u1�v�ȊO�͕K���ǂށA��ԉ��̌��Ȃ�Ή��ł��ǂ�
					if i[0] != '1' or len(i) == 1:
						s.append( self.numRead[i[0]] )
					s.append( self.numClass1[`len(i)`] )
				i = i[1:]

			## ��̈ʂ̏���
			# ��̈ʂ��[���Ȃ��
			if i[0] == '0':
				# �ꌅ�Ȃ�΁A
				if olen == 1:
					# �������Ȃ���Ε��ʂɓǂ�
					if r == '':
						s.append( self.numRead[i[0]] )
						i = i[1::]
					 # ����������ꍇ�́u�ꂢ�v�Ɠǂ�
					else:
						s.append( u"���C" )
			# ��̈ʂ��[���ȊO�Ȃ�Ε��ʂɓǂ�
			else:
				s.append( self.numRead[i[0]] )
				i = i[1::]

			## �����̏���
			# �����_�ȉ�������Γǂ�
			if r <> None:
				s.append( u"�e��" )
				r = r[1::]		# �����_�L�����̂Ă�
				for n in r:
					s.append( self.numRead2[n] )

			# �z���A������
			s = u''.join(s)

			# ���l�ǂݕ␳
			for i in self.numYomiHosei:
				s = re.sub( i, self.numYomiHosei[i], s )

			# ������u��
			temp = ""
			if val.start(0) > 0:
				temp = str[0:val.start(0)]
			temp = temp + s
			if len(str)>val.end(0):
				temp = temp + str[val.end(0):]
			str = temp


	# �ȈՎ�����ǂݍ���
	def load_userdic(self):
		"""���[�U�[������ǂݍ��ރ��\�b�h
		"""
		# �����̃\�[�g�p��r�֐��i�������̂����ɒ��ׂ�悤�ɂ���j
		def length_comp(a,b):
			"""��r�֐�
			"""
			a = a.split(',')
			if a == []:
				return -1
			b = b.split(',')
			if b == []:
				return 1
			return len(b[0]) - len(a[0])

		# �������Ȃ���΂��̂܂܋A��
		if not os.path.exists( self.userdic ):
			return False

		f = open( self.userdic, 'r')
		self.userDic = []
		for line in f:
			self.userDic.append(unicode(line.strip(),'sjis'))
		self.userDic.sort( length_comp )
		f.close()
		return True


	# �ȈՎ������g���ăA���t�@�x�b�g�Ȃǂ��J�i�\�L�ɒu��������
	def convert_bydic(self,s):
		"""�����ϊ����\�b�h
		"""
		for line in self.userDic:
			word = line.split(',')
			if len( word ) == 2:
				s = re.compile( word[0] ).sub( word[1], s )
		return s


	# ���f�ϊ�����
	def txt2pho(self,s):
		"""sjis�������PHO�f�[�^�ɕϊ�����
		"""

		# ���j�R�[�h�ɕϊ�
		s = unicode(s,'sjis')

		# �ȈՎ������g���ăA���t�@�x�b�g�Ȃǂ��J�i�\�L�ɒu��������
		if self.dic:
			s = self.convert_bydic(s)

		# �����񒆂̐��l����{��ɕϊ�
		s = self.convert_numstring(s)

		# MeCab�Ŋ����������ɕϊ�
		s = s.encode('sjis')
		s = self.mecab.parse(s)
		s = unicode(s,'sjis')

		# ���f�L���ɕϊ�
		t = self.convert(s)

		return t

	# end class #


# �e�L�X�g����PHO�t�@�C�����쐬����
def makePHO(str,filename):
	"""�e�L�X�g����PHO�t�@�C�����쐬����B
	��������t�@�C������sjis�ŃG���R�[�h����Ă���Ƃ���B
	�t�@�C������'.pho'�����ɕt������Ă���Ƃ݂Ȃ�
	"""

	# �������ݗp��PHO�t�@�C�����J��
	phofile = open( filename, 'w')

	# ���͕����񂪂Ȃ���Η�O����
	if str == '':
		return
		#raise Exception( '�����񂪂���܂���' )

	# ���f�N���X����
	phenomen = Phenomen()
	ps = phenomen.txt2pho(str)
	if ps == []:
		return
		# raise Exception( '�ϊ���ɕ����񂪂���܂���' )

	# ���f���X�g���o��
	wave = "";
	for ph in ps:
		phofile.write(ph+'\n')

	# ���f�t�@�C�������
	phofile.close()


# �e�L�X�g�������t�@�C���ɕϊ�����
def makeWAV(str,filename):
	"""�e�L�X�g�������t�@�C���ɕϊ�����B
	��������t�@�C������sjis�ŃG���R�[�h����Ă���Ƃ���B
	�t�@�C������'.wav'�����ɕt������Ă���Ƃ݂Ȃ��B
	"""

	global volume

	# ���͕����񂩂�]�����폜
	str = str.strip()

	# PHO�p�̈ꎞ�t�@�C�����쐬
	file = tempfile.mkstemp('.pho')
	file_obj = os.fdopen(file[0], 'w')
	file_obj.close()
	phofile = file[1]

	# pho�t�@�C�����쐬����
	makePHO(str,phofile)

	# mbrola�ɂ��pho�t�@�C����wav�t�@�C���ɕϊ�����
	pho2wav.convert( database, phofile, filename, volume )

	# �ꎞ�t�@�C�����폜
	os.remove(phofile)


def speak(str):
	"""�e�L�X�g�𔭉�����
	�������sjis�ŃG���R�[�h����Ă���Ƃ���B
	"""

	# wav�p�̈ꎞ�t�@�C�����쐬
	file = tempfile.mkstemp('.wav')
	file_obj = os.fdopen(file[0], 'w')
	file_obj.close()
	wavfile = file[1]

	# �����񂩂�ꎞ�I��wav�t�@�C�����쐬 
	makeWAV( str, wavfile )

	# ����
	winsound.PlaySound( wavfile, winsound.SND_FILENAME)

	# �ꎞ�t�@�C�����폜
	os.remove(wavfile)


def set_volume(vol):
	"""���ʂ�ݒ肷��
	�͈͂�[0.2,8.0]
	"""

	global volume
	if vol < 0.2:
		vol = 0.2

	if vol > 8.0:
		vol = 8.0

	volume = vol


def set_rate(val):
	"""�ǂݏグ���x��ݒ肷��
	�͈͂�[0.2,8.0]
	"""

	global rate
	if val < 0.2:
		val = 0.2

	if val > 8.0:
		val = 8.0

	rate = val


def set_pitch(val):
	"""�ǂݏグ�s�b�`��ݒ肷��
	�͈͂�[0.2,8.0]
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

	# �G�N�X�v���[������N�������Ƃ��A�������Ȃ��Ƃ�
	if argc == 1:
		# �W���̃e�L�X�g�t�@�C�����p�ӂ���Ă���Γǂ�
		if os.path.exists(text):
			for line in open(text, 'r'):
				speak( line )
		elif message != '':
			makePHO(message,'message.pho')
			speak(message)

	# �������� '-' �̂Ƃ��͕W�����͂�ǂݏグ��B����ȍ~�̈����͖���
	elif argv[1] == '-':
		print sys.stdin
		for line in sys.stdin:
			speak(line)

	# �������� -f �̎��͑��������t�@�C�����Ƃ݂Ȃ��Ă����ǂݏグ��B����ȍ~�͖��� 
	elif argv[1] == '-f' and argc >= 3:
		file = argv[2]
		for line in open(file, 'r'):
			speak( line )

	# ����ȊO�̂Ƃ��́A�������e�L�X�g�Ƃ݂Ȃ��ēǂݏグ��
	else:
		for word in argv[1:]:
			speak(word)
