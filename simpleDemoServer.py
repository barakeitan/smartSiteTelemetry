import http.server
import socketserver
import json
import os
import sys
import datetime


PORT = 8000  # Choose a port number you like

class MyHandler(http.server.BaseHTTPRequestHandler):

    def read_data(self, path):
        line = []
        with open(path, "rb") as file:
            try:
                file.seek(-2, os.SEEK_END)
                while file.read(1) != b'\n':
                    file.seek(-2, os.SEEK_CUR)
            except OSError:
                file.seek(0)
            line = (str)(file.readline()).split(' ')
#           timestamp = f'{line[0]}'
#            datetime_obj = datetime.datetime.strptime(timestamp.decode("utf-8"), '[%Y-%m-%dT%H:%M:%S.%fZ]')
#            formatted_timestamp = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        return str(line[0]), str(line[-2])

    def do_GET(self):
        # Read the request path
        path = self.path

        # Set the response status code
        self.send_response(200)

        # Set the response headers
        self.send_header('Content-type', 'application/json')
        # self.send_header("Access-Control-Allow-Origin", "http://localhost:3000")
        # self.send_header("Access-Control-Allow-Origin", "http://localhost:3001")
        self.send_header("Access-Control-Allow-Origin", "http://localhost:3002")
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
        self.end_headers()

        cpu = disk = memory = ''
        ts_cpu = ts_disk = ts_memory = '' # ts - TimeStamp

        ts_cpu, cpu = self.read_data(sys.path[0] + "/files/cpu.txt")
        ts_disk, disk = self.read_data(sys.path[0] + "/files/disk.txt")
        ts_memory, memory = self.read_data(sys.path[0] + "/files/memory.txt")
         
        response = {'ts_cpu':f'{ts_cpu}', 'cpu': f'{cpu}',
                    'ts_disk':f'{ts_disk}', 'disk' : f'{disk}',
                    'ts_memory':f'{ts_memory}', 'memory':f'{memory}', 
                    }
        response_json = json.dumps(response).encode('utf-8')
        self.wfile.write(response_json)
        cpu = (str) (self.read_data(sys.path[0] + "/files/cpu.txt"))


with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
