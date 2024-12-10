import os
import cv2

# Base configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# MongoDB Atlas Configuration
MONGODB_CONFIG = {
    'url': 'mongodb+srv://bhuvisins02:9806671598@attendance-info.5ub4f.mongodb.net/?retryWrites=true&w=majority&appName=attendance-info',
    'database': 'attendance-info'
}

# Directories
DIRECTORIES = {
    'faculty_faces': os.path.join(BASE_DIR, 'data', 'faculty_faces'),
    'student_faces': os.path.join(BASE_DIR, 'data', 'student_faces'),
    'attendance_logs': os.path.join(BASE_DIR, 'data', 'attendance_logs'),
    'training_images': os.path.join(BASE_DIR,'Training_images')
    
}

# Face Recognition Settings
FACE_RECOGNITION_CONFIG = {
    'cascade_path': cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
    'confidence_threshold': 70,
    'sample_images': 50
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s: %(message)s'
}

# Ensure directories exist
for directory in DIRECTORIES.values():
    os.makedirs(directory, exist_ok=True)