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

	// DLLをロード
	if (!load_MBR())
	{
		fputs("\nmbrola.dllをロードできません\n",stderr);
		unload_MBR();
		return false;
	}

	// 読み込み用としてPHOファイルを開く
	if( fopen_s(&fin,pho,"rt") < 0 )
	{
		fprintf(stderr,"\n入力ファイルを開けません\n");
		unload_MBR();
		return false;
	}


	// 書き込み用としてWAVファイルを開く
	if( fopen_s(&fout,wav,"wb") < 0 )
	{
		fprintf(stderr,"\n出力ファイルを開けません\n");

		fclose(fin);
		unload_MBR();
		return false;
	}
	// WAVファイルのヘッダ領域を仮に書き込む
	fwrite(wav_header,sizeof(char),44,fout);

	// データサイズ集計用変数初期化
	size = 0;

	// 分割用一時ファイルの名前を決める
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

	// 長文になるとエラーになるので、無音になるところで分割する。
	// ずっと無音がない場合は仕方が無い^^

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

		// 句点を区切りにして分割する
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

		// データベースの初期設定
		if (init_MBR(database)<0)
		{
			fprintf(stderr,"\nデータベース %s を見つけられません\n",database);
			fclose(fin);
			unload_MBR();
			remove(pho_d);
			return false;
		}

		// ボリューム設定
		setVolumeRatio_MBR(vol);

		// 読み込み用としてPHOファイルを開く
		if( fopen_s(&fin_d,pho_d,"rt") < 0 )
		{
			fprintf(stderr,"\n入力ファイルを開けません\n");

			fclose(fin);
			close_MBR();
			unload_MBR();
			remove(pho_d);
			return false;
		}

		// 入出力ループ
		while(!feof(fin_d))
		{
			// PHOファイルからMBRへの書き込みループ
			fgets(bufferin,BUFINSIZE,fin_d);
			while((write_MBR(bufferin)>0)&&(!feof(fin_d)))
			{
				fgets(bufferin,BUFINSIZE,fin_d);
			}

			// MBRからWAVファイルへの書き込みループ
			while((nbr=read_MBR(bufferout,BUFOUTSIZE))>0)
			{
				if ( size > WAVMAXSIZE )
					break;

				size += nbr*sizeof(short);

				fwrite(bufferout,sizeof(short),nbr,fout);
			}

			// Mbrolaエラー
			if (nbr<0)
			{
				lastErrorStr_MBR(bufferin,BUFINSIZE);
				fprintf(stderr,"\nMbrola エラー:\n%s",bufferin);

				fclose(fin_d);
				fclose(fin);
				fclose(fout);
				close_MBR();
				unload_MBR();
				remove(pho_d);
				return false;
			}
		}
		// MBRフラッシュ
		flush_MBR();

		// 残りのデータを MBRからWAVファイルへの書き込みループ
		while((nbr=read_MBR(bufferout,BUFOUTSIZE))>0)
		{
			if ( size > WAVMAXSIZE )
				break;

			size += nbr*sizeof(short);
			fwrite(bufferout,sizeof(short),nbr,fout);
		}

		// Mbrolaエラー
		if (nbr<0)
		{
			lastErrorStr_MBR(bufferin,BUFINSIZE);
			fprintf(stderr,"\nMbrola エラー:\n%s",bufferin);

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

	// データサイズを元に、ヘッダ情報を完成させる
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

	// ヘッダ情報を書き込む
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
** 引数
** database : データベースファイル
** pho      : 入力される pho ファイル
** wav      : 出力する wav ファイル
** vol      : ボリューム設定(0.2-8.0)
**
** 戻り値
** 成功 1
** 失敗 None
**
** 機能：
** MBROLA.DLLを利用して、PHOファイルからWAVファイルを作成する
** 
*/
static PyObject *convert(PyObject *self, PyObject *args)
{
	// 入力変数
	char *database;
	char *pho;
	char *wav;
	float vol;

	// 入力解析
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

	// 正常終了
	return Py_BuildValue("i",1);
}


// メソッドリスト
static PyMethodDef Methods[] = {
	{"convert", convert, METH_VARARGS, "phoファイルからwavファイルを生成します"},
	{NULL, NULL, 0, NULL}
};


// モジュール初期化
PyMODINIT_FUNC
initpho2wav(void)
{
	(void) Py_InitModule( "pho2wav", Methods );
}

/* EOF */