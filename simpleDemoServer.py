import http.server
import socketserver
import json
import os

PORT = 8000  # Choose a port number you like

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
        self.end_headers()

        cpu = disk = memory = ''
        with open("files/cpu.txt", "rb") as file:
            try:
                file.seek(-2, os.SEEK_END)
                while file.read(1) != b'\n':
                    file.seek(-2, os.SEEK_CUR)
            except OSError:
                 file.seek(0)
            cpu = (str)(file.readline()).split(' ')[-2]
 
        with open("files/disk.txt", "rb") as file:
             try:
                 file.seek(-2, os.SEEK_END)
                 while file.read(1) != b'\n':
                     file.seek(-2, os.SEEK_CUR)
             except OSError:
                 file.seek(0)
             disk = (str)(file.readline()).split(' ')[-2]
 
        with open("files/memory.txt", "rb") as file:
             try:
                 file.seek(-2, os.SEEK_END)
                 while file.read(1) != b'\n':
                     file.seek(-2, os.SEEK_CUR)
             except OSError:
                 file.seek(0)
             memory = (str)(file.readline()).split(' ')[-2]
         
        response = {'cpu': f'{cpu}', 'disk' : f'{disk}', 'memory':f'{memory}'}
        response_json = json.dumps(response).encode('utf-8')
        self.wfile.write(response_json)


with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
