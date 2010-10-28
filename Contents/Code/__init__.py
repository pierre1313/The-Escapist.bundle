# -*- coding: utf-8 -*-
from PMS import *
import re, urllib

ESCAPIST_PREFIX = '/video/escapist'

ESCAPIST_URL            = 'http://www.escapistmagazine.com'
ESCAPIST_GALERIES       = ESCAPIST_URL + '/vidoes/galleries'
ESCAPIST_HIGHLIGHTS     = ESCAPIST_URL + '/ajax/videos_index.php?videos_type=%s'
CACHE_INTERVAL    = 3600

def Start():

  Plugin.AddPrefixHandler(ESCAPIST_PREFIX, MainMenu, L('theescapist'), 'icon-default.jpg', 'art-default.jpg')
  Plugin.AddViewGroup('Details', viewMode='List', mediaType='items')
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.jpg')
  MediaContainer.viewGroup = 'Details'
  MediaContainer.title1 = L('theescapist')
  HTTP.SetCacheTime(CACHE_INTERVAL)
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2'


def MainMenu():

  dir = MediaContainer()
 
  page = XML.ElementFromURL(ESCAPIST_URL + '/videos/galleries', isHTML=True)

  # Add 'latest' and 'popular'
  dir.Append(Function(DirectoryItem(HighlightBrowser, title=L('latest'), thumb=R('icon-default.jpg'), summary=L('latest-summary')), mode='latest'))
  dir.Append(Function(DirectoryItem(HighlightBrowser, title=L('popular'), thumb=R('icon-default.jpg'), summary=L('popular-summary')), mode='popular'))

  shows = page.xpath("//div[@class='gallery_latest site_panel']")

  for show in shows:
 
    title = show.xpath(".//div[@class='gallery_title']/a")[0].text
    url = show.xpath(".//div[@class='gallery_title']/a")[0].get('href')
    summary = show.xpath(".//div[@class='gallery_description']")[0].text
    thumb = show.xpath(".//div[@class='gallery_title_card']//img")[0].get('src')
    if title!= '':
      dir.Append(Function(DirectoryItem(ShowBrowser, title=title, thumb=thumb, summary=summary), showUrl=url, showName=title, showThumb=thumb))

  return dir

def ShowBrowser(sender, showUrl, showName, showThumb, pageNumber=1):

  dir = MediaContainer()

  if pageNumber > 1:
    pageUrl = showUrl + "?page=" + str(pageNumber)
    dir.title1 = showName
    dir.title2 = L('page') + ' ' + str(pageNumber)
  else:
    dir.title2 = showName
    pageUrl = showUrl

  page = XML.ElementFromURL(pageUrl, isHTML=True)

  episodes = page.xpath("//div[@class='video']//div[@class='filmstrip_video']")

  for episode in episodes:

    title = episode.xpath(".//div[@class='title']")[0].text
    date = episode.xpath(".//div[@class='date']")[0].text
    url = episode.xpath(".//a")[0].get('href')
    Log(url[0:4])
    if url[0:4] != 'http':
      url = ESCAPIST_URL + url
    
    thumb = episode.xpath(".//img")[0].get('src')

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, duration='0', thumb=thumb), url=url))

  # Check for a next page link
  if len ( page.xpath("//a[@class='next_page']")) > 0:
    pageNumber = pageNumber + 1
    dir.Append(Function(DirectoryItem(ShowBrowser, title=L('nextpage'), thumb=showThumb, summary=L('nextpage')), showUrl=showUrl, showName=showName, showThumb=showThumb, pageNumber=pageNumber))

  return dir

def HighlightBrowser(sender, mode):

  dir = MediaContainer()
  dir.title2 = (mode)

  page = XML.ElementFromURL(ESCAPIST_HIGHLIGHTS % mode, isHTML=True)

  episodes = page.xpath("//div[@class='filmstrip_video']")

  for episode in episodes:

    title = episode.xpath(".//div[@class='title']")[0].text
    date = episode.xpath(".//div[@class='date']")[0].text
    url = episode.xpath(".//a")[0].get('href')
    if url[0:3] != 'http':
      url = ESCAPIST_URL + url
    thumb = episode.xpath(".//img")[0].get('src')

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, duration='0', thumb=thumb), url=url))

  return dir

def PlayVideo(sender, url):

  # Find the FLV for the episode and redirect to it
  Log(url)
  rawpage = HTTP.Request(url).replace('&lt;','<').replace('&gt;','>').replace('&quot;','"')
  page = XML.ElementFromString(rawpage, isHTML=True)

  configElement = page.xpath("//div[@id='video_embed']//embed")[0].get('flashvars')
  configUrl = re.search(r'config=(.*)', configElement).group(1)
  configUrl = urllib.quote(urllib.unquote(configUrl))
  jsonString = HTTP.Request("http://surf-proxy.de/index.php?q="+(configUrl))
#  jsonString = HTTP.Request(urllib.unquote(configUrl.strip()))
#  Log(jsonString)
  config = JSON.ObjectFromString(jsonString)
  video = config['playlist'][1]['url']

  return Redirect(video)

