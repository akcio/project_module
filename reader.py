import cv2

from threading import Thread
from queue import Queue

class Frame():

    def __init__(self, id, frame):
        self.id = id
        self.frame = frame


class Worker(Thread):

    def __init__(self):
        Thread.__init__(self)


    def start(self):
        


class Reader():

    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.waiting = Queue()
        self.id = 0

    def getNextId(self):
        self.id += 1
        return self.id