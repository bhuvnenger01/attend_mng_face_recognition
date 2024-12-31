import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import cv2
import numpy as np
from models.face_recognition import FaceRecognition
from sklearn.preprocessing import normalize
from config import DIRECTORIES
from models.database import MongoDBManager

class FacultyWindow:
    def __init__(self, parent):
        self.parent = parent
        self.face_recognizer = FaceRecognition()
        self.db_manager = MongoDBManager()
        self._create_faculty_window()

    def _create_faculty_window(self):
        self.window = tk.Frame(self.parent)
        self.window.pack(expand=True, fill='both')

        # Register Student Faces Button
        register_btn = tk.Button(
            self.window, 
            text="Register Student Faces", 
            command=self._register_student_faces,
            font=("Arial", 16),
            bg="#3498db",
            fg="white"
        )
        register_btn.pack(pady=20)

        # Logout Button
        logout_btn = tk.Button(
            self.window, 
            text="Logout", 
            command=self._logout,
            font=("Arial", 16),
            bg="#e74c3c",
            fg="white"
        )
        logout_btn.pack(pady=20)

    def _register_student_faces(self):
        """
        Register student faces using images from a specific folder.
        """
        reg_frame = tk.Frame(self.window)
        reg_frame.pack(expand=True, fill='both')

        # Title
        tk.Label(
            reg_frame, text="Student Registration", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white"
        ).pack(fill=tk.X, pady=10)

        # Student ID
        tk.Label(reg_frame, text="Student ID", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        student_id_entry = tk.Entry(reg_frame, width=30, font=("Arial", 10))
        student_id_entry.pack()

        # Name
        tk.Label(reg_frame, text="Name", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        name_entry = tk.Entry(reg_frame, width=30, font=("Arial", 10))
        name_entry.pack()

        # Select Images Button
        def select_images():
            folder_selected = filedialog.askdirectory(initialdir=DIRECTORIES['student_faces'], title="Select Folder")
            if folder_selected:
                student_id_entry.delete(0, tk.END)
                student_id_entry.insert(0, os.path.basename(folder_selected))
                name_entry.delete(0, tk.END)
                name_entry.insert(0, os.path.basename(folder_selected))

        select_images_btn = tk.Button(
            reg_frame, text="Select Images Folder", font=("Arial", 12),
            bg="#3498db", fg="white", command=select_images
        )
        select_images_btn.pack(pady=10)

        # Register Button
        def capture_and_register_faces():
            student_id = student_id_entry.get().strip()
            student_name = name_entry.get().strip()

            if not student_id or not student_name:
                messagebox.showerror("Error", "Both fields are required!")
                return

            student_folder = os.path.join(DIRECTORIES['student_faces'], student_id)
            os.makedirs(student_folder, exist_ok=True)

            cap = cv2.VideoCapture(0)
            face_count = 0

            while face_count < 5:  # Capture 5 images
                ret, frame = cap.read()
                if not ret:
                    break
                faces, gray = self.face_recognizer.detect_faces(frame)

                for (x, y, w, h) in faces:
                    face_img = gray[y:y+h, x:x+w]
                    face_path = os.path.join(student_folder, f"face_{face_count + 1}.jpg")
                    cv2.imwrite(face_path, cv2.resize(face_img, (100, 100)))
                    face_count += 1

                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.imshow("Capture Faces", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

            if face_count >= 5:
                self.face_recognizer.train_model(student_folder)
                self.db_manager.insert_document('students', {
                    'student_id': student_id,
                    'name': student_name
                })
                messagebox.showinfo("Success", "Student registered successfully!")
                reg_frame.destroy()
            else:
                messagebox.showerror("Error", "Not enough face images captured.")

        register_btn = tk.Button(
            reg_frame, text="Capture and Register Face", font=("Arial", 12),
            bg="#3498db", fg="white", command=capture_and_register_faces
        )
        register_btn.pack(pady=20)

    def _logout(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        from ui.faculty_login import FacultyLoginWindow
        FacultyLoginWindow(self.parent)
