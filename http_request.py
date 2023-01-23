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
        requestLines = request.splitlines()
        requestType = requestLines[0].split()

        self.method = requestType[0] #GET, POST, etc...
        self.path = requestType[1] #File path
        self.httpVersion = requestType[2] #Version of the http call

        requestLines.pop(0) #since we already parsed the first

        self.payload = self.parse_payload(requestLines)
        self.headers = self.parse_headers(requestLines) #by this point, we have removed the payload and the first part of the request, leaving only headers

    def parse_payload(self, requestLines):
        payload = bytes("", 'utf-8')

        if len(requestLines) >= 2 and requestLines[-2] == bytes("", 'utf-8'):
            payload = requestLines[-1]
            requestLines.pop()
            requestLines.pop()

        return payload, requestLines

    def parse_headers(self, requestLines):
        headers = dict()

        for header in requestLines:
            currentHeader = str(header, "utf-8").split(':')
            headers[currentHeader[0]] = currentHeader[1]

        return headers