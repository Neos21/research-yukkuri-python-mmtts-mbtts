# -*- coding: sjis -*-
#
# mmtts.py 0.92
#
# MBROLA JP2�f�[�^�x�[�X��p�̉����ϊ�
# 2010/03/05
# copyright(c) takayan
# http://neu101.seesaa.net/

import os
import re
import sys
import MeCab
import tempfile
import winsound
import pho2wav
from optparse import OptionParser


##### �ϐ� #####

# �f�o�b�O
DEBUG = 0

# �T���v���p�̃t�@�C����(SJIS)
text = 'text.txt'

# ���A������
message = '����ɂ���'

# �A�N�Z���g��L���ɂ��邩�̃t���O
accent_mode = 1

# �L����ǂނ��ǂ����̃t���O
reading_symbol_mode = 0

# �g�p���鎫���̖��O
dics = (
	u'ipadic',
	u'unidic',
)
default_dic = 1
dic_name = dics[default_dic]
#    ������ǉ�����Ƃ��́A�����ɖ��O��ǉ����A�R���X�g���N�^�Ƀf�B���N�g����I������if����ǉ����A
#    txt2pho���\�b�h���� �ǂ̌��ʂ��g�����̏������������ޕK�v������

# ���f�f�[�^�x�[�X�t�@�C���̏ꏊ
database = 'jp2'

# ���f�f�[�^�x�[�X���Ăяo���f�B���N�g���ɂȂ���΁A�X�N���v�g�̂���f�B���N�g����T��
if not os.path.isfile(database):
	database = os.path.dirname(__file__) + '\\' + database


##### �N���X #####

# jp2�p�̉��f�ɕϊ�����N���X
# PHO�𐶐�����܂ł̏�����S������
# �����I�ɂ́A���N���X��p�ӂ��đ��̉��f�f�[�^�x�[�X�����N���X�����

class Phenomen:
	"""JP2�p�̉��f�t�@�C���𐶐����邽�߂̃N���X
	"""

	##### �R���X�g���N�^ #####
	def __init__(self,dic_name):

		# ���O�t�@�C�����c��
		self.log = Log("log.txt")


		# �W�����ʔ䗦
		self.volume = 1.0

		# �W���ǂݏグ���x�䗦
		self.rate = 1.0

		# �W���s�b�`�䗦
		self.pitch = 1.0

		self.userdic = 'userdic.txt'	# �����̏ꏊ
		self.acc_diff       =  40		# �A�N�Z���g�̃s�b�`��
		self.ques_diff      =  40		# �^�����̃s�b�`��
		self.finish_rest    = 100		# �I����̋x�~����
		self.default_pt     = 220		# �W���̃s�b�`
		self.default_po     =  50		# �W���̃s�b�`�ʒu
		self.default_ms     = 150		# �W���̉��f�̕ꉹ��������
		self.default_scale  = 1.0		# �W���̉��f�̓ǂݏグ���x�␳(�ꉹ��150�̒l�𒲐����邽�߂̒l)

		self.flag_reading_symbol = 0	# �L����ǂނ��ǂ����̃t���O

		self.use_accent = 1				# �A�N�Z���g���������邩�̃t���O

		# MeCab�p�����̃p�X
		ipadidicdir = 'C:\\progra~1\\MeCab\\dic\\ipadic'
		unidicdir   = 'C:\\progra~1\\MeCab\\dic\\unidic'

		# �p�����[�^���������Ƃ��ēo�^����
		self.mecab_dic_name = dic_name.decode('sjis')

		# �����f�B���N�g���̐ݒ�
		if self.mecab_dic_name == 'ipadic':
			mecab_dic_dir = ipadidicdir
			self.use_accent = 0
		elif self.mecab_dic_name == 'unidic':
			mecab_dic_dir = unidicdir
			if not os.path.isdir(mecab_dic_dir):
				mecab_dic_dir = ipadidicdir
				self.mecab_dic_name = 'ipadic'
				self.use_accent = 0
		else:
			raise Exception( self.mecab_dic_name + '�͏�������Ă��Ȃ������ł��B')

		# MeCab�����̑��݂��m�F����
		if not os.path.isdir(mecab_dic_dir):
			raise Exception('�w���MeCab����' + self.mecab_dic_name + '��������܂���B')

		# MeCab�N���X�������A�����̎w��
		self.mecab = MeCab.Tagger( " -d " + mecab_dic_dir )

		# �ȈՎ���
		if not os.path.isfile(self.userdic):
			self.userdic = os.path.dirname(__file__) + '\\' + self.userdic
		self.dic_enable = self.load_userdic()


	##### �f�X�g���N�^ #####
	def __del__(self):
		pass


	### JP2 ���f�f�[�^ ###

	# �ꉹ���\
	phone_duration_vowel = {
	# �ꉹ
		'a'   :  150,
		'i'   :  150,
		'u'   :  150,
		'e'   :  150,
		'o'   :  150,
	# ���ꉹ
		'a:'  :  300,
		'i:'  :  300,
		'u:'  :  300,
		'e:'  :  300,
		'o:'  :  300,
	# �����ꉹ
		'i_0' :  150,
		'u_0' :  150,
	# �����L��
	    'Q'   :  150,
	# �����L��
		'X'   :  150,
	# �|�[�Y(�I�~)
		'_'   :  150,
		','   :  100,
	}


	# �q�����\
	phone_duration_consonant= {
		'k'  : 100,
		's'  : 100,
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
		'S'  : 100,
		'tS' : 100,
		'ts' : 100,
		'g'  :  50,
		'dz' :  50,
		'z'  : 100,
		'Z'  : 100,
		'dZ' : 100,
		'd'  :  50,
		'b'  :  50,
		'p'  :  50,
		'f'  :  50,
		'ts' :  50,
	}

	# �����Ή��\�i�㑱�̉��f�F�{���̝����L���j
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


	# ����/�����̂��Ƃɗ����Ƃ��ɒu�������鉹�̕\
	phone_head_remap = {
		'Z' : 'dZ',
		'z' : 'dz',
	}

	# �����������A���t�@�x�b�g�ɕϊ�����e�[�u��
	convert_table = {
		u'�A':['a'],
		u'��':['a'],
		u'�C':['i'],
		u'��':['i'],
		u'�E':['u'],
		u'��':['u'],
		u'�G':['e'],
		u'��':['e'],
		u'�I':['o'],
		u'��':['o'],
		u'�J':['k','a'],
		u'��':['k','a'],
		u'�L':['k','i'],
		u'��':['k','i'],
		u'�N':['k','u'],
		u'��':['k','u'],
		u'�P':['k','e'],
		u'��':['k','e'],
		u'�R':['k','o'],
		u'��':['k','o'],
		u'�T':['s','a'],
		u'��':['s','a'],
		u'�V':['S','i'],
		u'��':['S','i'],
		u'�X':['s','u'],
		u'��':['s','u'],
		u'�Z':['s','e'],
		u'��':['s','e'],
		u'�\':['s','o'],
		u'��':['s','o'],
		u'�^':['t','a'],
		u'��':['t','a'],
		u'�`':['tS','i'],
		u'��':['tS','i'],
		u'�c':['ts','u'],
		u'��':['ts','u'],
		u'�e':['t','e'],
		u'��':['t','e'],
		u'�g':['t','o'],
		u'��':['t','o'],
		u'�i':['n','a'],
		u'��':['n','a'],
		u'�j':['n1','i'],
		u'��':['n1','i'],
		u'�k':['n','u'],
		u'��':['n','u'],
		u'�l':['n','e'],
		u'��':['n','e'],
		u'�m':['n','o'],
		u'��':['n','o'],
		u'�n':['h','a'],
		u'��':['h','a'],
		u'�q':['C','i'],
		u'��':['C','i'],
		u'�t':['f','u'],
		u'��':['f','u'],
		u'�w':['h','e'],
		u'��':['h','e'],
		u'�z':['h','o'],
		u'��':['h','o'],
		u'�}':['m','a'],
		u'��':['m','a'],
		u'�~':['m','i'],
		u'��':['m','i'],
		u'��':['m','u'],
		u'��':['m','u'],
		u'��':['m','e'],
		u'��':['m','e'],
		u'��':['m','o'],
		u'��':['m','o'],
		u'��':['j','a'],
		u'��':['j','a'],
		u'��':['j','u'],
		u'��':['j','u'],
		u'��':['j','o'],
		u'��':['j','o'],
		u'��':['r','a'],
		u'��':['r','a'],
		u'��':['r','i'],
		u'��':['r','i'],
		u'��':['r','u'],
		u'��':['r','u'],
		u'��':['r','e'],
		u'��':['r','e'],
		u'��':['r','o'],
		u'��':['r','o'],
		u'��':['w','a'],
		u'��':['w','a'],
		u'��':['w','a'],
		u'��':['w','a'],
		u'��':['w','i'],
		u'��':['w','i'],
		u'��':['w','e'],
		u'��':['w','e'],
		u'��':['w','o'],
		u'��':['w','o'],
		u'�K':['g','a'],
		u'��':['g','a'],
		u'�M':['g','i'],
		u'��':['g','i'],
		u'�O':['g','u'],
		u'��':['g','u'],
		u'�Q':['g','e'],
		u'��':['g','e'],
		u'�S':['g','o'],
		u'��':['g','o'],
		u'�U':['z','a'],
		u'��':['z','a'],
		u'�W':['Z','i'],
		u'��':['Z','i'],
		u'�Y':['z','u'],
		u'��':['z','u'],
		u'�[':['z','e'],
		u'��':['z','e'],
		u'�]':['z','o'],
		u'��':['z','o'],
		u'�_':['d','a'],
		u'��':['d','a'],
		u'�a':['d','i'],
		u'��':['d','i'],
		u'�d':['Z','u'],
		u'��':['Z','u'],
		u'�f':['d','e'],
		u'��':['d','e'],
		u'�h':['d','o'],
		u'��':['d','o'],
		u'�o':['b','a'],
		u'��':['b','a'],
		u'�r':['b','i'],
		u'��':['b','i'],
		u'�u':['b','u'],
		u'��':['b','u'],
		u'�x':['b','e'],
		u'��':['b','e'],
		u'�{':['b','o'],
		u'��':['b','o'],
		u'�p':['p','a'],
		u'��':['p','a'],
		u'�s':['p','i'],
		u'��':['p','i'],
		u'�v':['p','u'],
		u'��':['p','u'],
		u'�y':['p','e'],
		u'��':['p','e'],
		u'�|':['p','o'],
		u'��':['p','o'],
		u'��':['v','u'],
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

	# �A���t�@�x�b�g�̓ǂ�
	alphabet_yomi = {
		u'A':u'�G�[',
		u'B':u'�r�[',
		u'C':u'�V�[',
		u'D':u'�f�B�[',
		u'E':u'�C�[',
		u'F':u'�G�t',
		u'G':u'�W�[',
		u'H':u'�G�b�`',
		u'I':u'�A�C',
		u'J':u'�W�F�[',
		u'K':u'�P�[',
		u'L':u'�G��',
		u'M':u'�G��',
		u'N':u'�G�k',
		u'O':u'�I�[',
		u'P':u'�s�[',
		u'Q':u'�L���[',
		u'R':u'�A�[��',
		u'S':u'�G�X',
		u'T':u'�e�B�[',
		u'U':u'���[',
		u'V':u'���C',
		u'W':u'�_�u�����[',
		u'X':u'�G�b�N�X',
		u'Y':u'���C',
		u'Z':u'�[�b�g',
		u'a':u'�G�[',
		u'b':u'�r�[',
		u'c':u'�V�[',
		u'd':u'�f�B�[',
		u'e':u'�C�[',
		u'f':u'�G�t',
		u'g':u'�W�[',
		u'h':u'�G�b�`',
		u'i':u'�A�C',
		u'j':u'�W�F�[',
		u'k':u'�P�[',
		u'l':u'�G��',
		u'm':u'�G��',
		u'n':u'�G�k',
		u'o':u'�I�[',
		u'p':u'�s�[',
		u'q':u'�L���[',
		u'r':u'�A�[��',
		u's':u'�G�X',
		u't':u'�e�B�[',
		u'u':u'���[',
		u'v':u'���C',
		u'w':u'�_�u�����[',
		u'x':u'�G�b�N�X',
		u'y':u'���C',
		u'z':u'�[�b�g',
		u'�`':u'�G�[',
		u'�a':u'�r�[',
		u'�b':u'�V�[',
		u'�c':u'�f�B�[',
		u'�d':u'�C�[',
		u'�e':u'�G�t',
		u'�f':u'�W�[',
		u'�g':u'�G�b�`',
		u'�h':u'�A�C',
		u'�i':u'�W�F�[',
		u'�j':u'�P�[',
		u'�k':u'�G��',
		u'�l':u'�G��',
		u'�m':u'�G�k',
		u'�n':u'�I�[',
		u'�o':u'�s�[',
		u'�p':u'�L���[',
		u'�q':u'�A�[��',
		u'�r':u'�G�X',
		u'�s':u'�e�B�[',
		u'�t':u'���[',
		u'�u':u'���C',
		u'�v':u'�_�u�����[',
		u'�w':u'�G�b�N�X',
		u'�x':u'���C',
		u'�y':u'�[�b�g',
		u'��':u'�G�[',
		u'��':u'�r�[',
		u'��':u'�V�[',
		u'��':u'�f�B�[',
		u'��':u'�C�[',
		u'��':u'�G�t',
		u'��':u'�W�[',
		u'��':u'�G�b�`',
		u'��':u'�A�C',
		u'��':u'�W�F�[',
		u'��':u'�P�[',
		u'��':u'�G��',
		u'��':u'�G��',
		u'��':u'�G�k',
		u'��':u'�I�[',
		u'��':u'�s�[',
		u'��':u'�L���[',
		u'��':u'�A�[��',
		u'��':u'�G�X',
		u'��':u'�e�B�[',
		u'��':u'���[',
		u'��':u'���C',
		u'��':u'�_�u�����[',
		u'��':u'�G�b�N�X',
		u'��':u'���C',
		u'��':u'�[�b�g',
	}


	# �L���̓ǂ�
	symbol_yomi = {
		u'_':u'�A���_�[�o�[',
		u':':u'�R����',
		u'�F':u'�R����',
		u';':u'�Z�~�R����',
		u'�G':u'�Z�~�R����',
		u'/':u'�X���b�V��',
		u'�^':u'�X���b�V��',
		u'��':u'�p�[�Z���g',
		u'%':u'�p�[�Z���g',
		u'>':u'�����Ȃ�',
		u'��':u'�����Ȃ�',
		u'<':u'���傤�Ȃ�',
		u'��':u'���傤�Ȃ�',
		u'(':u'������',
		u'�i':u'������',
		u')':u'�������Ƃ�',
		u'�j':u'�������Ƃ�',
		u'[':u'����������',
		u'�u':u'����������',
		u']':u'�����������Ƃ�',
		u'�v':u'�����������Ƃ�',
		u'�E':u'�Ȃ��Ă�',
		u'+':u'�v���X',
		u'-':u'�}�C�i�X',
		u'��':u'����',
		u'�~':u'�J�P��',
		u'�{':u'�v���X',
		u'�|':u'�}�C�i�X',
		u'=':u'�C�R�[��',
		u'��':u'�C�R�[��',
	}


	##### Phoneme_jp2���\�b�h��` #####

   	# �X���Ȃ�Εϊ�
   	def yoon(self,str,boin):
		"""�X���t���̕������ϊ����郁�\�b�h
		"""

		if str != [] and ( boin == 'a' or boin == 'u' or boin == 'o' ):
			if len(str)>=2 and str[-1] == 'i':
				c = str[-2]
				if c == 'C' or c == 'Z' or c == 'S' or c == 'tS' or c == 'n1' :
					str[-1] = boin
					return str
				elif c == 'n':
					str[-2] = 'n1'
					str[-1] = boin
					return str
				else:
					str[-1] = 'j'
					str.append(boin)
					return str
			else:
				return ['j',boin]

		return []


	# ���X���Ȃ�Εϊ�
	def hanyoon(self,str,boin):
		"""���X���t���̕������ϊ����郁�\�b�h
		"""

		# �v�f����ȏ�
		if len(str) >= 2:
			c = str[-2]
			v = str[-1]

			# ���J�� va,vi,ve,vo<-vu�A�ӂ� fa,fi,fe,fo<-fu
			if v == 'u' and ( boin == 'a' or  boin == 'i' or  boin == 'e' or  boin == 'o' )  and ( c == 'f' or c == 'v' ):
				str[-1] = boin
				return str

			# �Ă� ti<-te�A�ł� di<-de
			elif v == 'e' and boin == 'i' and ( c == 't' or c == 'd' ):
				str[-1] = boin
				return str

			# ���� Ze<-Zi�A���� tSe<-tSi
			elif v == 'i' and boin == 'e' and ( c == 'Z' or c == 'tS' ):
				str[-1] = boin
				return str

		# ���X�����g���Ȃ���A��L�ȊO�Ȃ�Εꉹ�ƌ��Ȃ�
		str.append(boin)
		return str


	# �����P�ʂŕϊ�
	# return (�m�艹��specified,���m�艹��unspecified)
	def convert_symbol(self,s,carryover):
		"""�����P�ʂŕϊ����Ă������\�b�h
		"""

		## �m�� ##
		# ��_
		if ( s == u'�B' ):
			carryover.append('.')
			return ( carryover, [] )

		# �Ǔ_
		elif ( s == u'�A' ) or ( s == u'�C' ) or ( s == u',' ):
			carryover.append(',')
			return ( carryover, [] )

		# �^�╄
		elif ( s == u'�H' ) or ( s == u'?' ):
			carryover.append('?')
			return ( carryover, [] )

		# ���Q��
		elif ( s == u'�I' ) or ( s == u'!' ):
			carryover.append('!')
			return ( carryover, [] )

		# �����L��
		elif ( s == u'�[' ):
			if carryover:
				last = carryover[-1] # �J�z������Ƃ������Ƃ͌J�z�ɗv�f�͈�͂���
				if last == 'a' or last == 'i' or last == 'u' or last == 'e' or last == 'o':
					carryover[-1] = last + ':'
			return ( carryover, [] )

		# �����i���̕�������ŉ����ς�邪�A����͂��ׂĂ��I����Ă���m�肳����j
		elif ( s == u'��' ) or ( s == u'��' ):
			carryover.append('X')
			return ( carryover, [] )

		# �����L��
		elif ( s == u'�b' ) or ( s == u'��' ):
			carryover.append('Q')
			return ( carryover, [] )

		## ���m�� ##
		# ���X���L���i�������������Ƃ�����̂Ŗ��m��j
		elif self.convert_hanyoon_table.has_key(s):
			unspecified = self.hanyoon(carryover,self.convert_hanyoon_table[s])
			return ( [], unspecified )

		# �X���L���i�������������Ƃ�����̂Ŗ��m��j
		elif self.convert_yoon_table.has_key(s):
			unspecified = self.yoon(carryover,self.convert_yoon_table[s])
			return ( [], unspecified )

		# �����L���B�u���J�v�̂Ƃ��̂݁B����ȊO�͕����N���A�i�������������Ƃ�����̂Ŗ��m��j
		elif ( s == u'�J' ):
			if carryover != [] and carryover[-1] == 'u':
				unspecified = ['v','u']
				return ( [], unspecified )
			else:
				return ( [], [] )

		## �m�聕���m�� ##
		# �P�����i�V�������߂��n�܂�̂ŁA�O�̂��̂��m��ɂȂ�j
		elif self.convert_table.has_key(s):
			unspecified = self.convert_table[s][:]
			return ( carryover, unspecified )

		## �s���ȕ��� ##
		# �J�z�����m�肵�A�s���ȕ����͎̂Ă�
		else:
			return ( carryover, [] )

		return ( carryover, [] )


	# ��������������f�L���ɕϊ�����B
	def convert(self,s):
		"""�ϊ��{�̃��\�b�h
		"""

		if DEBUG:
			## log
			self.log.writeln('�ϊ��Ώۉ�������:')
			self.log.writeln(s)
			self.log.writeln()

		# �ꂪ��Ȃ�Ή��������I��
		if s == '':
			return []

		if s == u' ' or s == u'�@':
			return [u' ']

		# ���������񂩂特�f�̔z������
		phonemes    = []
		unspecified = []
		for ch in s:
			( specified, unspecified ) = self.convert_symbol(ch,unspecified)

			if specified:
				for ph in specified:
					phonemes.append(ph)

		if unspecified:
			for ph in unspecified:
				phonemes.append(ph)

		# ���f�z�񂪋�Ȃ�ΏI��
		if not phonemes:
			return []

		if DEBUG:
			## log
			self.log.writeln('�����������特�f�z��ɕϊ���:')
			for n in phonemes:
				self.log.write(n)
			self.log.writeln()
			self.log.writeln()

		# ���[���P�ʂɕ�����
		temp = []
		keep = []
		while phonemes:
			ch = phonemes.pop(0)
			if ch == '.' or ch == '!' or ch == '?'  or ch == ',':
				keep.append(ch)
				temp.append(keep)
				keep = []
			elif ch == 'a' or ch == 'i' or ch == 'u' or ch == 'e' or ch == 'o':
				keep.append(ch)
				temp.append(keep)
				keep = []
			elif ch == 'a:' or ch == 'i:' or ch == 'u:' or ch == 'e:' or ch == 'o:':
				keep.append(ch[0])
				temp.append(keep)
				temp.append(':')
				keep = []
			elif ch == 'X' or ch == 'Q':
				temp.append( ch )
				keep = []
			else:
				keep.append(ch)
		phonemes = temp

		if DEBUG:
			## log
			self.log.writeln('���[�����ɕ�����:')
			for n in phonemes:
				if n:
					self.log.write('[')
					for m in n:
						self.log.write(m)
					self.log.write(']')
			self.log.writeln()
			self.log.writeln()

		# �e���f���p�����[�^�ƂƂ��ɏo�͂���
		return phonemes


	# pho�`���ŉ��f���o�͂���
	def make_pho_lines( self, nodes ):

		# node( ���f���X�g, �i��, �A�N�Z���g, �\�[�X )

		scale = 1 / rate / self.default_scale

		# �A�N�Z���g���l���������f�f�[�^���X�g���쐬
		phonemes = []
		prev_accent = ''
		prev_noun   = False
		for node in nodes:

			if DEBUG:
				self.log.write("���f��@�@�F")
				for n in node[0]:
					for m in n:
						self.log.write(m)
				self.log.writeln()
				self.log.writeln("�i���@�@�@�F" + node[1])
				if node[2]:
					self.log.writeln("�A�N�Z���g�F" + node[2])
				if node[1] !='�⏕�L��' and node[1] != '��_':
					self.log.writeln("���[�����@�F" + str(len(node[0])))
				self.log.writeln()
				# ���f�̏��@�@�i�L���A�����A����j


			# ���f�f�[�^���󔒂̏ꍇ
			if node and node[0] and node[0][0]== u' ':
				phonemes.append(['_',0,0])
				prev_accent = ''
				prev_noun   = False
				continue

			# �⏕�L���͋󔒈����ɂ���
			if node[1] == '�⏕�L��':
				ch = node[0][0][0]
				if ch == '?' or ch == '!' or ch =='.' or ch == ',':
					phonemes.append([ch,0,0])
				else:
					phonemes.append(['_',0,0])
				prev_accent = ''
				prev_noun   = False
				continue

			# �O�̃m�[�h�����A�N�Z���g�̖����Ȃ�΁A���̂��Ƃ̏����͍����ɂ���
			if ( node[1] == '����' ) and prev_noun and prev_accent == '0':

				for n in node[0]:
					for m in n:
						phonemes.append( [m,0,1] )
				continue

			# �ŏ��̗v�f�����f�f�[�^
			data = node[0]

			# �A�N�Z���g�̏���t������
			accent = node[2]
			prev_accent = accent
			prev_noun   = node[1]=='����'
			if accent:

				# ���^�A�N�Z���g
				if accent == '0':
					for m in data[0]:
						phonemes.append( [m,0,0] )

					for n in data[1:]:
						for m in n:
							phonemes.append( [m,0,1] )

				# �����^�A�N�Z���g
				elif accent == '1':
					for m in data[0]:
						phonemes.append( [m,0,1] )
					for n in data[1:]:
						for m in n:
							phonemes.append( [m,0,0] )

				# �����^
				elif accent == '2':
					for m in data[0]:
						phonemes.append( [m,0,0] )
					for m in data[1]:
						phonemes.append( [m,0,1] )
					for n in data[2:]:
						for m in n:
							phonemes.append( [m,0,0] )

				# �����^
				else:
					for n in data[:int(accent)-1]:
						for m in n:
							phonemes.append( [m,0,0] )

					for n in data[int(accent)-1:]:
						for m in n:
							phonemes.append( [m,0,1] )

			# �m�[�h�ɃA�N�Z���g���Ȃ��ꍇ
			else:
				for n in data:
					for m in n:
						phonemes.append( [m,0,0] )

		# �ȏ�A�e�m�[�h�ɑ΂��鏈��

		if DEBUG:
			self.log.writeln('�A�N�Z���g������:')
			self.log.dump_phonemes( phonemes )

		# �����L����O�̕ꉹ�Ɍ��т���
		prev = []
		temp = []
		for ph in phonemes:

			if ph[0] == ':':
				if prev:
					p = prev[0]
					if p == 'a' or p == 'i' or p == 'u' or p == 'e' or p == 'o':
						temp.append( [ p + ':',  prev[1], prev[2] ] )
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

		if DEBUG:
			self.log.writeln('����������:')
			self.log.dump_phonemes( phonemes )

		# ���f�̒������v�Z�B�ꉹ�͐旧�q���̒����������Ē�������
		temp = []
		length = 0
		for ph in phonemes:

			if ph:
				# ��_�̏���
				if ph[0] == '?' or  ph[0] == '!' or  ph[0] == '.'  or  ph[0] == ',':
					d = 100
					length = 0

				# �q���̏���
				if self.phone_duration_consonant.has_key(ph[0]):
					d = self.phone_duration_consonant[ph[0]]
					length = length + d

				# �ꉹ�̏���
				if self.phone_duration_vowel.has_key(ph[0]):
					d = self.phone_duration_vowel[ph[0]] - length
					length = 0

			temp.append( [ph[0],d,ph[2]] )
		phonemes = temp

		if DEBUG:
			self.log.writeln('����������:')
			self.log.dump_phonemes( phonemes )

		# �����y�ѝ����̒���̎��s�j�􉹋L�������s�j�C���ɕϊ��@Z->dZ, z->dz
		last = '_'
		t = []
		for ph in phonemes:
			if self.phone_head_remap.has_key(ph[0]) and ( last == ',' or last == '_' or last == 'Q' or last == 'X' ):
				t.append( [self.phone_head_remap[ph[0]],ph[1],ph[2]] )
			else:
				t.append( ph )
			last = ph[0]
		if not t:
			return []
		phonemes = t

		if DEBUG:
			self.log.writeln('���s�j�C��������:')
			self.log.dump_phonemes( phonemes )

		# �����L����{���̉��f�ɕϊ�����(�t���ŏ���)
		last = '_'
		t = []
		for ph in reversed(phonemes):
			p = ph[0]
			if p == 'X' and self.phone_N_map.has_key(last):
				p =  self.phone_N_map[last]
				t.append( [p,ph[1],ph[2]] )
			else:
				t.append(ph)
			last = p
		phonemes = t[::-1]

		if DEBUG:
			self.log.writeln('�����L��������:')
			self.log.dump_phonemes( phonemes )

		# �^�╶�̂Ƃ��́A�オ�蒲�q�ɂ���
		if phonemes and len(phonemes)>2:
			if phonemes[-1][0] == '?':
				ph = phonemes[-2]
				phonemes[-2] = [ ph[0], ph[1]+200, 2]

		if DEBUG:
			self.log.writeln('�^��`������:')
			self.log.dump_phonemes( phonemes )


		# �u�ł��v�̋[�������ꉹ���i����ėp������\��j
		if phonemes and len(phonemes)>3:
			if phonemes[-1][0] == '_' and  phonemes[-2][0] == 'u' and  phonemes[-3][0] == 's':
				ph = phonemes[-2]
				phonemes[-3] = [ phonemes[-3][0], 500, phonemes[-3][2]]
				phonemes[-2] = [ 'u_0', 10, ph[2]]

		if DEBUG:
			self.log.writeln('��������������:')
			self.log.dump_phonemes( phonemes )

		# ���Ή��A�����̒����ia:i:,i:u:,u:u:,o:u:,vu:�j->�ia:_i:,i:_u:,u:_u:,o:_u:,vuu:�j
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

		if DEBUG:
			self.log.writeln('���Ή��A�����̕␳:')
			self.log.dump_phonemes( phonemes )

		po = self.default_po			# �W���s�b�`�ʒu
		pt = self.default_pt			# �W�����f�s�b�`

		# �v�f�̉��f�̐������J��Ԃ�
		pitch_temp = str(int((pt)*pitch))

		result = []
		result.append( '_\t' + str(int(100*scale)) )
		
		for ph in phonemes:

			data = ph[0]

			if data == 'X': # �ϊ��ł��Ă��Ȃ������L������������폜
				continue

			if ph[1]:
				tm = ph[1]
			else:
				tm = self.default_ms

			if data == ',':  # �R���}��␳
				data = '_'

			elif data == 'Q':  # �����L����␳
				data = '_'

			# ��_�̂Ƃ��̓R�����g��}���iPYD�ŗ��p�j
			if data == '.' or data == '!':
				result.append( '_' + '\t' + str(int(tm*scale)) + '\t' + str(po) + '\t' + pitch_temp )
				result.append( ';kuten' )

			elif data == '?' :
				result.append( '_' + '\t' + str(int(tm*scale)) + '\t' + str(po) + '\t' + str(int((pt+ques_diff*1.5)*pitch)) )
				result.append( ';kuten' )

			# �ʏ�̉��f
			else:
				if  ph[2] == 0:
					pitch_temp = str(int((pt)*pitch))
				elif ph[2] == 1:
					pitch_temp = str(int((pt+self.acc_diff)*pitch))
				elif ph[2] == 2:
					pitch_temp = str(int((pt+self.ques_diff)*pitch))
				else:
					pitch_temp = str(int((pt)*pitch))

				result.append( data + '\t' + str(int(tm*scale)) + '\t' + str(po) + '\t' + pitch_temp )

		result.append( '_\t' + str(int(self.finish_rest*scale)) )

		if DEBUG:
			if result:
				self.log.writeln('�ϊ�����:')
				for i in result:
					self.log.writeln(i)
				self.log.writeln()


		return result

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
	def convert_using_dic(self,s):
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

		if DEBUG:
			self.log.writeln("�Ώە�����:")
			self.log.writeln(s)
			self.log.writeln()

		# �A���t�@�x�b�g��ϊ�
		temp = ''
		for c in s:
			if self.alphabet_yomi.has_key(c):
				c = self.alphabet_yomi[c]
			temp = temp + c
		s = temp

		if DEBUG:
			self.log.writeln('�A���t�@�x�b�g�ϊ���:')
			self.log.writeln(s)
			self.log.writeln()

		# �L����ϊ�
		temp = ''
		if self.flag_reading_symbol:
			for c in s:
				if self.symbol_yomi.has_key(c):
					c = self.symbol_yomi[c]
				temp = temp + c
		else:
			for c in s:
				if self.symbol_yomi.has_key(c):
					c = u'�@'
				temp = temp + c
		s = temp

		if DEBUG:
			self.log.writeln('�L���ϊ���:')
			self.log.writeln(s)
			self.log.writeln()

		# �ȈՎ������g���ăJ�i�\�L�ɒu��������
		if self.dic_enable:
			s = self.convert_using_dic(s)

		# �����񒆂̐��l����{��ɕϊ�
		s = self.convert_numstring(s)

		s = s.encode('sjis')

		node = self.mecab.parseToNode(s)
		node = node.next


		# feature ���X�g���l��
		def get_feature_list(feature):

			if not feature:
				return []

			t = feature.split(',')

			# ������Ƃ��Ă�','�̉��߂�␳
			ttt = ''
			s = []
			for tt in t:
				if tt and tt[0] == '"':
					ttt = tt[1:]
					tt  = ''
				elif ttt and tt and tt[-1] == '"':
					ttt = ttt + ',' + tt[:-1]
					tt = ttt
					ttt = ''
				elif ttt:
					ttt = ttt + ',' + tt
					tt  = ''
				if tt:
					s.append(tt)

			return s

		# mecab �̉�͌��ʂ����ƂɊe�v�f��ϊ�
		result = []
		while node:

			nodes = []

			# ��_�������͏I�[�����܂ł��W�߂āA�ϊ�����B
			while node:

				t = node.feature
				t = get_feature_list(node.feature)

				# Unidic�ɑ΂��Ă̏���
				if self.mecab_dic_name == 'unidic':

					if len(t)>9 and t[9]:
						s = unicode(t[9],'sjis')
					else:
						s = unicode( node.surface, 'sjis' )

					if t[0] == 'BOS/EOS':
						node = None
						break

					if DEBUG:
						self.log.writeln("str    :" + "'" + s + "'")
						self.log.writeln("feature:" + node.feature)
						self.log.writeln("surface:" + node.surface)
						self.log.writeln()

					data = self.convert(s)

					if self.use_accent:

						if len(t) > 22:
							accent = t[22]
							accent = accent.split(',')[0]
							if accent == '*':
								accent = ''
						else:
							accent = ''

						nodes.append( ( data, t[0], accent ) )

					else:
						nodes.append( ( data, t[0], None ) )

				# ipadic�ɑ΂��Ă̏���
				elif self.mecab_dic_name == 'ipadic':

					if t[0] == 'BOS/EOS':
						node = None
						break
					if len(t)>8:
						s = unicode(t[8],'sjis')
					else:
						s = unicode( node.surface, 'sjis' )

					if DEBUG:
						self.log.writeln("str    :" + "'" + s + "'")
						self.log.writeln("feature:" + node.feature)
						self.log.writeln("surface:" + node.surface)
						self.log.writeln()

					data = self.convert(s)
					nodes.append( ( data, t[0], None ) )

				if  t[1] == '��_':
					node = node.next
					break

				node = node.next

			if DEBUG:
				## log
				if nodes:
					self.log.writeln('�ϊ�����:')

					for n in nodes:
						self.log.writeln("�i���F" + n[1])

						if n[2]:
							accent = n[2]
							self.log.writeln("�A�N�Z���g�F" + accent)
						else:
							self.log.writeln("�A�N�Z���g�F���Ȃ�")
						self.log.write("���f�L���F")
						for l in n[0]:
							self.log.write('[')
							for m in l:
								self.log.write(m)
							self.log.write(']')
						self.log.writeln()
						self.log.writeln()
					self.log.writeln()

			# �e���f�̃p�����[�^��ݒ肷��
			if nodes:
				temp = self.make_pho_lines( nodes )

				# ���ł̌��ʂɘA��
				result.extend(temp)

		return result


	# �A�N�Z���g�̃��[�h��ݒ肷��
	def set_accent_mode(self,mode):
		if mode == 1:
			self.use_accent = 1
		else:
			self.use_accent = 0


	# �s�b�`��ݒ肷��
	def set_pitch(self,vol):
		"""���ʂ�ݒ肷��
		�͈͂�[0.2,8.0]
		"""

		if vol < 0.2:
			vol = 0.2

		if vol > 8.0:
			vol = 8.0

		self.pitch = vol


	# �ǂݏグ���x��ݒ肷��
	def set_rate(self,val):
		"""�ǂݏグ���x��ݒ肷��
		�͈͂�[0.2,8.0]
		"""

		if val < 0.2:
			val = 0.2

		if val > 8.0:
			val = 8.0

		self.rate = val


	# �L���ǂݏグ�̐ݒ�
	def set_reading_symbol(self,mode):

		if mode == 1:
			self.flag_reading_symbol = 1
		else:
			self.flag_reading_symbol = 0


# ���O�o�͗p�N���X
class Log:
	def __init__(self,name):
		pass

	def __del__(self):
		pass

	def write(self,data=""):
		print data,

	def writeln(self,data=""):
		print data

	def dump_phonemes(self,phonemes):
		for i in phonemes:
			self.writeln( str(i[0]) + '\t'  + str(i[1]) + '\t'  + str(i[2]) )
		self.writeln()


##### �N���X�I�� #####




# �W�����ʔ䗦
volume = 1.0

# �W���ǂݏグ���x�䗦
rate = 1.0

# �W���s�b�`�䗦
pitch = 1.0




# �e�L�X�g����PHO�t�@�C�����쐬����
def makePHO(str,filename):
	"""�e�L�X�g����PHO�t�@�C�����쐬����B
	��������t�@�C������sjis�ŃG���R�[�h����Ă���Ƃ���B
	�t�@�C������'.pho'�����ɕt������Ă���Ƃ݂Ȃ�
	"""

	global accent_mode
	global dic_name
	global rate
	global pitch

	# �������ݗp��PHO�t�@�C�����J��
	phofile = open( filename, 'w')

	if str == '':
		return

	# ���f�N���X����
	phenomen = Phenomen( dic_name )
	phenomen.set_accent_mode( accent_mode )					# �A�N�Z���g�̗L���ݒ�
	phenomen.set_rate( rate )								# ���[�g�̐ݒ�
	phenomen.set_pitch( pitch )								# �s�b�`�̐ݒ�
	phenomen.set_reading_symbol( reading_symbol_mode )		# �L���ǂ݂̐ݒ�

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


# �A�N�Z���g�̃��[�h��ݒ肷��
def set_accent_mode(mode):
	global accent_mode
	if mode == 1:
		accent_mode = 1
	else:
		accent_mode = 0


# �L���̓ǂ݂����邩�ǂ�����ݒ肷��
def set_reading_symbol(mode):
	"""�L���̓ǂ݂����邩�ǂ�����ݒ肷��
	"""

	global reading_symbol_mode
	if mode == 1:
		reading_symbol_mode = 1
	else:
		reading_symbol_mode = 0



##### �P�Ɨ��p���� #####

def main():

	global accent_mode,reading_symbol_mode,dics,default_dic,dic_name


	### �I�v�V�����̐ݒ� ###

	usage = u"usage: %prog [options] ������P ������Q..."

	parser = OptionParser(usage=usage)
	parser.add_option( "-f", "--file",         dest="filename",
		help=u"�ǂݏグ��t�@�C�����w�肵�܂��i-i�Ƃ̋����͕s�j" )
	parser.add_option( "-r", "--rate",         dest="rate",
		help=u"�ǂݏグ���x�̔䗦���w�肵�܂��i0.2�`8.0�j" )
	parser.add_option( "-v", "--volume",       dest="volume",
		help=u"�ǂݏグ���ʂ̔䗦���w�肵�܂��i0.2�`8.0�j" )
	parser.add_option( "-p", "--pitch",        dest="pitch",
		help=u"�ǂݏグ�s�b�`�̔䗦���w�肵�܂��i0.2�`8.0�j" )

	default_string =u"�i�W���ݒ�j"
	str1 = ""
	str2 = default_string
	if accent_mode:
		str1,str2 = str2,str1
	parser.add_option( "--accent-on",          action="store_true",   dest="accent_mode",
		help=u"�A�N�Z���g�ǂݏグ���I���ɂ��܂�" + str1 )
	parser.add_option( "-a", "--accent-off",   action="store_false",  dest="accent_mode",
		help=u"�A�N�Z���g�ǂݏグ���I�t�ɂ��܂�" + str2 )

	str1 = ""
	str2 = default_string
	if reading_symbol_mode:
		str1,str2 = str2,str1
	parser.add_option( "-s", "--symbol-on",    action="store_true",   dest="symbol_mode",
		help=u"�L���ǂݏグ���I���ɂ��܂�" + str1 )
	parser.add_option( "--symbol-off",         action="store_false",  dest="symbol_mode",
		help=u"�L���ǂݏグ���I�t�ɂ��܂�" + str2 )

	if dics:
		temp = u"�i" + u",".join(dics) + u"�j"
	parser.add_option( "-d", "--dic-name",     dest="dic_name",
		help=u"�g�p���鎫�����w�肵�܂�" + temp + u"�W����" + dics[default_dic] )

	parser.add_option( "-i", "--use-stdin",    action="store_true",   dest="enable_stdin",
		help=u"�W�����͂�ǂݏグ�܂��i-f�Ƃ̋����͕s�j" )
	(options, args) = parser.parse_args()


	### �p�����[�^����l������

	if options.rate:
		set_rate( float(options.rate) )

	if options.volume:
		set_volume( float(options.volume) )

	if options.pitch:
		set_pitch( float(options.pitch) )

	if options.pitch:
		set_pitch( float(options.pitch) )

	if options.accent_mode != None:
		set_accent_mode( options.accent_mode )

	if options.symbol_mode != None:
		set_reading_symbol( options.symbol_mode )

	if options.dic_name:
		dic_name = options.dic_name


	### �p�����[�^�ɉ��������� ###

	# �W�����͂���̓ǂݍ��݂��w�肳��Ă�����
	if options.enable_stdin != None:

		if options.filename:
			print "�W�����͂ƃt�@�C���𓯎��ɓ��͂ɂ��邱�Ƃ͂ł��܂���"
		else:
			for line in sys.stdin:
				speak(line)

	# �����ł͂Ȃ��A�t�@�C������̓ǂݍ��݂��w�肳��Ă�����
	elif options.filename:
		if os.path.exists(options.filename):
			f = open( options.filename, 'r')
			for l in f:
				speak(l)
			f.close()

	# �����ł��Ȃ��A�����񂪎w�肳��Ă�����
	elif len(args) > 0:
		for l in args:
			speak(l)

	# �����ł��Ȃ��A�w��̃e�L�X�g�t�@�C�������݂��Ă�����
	elif os.path.exists(text):
		f = open(text, 'r')
		for l in f:
			speak(l)
		f.close()

	# �����ł��Ȃ��A���A�̕����񂪎w�肳��Ă�����
	elif message != '':
		speak(message)



if __name__ == '__main__':
	main()
