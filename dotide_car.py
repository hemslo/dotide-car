import json
import serial
import requests
import datetime
import time
import threading
import Queue


API_KEY = ''
X_URL = ''
Y_URL = ''
CONTROL_URL = ''
SERIAL_PORT = 6


class ReadWorker(threading.Thread):
    def __init__(self, queue, serial):
        super(ReadWorker, self).__init__()
        self.queue = queue
        self.ser = serial

    def run(self):
        while True:
            print 'Read from car'
            data = (self.ser.readline()).split(',')
            self.queue.put({'at': datetime.now().isoformat(),
                            'x': float(data[0]),
                            'y': float(data[1])})
            time.sleep(1)


class PostWorker(threading.Thread):
    def __init__(self, queue):
        super(PostWorker, self).__init__()
        self.queue = queue

    def run(self):
        while True:
            print 'post to web'
            item = self.queue.get()
            headers = {'ApiKey': API_KEY, 'content-type': 'application/json'}
            payload = {'at': item['at'], 'value': item['x']}
            requests.post(X_URL, data=json.dumps(payload), headers=headers)

            headers = {'ApiKey': API_KEY, 'content-type': 'application/json'}
            payload = {'at': item['at'], 'value': item['y']}
            requests.post(Y_URL, data=json.dumps(payload), headers=headers)

            self.queue.task_done()


class ControlWorker(threading.Thread):

    def __init__(self, serial):
        super(ControlWorker, self).__init__()
        self.ser = serial

    def run(self):
        while True:
            print 'GetAndWrite to car'
            headers = {'ApiKey': API_KEY, 'content-type': 'application/json'}
            res = requests.get(CONTROL_URL, headers=headers)
            print 'get info '
            data = res.json()
            self.command = data['current_value']
            print self.command
            self.ser.write(self.command)
            time.sleep(1)


def main():
    ser = serial.Serial()
    ser.port = SERIAL_PORT
    ser.baudrate = 9600
    ser.open()
    time.sleep(1)
    q = Queue.Queue()

    read_thread = ReadWorker(q, ser)
    read_thread.setDaemon(True)
    read_thread.start()

    post_thread = PostWorker(q)
    post_thread.setDaemon(True)
    post_thread.start()

    control_thread = ControlWorker(ser)
    control_thread.setDaemon(True)
    control_thread.start()

    read_thread.join()
    post_thread.join()
    control_thread.join()


if __name__ == '__main__':
    main()
