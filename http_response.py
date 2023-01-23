from http_status import HTTPStatus
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
    def __init__(self, path: str = "", status: HTTPStatus = HTTPStatus.OK):
        self.httpVersion = "HTTP/1.1"
        self.status = status
        self.headers = dict()
        self.payload = ""

        if path != "":
            path = self.open_path(path)
            self.set_mime_types(path)

    #if path exists, and we don't have the correct path ending, redirect to that path /this -> /this/
    def open_path(self, path: str):
        wwwPath = "www" + path

        if os.path.isdir(wwwPath):
            if wwwPath[-1] != "/": #redirect
                self.status = HTTPStatus.MOVEDPERMANENTLY
                self.headers["Location"] = "http://" + str(server.HOST) + ":" + str(server.PORT) + str(path) + "/"

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
    def set_mime_types(self, path):
        if path != "":
            extension = os.path.splitext(path)[1]
            if extension == ".html": #add mime-types for html and css
                self.headers["Content-Type"] = "text/html"
            elif extension == ".css":
                self.headers["Content-Type"] = "text/css"
        return

    #allows for adding a header
    def add_custom_header(self, key, value):
        self.headers[key] = value
        return

    def construct_response(self):
        self.add_custom_header("Content-Length", len(self.payload)) #Figure out the length of the payload

        response = "" #begin creating response

        response += self.httpVersion + " " + self.status.status_to_bytes()

        for key, item in self.headers.items():
            response += "\r\n" + str(key) + ": " + str(item)

        response += "\r\n\r\n" + self.payload #add even if empty, just make sure we have the correct payload length
        
        return bytes(response, 'utf-8')