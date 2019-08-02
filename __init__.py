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
from mycroft.skills.core import MycroftSkill, intent_handler
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
