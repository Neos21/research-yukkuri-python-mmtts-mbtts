#!/usr/bin/env python
# -*- coding: utf8 -*-

#from setuptools import setup, find_packages, Extension, os
from distutils.core import setup,Extension,os
import platform
import string
import sys

def cmd1(str):
    return os.popen(str).readlines()[0][:-1]

def cmd2(str):
    return string.split (cmd1(str))

val_folder      = '.mbtts'
val_name        = "mbtts"
val_data        = {'': ['userdic.txt']}
val_version     = '0.9.5'
val_summary     = 'Japanese-Text-To-Japanese-Speech'
val_homepage    = 'http://neu101.seesaa.net/'
val_author      = 'takayan'
val_license     = 'BSD'
val_description = 'this program converts Japanese text to speech.'
val_packages    = ['mbtts']

ps = platform.system()
if ps == "Windows":
	val_inc_dir    = ['C:/Program Files/MeCab/sdk']
	val_lib_dir    = ['C:/Program Files/MeCab/sdk']
	val_lib        = ['libmecab']
	val_scripts    = ['mbtts_postinst.py'] # for Windows Inst
	val_data_files = []
else:
	val_mbtts_dir  = os.path.join(os.environ['HOME'], val_folder )
	val_inc_dir    = cmd2("mecab-config --inc-dir")
	val_lib_dir    = cmd2("mecab-config --libs-only-L")
	val_lib        = cmd2("mecab-config --libs-only-l")
	val_scripts    = []
	val_data_files = [(val_mbtts_dir, ['userdic.txt'])]

if ps == "Windows" and sys.argv[1] == 'install':
	val_mbtts_dir  = os.path.join(os.environ['HOMEPATH'], val_folder )
	val_scripts    = []
	val_data_files = [(val_mbtts_dir, ['userdic.txt'])]

val_ext_modules = [
	Extension("mbtts._mecab_mbtts",
		["mecab_mbtts_wrap.cxx"],
		include_dirs = val_inc_dir,
		library_dirs = val_lib_dir,
		libraries    = val_lib ) ]

setup( name      = val_name,
	package_data = val_data,
	version      = val_version,
	summary      = val_summary,
	homepage     = val_homepage,
	author       = val_author,
	license      = val_license,
	scripts      = val_scripts,
	data_files   = val_data_files,
	description  = val_description,
	packages     = val_packages,
	ext_modules  = val_ext_modules )

if ps != "Windows":
	user = os.environ['USER']
	if user == 'root':
		user = os.environ['SUDO_USER']
	if user:
		os.system( 'chown -R ' + os.environ['SUDO_USER'] + ' ' + val_mbtts_dir )
