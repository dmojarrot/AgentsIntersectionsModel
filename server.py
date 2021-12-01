from http.server import HTTPServer, BaseHTTPRequestHandler
from AgentsIntersection import runModel
import json

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        with open('archivoPosJson.json') as file:
            data = json.load(file)
        print(data)
        data = json.dumps(data)
        response = data
        # send 200 response
        self.send_response(200)
        # send response headers
        self.end_headers()
        # send the body of the response
        self.wfile.write(bytes(response, "utf-8"))

    def do_GET(self):
        with open('archivoPosJson.json') as file:
            data = json.load(file)
        print(data)
        data = json.dumps(data)
        response = data
        # send 200 response
        self.send_response(200)
        # send response headers
        self.end_headers()
        # send the body of the response
        self.wfile.write(bytes(response, "utf-8"))

runModel()
httpd = HTTPServer(('localhost', 8000), MyHandler)
httpd.serve_forever()
