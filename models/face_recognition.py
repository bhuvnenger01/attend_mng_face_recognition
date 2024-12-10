import cv2
import os
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import normalize
import pickle


class FaceRecognition:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.model = KNeighborsClassifier(n_neighbors=1)
        self.model_file = "face_recognition_model.pkl"
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_file):
            with open(self.model_file, 'rb') as f:
                self.model = pickle.load(f)
            print("Model loaded successfully.")
        else:
            print("No trained model found. Please train the model.")

    def save_model(self):
        with open(self.model_file, 'wb') as f:
            pickle.dump(self.model, f)
        print("Model saved successfully.")

    def detect_faces(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces, gray

    def is_model_trained(self):
        return hasattr(self.model, 'classes_') and len(self.model.classes_) > 0

    def train_model(self, faculty_faces):
        images = []
        labels = []

        for img_file in os.listdir(faculty_faces):
            if img_file.endswith(".jpg"):
                img_path = os.path.join(faculty_faces, img_file)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                images.append(img.flatten())
                labels.append(os.path.basename(faculty_faces))  # Use folder name as label

        if images:
            images = normalize(np.array(images))
            self.model.fit(images, labels)
            self.save_model()
            print(f"Trained with {len(labels)} images.")
            return True
        else:
            print("No images for training.")
            return False

    def recognize_face(self, face_img):
        try:
            if not self.is_model_trained():
                raise ValueError("Model has not been trained yet.")
            face_img = normalize(face_img.flatten().reshape(1, -1))
            label = self.model.predict(face_img)
            return label[0], 100  # Returning dummy confidence
        except Exception as e:
            print(f"Error: {e}")
            return None, None

