import cv2
import numpy

from threading import Thread
from queue import Queue
import face_recognition
from timer import Timer

# # Load a sample picture and learn how to recognize it.
# obama_image = face_recognition.load_image_file("obama.jpg")
# obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
#
# # Load a second sample picture and learn how to recognize it.
# biden_image = face_recognition.load_image_file("biden.jpg")
# biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    # obama_face_encoding,
    # biden_face_encoding
]
known_face_names = [
    # "Barack Obama",
    # "Joe Biden"
]

def loadDataSet():
    import os.path
    import glob
    global  known_face_names, known_face_encodings
    for f in glob.glob(os.path.join("images", "*.jpg")):
        print(f)
        img = face_recognition.load_image_file(f)
        face_encoding = face_recognition.face_encodings(img)[0]
        known_face_encodings += [face_encoding]
        known_face_names += [os.path.split(f)[-1]]

t = Timer()

t.start()
loadDataSet()
a = t.stop()
print ("Load TIme: ", a)

class Frame():

    def __init__(self, id, frame):
        self.id = id
        self.frame = frame


class Worker(Thread):

    def __init__(self, frame : Frame):
        Thread.__init__(self)
        self.frame = frame
        self.scaleFactor = 2

    def start(self):
        import face_recognition
        from datetime import datetime
        timeStart = datetime.now()
        small_frame = cv2.resize(self.frame.frame, (0, 0), fx=1/self.scaleFactor, fy=1/self.scaleFactor)

        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        timeEndSegmentation = datetime.now()
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

        timeEndClassification = datetime.now()

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # print(face_locations)
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= self.scaleFactor
            right *= self.scaleFactor
            bottom *= self.scaleFactor
            left *= self.scaleFactor

            # Draw a box around the face
            cv2.rectangle(self.frame.frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(self.frame.frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(self.frame.frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        timeEnd = datetime.now()
        # timeDelta = timeEnd - timeStart
        print((timeEndSegmentation - timeStart).total_seconds(),
              (timeEndClassification - timeEndSegmentation).total_seconds(),
              (timeEnd - timeEndClassification).total_seconds(),
              len([x for x in face_names if x != 'Unknown']), len(face_names))

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
                # sleep(0.01)

    def __del__(self):
        import cv2
        print('Len:', self.frameQueue.qsize())
        cv2.destroyAllWindows()

class Reader(Thread):
    def __init__(self, queue : Queue):
        Thread.__init__(self)
        # self.camera = cv2.VideoCapture(0)
        self.camera = cv2.VideoCapture('testVideo/1person.mp4')
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
                exit(100)
                return
            # print("Ok")
            # input()
            self.frameQueue.put(Frame(self.getNextId(), frame))
            # sleep(0.01)

    def __del__(self):
        self.camera.release()
