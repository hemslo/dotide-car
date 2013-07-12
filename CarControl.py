import json
import serial
import requests
import thread
import datetime
import time
import sys
import multiprocessing
import threading
import Queue




class Worker_Read(threading.Thread):
    def __init__(self,queue):
        super(Worker_Read, self).__init__()
        self.queue = queue
        self.value = None
        self.command = None
        self.ser = serial.Serial()
        self.ser.port = 6
        self.ser.baudrate = 9600
        self.ser.open()
        time.sleep(3)


    def run(self):
        while True:
            print "Read from car"
            data = (self.ser.readline()).split(',')
            self.queue.put({'at': datetime.now().isoformat(),
                            'x': float(data[0]),
                            'y': float(data[1])})


class Worker_Post(threading.Thread):
    def __init__(self,queue):
        super(Worker_Post, self).__init__()
        self.queue = queue

    def run(self):
        while True:
            print "post to web"
            item = self.queue.get()
            urlx = "__________________"
            headers = {"U-ApiKey": "_________________", "Content-type": "application/json"}
            content = json.dumps({"timestamp": item['at'], "value": item['x']})
            r= requests.post(urlx, data=content, headers=headers)
            
            urly = "__________________"
            headers = {"U-ApiKey": "_________________", "Content-type": "application/json"}
            content = json.dumps({"timestamp": item['at'], "value": item['y']})
            r= requests.post(urly, data=content, headers=headers)

            self.queue.task_done()


class Worker_GetAndWrite(threading.Thread):

    def __init__(self):
        super(Worker_GetAndWrite, self).__init__()

    def run(self):
        while True:
            print "GetAndWrite to car"
            url = "______________________"
            req = requests.get(url)
            req.headers['Content-type'] = "application/json"
            req.headers['U-ApiKey'] = "_______________"
            print "get info "
            data = json.loads(req.text)
            self.command = data['value']
            #this data only hold one single value
            print self.command
            self.ser.write(self.command)


def main():
    q = Queue.Queue()
    Thread_Read = Worker_Read(q)
    Thread_Read.setDaemon(True)
    Thread_GetAndWrite = Worker_GetAndWrite(q)
    Thread_GetAndWrite.setDaemon(True)
    Thread_Post = Worker_Post(q)
    Thread_Post.setDaemon(True)
    Thread_Read.start()
    Thread_GetAndWrite.start()
    Thread_Post.start()
    Thread_Read.join()
    Thread_GetAndWrite.join()
    Thread_Post.join()


if __name__ == "__main__":
    main()
