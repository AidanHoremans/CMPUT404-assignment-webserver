from urllib import parse

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

# Contains HTTP status codes and their message
# statusToBytes allows for easy converting to a string for responses

class HTTPRequest():
    def __init__(self, request: bytes):
        # parse request type out of what was sent from the client
        self.path = bytes("", 'utf-8')
        self.query = bytes("", 'utf-8')
        self.payload = bytes("", 'utf-8')
        self.method = bytes("", 'utf-8')
        self.httpVersion = bytes("", 'utf-8')
        self.headers = dict()

        req = request.split(bytes("\r\n\r\n", 'utf-8')) #split payload from headers and method

        if len(req) == 2: #if the request has a payload, attach it
            self.payload = req[1]

        headers = req[0].splitlines()
        topHeader = headers[0].split() #get method, path and version

        if len(topHeader) != 3: #should only have method, path and version
            return

        self.method = topHeader[0]

        try:
            result = parse.urlsplit(topHeader[1]) #parse the path in the request
        except:
            return

        self.path = result.path
        self.query = result.query
        
        self.httpVersion = topHeader[2]

        headers.pop(0) #since we already parsed the first inc method and path and such

        self.headers = self.parse_headers(headers)

    def parse_headers(self, headers):
        headersDict = dict()

        for header in headers:
            currentHeader = str(header, "utf-8").partition(": ")
            headersDict[currentHeader[0]] = currentHeader[2]

        return headersDict
    
    def print_request(self):
        query = self.query.decode('utf-8')
        if query:
            query = "?" + query
        
        return self.method.decode('utf-8') +" "+ self.path.decode('utf-8') + query + " " + self.httpVersion.decode('utf-8')

    def is_valid(self):
        if self.method and self.path and self.httpVersion:
            return True
        return False