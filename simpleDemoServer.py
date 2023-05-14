import http.server
import socketserver
import json
import os
import sys
import datetime

# [{
#       cpu_data: "7.89",
#       ts_cpu: "[2023-03-28T19:56:49.3559798Z]",
#       disk_data: "3.2",
#       ts_disk: "[2023-03-28T19:56:49.3559798Z]",
#       memory_data: "10.1",
#       ts_memory: "[2023-03-28T19:56:49.3559798Z]"
#     },{
#       cpu_data: "3.21",
#       ts_cpu: "[2023-03-28T19:56:50.3559798Z]",
#       disk_data: "3.2",
#       ts_disk: "[2023-03-28T19:56:50.3559798Z]",
#       memory_data: "16.789",
#       ts_memory: "[2023-03-28T19:56:50.3559798Z]"
#     },{
#       cpu_data: "17.463",
#       ts_cpu: "[2023-03-28T19:57:49.3559798Z]",
#       disk_data: "1.77",
#       ts_disk: "[2023-03-28T19:57:49.3559798Z]",
#       memory_data: "9.486",
#       ts_memory: "[2023-03-28T19:57:49.3559798Z]"
#     },{
#       cpu_data: "4.786",
#       ts_cpu: "[2023-03-28T19:58:49.3559798Z]",
#       disk_data: "1.8",
#       ts_disk: "[2023-03-28T19:58:49.3559798Z]",
#       memory_data: "3.74",
#       ts_memory: "[2023-03-28T19:58:49.3559798Z]"
#     }]

PORT = 8001  # Choose a port number you like

class DataLine():

    cpu_data = ts_cpu = disk_data = ts_disk = memory_data = ts_memory = ''

    def translate_line(self, Line):
        line = Line.split(' ')
        return str(line[0][1:-2]), str(line[-2])

    def __init__(self, cpuLine, diskLine, memLine):
        self.ts_cpu, self.cpu_data = self.translate_line(cpuLine)
        self.ts_disk, self.disk_data = self.translate_line(diskLine)
        self.ts_memory, self.memory_data = self.translate_line(memLine)
    
    def toJson(self):
                cpu_str = str(datetime.datetime.fromisoformat(self.ts_cpu))
                disk_str = str(datetime.datetime.fromisoformat(self.ts_disk))
                mem_str = str(datetime.datetime.fromisoformat(self.ts_memory))

                return {'ts_cpu':f'{cpu_str}', 'cpu': f'{self.cpu_data}',
                    'ts_disk':f'{disk_str}', 'disk' : f'{self.disk_data}',
                    'ts_memory':f'{mem_str}', 'memory':f'{self.memory_data}', 
                    }

class MyHandler(http.server.BaseHTTPRequestHandler):

    # These __x_curr__ holds a pointer the the last place the file was read,
    # it is used to increment the data every time we read from the files 
    cpu_curr = disk_curr = mem_curr=0        

    def read_lines(self, path, count):
        '''Read lines
           ----------
           @brief read the amount of lines and increment the current file seek t read from next time
           @param path The path of the parent directory where the files are stored
           @param count The number of lines you want to read from the files
           @return json string with an array of records '''
        lines=[]
        try:
            cpu_fd = open(path + '/cpu.txt', "rt")
            disk_fd = open(path + '/disk.txt', "rt")
            mem_fd = open(path + '/memory.txt',"rt")

            cpu_fd.seek(MyHandler.cpu_curr, 0) # 0 for the beginning of the file
            disk_fd.seek(MyHandler.disk_curr, 0) 
            mem_fd.seek(MyHandler.mem_curr, 0) 

            for i in range(0,count, 1):
                # Read a line
                line = DataLine(cpuLine=str(cpu_fd.readline()), diskLine=str(disk_fd.readline()),memLine=str(mem_fd.readline()))
                lines.append(line)

                # update the file's current pointer position and update it accordingly
                MyHandler.cpu_curr = cpu_fd.tell()
                MyHandler.disk_curr = disk_fd.tell()
                MyHandler.mem_curr = mem_fd.tell()
                
                # For some reason the readline function returns the same line every time, this solves it
                cpu_fd.seek(MyHandler.cpu_curr, 0) # 0 for the beginning of the file
                disk_fd.seek(MyHandler.disk_curr, 0) 
                mem_fd.seek(MyHandler.mem_curr, 0) 

        except Exception as e:
            print(str(e))
        finally:
            # When the file is closed the seek goes back to 0
            cpu_fd.close()
            disk_fd.close()
            mem_fd.close()
        return lines

    def read_calander(self, path, fromDate, toDate):
        '''
        read_calander
        -------------
        @brief Reads from the log files all the data relevent for a given range of dates
        @param path The path the the root directory where the files are stored
        @param fromDate A string telling the initial time of the logs in the format of [yyyy-dd-MMThh:mm:ssZ]
        @param toDate A string telling the end time of the logs in the format of [yyyy-dd-MMThh:mm:ssZ]
        '''
        lines = []
        try:
            cpu_fd = open(path + '/cpu.txt', "rt")
            disk_fd = open(path + '/disk.txt', "rt")
            mem_fd = open(path + '/memory.txt',"rt")

            fromDate = fromDate.decode("utf-8").replace('[', '').replace('Z]', '')
            toDate = toDate.decode("utf-8").replace('[', '').replace('Z]', '')
            lineDate = firstDate =  datetime.datetime.fromisoformat(fromDate)
            lastDate = datetime.datetime.fromisoformat(toDate)

            while(lineDate < lastDate):
                Data = DataLine(cpuLine=str(cpu_fd.readline()), diskLine=str(disk_fd.readline()),memLine=str(mem_fd.readline()))
                lineDate = datetime.datetime.fromisoformat(Data.ts_memory)
                if(lineDate >= firstDate):
                    lines.append(Data.toJson())
            print(str(lines))
            return lines
            
        except Exception as e:
            print(str(e))
        finally:
            cpu_fd.close()
            disk_fd.close()
            mem_fd.close()
         
    # TODO : change the function to read the last from all three files 
    def read_last(self, path):
        line = []
        with open(path, "rb") as file:
            try:
                file.seek(-2, os.SEEK_END)
                while file.read(1) != b'\n':
                    file.seek(-2, os.SEEK_CUR)
            except OSError:
                file.seek(0)
            line = (str)(file.readline()).split(' ')
        return str(line[0][2:-1]), str(line[-2])
    
    # TODO : implement
    def read_time_range(self):
        pass

    def do_GET(self):
        # Read the request path
        path = self.path

        # Set the response status code
        self.send_response(200)

        # Set the response headers
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = ''
         
        match path:
            case '/':
                lines = []
                temp = self.read_lines(sys.path[0] + '/files', 3)
                for i in range(0,3,1):
                    lines.append(str(temp[i].toJson()))
                response = {'data':lines}
                print(response['data'])
                pass
            case '/last':
                cpu = disk = memory = ''
                ts_cpu = ts_disk = ts_memory = '' # ts - TimeStamp

                ts_cpu, cpu = self.read_last(sys.path[0] + "/files/cpu.txt")
                ts_disk, disk = self.read_last(sys.path[0] + "/files/disk.txt")
                ts_memory, memory = self.read_last(sys.path[0] + "/files/memory.txt")

                ts_cpu = str(datetime.datetime.fromisoformat(ts_cpu.replace('[', '').replace('Z]', '')).strftime("%d-%m-%y %H:%M:%S"))
                ts_disk = str(datetime.datetime.fromisoformat(ts_disk.replace('[', '').replace('Z]', '')).strftime("%d-%m-%y %H:%M:%S"))
                ts_memory = str(datetime.datetime.fromisoformat(ts_memory.replace('[', '').replace('Z]', '')).strftime("%d-%m-%y %H:%M:%S"))
                response = {'ts_cpu':f'{ts_cpu}', 'cpu': f'{cpu}',
                        'ts_disk':f'{ts_disk}', 'disk' : f'{disk}',
                        'ts_memory':f'{ts_memory}', 'memory':f'{memory}'}
            case '/table':
                # TODO : implement the read parameters and decide the time format standard
                response = self.read_calander(sys.path[0] + '/files',b'[2023-03-28T19:50:24Z]', b'[2023-03-28T19:50:28Z]')
            case _:
                pass

        response_json = json.dumps(response).encode('utf-8')
        self.wfile.write(response_json)


with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
