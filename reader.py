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
        import face_recognition
        small_frame = cv2.resize(self.frame.frame, (0, 0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left) in face_locations:
            print(face_locations)
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(self.frame.frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(self.frame.frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(self.frame.frame, "Unknown", (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


class Processer():
    def __init__(self, queue : Queue):
        # Thread.__init__(self)
        self.frameQueue = queue
        self.processes = []
        self.maxWorkers = 4
        self.processQueue = []

    def start(self):
        from time import sleep
        import face_recognition
        while True:
            while self.frameQueue.not_empty:
                try:
                    frame = self.frameQueue.get_nowait()
                except Exception as ex:
                    # print(ex)
                    continue

                if len(self.processQueue) < self.maxWorkers:
                    self.processQueue.append(frame)
                    continue

                for i in range(self.maxWorkers):
                    worker = Worker(self.processQueue[i])
                    self.processes.append(worker)
                    worker.start()

                self.processQueue = []
                for i in range(self.maxWorkers):
                    self.processQueue.append(self.processes[i].frame)

                self.processQueue = sorted(self.processQueue, key=lambda x : x.id)



                for item in self.processQueue:


                # print("Frame:", frame.id)
                    cv2.imshow('Video', item.frame)
                # cv2.waitKey(0)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    exit(0)
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
