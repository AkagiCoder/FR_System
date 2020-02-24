import matplotlib.pyplot as plt
from keras.preprocessing import image
import warnings
warnings.filterwarnings("ignore")
import time
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import json


from deepface.basemodels import VGGFace, OpenFace, Facenet, FbDeepFace
from deepface.extendedmodels import Age, Gender, Race, Emotion
from deepface.commons import functions, distance as dst


import cv2
import sys
from deepface import DeepFace
import matplotlib.pyplot as plt

#cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier('/home/pi/Desktop/DFace/haarcascade_frontalface_default.xml')
img1_path = "/home/pi/Desktop/DFace/tests/dataset/Bryan.png"

video_capture = cv2.VideoCapture(0)

# @@@@@@@@@@@@ VGG-FACE @@@@@@@@@@@
#model_name ='VGG-Face'
#distance_metric = 'cosine'
#threshold = functions.findThreshold(model_name, distance_metric)
#print("Using VGG-Face model backend and", distance_metric,"distance.")
#model = VGGFace.loadModel()
#input_shape = (224, 224)

# @@@@@@@@@@@ OFace @@@@@@@@@@@
model_name ='OpenFace'
distance_metric = 'cosine'
threshold = functions.findThreshold(model_name, distance_metric)
print("Using OpenFace model backend", distance_metric,"distance.")
model = OpenFace.loadModel()
input_shape = (96, 96)



img1 = functions.detectFace(img1_path, input_shape)
img1_representation = model.predict(img1)[0,:]

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=10,
        minSize=(200, 200),
        flags=cv2.FONT_HERSHEY_SIMPLEX
    )
    
    if len(faces) > 0:
        #print(faces[0])
        x, y, w, h = faces[0]
        detected_face = frame[int(y):int(y+h), int(x):int(x+w)]
        detected_face = cv2.resize(detected_face, input_shape)
        img_pixels = image.img_to_array(detected_face)
        img_pixels = np.expand_dims(img_pixels, axis = 0)
        if True:
            #normalize input in [0, 1]
            img_pixels /= 255 
        else:
            #normalize input in [-1, +1]
            img_pixels /= 127.5
            img_pixels -= 1
            
        img2_representation = model.predict(img_pixels)[0,:]
        distance = dst.findCosineDistance(img1_representation, img2_representation)
        #print(distance)
        if distance < 0.2:
            print("Bryan Detected!")

            
    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Display the captured frame
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
