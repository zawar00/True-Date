import cv2
import numpy as np
from sklearn.cluster import KMeans
import dlib

import logging

logging.basicConfig(level=logging.DEBUG)

def detect_skin_color(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(rgb_frame, 1.1, 4)
    
    if len(faces) == 0:
        logging.warning("No faces detected")
        return None
    
    x, y, w, h = faces[0]
    face_region = rgb_frame[y:y + h, x:x + w]
    
    if face_region.size == 0:  # Check if the region is empty
        logging.warning("Empty face region detected")
        return None
    
    pixels = face_region.reshape((-1, 3))
    
    if pixels.shape[0] == 0:  # Check if there are no pixels
        logging.warning("No pixels in face region")
        return None
    
    kmeans = KMeans(n_clusters=1).fit(pixels)
    dominant_color = kmeans.cluster_centers_[0]
    return tuple(dominant_color.astype(int))

def detect_eye_color(frame):
    return None  # Placeholder for eye color detection logic
    # Initialize dlib face detector and predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_frame)
    
    if len(faces) == 0:
        return None

    face = faces[0]
    landmarks = predictor(gray_frame, face)
    
    # Extract the points for the eyes
    left_eye_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]  # Left eye (indices 36-41)
    right_eye_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]  # Right eye (indices 42-47)
    
    # Get the bounding box for the eyes
    x_min = min([p[0] for p in left_eye_points + right_eye_points])
    y_min = min([p[1] for p in left_eye_points + right_eye_points])
    x_max = max([p[0] for p in left_eye_points + right_eye_points])
    y_max = max([p[1] for p in left_eye_points + right_eye_points])
    
    # Crop the eye region from the image
    eye_region = frame[y_min:y_max, x_min:x_max]
    
    # Convert to RGB and reshape to a list of pixels for KMeans
    rgb_eye_region = cv2.cvtColor(eye_region, cv2.COLOR_BGR2RGB)
    pixels = rgb_eye_region.reshape((-1, 3))
    
    # Apply KMeans clustering to determine the dominant eye color
    kmeans = KMeans(n_clusters=1).fit(pixels)
    dominant_color = kmeans.cluster_centers_[0]
    
    # Convert to integer and return as a tuple
    return tuple(dominant_color.astype(int))

def detect_hair_color(frame, face_box):
    if face_box is None:
        return None  # No face box provided
    
    x, y, w, h = face_box
    
    # Ensure that the region for hair extraction is valid
    if y - int(0.3 * h) < 0:
        return None  # Invalid region for hair
    
    hair_region = frame[y - int(0.3 * h):y, x:x + w]
    
    if hair_region.size == 0:  # Check if the hair region is empty
        return None
    
    pixels = hair_region.reshape((-1, 3))
    
    if pixels.shape[0] == 0:  # Check if there are no pixels to process
        return None
    
    kmeans = KMeans(n_clusters=1).fit(pixels)
    dominant_color = kmeans.cluster_centers_[0]
    return tuple(dominant_color.astype(int))  # Return the hair color as an RGB tuple

def detect_tattoos(frame):
    # This is a placeholder; implement actual tattoo detection here
    # For example, using deep learning models trained for tattoo detection
    return False  # No tattoos detected in the mocked logic
