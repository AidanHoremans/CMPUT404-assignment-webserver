#  coding: utf-8 
import socketserver
import requests
from enum import Enum
import os
import cgitb
import cgi

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/



class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("\nGot a request of: %s\n" % self.data)
        print ("Client connected from: " + str(self.request))

        if self.data == bytearray("", 'utf-8'):
            return #ignore empty requests

        request = self.data.splitlines()

        if not request or request[0] == '':
            self.request.sendall(bytearray("HTTP/1.1 400 bad request\r\n",'utf-8'))

        #if header is not of type GET, return invalid request 405

        requestType = request[0].split()

        #take requestType, determine a few things
        #the request type, only GET is valid for this program

        # FIRST things, need to make sure the client can accept text/html

        # if path ends with /, see if that path exists. if it does, use index.html
            # if it DNE, then return 404
        # if path doesn't end with /, see if the file exists.
            # if it does, serve it
            # ELSE see if appending / makes the path exist.
                # if it does, then redirect the client with 301 to the index.html at the path with /
                # if not, return 404

        for i in requestType:
            print(str(i))

        #garbage to remove, just for testing
        print("Request type: " + str(requestType[0]))
        print("Request path: " + str(requestType[1]))
        print("Request version: " + str(requestType[2]))

        if requestType[0] == bytearray("GET", 'utf-8'):
            print("detected GET request")

        path = "www" + requestType[1].decode('utf-8')

        if os.path.exists(path):
            #self.request.sendall(bytearray("HTTP/1.1 200 ok\r\nContent-type: text/html\r\n\r\n<TITLE>CGI script output</TITLE> <h1>This is a Heading</h1>",'utf-8'))
            httpResponse = bytearray("HTTP/1.1 200 ok\r\nContent-type: text/html\r\n\r\n",'utf-8') + self.servePage(path)
            print("Sending server -> client response:\n\r" + str(httpResponse))
            self.request.sendall(httpResponse)
            return

        self.request.sendall(bytearray("HTTP/1.1 404 not found", 'utf-8'))

    def servePage(self, path):
        return bytearray(open(path + "index.html", 'r').read(), 'utf-8')

class HTTPRequest():
    def __init__(self):
        return self

class HTTPResponse():

    class HTTPStatus(Enum):
        OK = 200, "ok"
        BADREQUEST = 400, "bad request"
        NOTFOUND = 404, "not found"
        INTERNALSERVERERROR = 500, "internal server error" #likely never used

    def __init__(self, request: HTTPRequest):
        self.httpVersion = "HTTP/1.1"
        self.status = self.determineStatus(request)
        return

    def determineStatus(self, request: HTTPRequest):
        
        return
    


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        server.server_close()
        server.shutdown()

        

