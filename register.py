import sys
import urllib
import urllib2
from urlgrabber.keepalive import HTTPHandler

def craft_params(params):
    return urllib.unquote(urllib.urlencode(params))

headers = [
    ("User-Agent", "Withings UserAgentaasdasdasdas"), # apparently this doesn't matter
    ("Accept", "*/*"),
]

def do_request(opener, url, data):
    req = urllib2.Request(url, data)
    opener.addheaders = headers
    return opener.open(req).read()

urlbase  = "http://scalews.withings.net/cgi-bin/"
urlonce  = urlbase + "once"
urlsess  = urlbase + "session"
urlmaint = urlbase + "maint"
urlassoc = urlbase + "association"

opener = urllib2.build_opener(HTTPHandler()) # Keep-alive

##
# Step 1: /cgi-bin/once
##

params = {
    "action": "get"
}

data = craft_params(params)

print do_request(opener, urlonce, data)

if len(sys.argv) == 1:
    exit()

##
# Step 2: /cgi-bin/session
##

params = {
    "action": "new",
    "auth": "00:24:e4:06:59:dc",
    "hash": sys.argv[1],
    "mfgid": "262151",
    "currentfw": "200",
    "batterylvl": "69",
    "duration": "30",
    "zreboot": "1"
}

data = craft_params(params)

print do_request(opener, urlsess, data)

##
# Step 3: /cgi-bin/
