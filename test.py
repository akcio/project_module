import dlib  # dlib for accurate face detection
import cv2  # opencv
import imutils  # helper functions from pyimagesearch.com
import face_recognition

import numpy

# Grab video from your webcam
stream = cv2.VideoCapture(0)

# Face detector
detector = dlib.get_frontal_face_detector()

sp = dlib.shape_predictor('shape_predictor_5_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')


obama_image = face_recognition.load_image_file("obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
biden_image = face_recognition.load_image_file("biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

igor_image = face_recognition.load_image_file("vormanov_front.jpg")
igor_face_encoding = face_recognition.face_encodings(igor_image)[0]

print(len(igor_face_encoding))

# Create arrays of known face encodings and their names
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding,
    igor_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Joe Biden"
    "Igor"
]

cnt = 0

def calcDescriptor():
    pass

# Fancy box drawing function by Dan Masek
def draw_border(img, pt1, pt2, color, thickness, r, d):
    x1, y1 = pt1
    x2, y2 = pt2

    # Top left drawing
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

    # Top right drawing
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

    # Bottom left drawing
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

    # Bottom right drawing
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)


while True:
    # read frames from live web cam stream
    (grabbed, frame) = stream.read()

    # resize the frames to be smaller and switch to gray scale
    frame = imutils.resize(frame, width=700)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Make copies of the frame for transparency processing
    overlay = frame.copy()
    output = frame.copy()

    # set transparency value
    alpha = 0.5

    # detect faces in the gray scale frame
    face_rects = detector(gray, 0)
    face_encode = []

    # loop over the face detections
    for i, d in enumerate(face_rects):
        x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()

        # draw a fancy border around the faces
        draw_border(overlay, (x1, y1), (x2, y2), (162, 255, 0), 2, 10, 10)

        if cnt == 0:
            shape = sp(frame, d)
            face_descriptor = facerec.compute_face_descriptor(frame, shape)
            a = face_recognition.compare_faces(known_face_encodings, [face_descriptor])
            print(a)
        cnt = (cnt+1)%4


    # make semi-transparent bounding box
    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

    # show the frame
    cv2.imshow("Face Detection", output)
    key = cv2.waitKey(1) & 0xFF

    # press q to break out of the loop
    if key == ord("q"):
        break

# cleanup
cv2.destroyAllWindows()
stream.stop()