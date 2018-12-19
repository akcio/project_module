import cv2
import numpy

from threading import Thread
from queue import Queue

class Frame():

    def __init__(self, id, frame):
        self.id = id
        self.frame = frame
        self.face_locations = []
        self.face_encodings = []
        self.processed = False


    def process(self):
        import face_recognition
        small_frame = cv2.resize(self.frame, (0, 0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame[:, :, ::-1]

        self.face_locations = face_recognition.face_locations(rgb_small_frame)
        self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

        for (top, right, bottom, left) in self.face_locations:
            # print(face_locations)
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(self.frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(self.frame, "Unknown", (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        self.processed = True


    def delay(self, face_locations = None):
        if face_locations != None:
            face_locations = self.face_locations

        if len(face_locations) > 0:
            for (top, right, bottom, left) in self.face_locations:
                # print(face_locations)
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(self.frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(self.frame, "Unknown", (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

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
            # print(face_locations)
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




class SkyWorker(Thread):

    def __init__(self, frameQue: Queue, output: dict):
        Thread.__init__(self)
        self.frameQue = frameQue
        self.output = output # { frame_id: Frame }
        self.procFreq = 4
        self.sequence = self.procFreq - 1

    def isProcesseble(self):
        self.sequence = (self.sequence + 1) % self.procFreq
        return self.sequence == 0


    def run(self):
        while True:
            while not self.frameQue.empty():
                curFrame = self.frameQue.get()
                if self.isProcesseble():
                    curFrame.process()
                else:
                    pass
                    # curFrame.delay(self.lastFrame)
                if len(self.output) == 0 or (len(self.output) > 0 and curFrame.id > list(self.output.keys())[0]):
                    self.output.update({curFrame.id: curFrame})

                print(len(self.output))



class NewProcesser:
    def __init__(self, input: Queue, output: dict):
        self.input = input
        self.output = output
        self.showQue = Queue()
        self.lastProcessFrame = None

    def minimize(self, series: dict, cutPercent):
        if cutPercent >= 1 or cutPercent <= 0 or len(series) < 10:
            return
        cutSize = int(len(series) * cutPercent)

        while len(series) > cutSize:
            series.pop(list(series.keys())[0], None)
        return


    def start(self):
        from time import sleep
        while True:
            self.minimize(self.output, 0.7)
            while len(self.output.keys()) > 0:
                frame = list(self.output.values())[0]
                self.output.pop(list(self.output.keys())[0], None)

                self.showQue.put(frame)

                while not self.showQue.empty():
                    curFrame = self.showQue.get()
                    if curFrame.processed:
                        if len(curFrame.face_locations) > 0:
                            self.lastProcessFrame = curFrame.face_locations
                    else:
                        if self.lastProcessFrame != None:
                            curFrame.delay(self.lastProcessFrame)
                    cv2.imshow('Video', curFrame.frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    exit(0)
                sleep(0.01)



class Processer():
    def __init__(self, queue : Queue):
        # Thread.__init__(self)
        self.frameQueue = queue
        self.processes = []
        self.maxWorkers = 1
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

                self.processQueue = []
                self.processes = []
                # cv2.waitKey(0)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print('Len', len(self.frameQueue))
                    exit(0)
                sleep(0.01)

    def __del__(self):
        import cv2
        print('Len:', self.frameQueue.qsize())
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
            # print("Ok")
            # input()
            self.frameQueue.put(Frame(self.getNextId(), frame))
            sleep(0.01)

    def __del__(self):
        self.camera.release()
