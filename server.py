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



        # FIRST things, need to make sure the client can accept text/html

        # if path ends with /, see if that path exists. if it does, use index.html
            # if it DNE, then return 404
        # if path doesn't end with /, see if the file exists.
            # if it does, serve it
            # ELSE see if appending / makes the path exist.
                # if it does, then redirect the client with 301 to the index.html at the path with /
                # if not, return 404

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("\nGot a request of: %s\n" % self.data)
        print ("Client connected from: " + str(self.request))

        if self.data == bytearray("", 'utf-8'):
            return #ignore empty requests

        request = HTTPRequest(self.data)

        #garbage to remove, just for testing
        print("Request method: " + str(request.method)) #str(requestType[0]))
        print("Request path: " + str(request.path))#str(requestType[1]))
        print("Request version: " + str(request.httpVersion))#str(requestType[2]))

        request.printHeaders()

        if request.method == bytes("GET", 'utf-8'):
            print("GET request:")
            response = HTTPResponse(path=request.path.decode('utf-8'))
            construct = response.constructResponse()
            print(construct)
            self.request.sendall(bytes(construct, 'utf-8'))
            return

        print("invalid request")
        response = HTTPResponse(status = HTTPStatus.METHODNOTALLOWED)
        response.addCustomHeader("Allow", "GET")
        construct = response.constructResponse()
        self.request.sendall(bytes(construct, 'utf-8'))
        return

class HTTPStatus(Enum):
    OK = 200, "Ok"
    MOVEDPERMANENTLY = 301, "Moved Permanently"
    BADREQUEST = 400, "Bad Request"
    NOTFOUND = 404, "Not Found"
    METHODNOTALLOWED = 405, "method not allowed"
    INTERNALSERVERERROR = 500, "Internal Server Error" #likely never used

    def statusToBytes(self):
        return str(self.value[0]) + " " + self.value[1]

class HTTPResponse():
    def __init__(self, path: str = "", status: HTTPStatus = HTTPStatus.OK):
        self.httpVersion = "HTTP/1.1"
        self.status = status
        self.headers = dict()
        self.payload = ""

        if path != "":
            path = self.findPath(path)
            self.setMimeTypes(path)

    #if path exists, and we don't have the correct path ending, redirect to that path /this -> /this/
    def findPath(self, path: str):
        wwwPath = "www" + path

        if os.path.isdir(wwwPath):
            if wwwPath[-1] != "/": #redirect
                self.status = HTTPStatus.MOVEDPERMANENTLY
                self.headers["Location"] = "http://" + str(HOST) + ":" + str(PORT) + str(path) + "/"

            else: #otherwise just fetch index.html
                self.status = HTTPStatus.OK
                wwwPath = wwwPath + "index.html"
                self.payload = open(wwwPath, 'r').read()

        elif os.path.isfile(wwwPath): #check if the file itself exists, otherwise fail
            self.status = HTTPStatus.OK
            self.payload = open(wwwPath, 'r').read()

        else:
            self.status = HTTPStatus.NOTFOUND
            wwwPath = ""

        return wwwPath

    #for html and css file extensions, pass back the correct content type
    def setMimeTypes(self, path):
        if path != "":
            extension = os.path.splitext(path)[1]
            if extension == ".html": #add mime-types for html and css
                self.headers["Content-Type"] = "text/html"
            elif extension == ".css":
                self.headers["Content-Type"] = "text/css"
        return

    #allows for adding a header
    def addCustomHeader(self, key, value):
        self.headers[key] = value
        return

    def constructResponse(self):
        response = ""
        response = response + self.httpVersion + " " + self.status.statusToBytes()
        for key, item in self.headers.items():
            response = response + "\r\n" + str(key) + ": " + str(item)

        if self.payload != "":
            response = response + "\r\n" + self.payload

        response = response + "\r\n\r\n"

        return response


class HTTPRequest():
    def __init__(self, request: bytes):
        # parse request type out of what was sent from the client
        requestLines = request.splitlines()
        requestType = requestLines[0].split()

        self.method = requestType[0]
        self.path = requestType[1]
        self.httpVersion = requestType[2]

        requestLines.pop(0) #since we already parsed the first element

        self.payload = self.parsePayload(requestLines)
        self.headers = self.parseHeaders(requestLines) #by this point, we have removed the payload and the first part of the request, leaving only headers

        #return self

    def parsePayload(self, requestLines: list[bytes]):
        payload = bytes("", 'utf-8')

        if len(requestLines) >= 2 and requestLines[-2] == bytes("", 'utf-8'):
            payload = requestLines[-1]
            requestLines.pop()
            requestLines.pop()

        return payload, requestLines

    def parseHeaders(self, requestLines: list[bytes]):
        headers = dict()

        for header in requestLines:
            currentHeader = str(header, "utf-8").split(':')
            headers[currentHeader[0]] = currentHeader[1]

        return headers

    def printHeaders(self):
        print("--start headers--")
        for key, value in self.headers.items():
            print(key + ": " + value)
        print("--end headers--")
        #return self

if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080

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
        

