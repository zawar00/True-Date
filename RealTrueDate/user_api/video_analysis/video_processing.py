import cv2
import numpy as np
from sklearn.cluster import KMeans
# import dlib

def detect_skin_color(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(rgb_frame, 1.1, 4)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    face_region = rgb_frame[y:y + h, x:x + w]
    pixels = face_region.reshape((-1, 3))
    kmeans = KMeans(n_clusters=1).fit(pixels)
    dominant_color = kmeans.cluster_centers_[0]
    return tuple(dominant_color.astype(int))


def detect_eye_color(frame):
    return "brown"
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_frame)
    if len(faces) == 0:
        return None
    face = faces[0]
    landmarks = predictor(gray_frame, face)
    left_eye_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
    return "brown"  # Replace with clustering logic if needed


def detect_hair_color(frame, face_box):
    x, y, w, h = face_box
    hair_region = frame[y - int(0.2 * h):y, x:x + w]
    pixels = hair_region.reshape((-1, 3))
    kmeans = KMeans(n_clusters=1).fit(pixels)
    dominant_color = kmeans.cluster_centers_[0]
    return tuple(dominant_color.astype(int))


def detect_tattoos(frame):
    # Mocked logic for tattoo detection
    return False
