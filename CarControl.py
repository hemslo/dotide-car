import urllib2
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


q = Queue.Queue()


class worker_read(threading.Thread):
    def __init__(self):
        super(worker_read, self).__init__()
        self.queue = q
        self.value = None
        self.command = None
        self.ser = serial.Serial()
        self.ser.port = 6
        self.ser.baudrate = 9600
        self.ser.open()
        time.sleep(3)


    def run(self):
        while True:
            print "SerialRead"
            data = (self.ser.readline()).split(',')
            self.queue.put({'at': datetime.now().isoformat(),
                            'x': float(data[0]),
                            'y': float(data[1])})


class worker_post(threading.Thread):
    def __init__(self):
        super(worker_post, self).__init__()
        self.queue = q

    def run(self):
        while True:
            print "post to web"
            item = self.queue.get()
            urlx = "__________________"
            header = {"U-ApiKey": "_________________", "Content-type": "application/json"}
            content = json.dumps({"timestamp": item['at'], "value": item['x']})
            request = urllib2.Request(url, content, header)
            response = urllib2.urlopen(request)

            urly = "__________________"
            header = {"U-ApiKey": "_________________", "Content-type": "application/json"}
            content = json.dumps({"timestamp": item['at'],"value": item['y']})
            request = urllib2.Request(url, content, header)
            response = urllib2.urlopen(request)
            self.queue.task_done()


class worker_getandwrite(threading.Thread):

    def __init__(self):
        super(worker_getandwrite, self).__init__()

    def run(self):
        while True:
            url = ______________________
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
    thread_read = worker_read()
    thread_read.setDaemon(True)
    thread_getandwrite = worker_getandwrite()
    thread_getandwrite.setDaemon(True)
    thread_post = worker_post()
    thread_post.setDaemon(True)
    thread_read.start()
    thread_getandwrite.start()
    thread_post.start()
    thread_read.join()
    thread_getandwrite.join()
    thread_post.join()


if __name__ == "__main__":
    main()
