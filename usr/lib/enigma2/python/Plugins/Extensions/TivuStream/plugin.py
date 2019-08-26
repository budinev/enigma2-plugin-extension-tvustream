from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, getConfigListEntry, ConfigInteger, ConfigSelection, ConfigSubsection, ConfigYesNo, ConfigDirectory, configfile
from Components.config import *
from Components.ConfigList import *
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText#, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap, MultiPixmap#, MovingPixmap
from Components.ScrollLabel import ScrollLabel
from Components.SelectionList import SelectionList#, SelectionEntryComponent
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ServiceList import ServiceList
from Components.Sources.List import List
from Components.Sources.Source import Source
from Components.Sources.StaticText import StaticText
from Components.Sources.Progress import Progress
from Tools.Downloader import downloadWithProgress
from ServiceReference import ServiceReference
from enigma import *
from os import environ as os_environ
from os import path, listdir, remove, mkdir, chmod, sys, rename, system
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
import Components.PluginComponent
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.InfoBar import MoviePlayer, InfoBar
from Screens.InfoBarGenerics import *
from Screens.InputBox import InputBox
from Screens.LocationBox import LocationBox
from Screens.PluginBrowser import PluginBrowser
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop, Standby
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import resolveFilename, fileExists, copyfile, pathExists
from Tools.Directories import SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from twisted.web.client import downloadPage, getPage, error
from xml.dom import Node, minidom
import base64
import os, re, glob
import shutil
import time
from Components.Console import Console as iConsole
from urllib import urlencode, quote
from urllib2 import urlopen, Request, URLError, HTTPError 
from urlparse import urlparse
import StringIO
import httplib
import urllib
import urllib2
import cookielib


currversion = '1.8'
Version = ' 1.8 - 25.08.2019'
Crediti = ' Buio2005,Furlan,Lanus'
Maintainer2 = ' @Lululla'
#
plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/TivuStream/'
service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
dir_enigma2 = '/etc/enigma2/'

addFont(plugin_path + 'res/fonts/verdana_r.ttf', 'OpenFont1', 100, 1)
addFont(plugin_path + 'res/fonts/showg.ttf', 'OpenFont2', 100, 1)

#brand
BRAND = '/usr/lib/enigma2/python/boxbranding.so'
BRANDP = '/usr/lib/enigma2/python/Plugins/PLi/__init__.pyo'
BRANDPLI ='/usr/lib/enigma2/python/Tools/StbHardware.pyo'

def checkInternet():
    try:
        response = urllib2.urlopen("http://google.com", None, 5)
        response.close()
    except urllib2.HTTPError:
        return False
    except urllib2.URLError:
        return False
    except socket.timeout:
        return False
    else:
        return True
#
def ReloadBouquet():
    eDVBDB.getInstance().reloadServicelist()
    eDVBDB.getInstance().reloadBouquets() 

def OnclearMem():
        system("sync")
        system("echo 3 > /proc/sys/vm/drop_caches")
        
# def mountm3uf():
    # pthm3uf = []

    # if os.path.isfile('/proc/mounts'):
        # for line in open('/proc/mounts'):
            # if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
                # drive = line.split()[1].replace('\\040', ' ') + '/'
                # if drive== "/media/hdd/" :
                    # if not os.path.exists('/media/hdd/movie'):
                        # system('mkdir /media/hdd/movie')
                # if drive== "/media/usb/" :
                    # if not os.path.exists('/media/usb/movie'):
                        # system('mkdir /media/usb/movie')  
                # if drive== "/omb/" :
                    # drive = drive.replace('/media/omb/', '/media/omb/')
                    # if not os.path.exists('/media/omb/movie'):
                        # system('mkdir /media/omb/movie')                     
                # if drive== "/media/ba/" :
                    # drive = drive.replace('/media/ba/', '/media/ba/')   
                    # if not os.path.exists('/media/ba/movie'):
                        # system('mkdir /media/ba/movie')                      
                # if not drive in pthm3uf: 
                      # pthm3uf.append(drive)
    # pthm3uf.append('/tmp/')
    # return pthm3uf   

def isExtEplayer3Available():
    return os.path.isfile(eEnv.resolve('$bindir/exteplayer3'))   

def isStreamlinkAvailable():
    return os.path.isdir(eEnv.resolve('/usr/lib/python2.7/site-packages/streamlink'))  

    
if path.exists('/usr/lib/python2.7/site-packages/streamlink'):
    if fileExists('/usr/lib/python2.7/site-packages/streamlink/plugin/plugin.pyo'):
        streamlink = True
    else:
        streamlink = False
else:
    streamlink = False
    
sessions = []
config.plugins.TivuStream = ConfigSubsection()
config.plugins.TivuStream.server = ConfigSelection(default='PATBUWEB', choices=['PATBUWEB', 'CORVOBOYS'])
config.plugins.TivuStream.code = ConfigInteger(limits=(0, 9999), default=1234)
config.plugins.TivuStream.autoupd = ConfigYesNo(default=True)
config.plugins.TivuStream.bouquettop = ConfigSelection(default='Bottom', choices=['Bottom', 'Top'])
# config.plugins.TivuStream.pthm3uf = ConfigSelection(choices=mountm3uf())
config.plugins.TivuStream.pthm3uf = ConfigDirectory(default='/media/usb/movie')

if streamlink == True:
    if os.path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp') and isExtEplayer3Available():
        config.plugins.TivuStream.services = ConfigSelection(choices=['Gstreamer', 'Exteplayer3', 'StreamLink'])  
    else:
        config.plugins.TivuStream.services = ConfigSelection(default='Gstreamer', choices=['Gstreamer', 'StreamLink'])          

if streamlink == False:
    if os.path.exists ('/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp') and isExtEplayer3Available():
        config.plugins.TivuStream.services = ConfigSelection(default='Gstreamer', choices=['Gstreamer', 'Exteplayer3'])
    else: 
        config.plugins.TivuStream.services = ConfigSelection(default='Gstreamer', choices=[('Gstreamer')])
    
config.plugins.TivuStream.strtext = ConfigYesNo(default=True)
config.plugins.TivuStream.strtmain = ConfigYesNo(default=True)


def server_ref():
    global server, host, TXT_PUKPRG, upd_fr_txt, nt_upd_lnk, pnd_m3u, pnd_m3ulnk #, picon_ipk_usb, picon_ipk_hdd, picon_ipk_flash
    server = ''
    host = ''
    TEST1 = 'aHR0cDovL3BhdGJ1d2ViLmNvbQ==' #SERVER1- PATBUWEB
    ServerS1 = base64.b64decode(TEST1)
    data_s1 = 'L2lwdHYv'  # /iptv/
    FTP_1 = base64.b64decode(data_s1)

    TEST2 = 'aHR0cDovL2NvcnZvbmUuYWx0ZXJ2aXN0YS5vcmc=' #SERVER2 - CORVOBOYS
    ServerS2 = base64.b64decode(TEST2)
    data_s2 = 'L2lwdHYv' #/corvoboys.com/iptv/
    FTP_2 = base64.b64decode(data_s2)

    if config.plugins.TivuStream.server.value == 'PATBUWEB' :
        host = ServerS1
        print host
        server = ServerS1 + FTP_1
        print server
    else:
        host = ServerS2
        print host
        server = ServerS2 + FTP_2
        print server
    TXT_PUKPRG = ('%splugin/pinprogress.txt' % server)
    upd_fr_txt = ('%splugin/update.txt' % server) # fa anche il check delle liste ->verhurl
    nt_upd_lnk = ('wget %se2liste/note.txt -O /tmp/note.txt > /dev/null' % server) #e2liste/note.txt
    pnd_m3u = ('%se2liste/tivustream.m3u' % server)   #e2liste/tivustream.m3u
    pnd_m3ulnk = ('wget %se2liste/tivustream.m3u -O ' % server)   #e2liste/tivustream.m3u
    return server, host, TXT_PUKPRG, upd_fr_txt, nt_upd_lnk, pnd_m3u, pnd_m3ulnk#, picon_ipk_usb, picon_ipk_hdd, picon_ipk_flash
server_ref()


#locale
# -*- coding: utf-8 -*-
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
PluginLanguageDomain = 'TivuStream'
PluginLanguagePath = plugin_path + 'res/locale'
def localeInit():
    lang = language.getLanguage()[:2]
    os.environ['LANGUAGE'] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)
    gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE, ''))

def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.dgettext('enigma2', txt)
    return t

localeInit()
language.addCallback(localeInit)
################################




# SCREEN PATH SETTING
DESKHEIGHT = getDesktop(0).size().height()
SKIN_PATH = plugin_path
HD = getDesktop(0).size()

if HD.width() > 1280:
   SKIN_PATH = plugin_path + 'res/FullHD'
   
else:
   SKIN_PATH = plugin_path + 'res/HD'



def m3ulistEntry(download):
    res = [download]
    white = 16777215
    yellow = 16776960
    green = 3828297
    col = 16777215
    backcol = 0
    blue = 4282611429
    # res.append(MultiContentEntryText(pos=(0, 0), size=(1000, 40), text=download, color=col, color_sel=green, backcolor=backcol, backcolor_sel=yellow))
    # res.append(MultiContentEntryText(pos=(0, 0), size=(1000, 40), text=download, color=blue, color_sel=yellow))    
    # res.append(MultiContentEntryText(pos=(0, 0), size=(1000, 40), text=download, color=blue, color_sel=yellow, backcolor_sel=blue))    
    res.append(MultiContentEntryText(pos=(0, 0), size=(1000, 50), text=download))    
    return res

def m3ulist(data, list):
    icount = 0
    mlist = []
    for line in data:
        name = data[icount]
        mlist.append(m3ulistEntry(name))
        icount = icount + 1
    list.setList(mlist)

    
class ListMenu(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if DESKHEIGHT > 1000:
            self.l.setItemHeight(50)
            textfont = int(40)
            self.l.setFont(0, gFont('OpenFont2', textfont))
        else:
            self.l.setItemHeight(30)
            textfont = int(22)
            self.l.setFont(0, gFont('OpenFont2', textfont))
   
def remove_line(filename, what):
    if os.path.isfile(filename):
        file_read = open(filename).readlines()
        file_write = open(filename, 'w')
        for line in file_read:
            if what not in line:
                file_write.write(line)
        file_write.close()

#about
URL = ('%se2liste/note.txt'% server)
# def DownloadInfo(url):
    # text = ""
    # try:
        # req = urllib2.Request(url)
        # response = urllib2.urlopen(req)
        # link = response.read().decode("windows-1252")
        # response.close()
        # text = link.encode("utf-8")
    # except:
        # print"ERROR Download History %s" %(url)
    # return text    
    
def DownloadInfo(url):
        print "Here in getUrl url =", url
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link        
    
# class ABOUT(Screen):

    # def __init__(self, session):
        # self.session = session
        # skin = SKIN_PATH + '/ABOUT.xml'
        # f = open(skin, 'r')
        # self.skin = f.read()
        # f.close()          
        # Screen.__init__(self, session)
        # self['title'] = Label(_('..:: TiVuStream About ::..'))
        # self['key_red'] = Label(_('Esci'))
        # self['key_green'] = Label(_('Config'))
        # self['key_yellow'] = Label(_('Open List'))
        # self['key_blue'] = Label(_('Player'))
        # self['Maintainer'] = Label(_('Maintainer'))
        # self['Maintainer2'] = Label('%s' % Maintainer2)
        # self['infoc'] = Label(_('Crediti'))        
        # self['infoc2'] = Label('%s' % Crediti)        
        # # self['status'] = Label()
        # # self['progress'] = Progress()
        # # self['progresstext'] = StaticText()
        # info2 = ''
        # # self['text'] = ScrollLabel()
        # # self.downloading = False
        # self['actions'] = ActionMap(['OkCancelActions',
         # 'MenuActions',
         # 'SetupActions'
         # 'DirectionActions',
         # 'ColorActions',
         # 'WizardActions',
         # 'NumberActions',
         # 'EPGSelectActions'], {'ok': self.close,
         # 'cancel': self.close,
         # 'back': self.close,
         # 'red': self.close,
         # # 'up': self['text'].pageUp,
         # # 'down': self['text'].pageDown,
         # # 'left': self['text'].pageUp,
         # # 'right': self['text'].pageDown,
         # 'yellow': self.lista,
         # 'blue': self.M3uPlay,
         # 'menu': self.scsetup,
         # 'green': self.scsetup}, -1)
        # # self.checkCfg()


    # def M3uPlay(self):
        # self.session.open(OpenM3u)
                
    # # def checkCfg(self):
        # # server_ref()
        
        # # self.icount = 0
        # # self['text'].setText(_('Check Connection wait please...'))
        # # self.timer = eTimer()
        # # try:
            # # self.timer.callback.append(self.OpenCheck)
        # # except:
            # # self.timer_conn = self.timer.timeout.connect(self.OpenCheck)
        # # self.timer.start(100, 1)        
            
    # # def OpenCheck(self):
        # # url3 = upd_fr_txt
        # # print 'url3:', url3
        # # getPage(url3).addCallback(self.ConnOK).addErrback(self.ConnNOK)
        
    # # def ConnOK(self, data):
        # # try:
            # # self['text'].setText(DownloadInfo(URL))
        # # except:
            # # self['text'].setText(_('Errore nel download degli aggiornamenti') + ' !')
            # # print"ERROR Download History %s" %(url)
            
    # # def ConnNOK(self, error):
        # # self['text'].setText(_('Server Off') + ' !' + '\ncontrolla SERVER in config')  
        
    # def lista(self):
        # self.session.open(OpenScript)

    # def scsetup(self):
        # self.session.open(OpenConfig)
        # # self.onShown.append(self.checkCfg)
        
        
class OpenScript(Screen):
    def __init__(self, session):
        self.session = session
        
        if fileExists(BRAND) or fileExists(BRANDP):
            skin = SKIN_PATH + '/OpenScriptOpen.xml'
        else:
            skin = SKIN_PATH + '/OpenScript.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()         
        Screen.__init__(self, session)
        self.list = []
        self['list'] = MenuList([])

        self.icount = 0
        server_ref()        #ok
        global pin       
        pin = 2808

        if int(pin) == config.plugins.TivuStream.code.value :        
            self.list = []
            self.list.append("FREE_ALL")
            self.list.append("ITALIA")
            self.list.append("FICTION")   			
            self.list.append("INTERNATIONAL")                
            self.list.append("MEDIAPLAY")                
            self.list.append("SPORT")
            self.list.append("STREAMLINK")                 
            self.list.append("MUSIC")
            self.list.append("RADIO")
            self.list.append("ADULTXXX")
            self['list'] = MenuList(self.list)
        else:
            self.list = []     
            self.list.append("FREE_ALL")
            self.list.append("ITALIA")
            self.list.append("FICTION")  			
            self.list.append("INTERNATIONAL")                  
            self.list.append("MEDIAPLAY")                   
            self.list.append("SPORT")
            self.list.append("STREAMLINK")                  
            self.list.append("MUSIC")
            self.list.append("RADIO")
            self['list'] = MenuList(self.list)
            
        self['title'] = Label(_('..:: TiVuStream List V. %s  by Lululla ::..' % Version))
        self['Maintainer'] = Label(_('Maintainer'))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['infoc'] = Label(_('Crediti'))        
        self['infoc2'] = Label('%s' % Crediti) 
        self['key_red'] = Label(_('Esci'))
        self['key_green'] = Label(_('Ricarica Bouquet'))
        self['key_yellow'] = Label(_('Elimina'))
        self['key_blue'] = Label(_('Player'))
        self['key_menu'] = Label(_('Menu'))  
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'], 
        
         {'ok': self.messagerun,
         'menu': self.scsetup,         
         'red': self.close,
         'green': self.messagereload,
         'info': self.close,
         'yellow': self.messagedellist,
         'blue': self.M3uPlay,
         'back': self.close,
         'cancel': self.close}, -1)  
        # self.onShown.append(self.checkCfg)
         
    def scsetup(self):
        self.session.open(OpenConfig)

    # def readpin(self):
        # try:
            # getPage(TXT_PUKPRG).addCallback(self.gotUpdateInfo).addErrback(self.gotError)

        # except Exception as error:
            # print str(error)

    # def gotUpdateInfo(self, html):
        # tmp_infolines = html.splitlines()
        # puk = tmp_infolines[0]
        # pin = base64.b64decode(puk)
        
    # def gotError(self, error = ''):
        # pass
         
    # def Ver_URL(self, url):
        # req = urllib2.Request(url)
        # try:
            # response = urllib2.urlopen(req)
            # the_page = response.read()
            # print the_page 
            # verifica = True
            
        # except urllib2.HTTPError as e:
            # print e.code
            # the_page = '%s' % e.code
            # verifica = False
            
        # except urllib2.URLError as e:
            # print 'We failed to reach a server.'
            # print 'Reason: ', e.reason
            # the_page = '%s' % e.reason
            # verifica = False
        # return verifica

        
    def run(self, result):
            if result:
                returnValue = self["list"].l.getCurrentSelection()#[1]
                if returnValue is not None:
                        if returnValue is "FREE_ALL":
                                name = 'tivustream_free_all'
                                self.instal_listTv(name)
                        elif returnValue is "ITALIA":
                                name = 'tivustream_italia'
                                self.instal_listTv(name)
                        elif returnValue is "FICTION":
                                name = 'tivustream_fiction'
                                self.instal_listTv(name)                                
                        elif returnValue is "INTERNATIONAL":
                                name = 'tivustream_internat'
                                self.instal_listTv(name)                                   
                        elif returnValue is "MEDIAPLAY":
                                name = 'tivustream_mediaplay'
                                self.instal_listTv(name)                                
                        elif returnValue is "SPORT":
                                name = 'tivustream_sport'                    
                                self.instal_listTv(name)
                        elif returnValue is "STREAMLINK":
                                name = 'tivustream_streamlink'                    
                                self.instal_listTv(name)
                        elif returnValue is "MUSIC":
                                name = 'tivustream_musica'                    
                                self.instal_listTv(name)
                        elif returnValue is "RADIO":
                                name = 'tivustream_radio'                    
                                self.instal_listTv(name)
                        elif returnValue is "ADULTXXX":
                                name = 'tivustream_adultxxx'                    
                                self.instal_listTv(name)
                        elif returnValue.startswith("="):
                                name = '=='
                                self.instal_listTv(name)
                else:
                    self.mbox = self.session.open(openMessageBox, _('Bouquet non Installato'), openMessageBox.TYPE_ERROR, timeout=4)    
                    return
            else:
                return 
                       
    def instal_listTv(self, name):
            name = name
            groupname = 'userbouquet.tivustream.tv'  			
            bouquet = 'bouquets.tv' 										  
            if name == 'tivustream_radio' :
                bqtname = 'subbouquet.%s.radio' % name
                number = '2'
            else:    
                bqtname = 'subbouquet.%s.tv' % name
                number = '1'
                
            in_bouquets = 0
            linetv =0							
            if os.path.isfile('/etc/enigma2/%s' % bqtname):
                os.remove('/etc/enigma2/%s' % bqtname)
            
            #######
            cmd = ('wget %se2liste/%s -O /etc/enigma2/%s > /dev/null' % (server, bqtname, bqtname))
            print "cmd = ", cmd
            os.system(cmd)
          
            if not os.path.isfile('/etc/enigma2/userbouquet.tivustream.tv'): # % groupname) :
                # cmd = ('wget %se2liste/userbouquet.tivustream.tv -O /etc/enigma2/userbouquet.tivustream.tv > /dev/null' ) #% (server, groupname, groupname))
                # print "cmd = ", cmd
                # os.system(cmd)  
                filename = '/etc/enigma2/userbouquet.tivustream.tv'
                with open(filename, 'a+') as f:
                    nameString = "#NAME tivustream.com"
                    if nameString not in f:
                        f.write(nameString + '\r\n')
				
            os.system('chmod 0644 /etc/enigma2/userbouquet.tivustream.tv' )

            self.mbox = self.session.open(openMessageBox, _('Controlla nella lista favoriti ...'), openMessageBox.TYPE_INFO, timeout=5)

            with open('/etc/enigma2/bouquets.tv', 'a+') as f:
                bouquetTvString = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + groupname +  '" ORDER BY bouquet\n'
                if bouquetTvString not in f:

                    new_bouquet = open('/etc/enigma2/new_bouquets.tv', 'w')
                    file_read = open('/etc/enigma2/%s' % bouquet).readlines()                          
                    if config.plugins.TivuStream.bouquettop.value == 'Top': 
                        #top  
                        new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + groupname +  '" ORDER BY bouquet\n') #% (number, bqtname))   
                        for line in file_read:
                            new_bouquet.write(line)
                        new_bouquet.close()
                    if config.plugins.TivuStream.bouquettop.value == 'Bottom':
                        for line in file_read:
                            new_bouquet.write(line)
                        #bottom
                        new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + groupname +  '" ORDER BY bouquet\n') # % (number, bqtname))                            
                        new_bouquet.close()
                    os.system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
                    os.system('mv -f /etc/enigma2/new_bouquets.tv /etc/enigma2/bouquets.tv')
                    os.system('chmod 0644 /etc/enigma2/%s' %groupname )

            for line in open('/etc/enigma2/%s' % groupname):
                if bqtname in line:
                    linetv = 1
                else:
                    with open('/etc/enigma2/userbouquet.tivustream.tv', 'a+' ) as f:
                        bouquetTvString = ('#SERVICE 1:7:%s:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % (number, bqtname)) 
                        if bouquetTvString not in f:
                            f.write(bouquetTvString)                        
                        
            self.mbox = self.session.open(openMessageBox, _('Riordino liste Favorite in Corso') + '\n' + _('Attendere prego ...'), openMessageBox.TYPE_INFO, timeout=5)
            eDVBDB.getInstance().reloadServicelist()
            eDVBDB.getInstance().reloadBouquets() 
            return
         
####  
    def messagerun(self):
        returnValue = self["list"].l.getCurrentSelection()#[1]
        if returnValue is None or returnValue.startswith("=="):
            self.mbox = self.session.open(openMessageBox, _('ERRORE CONNESSIONE O UNKNOW'), openMessageBox.TYPE_ERROR, timeout=4) 
        elif returnValue.startswith("STREAMLINK") and not isStreamlinkAvailable(): 
            self.mbox = self.session.open(openMessageBox, _('StreamLink non Installato!!!\n\nInstallare prima'), openMessageBox.TYPE_INFO, timeout=9)    
        else:
            self.session.openWithCallback(self.messagerun2, openMessageBox, _('Installare lista %s selezionata' % returnValue), openMessageBox.TYPE_YESNO)

    def messagerun2(self, result):
        if result:
            self.session.openWithCallback(self.run, openMessageBox, _('Installazione in Corso') + '\n' + _('Attendere prego ...'), openMessageBox.TYPE_INFO, timeout=3)    
        
    def messagereload(self):
        self.session.openWithCallback(self.reloadSettings, openMessageBox, _('Riordino liste Favorite in Corso') + '\n' + _('Attendere prego ...'), openMessageBox.TYPE_INFO, timeout=3)

    def reloadSettings(self, result):
        if result:
            ReloadBouquet()

    def messagedellist(self):
        self.session.openWithCallback(self.deletelist, openMessageBox, _('ATTENZIONE') + ':\n' + _('Eliminare le liste canali TiVuStream') + ' ?', openMessageBox.TYPE_YESNO)

        
    def deletelist(self, result):
        if result:
            for file in os.listdir('/etc/enigma2/'):
                if file.startswith('userbouquet.tivustream') or file.startswith('subbouquet.tivustream'):
                    file = '/etc/enigma2/' + file
                    if os.path.exists(file):
                        print 'permantly remove file ', file
                        os.remove(file)
                        system("sed -i '/userbouquet.tivustream/d' /etc/enigma2/bouquets.tv")

                    radio = '/etc/enigma2/userbouquet.tivustream_radio.radio'
                    if os.path.exists(radio):
                        print 'permantly remove file ', radio
                        os.remove(radio)
                        system("sed -i '/userbouquet.tivustream/d' /etc/enigma2/bouquets.radio")
            self.reloadSettings2()          

    def reloadSettings2(self):
        ReloadBouquet()
        self.mbox = self.session.open(openMessageBox, _('Liste canali TiVuStream eliminate con successo'), openMessageBox.TYPE_INFO, timeout=4)

    def M3uPlay(self):
        self.session.open(OpenM3u)
        
        
##########################################################        
class OpenM3u(Screen):
    def __init__(self, session):
        self.session = session
        skin = SKIN_PATH + '/OpenM3u.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()           
        Screen.__init__(self, session)
        self.list = []
        self['list'] = ListMenu([])
        global srefInit
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        srefInit = self.initialservice
        self['title'] = Label(_('..:: TiVuStream List V. %s  by Lululla ::..' % Version))
        self['Maintainer'] = Label(_('Maintainer'))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['infoc'] = Label(_('Crediti'))        
        self['infoc2'] = Label('%s' % Crediti) 
        self['info'] = Label()
        pthm3uf = config.plugins.TivuStream.pthm3uf.value #+ '/' + 'movie' 
        self['path'] = Label(_('Percorso cartella %s') % pthm3uf)
        self['key_red'] = Label(_('Esci'))
        self['key_green'] = Label(_('Converti StreamLink'))        
        self['key_blue'] = Label(_('Converti ExtePlayer3'))
        self['key_yellow'] = Label(_('Converti Gstreamer'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'MenuActions', 'TimerEditActions'], 
        {
         # 'red': self.message1,
         'green': self.crea_bouquetstreamlink,
         'blue': self.crea_bouquet5002,
         'yellow': self.crea_bouquet,
         'cancel': self.cancel,
         'ok': self.runList}, -2)
        self.convert = False

        try:

            if not path.exists(config.plugins.TivuStream.pthm3uf.value +  '/tivustream.m3u'):
                cmd15 = pnd_m3ulnk + config.plugins.TivuStream.pthm3uf.value + '/tivustream.m3u > /dev/null'
                system(cmd15)
            else:
                cmd66 = 'rm -f ' + config.plugins.TivuStream.pthm3uf.value +  '/tivustream.m3u'
                system(cmd66)
                cmd15 = pnd_m3ulnk + config.plugins.TivuStream.pthm3uf.value + '/tivustream.m3u > /dev/null'
                system(cmd15)        
        
        except Exception as ex:
            print ex
            print 'ex download m3u player'      

        self['info'].setText(_('OK') + '\n' + _('Apri Selezione'))
        self.name = config.plugins.TivuStream.pthm3uf.value + '/' #'movie/' #name
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openList)

        
    def scsetup(self):
        self.session.openWithCallback(self.close, OpenConfig)
        
    def openList(self):
        self.names = []
        self.Movies = []
        path = self.name
        # AA = ['.mkv','.mp4','.avi','.m3u']
        AA = ['.m3u']        
        for root, dirs, files in os.walk(path):
            for name in files:
                for x in AA:
                    if not x in name:
                        continue
                    self.names.append(name)
                    self.Movies.append(root +'/'+name)
        pass
        m3ulist(self.names, self['list'])
		
    def runList(self):
        idx = self['list'].getSelectionIndex()
        path = self.Movies[idx]
        if idx == -1 or None:
            return
        else:
            name = path
            if '.m3u' in name : 
                self.session.open(M3uPlay, name)
                return
            else:
                return
				
    def message1(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            self.session.openWithCallback(self.callMyMsg1,openMessageBox,_("Vuoi rimuovere?"), openMessageBox.TYPE_YESNO)       

    def callMyMsg1(self, result):
        if result:
            idx = self['list'].getSelectionIndex()
            path = self.Movies[idx]
            dom = path
            if fileExists(dom):
                os.remove(dom)
            self.session.open(openMessageBox, dom +'   has been successfully deleted\nwait time to refresh the list...', openMessageBox.TYPE_INFO, timeout=5)

            del self.Movies[idx]
            del self.names[idx]
            self.onShown.append(self.openList)


                
    def crea_bouquet(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            self.create_bouquet()
            return

            
    def crea_bouquet5002(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            self.create_bouquet5002()
            return

    def crea_bouquetstreamlink(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            self.create_bouquetstreamlink()
            return
            
#SERVICE 5002:0:1:1:0:0:0:0:0:0:          
#SERVICE 5002:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/            
    def create_bouquetstreamlink(self):
            idx = self['list'].getSelectionIndex()
            self.convert = True
            name = self.names[idx]
            pth = self.name
            bqtname = 'userbouquet.%s.tv' % name
            self['info'] = StaticText()
            self.iConsole = iConsole()
            self['info'].text = _('Converting %s' % name)
            desk_tmp = hls_opt = ''
            in_bouquets = 0
            if os.path.isfile('/etc/enigma2/%s' % bqtname):
                os.remove('/etc/enigma2/%s' % bqtname)
            with open('/etc/enigma2/%s' % bqtname, 'w') as outfile:
                outfile.write('#NAME %s\r\n' % name.capitalize())
                for line in open(pth + '/%s' % name):
                    if line.startswith('http://') or line.startswith('https'):
                        eres ='http://127.0.0.1:8088'
                        outfile.write('#SERVICE 5002:0:1:0:0:0:0:0:0:0:%s/%s' % (eres.replace(':', '%3a'),line.replace(':', '%3a')))
                        outfile.write('#DESCRIPTION %s' % desk_tmp)
                    elif line.startswith('#EXTINF'):
                        desk_tmp = '%s' % line.split(',')[-1]
                    elif '<stream_url><![CDATA' in line:
                        eres ='http://127.0.0.1:8088'
                        outfile.write('#SERVICE 5002:0:1:0:0:0:0:0:0:0:%s/%s\r\n' % (eres.replace(':', '%3a'),line.split('[')[-1].split(']')[0].replace(':', '%3a')))
                        outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                    elif '<title>' in line:
                        if '<![CDATA[' in line:
                            desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                        else:
                            desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
                outfile.close()
            self['info'].setText(_('TiVuStream M3U:') + _('Apri Selezione'))
            self.mbox = self.session.open(openMessageBox, _('Controlla nella lista favoriti ...'), openMessageBox.TYPE_INFO, timeout=5)
            if os.path.isfile('/etc/enigma2/bouquets.tv'):
                for line in open('/etc/enigma2/bouquets.tv'):
                    if bqtname in line:
                        in_bouquets = 1

                if in_bouquets is 0:
                    if os.path.isfile('/etc/enigma2/%s' % bqtname) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                        remove_line('/etc/enigma2/bouquets.tv', bqtname)
                        with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                            outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % bqtname)
                            outfile.close()
            self.mbox = self.session.open(openMessageBox, _('Riordino liste Favorite in Corso') + '\n' + _('Attendere prego ...'), openMessageBox.TYPE_INFO, timeout=5)
            ReloadBouquet()
                            
    def create_bouquet5002(self):
            idx = self['list'].getSelectionIndex()
            self.convert = True
            name = self.names[idx]
            pth = self.name
            bqtname = 'userbouquet.%s.tv' % name
            self['info'] = StaticText()
            self.iConsole = iConsole()
            self['info'].text = _('Converting %s' % name)
            desk_tmp = hls_opt = ''
            in_bouquets = 0
            if os.path.isfile('/etc/enigma2/%s' % bqtname):
                os.remove('/etc/enigma2/%s' % bqtname)
            with open('/etc/enigma2/%s' % bqtname, 'w') as outfile:
                outfile.write('#NAME %s\r\n' % name.capitalize())
                for line in open(pth + '/%s' % name):
                    if line.startswith('http://') or line.startswith('https'):
                        outfile.write('#SERVICE 5002:0:1:1:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s' % desk_tmp)
                    elif line.startswith('#EXTINF'):
                        desk_tmp = '%s' % line.split(',')[-1]
                    elif '<stream_url><![CDATA' in line:
                        outfile.write('#SERVICE 5002:0:1:1:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                    elif '<title>' in line:
                        if '<![CDATA[' in line:
                            desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                        else:
                            desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
                outfile.close()
            self['info'].setText(_('TiVuStream M3U:') + _('Apri Selezione'))
            self.mbox = self.session.open(openMessageBox, _('Controlla nella lista favoriti ...'), openMessageBox.TYPE_INFO, timeout=5)
            if os.path.isfile('/etc/enigma2/bouquets.tv'):
                for line in open('/etc/enigma2/bouquets.tv'):
                    if bqtname in line:
                        in_bouquets = 1

                if in_bouquets is 0:
                    if os.path.isfile('/etc/enigma2/%s' % bqtname) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                        remove_line('/etc/enigma2/bouquets.tv', bqtname)
                        with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                            outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % bqtname)
                            outfile.close()
            self.mbox = self.session.open(openMessageBox, _('Riordino liste Favorite in Corso') + '\n' + _('Attendere prego ...'), openMessageBox.TYPE_INFO, timeout=5)
            ReloadBouquet()
            
    def create_bouquet(self):
            idx = self['list'].getSelectionIndex()
            self.convert = True
            name = self.names[idx]
            pth = self.name
            bqtname = 'userbouquet.%s.tv' % name
            self['info'] = StaticText()
            self.iConsole = iConsole()
            self['info'].text = _('Converting %s' % name)
            desk_tmp = hls_opt = ''
            in_bouquets = 0
            if os.path.isfile('/etc/enigma2/%s' % bqtname):
                os.remove('/etc/enigma2/%s' % bqtname)
            with open('/etc/enigma2/%s' % bqtname, 'w') as outfile:
                outfile.write('#NAME %s\r\n' % name.capitalize())
                for line in open(pth + '/%s' % name):
                    if line.startswith('http://') or line.startswith('https'):
                        outfile.write('#SERVICE 4097:0:1:1:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s' % desk_tmp)
                    elif line.startswith('#EXTINF'):
                        desk_tmp = '%s' % line.split(',')[-1]
                    elif '<stream_url><![CDATA' in line:
                        outfile.write('#SERVICE 4097:0:1:1:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
                        outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
                    elif '<title>' in line:
                        if '<![CDATA[' in line:
                            desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
                        else:
                            desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
                outfile.close()
            self['info'].setText(_('TiVuStream M3U:') + _('Apri Selezione'))
            self.mbox = self.session.open(openMessageBox, _('Controlla nella lista favoriti ...'), openMessageBox.TYPE_INFO, timeout=5)
            if os.path.isfile('/etc/enigma2/bouquets.tv'):
                for line in open('/etc/enigma2/bouquets.tv'):
                    if bqtname in line:
                        in_bouquets = 1

                if in_bouquets is 0:
                    if os.path.isfile('/etc/enigma2/%s' % bqtname) and os.path.isfile('/etc/enigma2/bouquets.tv'):
                        remove_line('/etc/enigma2/bouquets.tv', bqtname)
                        with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
                            outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % bqtname)
                            outfile.close()
            self.mbox = self.session.open(openMessageBox, _('Riordino liste Favorite in Corso') + '\n' + _('Attendere prego ...'), openMessageBox.TYPE_INFO, timeout=5)
            ReloadBouquet()

    def cancel(self):
        if self.convert == False:
            self['info'].setText(_('TiVuStream M3U:') + _('Apri Selezione'))
            self.close()
        else:
            self['info'].setText(_('TiVuStream M3U:') + _('Apri Selezione'))
            self.close()


class M3uPlay(Screen):
    def __init__(self, session, name):
        self.session = session
        skin = SKIN_PATH + '/M3uPlay.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()        
        Screen.__init__(self, session)
        self.list = []
        self['list'] = ListMenu([])
        self['info'] = Label()  
        self['title'] = Label(_('..:: TiVuStream List V. %s  by Lululla ::..' % Version))
        self['Maintainer'] = Label(_('Maintainer'))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['infoc'] = Label(_('Crediti'))        
        self['infoc2'] = Label('%s' % Crediti) 
        service = config.plugins.TivuStream.services.value 
        self['service'] = Label(_('Service Reference utilizzato %s') % service)        
        self['key_red'] = Label(_('Esci'))
        self['key_green'] = Label(_('Play'))
        self['key_yellow'] = Label(_('Aggiungi Stream a Bouquet'))		
        # self['key_blue'] = Label(_(''))        
        self['okpreview'] = Label(_('OK') + '\n' + _('Anteprima'))        
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {'red': self.cancel,
         'green': self.runChannel,
         'cancel': self.cancel,
         'yellow': self.AdjUrlFavo,
         'blue': self.runPreview, 
         'ok': self.runPreview}, -2)
        self['info'].setText(_('N.'))
        self['live'] = Label('')
        self['live'].setText('')
        self.name = name
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.playList)
        
    def playList(self):
        self.names = []
        self.urls = []
        try:
            if fileExists(self.name):
                f1 = open(self.name, 'r+')
                fpage = f1.read()
                regexcat = 'EXTINF.*?,(.*?)\\n(.*?)\\n'
                match = re.compile(regexcat, re.DOTALL).findall(fpage)
                for name, url in match:
                    url = url.replace(' ', '')
                    url = url.replace('\\n', '')
                    self.names.append(name)
                    self.urls.append(url)
                m3ulist(self.names, self['list'])
                self['live'].setText(str(len(self.names)) + ' Stream')
        except Exception as ex:
            print ex
            print 'ex playList' 
            
    def runChannel(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(M3uPlay2, name, url)
            return
            
    def runPreview(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            url = url.replace(':', '%3a')
            self.url = url
            self.name = name

            if ".ts" in self.url: 
                ref = '4097:0:1:0:0:0:0:0:0:0:' + url
                print "ref ts= ", ref        
        
            else:
         
                if config.plugins.TivuStream.services.value == 'Gstreamer':
                    ref = '4097:0:1:0:0:0:0:0:0:0:' + url
                    print "ref 4097= ", ref
                    
                elif config.plugins.TivuStream.services.value == 'StreamLink':
                    ref = '5002:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + url
                    print "ref= ", ref                    
                    
                else:
                    ref = '5002:0:1:0:0:0:0:0:0:0:' + url
                    print "ref 5002= ", ref
            sref = eServiceReference(ref)
            sref.setName(self.name)
            self.session.nav.stopService()
            self.session.nav.playService(sref)
            
    def AdjUrlFavo(self):
        idx = self['list'].getSelectionIndex()
        if idx == -1 or None:
            return
        else:
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(AddIpvStream, name, url)
            return

    def cancel(self):
        self.session.nav.stopService()
        self.session.nav.playService(srefInit)
        self.close()

class M3uPlay2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide): #, InfoBarAudioSelection, InfoBarSubtitleSupport):

    # STATE_IDLE = 0
    # STATE_PLAYING = 1
    # STATE_PAUSED = 2
    # ENABLE_RESUME_SUPPORT = True
    # ALLOW_SUSPEND = True
    def __init__(self, session, name, url):
        
        Screen.__init__(self, session)
        self.skinName = 'MoviePlayer'
        title = 'Play Stream'
        self['list'] = MenuList([])
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self)
        InfoBarShowHide.__init__(self)
        # InfoBarSubtitleSupport.__init__(self)
        # InfoBarAudioSelection.__init__(self)
        self['actions'] = ActionMap(['WizardActions',
         'MoviePlayerActions',
         'MovieSelectionActions',
         'MediaPlayerActions',
         'EPGSelectActions',
         'MediaPlayerSeekActions',
         'SetupActions',
         'ColorActions',
         'InfobarShowHideActions',
         'InfobarActions',
         'InfobarSeekActions'], {'leavePlayer': self.cancel,
         'showEventInfo': self.showVideoInfo,
         'stop': self.leavePlayer,
         'cancel': self.cancel,         
         'back': self.cancel}, -1)
        self.allowPiP = False
#        InfoBarSeek.__init__(self, actionmap='MediaPlayerSeekActions')
        InfoBarSeek.__init__(self, actionmap='InfobarSeekActions')       
        url = url.replace(':', '%3a')
        self.url = url
        self.name = name
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openPlay)

    #
    def openPlay(self):
        url = self.url
        if ".ts" or ".mp4" or ".avi" in self.url: 
            ref = '4097:0:1:0:0:0:0:0:0:0:' + url
            print "ref1= ", ref        
        else:
            if config.plugins.TivuStream.services.value == 'Gstreamer':
                ref = '4097:0:1:0:0:0:0:0:0:0:' + url
                print "ref2= ", ref
                
            elif config.plugins.TivuStream.services.value == 'StreamLink':
                ref = '5002:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + url
                print "ref3= ", ref   
                    
            else:
                ref = '5002:0:1:0:0:0:0:0:0:0:' + url
                print "ref4= ", ref
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)
        
    def keyNumberGlobal(self, number):
        self['text'].number(number)

    def cancel(self):
        self.session.nav.stopService()
        self.session.nav.playService(srefInit)
        self.close()

    def ok(self):
        if self.shown:
            self.hideInfobar()
        else:
            self.showInfobar()

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def leavePlayer(self):
        self.close()

class AddIpvStream(Screen):

    def __init__(self, session, name, url):
        self.session = session
        if fileExists(BRAND) or fileExists(BRANDP):
            skin = SKIN_PATH + '/AddIpvStreamOpen.xml'
        else:
            skin = SKIN_PATH + '/AddIpvStream.xml'        
        #skin = SKIN_PATH + '/AddIpvStream.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self['title'] = Label(_('..:: TiVuStream List V. %s  by Lululla ::..' % Version))
        self['Maintainer'] = Label(_('Maintainer'))
        self['Maintainer2'] = Label('%s' % Maintainer2) 
        self['infoc'] = Label(_('Crediti'))        
        self['infoc2'] = Label('%s' % Crediti) 
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keyOk,
         'blue': self.keyOk,
         'cancel': self.keyCancel,
         'green': self.keyOk,
         'red': self.keyCancel}, -2)
        self['statusbar'] = Label()
        self.list = []
        self['menu'] = MenuList([])
        self.mutableList = None
        self.servicelist = ServiceList(None)
        self.onLayoutFinish.append(self.createTopMenu)
        self.namechannel = name
        self.urlchannel = url
        return

    def initSelectionList(self):
        self.list = []
        self['menu'].setList(self.list)

    def createTopMenu(self):
        self.setTitle(_('Aggiungi Stream IPTV'))
        self.initSelectionList()
        self.list = []
        tmpList = []
        self.list = self.getBouquetList()
        self['menu'].setList(self.list)
        self['statusbar'].setText(_('Seleziona il Bouquet e premi OK per aggiungere'))        
        
    def getBouquetList(self):
        self.service_types = service_types_tv
        if config.usage.multibouquet.value:
            self.bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
        else:
            self.bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet' % self.service_types
        self.bouquet_root = eServiceReference(self.bouquet_rootstr)
        bouquets = []
        serviceHandler = eServiceCenter.getInstance()
        if config.usage.multibouquet.value:
            list = serviceHandler.list(self.bouquet_root)
            if list:
                while True:
                    s = list.getNext()
                    if not s.valid():
                        break
                    if s.flags & eServiceReference.isDirectory:
                        info = serviceHandler.info(s)
                        if info:
                            bouquets.append((info.getName(s), s))
                return bouquets
        else:
            info = serviceHandler.info(self.bouquet_root)
            if info:
                bouquets.append((info.getName(self.bouquet_root), self.bouquet_root))
            return bouquets
        return None

    def keyOk(self):
        if len(self.list) == 0:
            return
        self.name = ''
        self.url = ''
        self.session.openWithCallback(self.addservice, VirtualKeyBoard, title=_('Inserire Nome'), text=self.namechannel)

    def addservice(self, res):
        if res:
            self.url = res
            str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(self.url), quote(self.name))
            ref = eServiceReference(str)
            self.addServiceToBouquet(self.list[self['menu'].getSelectedIndex()][1], ref)
            self.close()

    def addServiceToBouquet(self, dest, service = None):
        mutableList = self.getMutableList(dest)
        if mutableList is not None:
            if service is None:
                return
            if not mutableList.addService(service):
                mutableList.flushChanges()
        return

    def getMutableList(self, root = eServiceReference()):
        if self.mutableList is not None:
            return self.mutableList
        else:
            serviceHandler = eServiceCenter.getInstance()
            if not root.valid():
                root = self.getRoot()
            list = root and serviceHandler.list(root)
            if list is not None:
                return list.startEdit()
            return
            return

    def getRoot(self):
        return self.servicelist.getRoot()

    def keyCancel(self):
        self.close()

class OpenConfig(Screen, ConfigListScreen):

    def __init__(self, session):

		
        if fileExists(BRAND) or fileExists(BRANDP):
            skin = SKIN_PATH + '/OpenConfigOpen.xml'
        else:
            skin = SKIN_PATH + '/OpenConfig.xml'        
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()  
        Screen.__init__(self, session)
        self.setup_title = _("TiVuStream Config")	
        self.onChangedEntry = [ ]
		
        self.session = session		
		
        info = '***'
        self['title'] = Label(_('..:: TiVuStream List V. %s  by Lululla ::..' % Version))
        self['Maintainer'] = Label(_('Maintainer'))
        self['Maintainer2'] = Label('%s' % Maintainer2) 
        self['infoc'] = Label(_('Crediti'))        
        self['infoc2'] = Label('%s' % Crediti) 
        self['key_red'] = Label(_('Esci'))
        self['key_yellow'] = Label(_('Aggiorna Plugin'))
        self['key_green'] = Label(_('Salva'))
        # self['key_blue'] = Label(_(''))        
        self['text'] = Label(info)
        self["description"] = Label(_(''))
        self.cbUpdate = False

        self["setupActions"] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions', 'VirtualKeyboardActions', 'ActiveCodeActions'],
        {
                "red": self.extnok,
                "cancel": self.extnok,
                'yellow': self.msgupdt1,
                "green": self.cfgok,
                "left": self.keyLeft,
                "right": self.keyRight,				
                'showVirtualKeyboard': self.KeyText,
                "ok": self.Ok_edit
        }, -1)       
        self.list = []	
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
        self.createSetup()
        self.checkUpdate()
        self.onLayoutFinish.append(self.layoutFinished) 

    def checkUpdate(self):
        server_ref()
        try:
            fp = urllib.urlopen(upd_fr_txt)
            count = 0
            self.labeltext = ''
            s1 = fp.readline()
            s2 = fp.readline()
            s3 = fp.readline()
            s1 = s1.strip()
            s2 = s2.strip()
            s3 = s3.strip()
            self.link = s2
            self.version = s1
            self.info = s3
            fp.close()
            if s1 == currversion:
                self['text'].setText(_('TiVuStream versione: ') + currversion + '\n'+ _('Nessun aggiornamento online!') + '\n' + _('se ti piace puoi fare una libera donazione') + '\n' + _('www.paypal.me/TivuStream'))# + _('\nPLEASE DONATE'))
                self.cbUpdate = False
            elif float(s1) < float(currversion):
                self['text'].setText(_('TiVuStream versione: ') + currversion + '\n'+ _('Nessun aggiornamento online!') + '\n' + _('se ti piace puoi fare una libera donazione') + '\n' + _('www.paypal.me/TivuStream'))# + _('\nPLEASE DONATE'))
                self.cbUpdate = False
            else:
                updatestr = (_('TiVuStream versione: ') + currversion + '\n' + _('Ultimo aggiornamento ') + s1 + ' ' + _('disponibile!') + '\n' + _('ChangeLog:') + self.info)
                self.cbUpdate = True
                self['text'].setText(updatestr)
        except:
            self.cbUpdate = False
            self['text'].setText(_('Nessun aggiornamento disponibile') + '\n' + _('Nessuna connessione Internet o server OFF') + '\n' + _('Prego riprova piu tardi o cambia SERVER in menu config.'))

        self.timerx = eTimer()
        self.timerx.start(100, 1)		
        if fileExists(BRAND)or fileExists(BRANDP):
            self.timerx.callback.append(self.msgupdt2) #pli
        else:
            self.timerx_conn = self.timerx.timeout.connect(self.msgupdt2) #cvs 
			

    def layoutFinished(self):
        self.setTitle(self.setup_title)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_('Server:'), config.plugins.TivuStream.server, _("Scelta del Server")))
        self.list.append(getConfigListEntry(_('Auto Update Plugin:'), config.plugins.TivuStream.autoupd, _("Aggiornarmento plugin automatico")))
        self.list.append(getConfigListEntry(_('Password Personale:'), config.plugins.TivuStream.code, _("Inserisci la password per scaricare Liste XXX Adulti")))
        self.list.append(getConfigListEntry(_('Posizione IPTV bouquets '), config.plugins.TivuStream.bouquettop, _("Configura posizione dei Bouquet delle liste convertite")))
        self.list.append(getConfigListEntry(_('Liste Player <.m3u>:'), config.plugins.TivuStream.pthm3uf, _("Percorso cartella contenente i file .m3u")))
        self.list.append(getConfigListEntry(_('Tipo Services Reference'), config.plugins.TivuStream.services, _("Configura Service Reference Gstreamer/Exteplayer3/StreamLink")))
        self.list.append(getConfigListEntry(_('Link in Extensions Menu:'), config.plugins.TivuStream.strtext, _("Mostra Plugin in Extensions Menu")))
        self.list.append(getConfigListEntry(_('Link in Menu Principale:'), config.plugins.TivuStream.strtmain, _("Mostra Plugin in Main Menu")))
        self['config'].list = self.list
        self["config"].setList(self.list)

    def changedEntry(self):
        for x in self.onChangedEntry:
                x()        

        #
    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

        #
    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

        #
    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary
            
        #
    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        print "current selection:", self["config"].l.getCurrentSelection()
        self.createSetup()

        #
    def keyRight(self):
        ConfigListScreen.keyRight(self)
        print "current selection:", self["config"].l.getCurrentSelection()
        self.createSetup()
            
        #
    def Ok_edit(self):    
        ConfigListScreen.keyRight(self)
        print "current selection:", self["config"].l.getCurrentSelection()
        self.createSetup()
		
    def Ok_edit(self): 		
        ConfigListScreen.keyOK(self)
        sel = self['config'].getCurrent()[1]
        if sel and sel == config.plugins.TivuStream.pthm3uf:
            self.setting = 'pthm3uf'
            print "current selection:", self["config"].l.getCurrentSelection()
            self.openDirectoryBrowser(config.plugins.TivuStream.pthm3uf.value)
          
        else:
            pass        
		
    def openDirectoryBrowser(self, path):
            try:
                self.session.openWithCallback(
                 self.openDirectoryBrowserCB,
                 LocationBox,
                 windowTitle=_('Choose Directory:'),
                 text=_('Choose directory'),
                 currDir=str(path),
                 bookmarks=config.movielist.videodirs,
                 autoAdd=False,
                 editDir=True,
                 inhibitDirs=['/bin', '/boot', '/dev', '/home', '/lib', '/proc', '/run', '/sbin', '/sys', '/var'],
                 minFree=15)
            except Exception as e:
                print ('openDirectoryBrowser get failed: ', str(e))


    def openDirectoryBrowserCB(self, path):
                if path is not None:
                    if self.setting == 'pthm3uf':
                        config.plugins.TivuStream.pthm3uf.setValue(path)
                return	
            
    def cfgok(self):
        self.save()

    def save(self):
        if not os.path.exists(config.plugins.TivuStream.pthm3uf.value):
            self.mbox = self.session.open(openMessageBox, _('Cartella Liste m3u non rilevato!'), openMessageBox.TYPE_INFO, timeout=4)
            return
        if self['config'].isChanged():
            for x in self['config'].list:
                x[1].save()
            server_ref()
            config.plugins.TivuStream.server.save()    
            configfile.save()
            plugins.clearPluginList()
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
            self.mbox = self.session.open(openMessageBox, _('Impostazioni salvate correttamente!'), openMessageBox.TYPE_INFO, timeout=5)
            self.close()
        else:
           self.close()            
        
    def KeyText(self):
        sel = self['config'].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

    def VirtualKeyBoardCallback(self, callback = None):
        if callback is not None and len(callback):
            self['config'].getCurrent()[1].value = callback
            self['config'].invalidate(self['config'].getCurrent())
        return                

    #
    def cancelConfirm(self, result):
        if not result:
            return
        for x in self['config'].list:
            x[1].cancel()
        
        self.close()
        
    def extnok(self):
        if self['config'].isChanged():
            self.session.openWithCallback(self.cancelConfirm, openMessageBox, _('Veramente chiudere senza salvare le impostazioni?'))
        else:
            self.close()
                
    def msgupdt2(self):
        if self.cbUpdate == False:
            return
        if config.plugins.TivuStream.autoupd.value == False:
            return
        self.session.openWithCallback(self.runupdate, openMessageBox, _('Nuova Versione Online!') + '\n\n' + _('Aggiornare Plugin alla Versione %s ?' % self.version), openMessageBox.TYPE_YESNO)

    def msgupdt1(self):
        if self.cbUpdate == False:
            return
        self.session.openWithCallback(self.runupdate, openMessageBox, _('Aggiornare Plugin ?'), openMessageBox.TYPE_YESNO)

    def runupdate(self, result):
        if self.cbUpdate == False:
            return
        if result:
            com = self.link
            dom = 'Nuova versione ' + self.version
            #wget http://patbuweb.com/iptv/plugin/tivustream.tar -O /tmp/tivustream.tar > /dev/null
            os.system('wget %s -O /tmp/tivustream.tar > /dev/null' % com)
            os.system('sleep 3')
            # self.session.open(OpenConsole, _('Aggiorno Plugin: %s') % dom, ['opkg install -force-overwrite %s' % com], finishedCallback=self.msgrstrt3, closeOnSuccess=True)
            self.session.open(OpenConsole, _('Aggiorno Plugin: %s') % dom, ['tar -xvf /tmp/tivustream.tar -C /'], finishedCallback=self.msgrstrt3, closeOnSuccess=True)
            
    def msgrstrt3(self):
        self.mbox = self.session.open(openMessageBox, _('Plugin Aggiornato!') + '\n' + _('Riavvio interfaccia utente'), openMessageBox.TYPE_INFO, timeout=4)
        os.system('rm -f /tmp/tivustream.tar')
        quitMainloop(3)
        
class OpenConsole(Screen):

    def __init__(self, session, title = None, cmdlist = None, finishedCallback = None, closeOnSuccess = False):
        self.session = session
        skin = SKIN_PATH + '/OpenConsole.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess       
        self['text'] = ScrollLabel('')
        self['title'] = Label(_('..:: TiVuStream List V. %s  by Lululla ::..' % Version))
        self['Maintainer'] = Label(_('Maintainer'))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['infoc'] = Label(_('Crediti'))        
        self['infoc2'] = Label('%s' % Crediti) 
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.cancel,
         'back': self.cancel,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown}, -1)
        self.cmdlist = cmdlist
        self.container = eConsoleAppContainer()
        self.run = 0
        try:
            self.container.appClosed.append(self.runFinished)
        except:
            self.appClosed_conn = self.container.appClosed.connect(self.runFinished)

        try:
            self.container.dataAvail.append(self.dataAvail)
        except:
            self.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)

        self.onLayoutFinish.append(self.startRun)

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self['text'].setText(_('Esecuzione in corso:') + '\n\n')
        print 'Console: executing in run', self.run, ' the command:', self.cmdlist[self.run]
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
        else:
            str = self['text'].getText()
            str += _('Esecuzione finita!!')
            self['text'].setText(str)
            self['text'].lastPage()
            if self.finishedCallback is not None:
                self.finishedCallback()
            if not retval and self.closeOnSuccess:
                self.cancel()
        return

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
        try:
            self.container.appClosed.remove(self.runFinished)
        except:
            self.appClosed_conn = None

        try:
            self.container.dataAvail.remove(self.dataAvail)
        except:
            self.dataAvail_conn = None

        return

    def dataAvail(self, str):
        self['text'].setText(self['text'].getText() + str)


class openMessageBox(Screen):
    TYPE_YESNO = 0
    TYPE_INFO = 1
    TYPE_WARNING = 2
    TYPE_ERROR = 3
    TYPE_MESSAGE = 4

    def __init__(self, session, text, type = TYPE_YESNO, timeout = -1, close_on_any_key = False, default = True, enable_input = True, msgBoxID = None, picon = None, simple = False, list = [], timeout_default = None):
        self.type = type
        self.session = session
        if fileExists(BRAND) or fileExists(BRANDP):
            skin = SKIN_PATH + '/OpenMessageBoxOpen.xml'
        else:
            skin = SKIN_PATH + '/OpenMessageBox.xml'        
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)
        self.msgBoxID = msgBoxID
        self['title'] = Label(_('..:: TiVuStream List V. %s  by Lululla ::..' % Version))
        self['Maintainer'] = Label(_('Maintainer'))
        self['Maintainer2'] = Label('%s' % Maintainer2)
        self['infoc'] = Label(_('Crediti'))        
        self['infoc2'] = Label('%s' % Crediti) 
        self['text'] = Label(text)
        self['Text'] = StaticText(text)
        self['selectedChoice'] = StaticText()
        self.text = text
        self.close_on_any_key = close_on_any_key
        self.timeout_default = timeout_default
        self['ErrorPixmap'] = Pixmap()
        self['QuestionPixmap'] = Pixmap()
        self['InfoPixmap'] = Pixmap()
        self['WarningPixmap'] = Pixmap()
        self.timerRunning = False
        self.initTimeout(timeout)
        picon = picon or type
        if picon != self.TYPE_ERROR:
            self['ErrorPixmap'].hide()
        if picon != self.TYPE_YESNO:
            self['QuestionPixmap'].hide()
        if picon != self.TYPE_INFO:
            self['InfoPixmap'].hide()
        if picon != self.TYPE_WARNING:
            self['WarningPixmap'].hide()
        self.title = self.type < self.TYPE_MESSAGE and [_('Question'),
         _('Information'),
         _('Warning'),
         _('Error')][self.type] or _('Message')
        if type == self.TYPE_YESNO:
            if list:
                self.list = list
            elif default == True:
                self.list = [(_('Si'), True), (_('No'), False)]
            else:
                self.list = [(_('No'), False), (_('Si'), True)]
        else:
            self.list = []
        self['list'] = MenuList(self.list)
        if self.list:
            self['selectedChoice'].setText(self.list[0][0])
        else:
            self['list'].hide()
        if enable_input:
            self['actions'] = ActionMap(['MsgBoxActions', 'DirectionActions'], {'cancel': self.cancel,
             'ok': self.ok,
             'alwaysOK': self.alwaysOK,
             'up': self.up,
             'down': self.down,
             'left': self.left,
             'right': self.right,
             'upRepeated': self.up,
             'downRepeated': self.down,
             'leftRepeated': self.left,
             'rightRepeated': self.right}, -1)
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(self.title)

    def initTimeout(self, timeout):
        self.timeout = timeout
        if timeout > 0:
            self.timer = eTimer()
            
            if fileExists(BRAND)or fileExists(BRANDP):
                self.timer.callback.append(self.timerTick) #pli
            else:
                self.timer_conn = self.timer.timeout.connect(self.timerTick) #cvs             
            
            self.onExecBegin.append(self.startTimer)
            self.origTitle = None
            if self.execing:
                self.timerTick()
            else:
                self.onShown.append(self.__onShown)
            self.timerRunning = True
        else:
            self.timerRunning = False
        return

    def __onShown(self):
        self.onShown.remove(self.__onShown)
        self.timerTick()

    def startTimer(self):
        self.timer.start(1000)

    def stopTimer(self):
        if self.timerRunning:
            del self.timer
            self.onExecBegin.remove(self.startTimer)
            self.setTitle(self.origTitle)
            self.timerRunning = False

    def timerTick(self):
        if self.execing:
            self.timeout -= 1
            if self.origTitle is None:
                self.origTitle = self.instance.getTitle()
            self.setTitle(self.origTitle + ' (' + str(self.timeout) + ')')
            if self.timeout == 0:
                self.timer.stop()
                self.timerRunning = False
                self.timeoutCallback()
        return

    def timeoutCallback(self):
        print 'Timeout!'
        if self.timeout_default is not None:
            self.close(self.timeout_default)
        else:
            self.ok()
        return

    def cancel(self):
        self.close(False)

    def ok(self):
        if self.list:
            self.close(self['list'].getCurrent()[1])
        else:
            self.close(True)

    def alwaysOK(self):
        self.close(True)

    def up(self):
        self.move(self['list'].instance.moveUp)

    def down(self):
        self.move(self['list'].instance.moveDown)

    def left(self):
        self.move(self['list'].instance.pageUp)

    def right(self):
        self.move(self['list'].instance.pageDown)

    def move(self, direction):
        if self.close_on_any_key:
            self.close(True)
        self['list'].instance.moveSelection(direction)
        if self.list:
            self['selectedChoice'].setText(self['list'].getCurrent()[0])
        self.stopTimer()

    def __repr__(self):
        return str(type(self)) + '(' + self.text + ')'

        
        
class plgnstrt(Screen):
    
    def __init__(self, session):
        self.session = session
        skin = SKIN_PATH + '/Plgnstrt.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()          
        Screen.__init__(self, session)    
        self['text'] = ScrollLabel()
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions','ColorActions', 'SetupActions'], {'ok': self.clsgo,
         'cancel': self.clsgo,
         'back': self.clsgo,
         'red': self.clsgo,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown,
         'left': self['text'].pageUp,
         'right': self['text'].pageDown,
         'green': self.clsgo}, -1)        
        
        # self.timer = eTimer()
        # try:
            # self.timer_conn = self.timer.timeout.connect(self.clsgo)
        # except:
            # self.timer.callback.append(self.clsgo)
        # self.timer.start(2500, True)
        self.onLayoutFinish.append(self.checkDwnld)

        # self.checkDwnld()

    def checkDwnld(self):
        server_ref()
        
        self.icount = 0
        self['text'].setText(_('\n\n\nCheck Connection wait please...'))
        self.timer = eTimer()
        self.timer.start(100, 1)        
        if fileExists(BRAND)or fileExists(BRANDP):
            self.timer.callback.append(self.OpenCheck) #pli
        else:
            self.timer_conn = self.timer.timeout.connect(self.OpenCheck) #cvs          

            
    def OpenCheck(self):
        url3 = upd_fr_txt
        print 'url3:', url3
        getPage(url3).addCallback(self.ConnOK).addErrback(self.error)
        
    def ConnOK(self, data):
        try:
            self['text'].setText(DownloadInfo(URL))
        except:
            self['text'].setText(_('\n\n' + 'Errore nel download degli aggiornamenti !'))
            print"ERROR Download History %s" %(url)
            
            
    def error(self, error):
        self['text'].setText(_('\n\n' + 'Server Off !') + '\n' + _('controlla SERVER in config'))          
        
        
    def clsgo(self):
        self.session.openWithCallback(self.close, OpenScript)        
        # self.session.open(OpenScript)
        
def main(session, **kwargs):
    if checkInternet():
        # session.open(ABOUT)
        session.open(plgnstrt)        
        
    else:
        session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)  
        
def main2(session, **kwargs):
    if checkInternet():
        session.open(OpenM3u)
    else:
        session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)  

def mainmenu(session, **kwargs):
    main(session, **kwargs)


def cfgmain(menuid):
    if menuid == 'mainmenu':
        return [('TiVuStream',
          main,
          'TiVuStream List by Lululla',
          44)]
    else:
        return []

def Plugins(**kwargs):

    icona = 'logo.png'

    if fileExists(BRAND) or fileExists(BRANDP):   
        icona = SKIN_PATH + '/logo.png'

    iconaplayer = SKIN_PATH + '/player.png'
    extDescriptor = PluginDescriptor(name='TiVuStream List', description=_('TiVuStream List'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=icona, fnc=main)
    mainDescriptor = PluginDescriptor(name='TiVuStream List', description=_('TiVuStream List v.' + currversion), where=PluginDescriptor.WHERE_MENU, icon=icona, fnc=cfgmain)
    # result = [PluginDescriptor(name='TiVuStream List', description=_('TiVuStream List v.' + currversion), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=icona, fnc=main), PluginDescriptor(name='TiVuStream List Player', description='TiVuStream List Player v.' + currversion, where=[PluginDescriptor.WHERE_PLUGINMENU], icon=iconaplayer, fnc=main2)]
    result = [PluginDescriptor(name='TiVuStream List', description=_('TiVuStream List v.' + currversion), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=icona, fnc=main)]
    if config.plugins.TivuStream.strtext.value:
        result.append(extDescriptor)
    if config.plugins.TivuStream.strtmain.value:
        result.append(mainDescriptor)
    return result

