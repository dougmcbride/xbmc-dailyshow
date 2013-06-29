import urllib,urllib2,re,xbmcplugin,xbmcgui
import os,datetime
import demjson
import BeautifulSoup

DATELOOKUP = "http://www.thedailyshow.com/feeds/timeline/coordinates/"

pluginhandle = int(sys.argv[1])
shownail = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),"icon.png"))
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(pluginhandle, fanart, color2='0xFFFF3300')
TVShowTitle = 'The Daily Show'

if xbmcplugin.getSetting(pluginhandle,"sort") == '0':
    SORTORDER = 'date'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '1':
    SORTORDER = 'views'
elif xbmcplugin.getSetting(pluginhandle,"sort") == '2':
    SORTORDER = 'rating'

################################ Common
def getURL( url ):
    try:
        print 'The Daily Show --> getURL :: url = '+url
        txdata = None
        txheaders = {
            'Referer': 'http://www.thedailyshow.com/videos/',
            'X-Forwarded-For': '12.13.14.15',
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)',
            }
        req = urllib2.Request(url, txdata, txheaders)
        #req = urllib2.Request(url)
        #req.addheaders = [('Referer', 'http://www.thedailyshow.com/videos'),
        #                  ('Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)')]
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
    except urllib2.URLError, e:
        error = 'Error code: '+ str(e.code)
        xbmcgui.Dialog().ok(error,error)
        print 'Error code: ', e.code
        return False
    else:
        return link

def addLink(name,url,iconimage='',plot=''):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot, "TVShowTitle":TVShowTitle})
    liz.setProperty('fanart_image',fanart)
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=url,listitem=liz)
    return ok

def addDir(name,url,mode,iconimage=shownail,plot=''):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot":plot, "TVShowTitle":TVShowTitle})
    liz.setProperty('fanart_image',fanart)
    ok=xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz,isFolder=True)
    return ok

def pageFragments(url):
    pageNum = int(url[-1])
    nextPage = pageNum + 1
    nurl = url.replace('page='+str(pageNum),'page='+str(nextPage))
    prevPage = pageNum - 1
    purl = url.replace('page='+str(pageNum),'page='+str(prevPage))
    if '/box' in nurl or '/box' in purl:
        nurl = nurl.replace('/box','')
        purl = purl.replace('/box','')
    data = getURL(nurl)
    if 'Your search returned zero results' not in data:
        addDir('Next Page ('+str(nextPage)+')',nurl,7)
    if prevPage >= 1:
        addDir('Previous Page ('+str(prevPage)+')',purl,7)
    LISTVIDEOS(url)
    xbmcplugin.endOfDirectory(pluginhandle,updateListing=True)

################################ Root listing
def ROOT():
    addDir('Full Episodes','full',5)
    addDir('Guests','guests',3)
    xbmcplugin.endOfDirectory(pluginhandle)

def FULLEPISODES():
    xbmcplugin.setContent(pluginhandle, 'episodes')
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_NONE)
    full = 'http://www.thedailyshow.com/full-episodes/'
    allData = getURL(full)

    episodeURLs = re.compile('<a href="(http://www.thedailyshow.com/full-episodes/....+?)"').findall(allData) 
    episodeURLSet = set(episodeURLs)

    listings = []
    for episodeURL in episodeURLs:
        if episodeURL in episodeURLSet:
            episodeURLSet.remove(episodeURL)
            episodeData = getURL(episodeURL)

            title=re.compile('<meta property="og:title" content="(.+?)"').search(episodeData)
            thumbnail=re.compile('<meta property="og:image" content="(.+?)"').search(episodeData)
            description=re.compile('<meta property="og:description" content="(.+?)"').search(episodeData)
            airDate=re.compile('<meta itemprop="uploadDate" content="(.+?)"').search(episodeData)
            epNumber=re.compile('/season_\d+/(\d+)').search(episodeData)
            link=re.compile('<link rel="canonical" href="(.+?)"').search(episodeData)

            listing = []
            listing.append(title.group(1))
            listing.append(link.group(1))
            listing.append(thumbnail.group(1))
            listing.append(description.group(1))
            listing.append(airDate.group(1))
            listing.append(epNumber.group(1))
            listings.append(listing)

    print listings

    for name, link, thumbnail, plot, date, seasonepisode in listings:
        mode = 10
        season = int(seasonepisode[:-3])
        episode = int(seasonepisode[-3:])
        u=sys.argv[0]+"?url="+urllib.quote_plus(link)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        u += "&season="+urllib.quote_plus(str(season))
        u += "&episode="+urllib.quote_plus(str(episode))
        u += "&premiered="+urllib.quote_plus(date)
        u += "&plot="+urllib.quote_plus(plot)
        u += "&thumbnail="+urllib.quote_plus(thumbnail)
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": BeautifulSoup.BeautifulSoup(name, convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES),
                                                "Plot": BeautifulSoup.BeautifulSoup(plot, convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES),
                                                "Season":season,
                                                "Episode": episode,
                                                "premiered":date,
                                                "TVShowTitle":TVShowTitle})
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image',fanart)
        xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)

    xbmcplugin.endOfDirectory(pluginhandle)




class Guest(object):
    def __init__(self,data):
        self.soup = data

    def day(self):        
        raw_text = self.soup('a',{'class' : 'full-episode-url'})[0].getText()

        raw_text = raw_text.replace('Full Episode Available','')
        m = re.search(r'(.*) - .*', raw_text)

        return m.group(1)

    def name(self):
        return self.soup('span', {'class' : 'title'})[0].getText().replace('Exclusive - ','')

    def url(self):
        return self.soup('a', {'class' : 'imageHolder'})[0]['href']

def GUESTS():
    gurl = "http://www.thedailyshow.com/feeds/search?keywords=&tags=interviews&sortOrder=desc&sortBy=date&page=1"
    data = getURL(gurl).replace('</pre>','</div>')

    soup = BeautifulSoup.BeautifulSoup(data)

    guest_items = soup('div', {'class' : 'entry'})
    mode = 10
    for item in guest_items:
        g = Guest(item)
        
        liz=xbmcgui.ListItem(g.name(), iconImage='', thumbnailImage='')
        liz.setInfo( type="Video", infoLabels={ "Title": g.name(),
                                                "TVShowTitle":'The Daily Show'})
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image',fanart)
        
        
        u=sys.argv[0]+"?url="+g.url()+"&mode="+str(mode)+"&name="+g.name()
        
        xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u, listitem=liz)

    xbmcplugin.endOfDirectory(pluginhandle)

################################ List Videos

def LISTVIDEOS(url):
    xbmcplugin.setContent(pluginhandle, 'episodes')
    data = getURL(url)
    playbackUrls=re.compile('<a href="http://www.thedailyshow.com/watch/(.+?)".+?>').findall(data)
    thumbnails=re.compile("<img width='.+?' height='.+?' src='(.+?)'").findall(data)
    names=re.compile('<span class="title"><a href=".+?">(.+?)</a></span>').findall(data)
    descriptions=re.compile('<span class="description">(.+?)\(.+?</span>').findall(data)
    durations=re.compile('<span class="description">.+?\((.+?)</span>').findall(data)
    epNumbers=re.compile('<span class="episode">Episode #(.+?)</span>').findall(data)
    airdates=re.compile('<span>Aired.+?</span>(.+?)</div>').findall(data)
    for pb in playbackUrls:
        url = "http://www.thedailyshow.com/watch/"+pb
        marker = playbackUrls.index(pb)
        
        log( 'marker --> %s' % marker )
        log('names --> %s' % names)
        
        thumbnail = thumbnails[marker]
        fname = names[marker]
        description = descriptions[marker]
        duration = durations[marker].replace(')','')
        try:
            seasonepisode = epNumbers[marker]
            season = int(seasonepisode[:-3])
            episode = int(seasonepisode[-3:])
        except:
            season = 0
            episode = 0
        date = airdates[marker]
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(13)+"&name="+urllib.quote_plus(fname)
        u += "&season="+urllib.quote_plus(str(season))
        u += "&episode="+urllib.quote_plus(str(episode))
        u += "&premiered="+urllib.quote_plus(date)
        u += "&plot="+urllib.quote_plus(plot)
        u += "&thumbnail="+urllib.quote_plus(thumbnail)
        liz=xbmcgui.ListItem(fname, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
        liz.setInfo( type="Video", infoLabels={ "Title": fname,
                                                "Episode":episode,
                                                "Season":season,
                                                "Plot":description,
                                                "premiered":date,
                                                "Duration":duration,
                                                "TVShowTitle":TVShowTitle})
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('fanart_image',fanart)
        xbmcplugin.addDirectoryItem(handle=pluginhandle,url=u,listitem=liz)



################################ Play Video

def PLAYVIDEO(name,url):
    data = getURL(url)
    uri = re.compile('"http://media.mtvnservices.com/(.+?)"/>').findall(data)[0].replace('fb/','').replace('.swf','')
    
    print 'uri --> %s' % uri
    
    rtmp = GRAB_RTMP(uri)
    item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail, path=rtmp)
    item.setInfo( type="Video", infoLabels={ "Title": name,
                                             "Plot":plot,
                                             "premiered":premiered,
                                             "Season":int(season),
                                             "Episode":int(episode),
                                             "TVShowTitle":TVShowTitle})
    item.setProperty('fanart_image',fanart)
    
    print 'item --> %s' % item
    
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

################################ Play Full Episode

def PLAYFULLEPISODE(name,url):
    data = getURL(url)
    uri = re.compile('(mgid:cms:episode:thedailyshow.com:\d{6}|mgid:cms:video:thedailyshow.com:\d{6})').findall(data)[0]
    #url = 'http://media.mtvnservices.com/player/config.jhtml?uri='+uri+'&group=entertainment&type=network&site=thedailyshow.com'
    url = 'http://shadow.comedycentral.com/feeds/video_player/mrss/?uri='+uri
    data = getURL(url)
    uris=re.compile('<guid isPermaLink="false">(.+?)</guid>').findall(data)
    stacked_url = 'stack://'
    for uri in uris:
        rtmp = GRAB_RTMP(uri)
        stacked_url += rtmp.replace(',',',,')+' , '
    stacked_url = stacked_url[:-3]
    
    print 'stacked_url --> %s' % stacked_url
    
    item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumbnail, path=stacked_url)
    
    print 'item --> %s' % item
    
    item.setInfo( type="Video", infoLabels={ "Title": name,
                                             "Plot":plot,
                                             "premiered":premiered,
                                             "Season":int(season),
                                             "Episode":int(episode),
                                             "TVShowTitle":TVShowTitle})
    item.setProperty('fanart_image',fanart)
    
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    

################################ Grab rtmp        

def GRAB_RTMP(uri):
    swfurl = 'http://media.mtvnservices.com/player/release/?v=4.5.3'
    url = 'http://www.comedycentral.com/global/feeds/entertainment/media/mediaGenEntertainment.jhtml?uri='+uri+'&showTicker=true'
    mp4_url = "http://mtvnmobile.vo.llnwd.net/kip0/_pxn=0+_pxK=18639+_pxE=/44620/mtvnorigin"
    data = getURL(url)
    widths = re.compile('width="(.+?)"').findall(data)
    heights = re.compile('height="(.+?)"').findall(data)
    bitrates = re.compile('bitrate="(.+?)"').findall(data)
    rtmps = re.compile('<src>rtmp(.+?)</src>').findall(data)
    
    print 'rtmps --> %s' % rtmps
    
    mpixels = 0
    mbitrate = 0
    lbitrate = 0
    if xbmcplugin.getSetting(pluginhandle,"bitrate") == '0':
        lbitrate = 0
    elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '1':
        lbitrate = 1720
    elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '2':
        lbitrate = 1300
    elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '3':
        lbitrate = 960
    elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '4':
        lbitrate = 640
    elif xbmcplugin.getSetting(pluginhandle,"bitrate") == '5':
        lbitrate = 450
    for rtmp in rtmps:
        print 'processing rtmp: %s' % rtmp
        marker = rtmps.index(rtmp)
        w = int(widths[marker])
        h = int(heights[marker])
        bitrate = int(bitrates[marker])
        if bitrate == 0:
            continue
        elif bitrate > lbitrate and lbitrate <> 0:
            continue
        elif lbitrate <= bitrate or lbitrate == 0:
            pixels = w * h
            if pixels > mpixels or bitrate > mbitrate:
                mpixels = pixels
                mbitrate = bitrate
                furl = mp4_url + rtmp.split('viacomccstrm')[2]
                #rtmpsplit = rtmp.split('/ondemand')
                #server = rtmpsplit[0]
                #path = rtmpsplit[1].replace('.flv','')
                #if '.mp4' in path:
                #    path = 'mp4:' + path
                #port = ':1935'
                #app = '/ondemand?ovpfv=2.1.4'
                #furl = 'rtmp'+server+port+app+path+" playpath="+path+" swfurl="+swfurl+" swfvfy=true"

    print 'furl --> %s' % furl
    return furl


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]

    return param


params=get_params()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    thumbnail=urllib.unquote_plus(params["thumbnail"])
except:
    thumbnail=''
try:
    season=int(params["season"])
except:
    season=0
try:
    episode=int(params["episode"])
except:
    episode=0
try:
    premiered=urllib.unquote_plus(params["premiered"])
except:
    premiered=''
try:
    plot=urllib.unquote_plus(params["plot"])
except:
    plot=''

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)


if mode==None or url==None or len(url)<1:
    ROOT()
elif mode==3:
    GUESTS()
elif mode==5:
    FULLEPISODES()
elif mode==7:
    pageFragments(url)
elif mode==9:
    LISTVIDEOS(url)
elif mode==10:
    PLAYFULLEPISODE(name,url)
elif mode==13:
    PLAYVIDEO(name,url)
