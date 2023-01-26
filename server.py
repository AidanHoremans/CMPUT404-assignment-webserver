#  coding: utf-8 
import socketserver
from http_response import HTTPResponse
from http_status import HTTPStatus
from http_request import HTTPRequest
import server_constants as server
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Aidan Horemans
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
        except Exception as e:
            httpResponse = HTTPResponse(status = HTTPStatus.INTERNALSERVERERROR)
            print("The server threw an exception (whoops), responding with 500...")
            print(f"Exception of: {e}")
            self.request.sendall(httpResponse.construct_response())

    def handle_request(self):
        self.data = self.request.recv(1024).strip()

        if self.data == bytearray("", 'utf-8'):
            return #ignore empty requests

        httpRequest = HTTPRequest(self.data)

        print(f"Received request of {httpRequest.print_request()}")

        #httpRequest.path = bytes("/../../../../", 'utf-8')

        base = os.getcwd()
        requested = os.path.abspath(os.getcwd() + "/www" + httpRequest.path.decode('utf-8')) #abs path calculates the actual path


        print(base)
        print(requested)

        print(os.path.commonprefix([base, requested]))

        response = HTTPResponse(httpRequest)

        print(f"Responding with {response.status.status_to_string()}\n")

        constructedResponse = response.construct_response()
        self.request.sendall(constructedResponse)
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
        

