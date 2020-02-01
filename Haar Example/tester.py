import cv2
import os
import numpy as np
import faceRecognition as fr

# Read the test image
test_img = cv2.imread('/Users/bryan/Desktop/FR_Project/TestImages/jfk.jpg')
faces_detected, gray_img = fr.faceDetection(test_img)
print("faces_detected: ", faces_detected)

faces, faceID = fr.labels_for_training_data('/Users/bryan/Desktop/FR_Project/trainingImages')
face_recognizer = fr.train_classifier(faces, faceID)
face_recognizer.save('trainingData.yml')

name = {0:"Random", 1:"Bryan"}

for face in faces_detected:
    (x, y, w, h) = face
    roi_gray = gray_img[y : y + h, x: x + h]
    label, confidence = face_recognizer.predict(roi_gray)
    print("confidence: ", confidence)
    print("label: ", label)
    fr.draw_rect(test_img, face)
    predicted_name = name[label]
    if(confidence > 20):
        continue
    fr.put_text(test_img, predicted_name, x, y)

# Fix the resolution of the image (sometimes the image is too big)
resized_img = cv2.resize(test_img, (1000, 700))
cv2.imshow("face detection tutorial", resized_img)
cv2.waitKey(0)
cv2.destroyAllWindows
