import hashlib
import Image
import json
import sys
import time
import urllib
import urllib2
from urlgrabber.keepalive import HTTPHandler

MARGIN = 3000

urlbase  = "http://scalews.withings.net/cgi-bin/"
urlonce  = urlbase + "once"
urlsess  = urlbase + "session"
urlmaint = urlbase + "maint"
urlassoc = urlbase + "association"
urlmeas  = urlbase + "measure"

def craft_params(params):
    return urllib.unquote(urllib.urlencode(params))

def do_request(opener, url, data):
    req = urllib2.Request(url, data)
    opener.addheaders = headers
    return opener.open(req).read()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "%s <mac_addr> <secret> <image>" % sys.argv[0]
        exit()

    mac_addr = sys.argv[1]
    secret = sys.argv[2]

    headers = [
        ("User-Agent", "Withings UserAgent"),
        ("Accept", "*/*"),
    ]

    opener = urllib2.build_opener(HTTPHandler()) # Keep-alive

    ##
    # Step 1: /cgi-bin/once
    ##

    params = {
        "action": "get"
    }

    data = craft_params(params)

    resp = do_request(opener, urlonce, data)

    print resp

    once = json.loads(resp)["body"]["once"]

    ##
    # Step 2: /cgi-bin/session
    ##

    md5 = hashlib.md5()
    md5.update("%s:%s:%s" % (mac_addr, secret, once))
    hash_calc = md5.digest().encode("hex")

    params = {
        "action": "new",
        "auth": mac_addr,
        "hash": hash_calc,
        "mfgid": "262151",
        "currentfw": "200",
        "batterylvl": "1337",
        "duration": "30",
        "zreboot": "1"
    }

    data = craft_params(params)

    resp = do_request(opener, urlsess, data)

    print resp

    tmp = json.loads(resp)
    sessionid = tmp["body"]["sessionid"]
    user_id = tmp["body"]["sp"]["users"][0]["id"]

    ##
    # Step 3: /cgi-bin/measure
    ##

    curtime = int(time.time())
    print "Current time: %d" % curtime

    im = Image.open(sys.argv[3])

    width, height = im.size
    print "Image width: %d" % width
    print "Image height: %d" % height

    print "Iterating pixels..."
    pix = im.load()
    count = 0

    for x in xrange(width):
        points = {
            "measures": [
            ]
        }

        for y in xrange(height):
            a, b, c, d = pix[x,y]
            if a < 128:
                point = {
                    "value": 20000 + ((height - y) * MARGIN),
                    "type": 1,
                    "unit": -3
                }
                points["measures"].append(point)
                count += 1
        print "total points = %d" % count

        if len(points["measures"]) == 0:
            print "Blank column, skipping request"
            continue

        params = {
            "action": "store",
            "sessionid": sessionid,
            "macaddress": mac_addr,
            "userid": user_id,
            "meastime": curtime - ((width - x) * MARGIN),
            "devtype": 1,
            "attribstatus": 0,
            "measures": urllib.quote_plus(json.dumps(points, separators=(",", ":")))
        }

        data = craft_params(params)

        print data

        resp = do_request(opener, urlmeas, data)

        print resp

    ##
    # Step 4: /cgi-bin/session
    ##

    params = {
        "action": "delete",
        "sessionid": sessionid
    }

    data = craft_params(params)

    print data

    resp = do_request(opener, urlsess, data)

    print resp
