@echo off
if "%1" == "" goto help
python %~dp0mbspeak.py %1 %2 %3 %4 %5 %6 %7 %8 %9
goto end
:help
python %~dp0mbspeak.py --help
python %~dp0mbspeak.py これは文字列を合成音声にするコマンドです。パラメータに文字列かスイッチを指定します。ただしMBROLA以外の音声に対しては簡易対応です。wオプションぐらいしか使えません。
:end
