# -*- coding: utf-8 -*-
import re

ESCAPIST_PREFIX = '/video/escapist'

ESCAPIST_URL            = 'http://www.escapistmagazine.com'
ESCAPIST_GALERIES       = ESCAPIST_URL + '/vidoes/galleries'
ESCAPIST_HIGHLIGHTS     = ESCAPIST_URL + '/ajax/videos_index.php?videos_type=%s'

def Start():

  Plugin.AddPrefixHandler(ESCAPIST_PREFIX, MainMenu, L('theescapist'), 'icon-default.jpg', 'art-default.jpg')
  Plugin.AddViewGroup('Details', viewMode='List', mediaType='items')
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.jpg')
  MediaContainer.viewGroup = 'Details'
  MediaContainer.title1 = L('theescapist')
  
  DirectoryItem.thumb = R('icon-default.jpg')
  VideoItem.thumb = R('icon-default.jpg')
    
  HTTP.CacheTime  = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'

def MainMenu():

  dir = MediaContainer()
 
  page = HTML.ElementFromURL(ESCAPIST_URL + '/videos/galleries')

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
      dir.Append(Function(DirectoryItem(ShowBrowser, title=title, thumb=Function(Thumb,url=thumb), summary=summary), showUrl=url, showName=title, showThumb=thumb))

  return dir
  
def Thumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R('icon-default.jpg'))

def ShowBrowser(sender, showUrl, showName, showThumb, pageNumber=1):

  dir = MediaContainer()

  if pageNumber > 1:
    pageUrl = showUrl + "?page=" + str(pageNumber)
    dir.title1 = showName
    dir.title2 = L('page') + ' ' + str(pageNumber)
  else:
    dir.title2 = showName
    pageUrl = showUrl

  page = HTML.ElementFromURL(pageUrl)

  episodes = page.xpath("//div[@class='video']//div[@id='gallery_display']//div[@class='filmstrip_video']")

  for episode in episodes:

    title = episode.xpath(".//div[@class='title']")[0].text
    date = episode.xpath(".//div[@class='date']")[0].text
    url = episode.xpath(".//a")[0].get('href')
#    Log(url[0:4])
    if url[0:4] != 'http':
      url = ESCAPIST_URL + url
    
    thumb = episode.xpath(".//img")[0].get('src')
    Log(thumb)
    
    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, duration='0', thumb=Function(Thumb,url=thumb)), url=url))

  # Check for a next page link
  if len ( page.xpath("//a[@class='next_page']")) > 0:
    pageNumber = pageNumber + 1
    dir.Append(Function(DirectoryItem(ShowBrowser, title=L('nextpage'), thumb=Function(Thumb,url=showThumb), summary=L('nextpage')), showUrl=showUrl, showName=showName, showThumb=Function(Thumb,url=showThumb), pageNumber=pageNumber))

  return dir

def HighlightBrowser(sender, mode):

  dir = MediaContainer()
  dir.title2 = (mode)

  page = HTML.ElementFromURL(ESCAPIST_HIGHLIGHTS % mode)

  episodes = page.xpath("//div[@class='filmstrip_video']")

  for episode in episodes:

    title = episode.xpath(".//div[@class='title']")[0].text
    date = episode.xpath(".//div[@class='date']")[0].text
    url = episode.xpath(".//a")[0].get('href')
    if url[0:4] != 'http':
      url = ESCAPIST_URL + url
    thumb = episode.xpath(".//img")[0].get('src')
    
    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, duration='0', thumb=Function(Thumb,url=thumb)), url=url))

  return dir

def PlayVideo(sender, url):

  # Find the FLV for the episode and redirect to it
#  Log(url)
  rawpage = HTTP.Request(url).content.replace('&lt;','<').replace('&gt;','>').replace('&quot;','"')
  page = HTML.ElementFromString(rawpage)

  configElement = page.xpath("//div[@id='video_embed']//embed")[0].get('flashvars')
  configUrl = re.search(r'config=(.*)', configElement).group(1)
  configUrl = String.Unquote(configUrl, usePlus=True)
  jsonString = HTTP.Request("http://surf-proxy.de/index.php?q=" + String.Quote(configUrl, usePlus=True)).content
#  Log(jsonString)
  config = JSON.ObjectFromString(jsonString)
  video = config['playlist'][1]['url']

  return Redirect(video)
