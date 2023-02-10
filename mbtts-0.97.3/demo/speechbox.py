#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import sys
import time
import mbtts

class MyApp(wx.PySimpleApp):
	def OnInit(self):
		# TTS生成
		self.guide = mbtts.create('jp3')
		self.tts   = mbtts.create('jp2')

		# コントロール登録
		self.Frm = wx.Frame(None, -1, u'mbtts Speech BOX', size=(500, 400) )
		self.TxtCtr = wx.TextCtrl(self.Frm, -1,
				u'ここに文章を入力するか、貼り付けてください。', style=wx.TE_MULTILINE )
		self.Menu = wx.Menu()
		self.ID101 = wx.NewId()
		self.ID102 = wx.NewId()
		self.ID103 = wx.NewId()
		self.ID104 = wx.NewId()
		self.ID105 = wx.NewId()
		self.Menu.Append(self.ID101, u'読み上げる\tCtrl-E')
		self.Menu.Append(self.ID102, u'停止\tCtrl-S')
		self.Menu.Append(self.ID103, u'音声ファイルの作成\tCtrl-W')
		self.Menu.Append(self.ID104, u'テキストボックスのクリア\tCtrl-D')
		self.Menu.Append(self.ID105, u'終了(&X)')
		self.Menu.Enable(self.ID102, False )
		self.MenuBar = wx.MenuBar()
		self.MenuBar.Append(self.Menu, u'操作(&O)')
		self.Frm.SetMenuBar(self.MenuBar)

		# フォントの設定
		self.TxtCtr.SetFont(wx.Font(12, wx.NORMAL, wx.NORMAL, wx.NORMAL))

		# イベント登録
		self.Frm.Bind(wx.EVT_MENU, self.Say,    id=self.ID101)
		self.Frm.Bind(wx.EVT_MENU, self.Stop,   id=self.ID102)
		self.Frm.Bind(wx.EVT_MENU, self.Wave,   id=self.ID103)
		self.Frm.Bind(wx.EVT_MENU, self.Clear,  id=self.ID104)
		self.Frm.Bind(wx.EVT_MENU, self.Exit,   id=self.ID105)

		self.guide.speak(u'起動しました',0)
		self.Frm.Show()

		return 1


	def StartCallBack(self):
		self.Menu.SetLabel(self.ID101, u'一時停止\tCtrl-P')
		self.Frm.Bind(wx.EVT_MENU, self.Pause, id=self.ID101)
		self.Menu.Enable(self.ID102, True )
		return


	def FinishCallBack(self):
		self.Menu.Enable(self.ID102, False )
		self.Menu.SetLabel(self.ID101, u'読み上げる\tCtrl-E')
		self.Frm.Bind(wx.EVT_MENU, self.Say,  id=self.ID101)
		return

	def Say(self,event):
		txt = self.TxtCtr.GetValue()
		txt = txt.split('\n')
		for t in txt:
			self.tts.speak_with_callback(t,self.StartCallBack,self.FinishCallBack,0)

	def Stop(self,event):
		self.tts.stop()

	def Pause(self,event):
		self.Menu.SetLabel(self.ID101, u'再開\tCtrl-P')
		self.Frm.Bind(wx.EVT_MENU, self.Resume, id=self.ID101)
		self.tts.pause()

	def Resume(self,event):
		self.Menu.SetLabel(self.ID101, u'一時停止\tCtrl-P')
		self.Frm.Bind(wx.EVT_MENU, self.Pause, id=self.ID101)
		self.tts.resume()

	def Wave(self,event):
		self.tts.stop()
		txt = self.TxtCtr.GetValue()
		name = txt.replace('\n','')
		name = name[0:10]
		self.guide.speak(u'保存先の音声ファイルの名前と場所を指定してください。',0,0)
		dir = "./"
		dlg = wx.FileDialog(self.Frm, message=u"音声ファイルの作成",
			defaultDir=dir, defaultFile=name + u'.wav',
			wildcard = u"WAVファイル .wav |*.wav", style=wx.FD_SAVE)
		btn = dlg.ShowModal()
		filename = dlg.GetPath()
		if btn == wx.ID_OK:
			txt = txt.replace('\n',u'。。')
			self.tts.speak_to_file( txt, filename )
			self.guide.speak(u'音声ファイルの作成が完了しました')
		else:
			self.guide.speak(u'音声ファイルの作成はキャンセルされました',0)
		dlg.Destroy()

	def Clear(self,event):
		self.tts.stop()
		self.guide.speak(u'テキストボックスを消去しますか',0,0)
		Dlg = wx.MessageDialog(self.Frm, u'消去しますか？', u'消去確認',
			style = wx.OK | wx.CANCEL | wx.ICON_HAND)
		result = Dlg.ShowModal()
		if result == wx.ID_OK:
			self.guide.speak(u'それでは、消去します')
			self.TxtCtr.SetValue('')
		else:
			self.guide.speak(u'消去はキャンセルされました',0)

	def Exit(self,event):
		self.tts.stop()
		self.guide.speak(u'終了しますか？',0,0)
		Dlg = wx.MessageDialog(self.Frm, u'終了しますか？', u'終了確認',
			style = wx.OK | wx.CANCEL | wx.ICON_HAND)
		result = Dlg.ShowModal()
		if result == wx.ID_OK:
			self.guide.speak(u'それでは、さようなら')
			sys.exit()
		else:
			self.guide.speak(u'終了はキャンセルされました',0)

app = MyApp()
app.MainLoop()
