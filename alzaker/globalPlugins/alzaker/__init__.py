import api
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
import tones
from time import sleep
from scriptHandler import script
import addonHandler
addonHandler.initTranslation()

roleSECTION = "alzaker"
confspec = {
"type": "integer(default=0)",
"d": "integer(default=1)"}

config.conf.spec[roleSECTION] = confspec
path=os.path.join(os.path.abspath(os.path.dirname(__file__)), "ad")
zkr="None"
def allah ():
	global zkr
	while True:
		#Important note: if we put the while loop under the below condition, the loop starts if the reminder interval is not 0, but it'll continue running even if the value of the interval changes back to 0, thus; it results in the addon spamming with remembrances!
		# Returnes if the interval is set to 0. The reason for this was explained in the above line.
		if not config.conf[roleSECTION]["d"]: return
		sleep(config.conf[roleSECTION]["d"]*60)
		if config.conf[roleSECTION]["type"]==0:
			with open(path + "/text.txt","r",encoding="utf-8") as file:
				ass=choice(file.read().split("\n"))
				ui.message(ass)
				zkr=ass
		elif config.conf[roleSECTION]["type"]==1:
			nvwave.playWaveFile(os.path.join(path,"sounds",choice(os.listdir(path + "/sounds"))),1)
		else:
			with open(path + "/text.txt","r",encoding="utf-8") as file:
				ass=choice(file.read().split("\n"))
				NM(_("alzaker"),ass).Show(50)
				zkr=ass

t=Thread(target=allah, daemon=True)
t.start()
class CRSettingsPanel(SettingsPanel):
	title = _("alzaker")
	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.tlable = sHelper.addItem(wx.StaticText(self, label=_("select reminder type"), name="ts"))
		self.sou= sHelper.addItem(wx.Choice(self, name="ts"))
		self.tlable1 = sHelper.addItem(wx.StaticText(self, label=_("select interval between each remembrances buy minutes"), name="ts1"))
		self.sou1= sHelper.addItem(wx.SpinCtrl(self, name="ts1",min=0,max=500))
		self.sou.Set([_("by TTS"),_("by audio files"),_("as a windows Notification")])
		self.sou.SetSelection(config.conf[roleSECTION]["type"])
		self.sou1.SetValue(config.conf[roleSECTION]["d"])
		donate=sHelper.addItem(wx.Button(self,label=_("donate")))
		donate.Bind(wx.EVT_BUTTON,self.ondonate)
	def postInit(self):
		self.sou.SetFocus()
	def onSave(self):
		ShouldCall=False
		if config.conf[roleSECTION]["d"]==0 and self.sou1.Value>0:
			ShouldCall = True
		else:
			ShouldCall = False
		config.conf[roleSECTION]["type"]=self.sou.Selection
		config.conf[roleSECTION]["d"]=self.sou1.Value
		config.conf.save()
		if ShouldCall:
			t=Thread(target=allah, daemon=True)
			t.start()

	def ondonate(self,e):
		ui.message("please wait")
		web.open("https://www.paypal.me/ahmedthebest31")
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	NVDASettingsDialog.categoryClasses.append(CRSettingsPanel)
	scriptCategory= _("alzaker")
	@script(gesture="kb:NVDA+alt+z")
	def script_toggle(self,gesture):
		global zkr
		with open(path + "/text.txt","r",encoding="utf-8") as file:
			ass=choice(file.read().split("\n"))
			ui.message(ass)
			zkr=ass
	script_toggle.__doc__= _("say a random remembrances")


	@script(gesture="kb:NVDA+alt+x")
	def script_toggle1(self,gesture):
		if zkr is not "None":
			if api.copyToClip(zkr):
				ui.message(_("copied"))

		else:
			ui.message ("Could not find any previously generated remembrance to copy!")
	script_toggle1.__doc__= _("coppy it to  system clipboard")


	def terminate(self):
		NVDASettingsDialog.categoryClasses.remove(CRSettingsPanel)