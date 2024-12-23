# video_analysis/utils.py

import cv2
import dlib
from sklearn.cluster import KMeans

def detect_face_and_features(video_path):
    # Load the dlib face detector and shape predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("utils/shape_predictor_68_face_landmarks.dat")

    # Load the video
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()

    if not ret:
        return None, None, None, None  # No frame found

    # Convert the frame to grayscale for dlib face detection
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = detector(gray_frame)

    if len(faces) == 0:
        return None, None, None, None  # No faces detected

    # Assuming we take the first detected face
    face = faces[0]

    # Get landmarks for the face (eye, hair, and skin color)
    landmarks = predictor(gray_frame, face)

    # Skin Color Detection
    skin_color = detect_skin_color(frame, face)

    # Hair Color Detection
    hair_color = detect_hair_color(frame, face)

    # Eye Color Detection
    eye_color = detect_eye_color(frame, landmarks)

    # Tattoo Detection (This is a placeholder)
    tattoo_detected = detect_tattoos(frame)

    cap.release()
    return skin_color, hair_color, eye_color, tattoo_detected

def detect_skin_color(frame, face_box):
    x, y, w, h = face_box.left(), face_box.top(), face_box.width(), face_box.height()
    face_region = frame[y:y + h, x:x + w]
    pixels = face_region.reshape((-1, 3))
    kmeans = KMeans(n_clusters=1).fit(pixels)
    dominant_color = kmeans.cluster_centers_[0]
    return tuple(dominant_color.astype(int))

def detect_hair_color(frame, face_box):
    x, y, w, h = face_box.left(), face_box.top(), face_box.width(), face_box.height()
    hair_region = frame[y - int(0.3 * h):y, x:x + w]  # Region above the face
    pixels = hair_region.reshape((-1, 3))
    kmeans = KMeans(n_clusters=1).fit(pixels)
    dominant_color = kmeans.cluster_centers_[0]
    return tuple(dominant_color.astype(int))

def detect_eye_color(frame, landmarks):
    # Extract left and right eye points from the landmarks
    left_eye_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
    right_eye_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]
    
    # Get the bounding box for the eyes
    x_min = min([p[0] for p in left_eye_points + right_eye_points])
    y_min = min([p[1] for p in left_eye_points + right_eye_points])
    x_max = max([p[0] for p in left_eye_points + right_eye_points])
    y_max = max([p[1] for p in left_eye_points + right_eye_points])
    
    eye_region = frame[y_min:y_max, x_min:x_max]
    rgb_eye_region = cv2.cvtColor(eye_region, cv2.COLOR_BGR2RGB)
    pixels = rgb_eye_region.reshape((-1, 3))
    kmeans = KMeans(n_clusters=1).fit(pixels)
    dominant_color = kmeans.cluster_centers_[0]
    return tuple(dominant_color.astype(int))

def detect_tattoos(frame):
    # Placeholder for tattoo detection logic
    # A real implementation would require a pre-trained model for tattoo detection
    return False
