import http.server
import socketserver
import json
import os
import sys
import datetime
import psutil
import threading
import time
import socket
import requests

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

                return {"ts_cpu":f"{cpu_str}", "cpu": f"{self.cpu_data}",
                    "ts_disk":f"{disk_str}", "disk" : f"{self.disk_data}",
                    "ts_memory":f"{mem_str}", "memory":f"{self.memory_data}", 
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

            # get the file size by reading 0 bytes from the end 2 = SEEK_END and get the current fd 
            cpu_fd.seek(0, 2)
            cpu_file_size =  cpu_fd.tell()
            disk_fd.seek(0, 2)
            disk_file_size = disk_fd.tell()
            mem_fd.seek(0, 2)
            mem_file_size = mem_fd.tell()

            cpu_fd.seek(MyHandler.cpu_curr, 0) # start from the last place you stopped, 0 for the beginning of the file
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

                if MyHandler.cpu_curr == cpu_file_size:
                    MyHandler.cpu_curr = 0
                if MyHandler.disk_curr == disk_file_size:
                    MyHandler.disk_curr = 0
                if MyHandler.mem_curr == mem_file_size:
                    MyHandler.mem_curr = 0
                
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

                cpu_pr = psutil.cpu_percent();
                disk_pr = psutil.disk_usage('/');
                mem_pr = psutil.virtual_memory().percent;

                #Get all running processes
                processes = list(psutil.process_iter(attrs=['pid', 'name', 'cpu_percent']))

                #Sort the processes by CPU usage in descending order
                sorted_processes = sorted(processes, key=lambda p: p.info['cpu_percent'], reverse=True)


                #Get the process with the highest CPU usage
                highest_cpu_process = sorted_processes[0]
                highest_process_name = highest_cpu_process.info['name']

                temp = self.read_lines(sys.path[0] + '/files', 3)
                for i in range(0,3,1):
                    lines.append(str(temp[i].toJson()))
                response = {'data':lines, 'process':f'{highest_process_name}'}
                print(response)

                # print('cpu '+str(cpu_pr)+'%, disk '+str(disk_pr)+'%, mem '+str(mem_pr)+'%;')

                #Print the process details
                # print("Process ID:", highest_cpu_process.info['pid'])
                # print("Process Name:", highest_cpu_process.info['name'])
                # print("CPU Usage:", highest_cpu_process.info['cpu_percent'])
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
                
                cpu_pr = psutil.cpu_percent();
                disk_pr = psutil.disk_usage('/');
                mem_pr = psutil.virtual_memory().percent;
                print('cpu '+str(cpu_pr)+'%, disk '+str(disk_pr)+'%, mem '+str(mem_pr)+'%;')

                #Get all running processes
                processes = list(psutil.process_iter(attrs=['pid', 'name', 'cpu_percent']))

                #Sort the processes by CPU usage in descending order
                sorted_processes = sorted(processes, key=lambda p: p.info['cpu_percent'], reverse=True)

                #Get the process with the highest CPU usage
                highest_cpu_process = sorted_processes[0]
                highest_process_name = highest_cpu_process.info['name']
                
                response = {'ts_cpu':f'{datetime.datetime.now()}', 'cpu': f'{cpu_pr}',
                        'ts_disk':f'{datetime.datetime.now()}', 'disk' : f'{disk_pr}',
                        'ts_memory':f'{datetime.datetime.now()}', 'memory':f'{mem_pr}',
                        'process':f'{highest_process_name}'}
            case '/table':
                # TODO : implement the read parameters and decide the time format standard
                response = self.read_calander(sys.path[0] + '/files',b'[2023-03-28T19:50:24Z]', b'[2023-03-28T19:50:28Z]')
            case _:
                pass

        response_json = json.dumps(response).encode('utf-8')
        self.wfile.write(response_json)



# Function to write data to a file
def write_data(file_name, data):
    with open(file_name, 'at') as file:
        file.write(data + '\n')

# Function to write data at a regular interval
def write_data_interval(interval):
    while True:

        # Data for each file
        cpu_pr = psutil.cpu_percent();
        disk_pr = psutil.disk_usage('/');
        mem_pr = psutil.virtual_memory().percent;

        #Get all running processes
        processes = list(psutil.process_iter(attrs=['pid', 'name', 'cpu_percent']))

        #Sort the processes by CPU usage in descending order
        sorted_processes = sorted(processes, key=lambda p: p.info['cpu_percent'], reverse=True)

        #Get the process with the highest CPU usage
        highest_cpu_process = sorted_processes[0]
        highest_process_name = highest_cpu_process.info['name']

        cpu_data = "["+str(datetime.datetime.now())+"] cpuUsage: " + str(cpu_pr) + " % p : " + highest_process_name
        disk_data = "["+str(datetime.datetime.now())+"] DiskUtilization: " + str(disk_pr) + " %"
        mem_data = "["+str(datetime.datetime.now())+"] mem: " + str(mem_pr) + " %"

        write_data(sys.path[0] + "/files/cpu2.txt", cpu_data)
        write_data(sys.path[0] + "/files/disk2.txt", disk_data)
        write_data(sys.path[0] + "/files/memory2.txt", mem_data)
        time.sleep(interval)

def send_post_message():
    url = "http://127.0.0.1:3007/api/entityTelemetry"
    headers = {"Content-Type": "application/json"}  # Replace with your desired headers

    hostname = socket.gethostname()
    cpu_pr = psutil.cpu_percent();
    disk_pr = psutil.disk_usage('/');
    mem_pr = psutil.virtual_memory().percent;
    print('cpu '+str(cpu_pr)+'%, disk '+str(disk_pr)+'%, mem '+str(mem_pr)+'%;')

    #Get all running processes
    processes = list(psutil.process_iter(attrs=['pid', 'name', 'cpu_percent']))

    #Sort the processes by CPU usage in descending order
    sorted_processes = sorted(processes, key=lambda p: p.info['cpu_percent'], reverse=True)

    #Get the process with the highest CPU usage
    highest_cpu_process = sorted_processes[0]
    highest_process_name = highest_cpu_process.info['name']

    response = {"roomId": "647b44a207ab16da82a6a0ca", 
                "siteId": "647b456a07ab16da82a6a0cb", "telemetryEntitiy":f'{hostname}', 
                'ts_cpu':f'{datetime.datetime.now()}', 'cpu': f'{cpu_pr}',
                'ts_disk':f'{datetime.datetime.now()}', 'disk' : f'{disk_pr}',
                'ts_memory':f'{datetime.datetime.now()}', 'memory':f'{mem_pr}',
                'process':f'{highest_process_name}'}
    response_json = json.dumps(response).replace("\"", "\'")
    print(response_json)
    http_response = requests.post(url, json=response, headers=headers)

    if http_response.status_code == 200:
        print("POST request sent successfully!")
    else:
        print("Error sending POST request:", http_response.status_code)

# Create and start threads for each file
thread1 = threading.Thread(target=write_data_interval, args=(1,))
thread1.start()

# Send a POST message every three seconds indefinitely
while True:
    send_post_message()
    time.sleep(3)


with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
