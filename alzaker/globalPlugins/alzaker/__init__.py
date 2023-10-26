"""
this file typed by mesteranas
email:anasformohammed@gmail.com
github:https://github.com/mesteranas/
thankyou ahmed samy (ahmedthebest) to give me sounds ,texts and type readme file
"""
from wx.adv import NotificationMessage as NM
import webbrowser as web
import os
import nvwave
from random import choice
from gui import SettingsPanel, NVDASettingsDialog,guiHelper
import config
import wx
import gui
import globalPluginHandler
import ui
from threading import Thread
from time import sleep
from winsound import PlaySound
from scriptHandler import script
import addonHandler
addonHandler.initTranslation()

roleSECTION = "alzaker"
confspec = {
"type": "integer(default=0)",
"d": "integer(default=1)"}

config.conf.spec[roleSECTION] = confspec
path=os.path.join(os.path.abspath(os.path.dirname(__file__)), "ad")
def allah ():
	if config.conf[roleSECTION]["d"] >0:
		while True:
			sleep(config.conf[roleSECTION]["d"]*60)
			if config.conf[roleSECTION]["type"]==0:
				with open(path + "/text.txt","r",encoding="utf-8") as file:
					ui.message(choice(file.read().split("\n")))
			elif config.conf[roleSECTION]["type"]==1:
				nvwave.playWaveFile(os.path.join(path,"sounds",choice(os.listdir(path + "/sounds"))),1)
			else:
				with open(path + "/text.txt","r",encoding="utf-8") as file:
					NM(_("alzaker"),choice(file.read().split("\n"))).Show(50)

t=Thread(target=allah)
t.start()
class CRSettingsPanel(SettingsPanel):
	title = _("alzaker")
	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.tlable = sHelper.addItem(wx.StaticText(self, label=_("type"), name="ts"))
		self.sou= sHelper.addItem(wx.Choice(self, name="ts"))
		self.tlable1 = sHelper.addItem(wx.StaticText(self, label=_("duration"), name="ts1"))
		self.sou1= sHelper.addItem(wx.SpinCtrl(self, name="ts1",min=0,max=500))
		self.sou.Set([_("speak"),_("sound"),_("Notification")])
		self.sou.SetSelection(config.conf[roleSECTION]["type"])
		self.sou1.SetValue(config.conf[roleSECTION]["d"])
		donate=sHelper.addItem(wx.Button(self,label=_("donate")))
		donate.Bind(wx.EVT_BUTTON,self.ondonate)
	def postInit(self):
		self.sou.SetFocus()
	def onSave(self):
		config.conf[roleSECTION]["type"]=self.sou.Selection
		config.conf[roleSECTION]["d"]=self.sou1.Value
	def ondonate(self,e):
		ui.message("please wait")
		web.open("https://www.paypal.me/ahmedthebest31")
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	NVDASettingsDialog.categoryClasses.append(CRSettingsPanel)
	scriptCategory= _("alzaker")
	@script(gesture="kb:NVDA+alt+z")
	def script_toggle(self,gesture):
		with open(path + "/text.txt","r",encoding="utf-8") as file:
			ui.message(choice(file.read().split("\n")))
	script_toggle.__doc__= _("view random 1")
	def terminate(self):
		NVDASettingsDialog.categoryClasses.remove(CRSettingsPanel)