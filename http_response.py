from http_status import HTTPStatus
from http_request import HTTPRequest
import os
import server_constants as server

# Copyright 2023 Aidan Horemans
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

class HTTPResponse():
    def __init__(self, request:HTTPRequest=None, status: HTTPStatus = HTTPStatus.OK):
        self.httpVersion = "HTTP/1.1"
        self.status = status
        self.headers = dict()
        self.payload = ""

        if request != None:
            requestPath = request.path.decode('utf-8')
            requestQuery = request.query.decode('utf-8')

            filePath = self.open_path(requestPath, requestQuery)
            self.set_mime_types(filePath)
        return

    #if path exists, and we don't have the correct path ending, redirect to that path /this -> /this/
    def open_path(self, rootPath: str, requestQuery: str):

        path = "www" + rootPath

        if not self.is_safe_path(rootPath):
            self.status = HTTPStatus.NOTFOUND
            path = ""
            return path

        if os.path.isdir(path): #check if the given path is a directory
            if path[-1] != "/": #check if path ends with /, if not, we need to redirect
                self.status = HTTPStatus.MOVEDPERMANENTLY

                #redirect with query
                if requestQuery != "":
                    requestQuery = "?" + requestQuery
                
                redirectUrl = "http://" + str(server.HOST) + ":" + str(server.PORT) + str(rootPath) + "/" + str(requestQuery)

                self.add_custom_header("Location", redirectUrl)

            else: #otherwise if path DOES end with /, just serve index.html
                self.status = HTTPStatus.OK
                path = path + "index.html"
                self.payload = open(path, 'r').read()

        elif os.path.isfile(path): #check if the file itself exists,
            self.status = HTTPStatus.OK
            self.payload = open(path, 'r').read()

        else: #selected path is neither a file nor a directory, dne
            self.status = HTTPStatus.NOTFOUND
            path = ""

        return path

    def is_safe_path(self, path: str):
        depth = 0
        levels = path.split('/')

        for level in levels:
            if level:
                if level == "..":
                    depth -= 1
                else:
                    depth += 1

        if depth < 0:
            return False
        
        return True

    #for html and css file extensions, pass back the correct content type
    def set_mime_types(self, path):
        value = "text/plain" #tried to use application/octet-stream as default, but firefox automatically downloads files of that mime-type
        if path != "":
            extension = os.path.splitext(path)[1]
            if extension == ".html": #add mime-types for html and css
                value = "text/html"
            elif extension == ".css":
                value = "text/css"
            self.add_custom_header("Content-Type", value)
        return

    def construct_response(self):
        self.add_custom_header("Content-Length", len(self.payload)) #Figure out the length of the payload

        response = "" #begin creating response

        response += self.httpVersion + " " + self.status.status_to_bytes()

        for key, item in self.headers.items():
            response += "\r\n" + str(key) + ": " + str(item)

        response += "\r\n\r\n" + self.payload #add even if empty, just make sure we have the correct payload length
        
        return bytes(response, 'utf-8')

    #allows for adding a header
    def add_custom_header(self, key, value):
        self.headers[key] = value