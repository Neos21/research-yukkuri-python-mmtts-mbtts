/*
** pho2wav.cpp
** 2010/02/28
** copyright(c) takayan
** http://neu101.seesaa.net/
*/

#include <Python.h>
#include <stdio.h>
#include <windows.h>
#include "mbrola.h"

#define WAVMAXSIZE 4294960000
#define BUFOUTSIZE 4096
#define BUFINSIZE 260
#define KUTEN_MARK ";kuten"


unsigned char wav_header[44] = 
{
	0x52,0x49,0x46,0x46,
	0x00,0x00,0x00,0x00, // size1
	0x57,0x41,0x56,0x45,
	0x66,0x6D,0x74,0x20,
	0x10,0x00,0x00,0x00,
	0x01,0x00,0x01,0x00,
	0x22,0x56,0x00,0x00,
	0x44,0xac,0x00,0x00,
	0x02,0x00,0x10,0x00,
	0x64,0x61,0x74,0x61,
	0x00,0x00,0x00,0x00, // size2
};


bool _pho2wav( char *database, char *pho, char *wav, float vol )
{
	char  bufferin[BUFINSIZE];
	short bufferout[BUFOUTSIZE];
	FILE *fin;
	FILE *fin_d;
	FILE *fout;
	int nbr;
	unsigned long int size, work;

	// DLL�����[�h
	if (!load_MBR())
	{
		fputs("\nmbrola.dll�����[�h�ł��܂���\n",stderr);
		unload_MBR();
		return false;
	}

	// �ǂݍ��ݗp�Ƃ���PHO�t�@�C�����J��
	if( fopen_s(&fin,pho,"rt") < 0 )
	{
		fprintf(stderr,"\n���̓t�@�C�����J���܂���\n");
		unload_MBR();
		return false;
	}


	// �������ݗp�Ƃ���WAV�t�@�C�����J��
	if( fopen_s(&fout,wav,"wb") < 0 )
	{
		fprintf(stderr,"\n�o�̓t�@�C�����J���܂���\n");

		fclose(fin);
		unload_MBR();
		return false;
	}
	// WAV�t�@�C���̃w�b�_�̈�����ɏ�������
	fwrite(wav_header,sizeof(char),44,fout);

	// �f�[�^�T�C�Y�W�v�p�ϐ�������
	size = 0;

	// �����p�ꎞ�t�@�C���̖��O�����߂�
	char path[MAX_PATH];
	if( ::GetTempPath(MAX_PATH, path ) == 0 )
	{
		fclose(fin);
		fclose(fout);
		unload_MBR();
		return false;
	}
	char pho_d[MAX_PATH];
	if( ::GetTempFileName( path, "pho", 0, pho_d ) == 0 )
	{
		fclose(fin);
		fclose(fout);
		unload_MBR();
		return false;
	}

	if( fopen_s(&fin_d,pho_d,"wb") < 0 )
	{
		fclose(fin);
		fclose(fout);
		unload_MBR();
		return false;
	}
	fclose(fin_d);

	// �����ɂȂ�ƃG���[�ɂȂ�̂ŁA�����ɂȂ�Ƃ���ŕ�������B
	// �����Ɩ������Ȃ��ꍇ�͎d��������^^

	while(!feof(fin))
	{
		if( fopen_s(&fin_d,pho_d,"wb") < 0 )
		{
			fclose(fin);
			fclose(fout);
			unload_MBR();
			remove(pho_d);
			return false;
		}

		// ��_����؂�ɂ��ĕ�������
		char buf[1024];
		while( fgets( buf, 1024, fin ) != NULL )
		{
			if ( strlen(buf)>=6 && strncmp(buf,KUTEN_MARK,6 )==0 )
			{
				break;
			}
			fputs( buf, fin_d );
		}
		fclose(fin_d);

		// �f�[�^�x�[�X�̏����ݒ�
		if (init_MBR(database)<0)
		{
			fprintf(stderr,"\n�f�[�^�x�[�X %s ���������܂���\n",database);
			fclose(fin);
			unload_MBR();
			remove(pho_d);
			return false;
		}

		// �{�����[���ݒ�
		setVolumeRatio_MBR(vol);

		// �ǂݍ��ݗp�Ƃ���PHO�t�@�C�����J��
		if( fopen_s(&fin_d,pho_d,"rt") < 0 )
		{
			fprintf(stderr,"\n���̓t�@�C�����J���܂���\n");

			fclose(fin);
			close_MBR();
			unload_MBR();
			remove(pho_d);
			return false;
		}

		// ���o�̓��[�v
		while(!feof(fin_d))
		{
			// PHO�t�@�C������MBR�ւ̏������݃��[�v
			fgets(bufferin,BUFINSIZE,fin_d);
			while((write_MBR(bufferin)>0)&&(!feof(fin_d)))
			{
				fgets(bufferin,BUFINSIZE,fin_d);
			}

			// MBR����WAV�t�@�C���ւ̏������݃��[�v
			while((nbr=read_MBR(bufferout,BUFOUTSIZE))>0)
			{
				if ( size > WAVMAXSIZE )
					break;

				size += nbr*sizeof(short);

				fwrite(bufferout,sizeof(short),nbr,fout);
			}

			// Mbrola�G���[
			if (nbr<0)
			{
				lastErrorStr_MBR(bufferin,BUFINSIZE);
				fprintf(stderr,"\nMbrola �G���[:\n%s",bufferin);

				fclose(fin_d);
				fclose(fin);
				fclose(fout);
				close_MBR();
				unload_MBR();
				remove(pho_d);
				return false;
			}
		}
		// MBR�t���b�V��
		flush_MBR();

		// �c��̃f�[�^�� MBR����WAV�t�@�C���ւ̏������݃��[�v
		while((nbr=read_MBR(bufferout,BUFOUTSIZE))>0)
		{
			if ( size > WAVMAXSIZE )
				break;

			size += nbr*sizeof(short);
			fwrite(bufferout,sizeof(short),nbr,fout);
		}

		// Mbrola�G���[
		if (nbr<0)
		{
			lastErrorStr_MBR(bufferin,BUFINSIZE);
			fprintf(stderr,"\nMbrola �G���[:\n%s",bufferin);

			fclose(fin_d);
			fclose(fin);
			fclose(fout);
			close_MBR();
			unload_MBR();
			remove(pho_d);
			return false;
		}
		fclose(fin_d);
		close_MBR();
	}

	// �f�[�^�T�C�Y�����ɁA�w�b�_��������������
	work = size;
	wav_header[40] = work & 0xff;  // 4
	work >>= 8;
	wav_header[41] = work & 0xff;  // 3
	work >>= 8;
	wav_header[42] = work & 0xff;  // 2
	work >>= 8;
	wav_header[43] = work & 0xff;  // 1
	work = size + 36;
	wav_header[4]  = work & 0xff;  // 4
	work >>= 8;
	wav_header[5]  = work & 0xff;  // 3
	work >>= 8;
	wav_header[6]  = work & 0xff;  // 2
	work >>= 8;
	wav_header[7]  = work & 0xff;  // 1

	// �w�b�_������������
	fseek( fout, 0, SEEK_SET );
	fwrite(wav_header,sizeof(char),44,fout);

	fclose(fin);
	fclose(fout);
	unload_MBR();
	remove(pho_d);

	return true;
}



/*
** convert( database, pho, wav, vol )
**
** ����
** database : �f�[�^�x�[�X�t�@�C��
** pho      : ���͂���� pho �t�@�C��
** wav      : �o�͂��� wav �t�@�C��
** vol      : �{�����[���ݒ�(0.2-8.0)
**
** �߂�l
** ���� 1
** ���s None
**
** �@�\�F
** MBROLA.DLL�𗘗p���āAPHO�t�@�C������WAV�t�@�C�����쐬����
** 
*/
static PyObject *convert(PyObject *self, PyObject *args)
{
	// ���͕ϐ�
	char *database;
	char *pho;
	char *wav;
	float vol;

	// ���͉��
	if (!PyArg_ParseTuple(args, "sssf", &database, &pho, &wav, &vol ))
	{
	    Py_INCREF(Py_None);
		return Py_None;
	}

	if ( vol < 0.2f )
		vol = 0.2f;
	if ( vol > 8.0f )
		vol = 8.0f;

	if ( !_pho2wav( database, pho, wav, vol ) )
	{
	    Py_INCREF(Py_None);
		return Py_None;
	}

	// ����I��
	return Py_BuildValue("i",1);
}


// ���\�b�h���X�g
static PyMethodDef Methods[] = {
	{"convert", convert, METH_VARARGS, "pho�t�@�C������wav�t�@�C���𐶐����܂�"},
	{NULL, NULL, 0, NULL}
};


// ���W���[��������
PyMODINIT_FUNC
initpho2wav(void)
{
	(void) Py_InitModule( "pho2wav", Methods );
}

/* EOF */