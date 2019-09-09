"""
AutoDash Mycroft Skill.
"""
from __future__ import unicode_literals
import requests
from os.path import dirname
import sys
import youtube_dl
import json
import dbus
import subprocess
from adapt.intent import IntentBuilder
from bs4 import BeautifulSoup
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
import threading
import collections
import feedparser

__author__ = 'aix'
LOGGER = getLogger(__name__)
searchlst = {}
soundlst = []
searchlstobject = []
baloosearchobj = []
newsItemList = []
newsItemObject = {}

class AutoDashSkill(MycroftSkill):
    def __init__(self):
        """
        AutoDash Skill Class.
        """    
        super(AutoDashSkill, self).__init__(name="AutoDashSkill")
    
    def initialize(self):
    # Initialize...
        self.add_event('soundcloud_Search', self.soundcloud_Search)
        self.add_event('news_headlines', self.handle_get_latest_news_intent)
        self.add_event('bbc_cast', self.handle_get_bbc_one_min_cast)
        self.add_event('automobile.skill.speak', self.speakNotification)

    def speakNotification(self, message):
        notification = message.data["speak"]
        self.speak(notification)
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.showNotif(notification, dbus_interface="org.kde.autodashapplet")
        
    def searchSongInBaloo(self, songtitle):
        global baloosearchobj
        for x in baloosearchobj:
            title = x['title'].split(".")
            LOGGER.info(title[0].replace('-', '').lower())
            LOGGER.info(songtitle.replace('-', '').lower())
            if title[0].replace('-', '').lower() == songtitle[6:].replace('-', '').replace(' ', '').lower():
                found_obj = [x['url'], x['thumbnail'], x['title']]
                return found_obj

    @intent_handler(IntentBuilder("nav_dashboard").require("navDashboardKeyword").build())
    def nav_dashboard(self, message):
        """
        Menu Navigation To Dashboard
        """
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.viewAutoDash(dbus_interface="org.kde.autodashapplet")

    @intent_handler(IntentBuilder("nav_navigation").require("navNavigationKeyword").build())
    def nav_navigation(self, message):
        """
        Menu Navigation To Navigation
        """
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.viewNavigation(dbus_interface="org.kde.autodashapplet")

    @intent_handler(IntentBuilder("nav_radio").require("navRadioKeyword").build())
    def nav_radio(self, message):
        """
        Menu Navigation To Radio
        """
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.viewMusic(dbus_interface="org.kde.autodashapplet")

    @intent_handler(IntentBuilder("nav_music").require("navMusicKeyword").build())
    def nav_music(self, message):
        """
        Menu Navigation To Music
        """
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.viewMusic(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashUnLockLeftDoor.intent")
    def internalDash_UnlockLeftDoor(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashUnLockLeftDoor(dbus_interface="org.kde.autodashapplet")    

    @intent_file_handler("internalDashLockLeftDoor.intent")
    def internalDash_LockLeftDoor(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashLockLeftDoor(dbus_interface="org.kde.autodashapplet")    

    @intent_file_handler("internalDashUnLockRightDr.intent")
    def internalDash_UnlockRightDoor(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashUnLockRightDoor(dbus_interface="org.kde.autodashapplet")    

    @intent_file_handler("internalDashLockRightDoor.intent")
    def internalDash_LockRightDoor(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashLockRightDoor(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("radioPlayerTurnOn.intent")
    def radioPlayerTurnOn(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.radioPlayerTurnOn(dbus_interface="org.kde.autodashapplet")

    @intent_file_handler("radioPlayerTurnOff.intent")
    def radioPlayerTurnOff(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.radioPlayerTurnOff(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("radioPlayerChangeMode.intent")
    def radioPlayerChangeMode(self, message):
        mode = message.data['mode']
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.radioPlayerChangeMode(mode, dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("radioPlayerScanStations.intent")
    def radioPlayerScanStations(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.radioPlayerScanStations(dbus_interface="org.kde.autodashapplet")

    @intent_file_handler("radioPlayerSelectStation.intent")
    def radioPlayerSelectStation(self, message):
        stationname = message.data["stationname"]
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.radioPlayerSelectStation(1, dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("musicPlayerChangeMode.intent")
    def musicPlayerChangeMode(self, message):
        mode = message.data["playermode"]
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.musicPlayerChangeMode(mode, dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("musicPlayerPlaySongFromList.intent")
    def musicPlayerPlaySongFromList(self, message):
        global searchlstobject
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.musicPlayerPlaySongFromList(searchlstobject[1]['url'], searchlstobject[1]['thumbnail'], searchlstobject[1]['title'], dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("musicPlayerNextTrack.intent")
    def musicPlayerNextTrack(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.musicPlayerNextTrack(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("musicPlayerPreviousTrack.intent")
    def musicPlayerPreviousTrack(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.musicPlayerPreviousTrack(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("musicPlayerPauseTrack.intent")
    def musicPlayerPauseTrack(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.musicPlayerPauseTrack(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("musicPlayerStopTrack.intent")
    def musicPlayerStopTrack(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.musicPlayerStopTrack(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("navigationGetToLocation.intent")
    def navigationGetToLocation(self, message):
        location = message.data["location"]
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.navigationGetToLocation(location, dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("navigationShowHomeLocation.intent")
    def navigationShowHomeLocation(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.navigationShowHomeLocation(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("navigationChangeMapMode.intent")
    def navigationChangeMapMode(self, message):
        mapmode = message.data["mapmode"]
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.navigationChangeMapMode(mapmode, dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("navigationChangeMapStyle.intent")
    def navigationChangeMapStyle(self, message):
        mapstyle = message.data["mapstyle"]
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.navigationChangeMapStyle(mapstyle, dbus_interface="org.kde.autodashapplet")
    
    @intent_file_handler("internalDashLockHood.intent")
    def internalDashLockHood(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashLockHood(dbus_interface="org.kde.autodashapplet")

    @intent_file_handler("internalDashUnLockHood.intent")
    def internalDashUnLockHood(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashUnLockHood(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashLockTrunk.intent")
    def internalDashLockTrunk(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashLockTrunk(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashUnLockTrunk.intent")
    def internalDashUnLockTrunk(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashUnLockTrunk(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashHeadlightOn.intent")
    def internalDashHeadlightOn(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashHeadlightOn(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashHeadlightOff.intent")
    def internalDashHeadlightOff(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashHeadlightOff(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashHeadlightLevel.intent")
    def internalDashHeadlightLevel(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashHeadlightLevel(2, dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashWiperBladeOn.intent")
    def internalDashWiperBladeOn(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashWiperBladeOn(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashWiperBladeOff.intent")
    def internalDashWiperBladeOff(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashWiperBladeOff(dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashWiperBladeLevel.intent")
    def internalDashWiperBladeLevel(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashWiperBladeLevel(2, dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashAdjLeftSeatIncrease.intent")
    def internalDashAdjLeftSeatIncrease(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashAdjLeftSeat("increase", 120, dbus_interface="org.kde.autodashapplet")
    
    @intent_file_handler("internalDashAdjLeftSeatDecrease.intent")
    def internalDashAdjLeftSeatDecrease(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashAdjLeftSeat("decrease", 100, dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("internalDashAdjRightSeatIncrease.intent")
    def internalDashAdjRightSeatIncrease(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashAdjRightSeat("increase", 10, dbus_interface="org.kde.autodashapplet")

    @intent_file_handler("internalDashAdjRightSeatDecrease.intent")
    def internalDashAdjRightSeatDecrease(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashAdjRightSeat("decrease", 10, dbus_interface="org.kde.autodashapplet")

    @intent_file_handler("internalDashAdjAcTempIncrease.intent")
    def internalDashAdjAcTempIncrease(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashAdjAcTemp("increase", 10, dbus_interface="org.kde.autodashapplet")

    @intent_file_handler("internalDashAdjAcTempDecrease.intent")
    def internalDashAdjAcTempDecrease(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashAdjAcTemp("decrease", 10, dbus_interface="org.kde.autodashapplet")

    @intent_file_handler("internalDashAdjSteerHeightIncrease.intent")
    def internalDashAdjSteerHeight(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashAdjSteerHeight("increase", 10, dbus_interface="org.kde.autodashapplet")

    @intent_file_handler("internalDashAdjSteerHeightDecrease.intent")
    def internalDashAdjSteerHeightDecrease(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.internalDashAdjSteerHeight("decrease", 1, dbus_interface="org.kde.autodashapplet")
        
    @intent_file_handler("navigationFindNearbyPlacesType.intent")
    def navigationFindNearbyPlacesType(self, message):
        placeofinterest = message.data["interest"]
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.navigationFindNearbyPlacesType(placeofinterest, dbus_interface="org.kde.autodashapplet")
    
    @intent_handler(IntentBuilder("soundcloud_Search").require("soundcloudSearchKeyword").build())
    def soundcloud_Search(self, message):
        """
        Search Sc By Keywords
        """
        global soundlst
        global current_song
        soundlst.clear()
        utterance = message.data.get('utterance').lower()
        utterance = utterance.replace(message.data.get('soundcloudSearchKeyword'), '')
        searchString = utterance
        query = searchString
        url = "https://soundcloud.com/search/sounds?q=" + query
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('h2'):
            for x in link.find_all('a'):
               r = x.get('href')
               countOfWords = collections.Counter(r)
               result = [i for i in countOfWords if countOfWords[i]>1]
               if "/" in result:
                 soundlst.append("https://soundcloud.com" + x.get('href'))
        
        if len(soundlst) != 0:
            genMusicUrl = soundlst[0]
            self.genMusicSearchList = threading.Thread(target=self.getSearchListInfo, args=[soundlst])
            self.genMusicSearchList.start()
            return genMusicUrl
        else:
            self.speak("No Song Found")
            return False                

    def getSearchListInfo(self, soundlst):
        global searchlst
        global searchlstobject
        ydl_opts = {}
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        searchlstobject.clear();
        for x in range(len(soundlst)):
            info_dict = ydl.extract_info(soundlst[x], download=False)
            searchlstobject.append({"title": info_dict.get("title", None), "url": info_dict.get("url", None), "thumbnail": info_dict.get("thumbnail", None)})
            result = json.dumps(searchlstobject)
            bus = dbus.SessionBus()
            remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
            remote_object.scSearchResult(result, dbus_interface="org.kde.autodashapplet")
            
    @intent_handler(IntentBuilder("localbaloo_Search").require("localSearchKeyword").build())
    def localbaloo_Search(self, message):
        utterance = message.data.get('utterance').lower()
        utterance = utterance.replace(message.data.get('localSearchKeyword'), '')
        searchString = utterance.split(" ")
        baloosearchobj.clear()
        searchTerm = "baloosearch -t=audio -d /home/$USER/Music -l 10 mp3"
        p = subprocess.Popen(searchTerm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        resultblock = p.communicate()[0].splitlines()
        for x in range(len(resultblock)):
            songtitle = resultblock[x].split("/")[-1]
            songurl = "file://" + resultblock[x]
            songthumb = "http://virtualdjradio.com/images/no-cover.png"
            baloosearchobj.append({"title": songtitle, "url": songurl, "thumbnail": songthumb})
            result = json.dumps(baloosearchobj)
        LOGGER.info("BalooCompleted")
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.lcSearchResult(result, dbus_interface="org.kde.autodashapplet")
        
    def handle_get_latest_news_intent(self, message):
        """ 
        Get News and Read Title
        """
        global newsItemList
        global newsItemObject
        getNewsLang = self.lang.split("-")
        newsLang = getNewsLang[1]
        newsAPIURL = 'https://newsapi.org/v2/top-headlines?country=in&apiKey=a1091945307b434493258f3dd6f36698'.format(newsLang)
        newsAPIRespone = requests.get(newsAPIURL)
        newsItems = newsAPIRespone.json()
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.nwsSearchResult(newsItems, dbus_interface="org.kde.autodashapplet")

    def handle_get_bbc_one_min_cast(self, message):
        """
        Get BBC One Min News Cast
        """
        rrsFeedURL = "http://wsrss.bbc.co.uk/bizdev/bbcminute/bbcminute.rss"
        rrsFeedRespone = feedparser.parse(rrsFeedURL)
        for item in rrsFeedRespone.entries:
            playurl = item.links[0].href;
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.autodashapplet", "/autodashapplet")
        remote_object.castnwsSearchResult(playurl, dbus_interface="org.kde.autodashapplet")

    def stop(self):
        """
        Mycroft Stop Function
        """
        pass
    
def create_skill():
    """
    Mycroft Create Skill Function
    """
    return AutoDashSkill()
