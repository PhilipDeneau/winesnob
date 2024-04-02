

from re import U
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from datetime import datetime


def make_request(url, headers=None):
     request = Request(url, headers=headers or {})
     try:
        with urlopen(request, timeout=10) as response:
             #print(response.status)
             return response.read(), response
     except HTTPError as error:
         print(error.status, error.reason)
     except URLError as error:
         print(error.reason)
     except TimeoutError:
         print("Request timed out")

def getSubStr (mainStr, index, startString, endString):
        startIndex = mainStr.find(startString,index)
        if startIndex ==-1:
            return "",-1
        tempIndex = mainStr.find(endString,startIndex)
        if tempIndex ==-1:
            return "",-1
        endIndex = tempIndex
        retStr=mainStr[startIndex+len (startString):endIndex]
        #print (f"Returning {retStr}")
        return mainStr[startIndex+len (startString):endIndex], endIndex

def getWineLink (mainStr, index):
    #<a class="entry-title-link" rel="bookmark" href="https://www.reversewinesnob.com/aldi-specially-selected-alto-adige-pinot-grigio-review/">Aldi
    href,hrefIndex=getSubStr (mainStr,index, "entry-title-link","bookmark" )
    link,linkIndex=getSubStr (mainStr,hrefIndex, 'href="','">')
    
    return link,linkIndex
                 
class wineRating:
    def __str__(self):
       return str(self.__class__) + ": " + str(self.__dict__)

    def __init__(self, name, taste, cost, overAll, buy,url) -> None:
        self.name=name 
        self.taste=taste
        self.cost=cost
        self.overAll=overAll
        self.buy=buy
        self.url=url

def printWineRating (wr):
    print (f"{wr.name}, {wr.buy}, {wr.overAll}, {wr.taste}, {wr.cost}, {wr.url}")
    
    
def readWine (url,html,index):
    #check date
    dateStr,dateIndex = getSubStr(html, 0, 'entry-modified-time">','</time>')
    #print (dateStr)
    dateObj= datetime.strptime(dateStr,"%B %d, %Y")
    startDate=datetime (2022, 1, 1)
    if (dateObj < startDate):
        #print (f"skipping {dateObj} {url}")
        return wineRating ("", "", "", "", "",url)
    greyIndex= html.find ("content-box-gray")
    #print (greyIndex)
    if (greyIndex < 0):
        print (f"Bad url format {url}")
        return wineRating ("", "", "", "", "",url)
    wine,wineIndex = getSubStr(html, greyIndex, "<h2>","</h2")
    #print (wine)
    span,spanIndex = getSubStr(html, wineIndex, "<span","/span>")
    if len(span) < 20:
        print (url)
        print (f"Bad SPAN {span}")
        return wineRating ("", "", "", "", "",url)
    span=''.join(c for c in span if c.isprintable())
    #print (f"SPAN {span}")
    if ("SATURDAY SPLURGE" in span or "Saturday Splurge" in span):
        taste=""
        cost=""
        overAll=""
        rating="Saturday Splurge"
    else :    
        taste,tasteIndex = getSubStr(span, 0, "Taste:","C")
        if (tasteIndex<0):
            taste,tasteIndex = getSubStr(span, 0, "TASTE:"," C")
            tasteIndex=tasteIndex-1
        taste=''.join((ch if ch in '0123456789.-' else ' ') for ch in taste)
        if (len(taste) > 20) :
            print ("Taste"+taste)
        if (len(taste) >3):
            taste=taste.split()[0]
        #print ("Taste"+taste)
        cost,costIndex = getSubStr(span, tasteIndex, "Cost:","<")
        if (costIndex<0):
            cost,costIndex = getSubStr(span, tasteIndex, "COST:","<")
        if (len(cost)>3):
            print ("Cost "+cost)
        cost =''.join((ch if ch in '0123456789.' else ' ') for ch in cost)
        #print ("Cost "+cost)
        overAll,overIndex = getSubStr(html, spanIndex, "OVERALL RATING:","</span>")
        if (overIndex == -1):
            overAll,overIndex = getSubStr(html, spanIndex, "Overall Rating:","</span>")
        if ( "strong" in overAll):
            overAll =''.join((ch if ch in '0123456789.' else ' ') for ch in overAll)
        overAll=overAll.strip()
        #print ("OverallRating "+overAll)

        rating,ratingIndex = getSubStr(html, overIndex, 'rating-system.html\">',"</a>")
        if ("strong" in rating):
            rating,ratingIndex = getSubStr(rating, 0, '<strong>',"</strong>")
        rating=rating.title()
        #print (rating)        
        if (taste == "" or cost == "" or overAll==""):
            print (f" {taste} {cost} {overAll} {span}")
    return wineRating (wine, taste, cost, overAll, rating,url)

def doTopLevelStore (url):
    wineList=[]
    nextPage=url
    skip=["calendar", "Calendar", "CALENDAR", "set", "Set", "SET"]
    while (nextPage!=""):
        #print (f"Processing {nextPage}")
        html_bytes, response = make_request (nextPage, {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"})
        html = html_bytes.decode("utf-8")
        #print (html)
        index=0
        oldIndex=0
        linkList=[]
        while (True):
            link,index=getWineLink (html, index)
            found=False
            for s in skip:
                if s in link:
                    found = True
                    
            if (found == False and link != ""):
                #if ('calendar' not in link and 'Calendar' not in link and 'CALENDAR' not in link):               
                linkList.append(link)
            if (oldIndex == 0 or oldIndex < index):
                oldIndex=index
            elif index < oldIndex :
                break            
        #Look for next page
        nextIndex=html.find('"pagination-next">',oldIndex)
        if ( nextIndex > 0):
            nextPage,nextIndex=getSubStr(html, nextIndex, ' href="','" >')
        else:
            nextPage=""
        #loop through list and process each link
        for l in linkList:
            #print ("\n")
            #print (l)
            url = l
            html_bytes, response = make_request (url, {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"})
            html = html_bytes.decode("utf-8")
            wr=readWine(url,html,0)
            if wr.name != "" :
                wineList.append(wr)
                printWineRating (wr)

    #print("Done")
    

## Aldi
print ("*** ALDI ***")
url="https://www.reversewinesnob.com/aldi-wine"
doTopLevelStore (url)
print ("\n")

print ("*** Costco ***")
url="https://www.reversewinesnob.com/search/label/costco"
doTopLevelStore (url)

print ("*** Trader Joes ***")
url="https://www.reversewinesnob.com/search/label/trader-joes/"
doTopLevelStore (url)
print ("\n")
