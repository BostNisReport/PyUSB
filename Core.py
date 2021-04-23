from serial import *
import threading
import os
import time


class OximeterCore(object):
    def __init__(self):
        pass

    # find all Oximeter Devices using device file.
    def find_devices(self):
        oximeter_devices = []

        fd = os.popen("ls /dev | grep ttyACM")
        lines = fd.readlines()
        fd.close()

        # loop through devices, printing vendor and product ids in decimal and hex
        for line in lines:
            line = line.replace('\n', '')
            device = OximeterDevice(line)
            oximeter_devices.append(device)

        return oximeter_devices


# read thread worker
def oximeter_reader(device):
    device.read_from_device()


class OximeterDevice(object):
    device = None
    handle = None
    thread = None
    running = False
    callback = None
    buffer = []
    lock = None

    STX = 2
    ETX = 3

    def __init__(self, device):
        self.device = device
        self.handle = None

    def open(self):
        self.handle = Serial(port="/dev/" + self.device, timeout=1)

        if self.handle is None:
            return False

        return True

    def close(self):
        self.handle.close()
        self.handle = None

    def start(self):
        t = threading.Thread(target=oximeter_reader, args=(self,))
        self.thread = t
        self.lock = threading.Lock()
        self.running = True
        self.thread.start()
        pass

    def stop(self):
        self.running = False
        self.thread.stop()

    def read(self, count):
        data = []
        ret_count = 0

        self.lock.acquire()
        buffer_length = len(self.buffer)
        ret_count = count
        if count > buffer_length:
            ret_count = buffer_length

        i = ret_count
        while i > 0:
            item = self.buffer.pop(0)
            data.append(item)
            i -= 1

        self.lock.release()

        return buffer_length, data

    def read_from_device(self):
        while self.running:
            data = self.handle.read(12)

            if data is not None and data != b''and len(data) == 12:
                if data[0] == self.STX and data[11] == self.ETX:
                    length = data[1]
                    status = data[2]
                    pi = data[4] + data[5]*0.001
                    counter = data[6] * 256 + data[7]
                    spo2 = data[8]
                    pulse_rate = data[9]*256 + data[10]

                    self.lock.acquire()
                    self.buffer.append({"status":status, "pi":pi, "counter":counter, "spo2":spo2, "pulse_rate":pulse_rate})
                    length = len(self.buffer)
                    self.lock.release()

                    if self.callback is not None:
                        self.callback(self, length)
            else:
                print("no data")
            time.sleep(0.5)

        return True

    def set_callback(self, func):
        self.callback = func
