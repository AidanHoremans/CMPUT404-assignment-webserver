#  coding: utf-8 
import socketserver
from http_response import HTTPResponse
from http_status import HTTPStatus
from http_request import HTTPRequest
import server_constants as server

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, ME?
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
#
# try: curl -v -X GET http://127.0.0.1:8080/

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        try:
            self.handle_request()
        except:
            httpResponse = HTTPResponse(status = HTTPStatus.INTERNALSERVERERROR)
            print("The server threw an exception (whoops), responding with 500...")
            self.request.sendall(httpResponse.construct_response())

    def handle_request(self):
        self.data = self.request.recv(1024).strip()

        if self.data == bytearray("", 'utf-8'):
            return #ignore empty requests

        print("\nGot a request of: %s\n" % self.data)
        print("Client connected to: " + str(self.request))

        httpRequest = HTTPRequest(self.data)

        #garbage to remove, just for testing
        print("Request method: " + str(httpRequest.method))
        print("Request path: " + str(httpRequest.path))
        print("Request version: " + str(httpRequest.httpVersion))

        if httpRequest.method == bytes("GET", 'utf-8'):
            print("GET request:")
            response = HTTPResponse(path = httpRequest.path.decode('utf-8'))
            constructedResponse = response.construct_response()
            print(constructedResponse)
            self.request.sendall(constructedResponse)
            return

        print("invalid request")
        response = HTTPResponse(status = HTTPStatus.METHODNOTALLOWED)
        response.add_custom_header("Allow", "GET")
        self.request.sendall(response.construct_response())
        return

if __name__ == "__main__":

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((server.HOST, server.PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        server.server_close()
        server.shutdown()
        

