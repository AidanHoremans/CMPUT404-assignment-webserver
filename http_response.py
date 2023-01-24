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

        if request == None: #for basic responses that don't need anything above a status, return here
            return

        if request.method == bytes("GET", 'utf-8'):
            requestPath = request.path.decode('utf-8')
            requestQuery = request.query.decode('utf-8')

            filePath = self.open_path(requestPath, requestQuery)
            if self.is_status_successful(): #need to make sure the status is successful for opening the desired path before we give away mime-type information
                self.set_mime_types(filePath)

        else: #unsupported method
            self.status = HTTPStatus.METHODNOTALLOWED
            self.add_custom_header("Allow", "GET")
        return

    def is_status_successful(self):
        return self.status.value[0] >= 200 and self.status.value[0] <= 299

    def add_custom_header(self, key, value):
        self.headers[key] = value

    #if path exists, and we don't have the correct path ending, redirect to that path /this -> /this/
    def open_path(self, rootPath: str, requestQuery: str):

        path = server.FILEDIRECTORY + rootPath

        if not self.is_safe_path(rootPath):
            self.status = HTTPStatus.NOTFOUND
            path = "" #just in case, reset the path, dont want unsafe paths floating around
            return path

        if os.path.isdir(path): #check if the given path is a directory
            if path[-1] != "/": #check if path ends with /, if not, we need to redirect

                self.status = HTTPStatus.MOVEDPERMANENTLY

                #redirect with query
                if requestQuery != "":
                    requestQuery = "?" + requestQuery
                
                redirectUrl = "http://" + str(server.HOST) + ":" + str(server.PORT) + str(rootPath) + "/" + str(requestQuery)

                self.add_custom_header("Location", redirectUrl)

                return #we are done with the path for the redirect

            else: #otherwise if path DOES end with /, just serve index.html -> i.e. fall into the if os.path.isfile(path) assuming index.html exists
                path = path + "index.html"

        if os.path.isfile(path): #check if the file itself exist
            self.status = HTTPStatus.OK
            self.payload = open(path, 'r').read()

        else: #selected path is neither a file nor a directory, dne
            self.status = HTTPStatus.NOTFOUND

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

        return depth >= 0

    #for html and css file extensions, pass back the correct content type
    def set_mime_types(self, path):
        value = "text/plain" #tried to use application/octet-stream as default, but firefox automatically downloads files of that mime-type
        if path != "":
            extension = os.path.splitext(path)[1]
            if extension == ".html": #add mime-types for html and css
                value = "text/html"
            elif extension == ".css":
                value = "text/css"
            self.add_custom_header("Content-Type", value) #only add the header if path is not empty
        return

    def construct_response(self):
        self.add_custom_header("Content-Length", len(self.payload)) #Figure out the length of the payload

        response = "" #begin creating response

        response += self.httpVersion + " " + self.status.status_to_bytes()

        for key, item in self.headers.items():
            response += "\r\n" + str(key) + ": " + str(item)

        response += "\r\n\r\n" + self.payload #add even if empty, just make sure we have the correct payload length
        
        return bytes(response, 'utf-8')