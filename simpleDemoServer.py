import http.server
import socketserver
import json
import os
import sys

PORT = 8001  # Choose a port number you like

class MyHandler(http.server.BaseHTTPRequestHandler):

    def read_data(self, path):
        with open(path, "rb") as file:
            try:
                file.seek(-2, os.SEEK_END)
                while file.read(1) != b'\n':
                    file.seek(-2, os.SEEK_CUR)
            except OSError:
                file.seek(0)
        return file.readline().split(' ')[-1]

    def do_GET(self):
        # Read the request path
        path = self.path

        # Set the response status code
        self.send_response(200)

        # Set the response headers
        self.send_header('Content-type', 'application/json')
        self.send_header("Access-Control-Allow-Origin", "http://localhost:3000")
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
        self.end_headers()

        cpu = disk = memory = ''
        ts_cpu = ts_disk = ts_memory = '' # ts - TimeStamp
        with open(sys.path[0] + "/files/cpu.txt", "rb") as file:
            try:
                file.seek(-2, os.SEEK_END)
                while file.read(1) != b'\n':
                    file.seek(-2, os.SEEK_CUR)
            except OSError:
                 file.seek(0)
            line = (str)(file.readline()).split(' ')
            cpu = line[-2]
            ts_cpu = line[0]
            
 
        with open(sys.path[0] + "/files/disk.txt", "rb") as file:
             try:
                 file.seek(-2, os.SEEK_END)
                 while file.read(1) != b'\n':
                     file.seek(-2, os.SEEK_CUR)
             except OSError:
                 file.seek(0)
             line = (str)(file.readline()).split(' ')
             disk = line[-2]
             ts_disk = line[0]
 
        with open(sys.path[0] + "/files/memory.txt", "rb") as file:
             try:
                 file.seek(-2, os.SEEK_END)
                 while file.read(1) != b'\n':
                     file.seek(-2, os.SEEK_CUR)
             except OSError:
                 file.seek(0)
             line = (str)(file.readline()).split(' ')
             memory = line[-2]
             ts_memory = line[0]
         
        response = {'cpu': f'{cpu}', 'disk' : f'{disk}', 'memory':f'{memory}', ts_cpu:f'{ts_cpu}'
                    , ts_disk:f'{ts_disk}', ts_memory:f'{ts_memory}'}
        response_json = json.dumps(response).encode('utf-8')
        self.wfile.write(response_json)
        


with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
