import os
import cv2
import pickle
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import normalize
from tkinter import Tk
from tkinter.filedialog import askopenfilename

model_file = "face_recognition_model.pkl"
training_folder = "training_images"  # Path to the folder containing training images

# Train the model using images in the training_images folder
def train_model():
    images = []
    labels = []
    if not os.path.exists(training_folder):
        raise ValueError(f"Training folder '{training_folder}' does not exist.")
    
    for label in os.listdir(training_folder):
        label_path = os.path.join(training_folder, label)
        if os.path.isdir(label_path):
            for img_file in os.listdir(label_path):
                if img_file.endswith(".jpg") or img_file.endswith(".png"):
                    img_path = os.path.join(label_path, img_file)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        images.append(img.flatten())
                        labels.append(label)

    if images:
        images = normalize(np.array(images))
        model = KNeighborsClassifier(n_neighbors=1)
        model.fit(images, labels)
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        print(f"Model trained using images from '{training_folder}' and saved as '{model_file}'.")
        return model
    else:
        raise ValueError(f"No images found in the training folder '{training_folder}'.")

# Recognize faces in an input image
def recognize_faces(image_path, model):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        face_img = gray[y:y+h, x:x+w].flatten()
        face_img = normalize(face_img.reshape(1, -1))
        label = model.predict(face_img)
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(image, label[0], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    cv2.imshow("Recognized Faces", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Step 1: Train the model using images in the training_images folder
    try:
        model = train_model()
    except Exception as e:
        print(f"Error: {e}")
        exit()

    # Step 2: Open a file dialog to select the image for face recognition
    print("Please select an image file for face recognition.")
    Tk().withdraw()  # Hide the root tkinter window
    image_path = askopenfilename(filetypes=[("Image files", "*.jpg *.png")])

    if image_path:
        recognize_faces(image_path, model)
    else:
        print("No file selected.")
