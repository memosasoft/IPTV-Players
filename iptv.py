#!/usr/bin/python3

# Simple IPTV player for sources in m3u files
# TVOK. Version 0.6.0 (2019.12.18). By Oleg Kochkin. License GPL.



import sys, vlc, os
from PyQt5.QtWidgets import QApplication,QWidget,QMainWindow,QMenu,QAction,QLabel,QSystemTrayIcon, QFrame,QGridLayout,QBoxLayout
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSettings, Qt, pyqtSlot, QTimer
from PyQt5.QtDBus import QDBusConnection, QDBusMessage, QDBusInterface, QDBusReply, QDBus

# Create a custom "QProxyStyle" to enlarge the QMenu icons
#-----------------------------------------------------------
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MyProxyStyle(QProxyStyle):
    pass
    def pixelMetric(self, QStyle_PixelMetric, option=None, widget=None):

        if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
            return 30
        else:
            return QProxyStyle.pixelMetric(self, QStyle_PixelMetric, option, widget)


WINDOW_DECORATION_HEIGHT_TITLE = 25
WINDOW_DECORATION_WIDTH_BORDER = 4
VOLUME_CHANGE=5

# Get folder with script
scriptDir = os.path.dirname(os.path.realpath(__file__))
# Config file init 
cfg = QSettings('tvok','tvok')
# Load playlist
pl = []

# Request to get url that are updated
# save url to file in x.u3m format

try:
	list = sys.argv[1]
except:
	try:
		import requests

		print("Free IPTV 1.0 - Memosa Soft - free software")
		print("Please select a iptv channel list for viewing: ")
		print("_________________________________________________________________________")
		print("")
		print("1) UK - Public channels")
		print("2) USA - Public channels")
		print("3) Canada - Public channels")
		print("4) France - Public channels")
		print("5) International Movies - all languages mixed")
		print("6) French channels - all countries mixed")
		print("7) English channels - all countries  mixed")
		print("8) Quality channel list - all languages mixed")
		print("_________________________________________________________________________")

		interaction = input("Please select a list: ")
		interaction = int(interaction)	

		print("Some channel require a vpn...")
		print("Loading channels may take some time...")
		print("The script will also verify channel availability...")
		print("The start up process will take but all found channel will work...")
		print("Enjoy the free and legal TV")

		if interaction == 1 : url = 'https://iptv-org.github.io/iptv/countries/uk.m3u'
		if interaction == 2 : url = 'https://iptv-org.github.io/iptv/countries/us.m3u'
		if interaction == 3 : url = 'https://iptv-org.github.io/iptv/countries/ca.m3u'
		if interaction == 4 : url = 'https://iptv-org.github.io/iptv/countries/fr.m3u'
		if interaction == 5 : url = 'https://iptv-org.github.io/iptv/categories/movies.m3u'
		if interaction == 6 : url = 'https://iptv-org.github.io/iptv/languages/fra.m3u'
		if interaction == 7 : url = 'https://iptv-org.github.io/iptv/languages/eng.m3u'
		if interaction == 8 : url = 'https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8'
		
		#https://iptv-org.github.io/iptv/countries/uk.m3u
		#https://iptv-org.github.io/iptv/countries/us.m3u
		#https://iptv-org.github.io/iptv/countries/ca.m3u
		#https://iptv-org.github.io/iptv/countries/fr.m3u
		#https://iptv-org.github.io/iptv/categories/movies.m3u
		#https://iptv-org.github.io/iptv/languages/fra.m3u
		#https://iptv-org.github.io/iptv/languages/eng.m3u

		r = requests.get(url)

		with open('x.m3u', 'wb') as f:
			f.write(r.content)

		list = scriptDir+os.path.sep+'x.m3u'
	except:
		print("Run example:\n\ttvok.py ChannelsFile.m3u")
		exit(1)

f = open(list)
line = f.readline()

iCh = 0

while line:
	if "#EXTINF:" in line:
		ch = line.split(',')[1].strip()
		url = f.readline().strip()

		try:
		
			#r = requests.get(url, timeout=10)
			#if (r.status_code==200):

			print("Processing: " + url)
			img = line

			# get image
			start = img.find("tvg-logo=")
			start = start + 10
			end = img.find("png", start)
			img = img[start:end+3]
			png = ""

			try:

				if len(img) > 1:
					r = requests.get(img)
					
					png = img.split("/", -1)

					with open("./ch/" + png[len(png)-1], 'wb') as file:
						file.write(r.content)
					
					pl.append([ch,url,png[len(png)-1]])
					print("Found channel image...")
					print("Channels found " + str(iCh))
					iCh = iCh + 1	
				#else:
					# pl.append([ch,url,"x.png"])
					#print("Found channel image...")
					#print("Channels found " + str(iCh))

									
					
			except:
				print("ERROR - in getting png channel")
		except:
			print("ERROR - site unavailable")
			
	line = f.readline()
f.close()

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
	def createUI(self):
		self.home = os.getenv("HOME")
# vlc player init
#		self.instance = vlc.Instance('-q')
		self.instance = vlc.Instance('-q --network-caching=500')
		self.mediaplayer = self.instance.media_player_new()
#		self.mediaplayer.set_xwindow(self.winId())
# Main window settings    
		self.gridLayout = QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		self.videoFrame = QFrame(self)
		self.videoFrame.setObjectName("videoFrame")
		self.gridLayout.addWidget(self.videoFrame, 0, 0, 1, 1)
		self.mediaplayer.set_xwindow(self.winId())
#		self.mediaplayer.set_xwindow(self.videoFrame.winId())

		self.setWindowIcon(QIcon(scriptDir+os.path.sep+'pics'+os.path.sep+'logo.png'))
		self.resize(cfg.value('Width',456,type=int),cfg.value('Height',256,type=int))
		self.setGeometry(cfg.value('Left',456,type=int)+WINDOW_DECORATION_WIDTH_BORDER,
										cfg.value('Top',256,type=int)+WINDOW_DECORATION_HEIGHT_TITLE,
										cfg.value('Width',456,type=int),
										cfg.value('Height',256,type=int))
		pal = self.palette()
		pal.setColor(self.backgroundRole(), Qt.black)
		self.setPalette(pal)
#    self.setAutoFillBackground(True)
		self.currentCursor = self.cursor()
# Save status audio mute
		self.AudioMuteOnStart = self.mediaplayer.audio_get_mute()
		self.AudioVolumeOnStart = self.mediaplayer.audio_get_volume()
		self.Volume = cfg.value('Volume',80,type=int)

# Registered DBUS service
#		DBUSName = 'tv.ok'
#		DBUSConn = QDBusConnection.connectToBus(QDBusConnection.SessionBus, DBUSName)
#		DBUSConn.registerService(DBUSName)
#		DBUSConn.registerObject("/", self, QDBusConnection.ExportAllContents)
# Timer 1 second init. Once second call function t1secEvent
		self.t1sec = QTimer(self)
		self.t1sec.timeout.connect(self.t1secEvent)
		self.t1sec.start(1000)
# Select channel saved previous run
		self.chNum = cfg.value('Channel',1,type=int)
		self.chPrev = self.chNum + 1
		self.chChange()
		
		self.trayIcon = QSystemTrayIcon()
		self.trayIcon.setToolTip('MemosaSoft TV service')
		self.trayIcon.activated.connect(self.ToggleMute)
		self.swapIcon()

		self.selectChannel = ''
		self.tChSelect = QTimer(self)
		self.tChSelect.timeout.connect(self.tChSelectTimeout)
		
		self.label = QLabel(self)
		self.label.setText("<font color='white'>IPTV Memosa please wait loading the stream and thank you for using our IPTV service</font>")

	def osdView(self, mess):
		print("Calling internal function")
# Send OSD
# If DBUS daemon org.kochkin.okindd is running
#		dbus_interface = QDBusInterface("org.kochkin.okindd", "/Text")
#		if dbus_interface.isValid():
#			dbus_interface.call('printText', 'TV Memosa', mess, 5000)

	@pyqtSlot(int)
	def channelNum(self,digit):
		if (digit >= 0) and (digit <= 9):
			self.selectChannel = self.selectChannel+str(digit)
			if int(self.selectChannel) > len(pl): self.selectChannel = self.selectChannel[:-1]
			if int(self.selectChannel) < 1: self.selectChannel = self.selectChannel[:-1]
			self.osdView(self.selectChannel+': '+pl[int(self.selectChannel)-1][0])
			self.tChSelect.start(2000)

	@pyqtSlot()
	def tChSelectTimeout(self):
		self.tChSelect.stop()
		self.chNum = int (self.selectChannel)
		self.selectChannel = ''
		self.chChange()

	def swapIcon(self):
		menu = QMenu(self)
		picture = scriptDir+os.path.sep+'pics'+os.path.sep+'din-on.png'
		if not self.mute(): 
			picture = scriptDir+os.path.sep+'pics'+os.path.sep+'din-off.png'
		self.trayIcon.setIcon (QIcon (picture))
		self.trayIcon.setContextMenu(menu)
		self.trayIcon.show()

	@pyqtSlot(result=bool)
	def mute(self): return self.mediaplayer.audio_get_mute()

	@pyqtSlot(result=int)
	def GetChannelNum(self): return self.chNum

	@pyqtSlot(result=str)
	def GetChannel(self): return pl[self.chNum-1][0]

	@pyqtSlot(result=int)
	def GetVolume(self): return self.mediaplayer.audio_get_volume()

	@pyqtSlot()
	def VolumeIncrease(self):
		self.mediaplayer.audio_set_volume(self.mediaplayer.audio_get_volume()+VOLUME_CHANGE)
		cfg.setValue('Volume',self.mediaplayer.audio_get_volume())
	
	@pyqtSlot()
	def VolumeDecrease(self):
		self.mediaplayer.audio_set_volume(self.mediaplayer.audio_get_volume()-VOLUME_CHANGE)
		cfg.setValue('Volume',self.mediaplayer.audio_get_volume())

# Once second
	def t1secEvent(self):
		if self.isFullScreen(): self.setCursor (Qt.BlankCursor)

	@pyqtSlot()
	def ToggleMute(self):
		self.mediaplayer.audio_set_mute(not self.mediaplayer.audio_get_mute())
		self.swapIcon()

	@pyqtSlot()
	def ChannelNext(self):
		self.chNum += 1
		self.chChange()
		
	@pyqtSlot()
	def ChannelPrev(self):
		if (self.chNum-1>0):
			self.chNum -= 1
			self.chChange()

# On mouse wheel change    
	def wheelEvent(self,event):
		if event.angleDelta().y() > 0: self.ChannelNext()
		if event.angleDelta().y() < 0: self.ChannelPrev()

	@pyqtSlot()
	def ChannelRestart(self): self.chChange()

# Stop current channel and start chNum channel
	def chChange(self):
		if self.chNum != self.chPrev:
			if self.chNum > len(pl): self.chNum = 1
			if self.chNum < 1: self.chNum = len(pl)
			self.setWindowTitle(str(self.chNum)+'. '+pl[self.chNum-1][0])
			self.osdView(str(self.chNum)+': '+pl[self.chNum-1][0])
			self.mediaplayer.stop()

			self.media = self.instance.media_new(pl[self.chNum-1][1])
			self.mediaplayer.set_media(self.media)
			playerError = self.mediaplayer.play()
			if playerError != 0: sys.exit()
			cfg.setValue('Channel',self.chNum)
			cfg.setValue('Volume',self.mediaplayer.audio_get_volume())
			self.chPrev = self.chNum

# If double click mouse - toggle full screen    
	def mouseDoubleClickEvent(self,event): 
		self.ToggleFullScreen()
		
	@pyqtSlot()
	def ToggleFullScreen(self):
		if self.isFullScreen():
			self.showNormal()
			self.setCursor (self.currentCursor)
		else: 
			self.showFullScreen()
			self.setCursor (Qt.BlankCursor)


# Mouse pressed for context menu
	def contextMenuEvent(self, event):
		menu = QMenu(self)
		
# Fill channels
# Create a QT dialog boix to browse thrue the different channels
		index = 0
		for chs in pl:	
			action = menu.addAction(QIcon("./ch/" + chs[2]), chs[0])
			if index == self.chNum-1:
				menu.setActiveAction(action)
				print (index)
			index += 1
		
		menu.addSeparator()
		quitAction = menu.addAction(self.tr("Quit"))
		font = menu.font()
		font.setPointSize(12)
		menu.setFont(font)

		action = menu.exec_(self.mapToGlobal(event.pos()))
		if action: 
			value_index=1
			for value in pl:
				if value[0] == action.iconText():
					if self.chNum != value_index:
						self.chNum = value_index
						self.chChange()
					break
				else: value_index += 1
			if action == quitAction:
				self.close()

	def closeEvent(self, event):
		self.mediaplayer.stop()
		if not self.isFullScreen():
			cfg.setValue('Left',self.x())
			cfg.setValue('Top',self.y())
			cfg.setValue('Width',self.width())
			cfg.setValue('Height',self.height())
		cfg.setValue('Volume',self.mediaplayer.audio_get_volume())
		cfg.sync()
		self.mediaplayer.audio_set_mute(self.AudioMuteOnStart)
		self.mediaplayer.audio_set_volume(self.AudioVolumeOnStart)
		self.trayIcon.close()
		exit()
		
app = QApplication(sys.argv)

myStyle = MyProxyStyle('Fusion')    # The proxy style should be based on an existing style,
                                        # like 'Windows', 'Motif', 'Plastique', 'Fusion', 
app.setStyle(myStyle)

# app.setQuitOnLastWindowClosed(True)
tvok = MainWindow()
tvok.createUI()
tvok.show()
sys.exit(app.exec_())

