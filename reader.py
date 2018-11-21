import cv2
import numpy

from threading import Thread
from queue import Queue

class Frame():

    def __init__(self, id, frame):
        self.id = id
        self.frame = frame


class Worker(Thread):

    def __init__(self, frame : Frame):
        Thread.__init__(self)
        self.frame = frame

    def start(self):
        pass

class Processer():
    def __init__(self, queue : Queue):
        # Thread.__init__(self)
        self.frameQueue = queue

    def start(self):
        from time import sleep
        while True:
            while self.frameQueue.not_empty:
                try:
                    frame = self.frameQueue.get_nowait()
                except Exception as ex:
                    # print(ex)
                    continue
                print("Frame:", frame.id)
                cv2.imshow('Video', frame.frame)
                sleep(0.01)

    def __del__(self):
        cv2.destroyAllWindows()

class Reader(Thread):
    def __init__(self, queue : Queue):
        Thread.__init__(self)
        self.camera = cv2.VideoCapture(0)
        self.waiting = Queue()
        self.id = 0
        self.frameQueue = queue

    def getNextId(self):
        self.id += 1
        return self.id

    def run(self):
        from time import sleep
        while True:
            ret, frame = self.camera.read()
            if not ret:
                return
            print("Ok")
            # input()
            self.frameQueue.put(Frame(self.getNextId(), frame))
            sleep(0.01)

    def __del__(self):
        self.camera.release()
