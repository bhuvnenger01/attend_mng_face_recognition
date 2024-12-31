import tkinter as tk
from tkinter import messagebox
import cv2
import os
from models.database import MongoDBManager
from models.face_recognition import FaceRecognition
from config import DIRECTORIES
from ui.faculty_window import FacultyWindow
import datetime
from tkinter import ttk

class FacultyLoginWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db_manager = MongoDBManager()
        self.face_recognizer = FaceRecognition()
        self._create_login_window()

    def _create_login_window(self):
        self.window = tk.Frame(self.parent)
        self.window.pack(expand=True, fill='both')

        # Title
        title_label = tk.Label(
            self.window, text="Faculty Authentication", font=("Arial", 24, "bold"),
            bg="#2c3e50", fg="white", pady=20)
        title_label.pack(fill=tk.X)

        # Login Methods Frame
        login_frame = tk.Frame(self.window, bg='#f0f0f0')
        login_frame.pack(expand=True)

        # Face Recognition Login Button
        face_login_btn = tk.Button(
            login_frame, text="Login with Face Recognition",
            command=self._face_login, font=("Arial", 14),
            bg="#3498db", fg="white")
        face_login_btn.pack(pady=20)

        # Register New Faculty Button
        register_btn = tk.Button(
            login_frame, text="Register New Faculty",
            command=self._register_faculty, font=("Arial", 14),
            bg="#2ecc71", fg="white")
        register_btn.pack(pady=10)

        # Manual Login Button
        manual_login_btn = tk.Button(
            login_frame, text="Manual Login with Credentials",
            command=self._manual_login, font=("Arial", 14),
            bg="#e74c3c", fg="white")
        manual_login_btn.pack(pady=10)

    def _generate_faculty_id(self):
        """
        Generate a new unique Faculty ID based on the last faculty ID in the database.
        :return: New Faculty ID as a string.
        """
        last_faculty = self.db_manager.find_documents('faculty', {}, sort=[("faculty_id", -1)])
        last_faculty = list(last_faculty)
        if last_faculty:
            last_id = last_faculty[0]["faculty_id"]
            number = int(last_id.replace("FACULTY", ""))
            new_id = f"FACULTY{number + 1:02d}"
        else:
            new_id = "FACULTY01"
        return new_id

    def _manual_login(self):
        login_window = tk.Toplevel(self.window)
        login_window.title("Manual Login")
        login_window.geometry("400x400")

        # Faculty ID
        tk.Label(login_window, text="Faculty ID").pack()
        faculty_id_entry = tk.Entry(login_window, width=30)
        faculty_id_entry.pack()

        # Password
        tk.Label(login_window, text="Password").pack()
        password_entry = tk.Entry(login_window, show='*', width=30)
        password_entry.pack()

        # Subject Selection
        tk.Label(login_window, text="Select Subject").pack(pady=10)
        self.subject_var = tk.StringVar()
        subjects = self._get_subjects()
        subject_dropdown = ttk.Combobox(
            login_window, 
            textvariable=self.subject_var, 
            values=subjects,
            font=("Arial", 14)
        )
        subject_dropdown.pack(pady=10)

        def authenticate():
            faculty_id = faculty_id_entry.get().strip()
            password = password_entry.get().strip()
            subject = self.subject_var.get()

            if not faculty_id or not password or not subject:
                messagebox.showerror("Error", "All fields are required.")
                return

            # Fetch user details from the database
            faculty_cursor = self.db_manager.find_documents('faculty', {'faculty_id': faculty_id, 'password': password})
            faculty = list(faculty_cursor)
            if faculty:
                messagebox.showinfo("Login Success", f"Welcome {faculty[0]['name']}")
                login_window.destroy()
                self._open_faculty_window()
            else:
                messagebox.showerror("Error", "Invalid credentials. Please try again.")

        # Login Button
        login_btn = tk.Button(login_window, text="Login", command=authenticate, bg="#3498db", fg="white")
        login_btn.pack(pady=20)

    def _get_subjects(self):
        """
        Fetch subjects from the database with comprehensive error handling
        and fallback mechanism.
        """
        try:
            subjects_cursor = self.db_manager.get_collection('subjects').find({}, {'name': 1})
            subjects = [subject.get('name', 'Unknown Subject') for subject in subjects_cursor]
            
            if not subjects:
                subjects_cursor = self.db_manager.get_collection('attendance').distinct('subject')
                subjects = list(subjects_cursor)
            
            if not subjects:
                subjects = [
                    "Mathematics", 
                    "Science", 
                    "History", 
                    "English", 
                    "Computer Science", 
                    "Physics", 
                    "Chemistry"
                ]
                
                self._insert_default_subjects(subjects)
            
            return subjects
        
        except Exception as e:
            self.logger.error(f"Error retrieving subjects: {e}")
            messagebox.showwarning("Subject Retrieval Error", "Could not fetch subjects. Using default list.")
            return [
                "Mathematics", 
                "Science", 
                "History", 
                "English", 
                "Computer Science", 
                "Physics", 
                "Chemistry"
            ]

    def _insert_default_subjects(self, subjects):
        """
        Insert default subjects into the database if they don't exist
        """
        try:
            inserted_ids = self.db_manager.insert_subjects(subjects)
            if inserted_ids:
                self.logger.info("Default subjects inserted successfully")
            else:
                self.logger.warning("No subjects were inserted")
        except Exception as e:
            self.logger.warning(f"Could not insert default subjects: {e}")

    def _face_login(self):
        if not self.face_recognizer.is_model_trained():
            messagebox.showerror("Error", "Face recognition model is not trained. Register faculty first!")
            return

        cap = cv2.VideoCapture(0)
        recognized = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            faces, gray = self.face_recognizer.detect_faces(frame)
            for (x, y, w, h) in faces:
                face_img = gray[y:y+h, x:x+w]
                faculty_id, confidence = self.face_recognizer.recognize_face(face_img)

                if faculty_id:
                    faculty_cursor = self.db_manager.find_documents('faculty', {'faculty_id': faculty_id})
                    faculty = list(faculty_cursor)
                    if faculty:
                        recognized = True
                        messagebox.showinfo("Login Success", f"Welcome {faculty[0]['name']}")
                        break

            if recognized:
                self._open_faculty_window()
                break

            cv2.imshow('Faculty Login', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        if not recognized:
            messagebox.showerror("Login Failed", "Face not recognized. Please try again.")

    def _register_faculty(self):
        reg_window = tk.Toplevel(self.window)
        reg_window.title("Faculty Registration")
        reg_window.geometry("400x400")
        reg_window.configure(bg="#f0f0f0")
    
        # Title
        tk.Label(
            reg_window, text="Faculty Registration", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white"
        ).pack(fill=tk.X, pady=10)
    
        # Faculty ID
        tk.Label(reg_window, text="Faculty ID", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        faculty_id = self._generate_faculty_id()
        id_entry = tk.Entry(reg_window, width=30, font=("Arial", 10))
        id_entry.insert(0, faculty_id)
        id_entry.config(state='disabled')
        id_entry.pack()
    
        # Name
        tk.Label(reg_window, text="Name", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        name_entry = tk.Entry(reg_window, width=30, font=("Arial", 10))
        name_entry.pack()
    
        # Email
        tk.Label(reg_window, text="Email", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        email_entry = tk.Entry(reg_window, width=30, font=("Arial", 10))
        email_entry.pack()
    
        # Password
        tk.Label(reg_window, text="Password", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
        password_entry = tk.Entry(reg_window, show='*', width=30, font=("Arial", 10))
        password_entry.pack()
    
        # Register Button
        def capture_and_train_faces():
            if not name_entry.get().strip() or not email_entry.get().strip() or not password_entry.get().strip():
                messagebox.showerror("Error", "All fields are required!")
                return
    
            faculty_folder = os.path.join(DIRECTORIES['faculty_faces'], faculty_id)
            os.makedirs(faculty_folder, exist_ok=True)
    
            cap = cv2.VideoCapture(0)
            face_count = 0
    
            while face_count < 5:  # Capture 5 images
                ret, frame = cap.read()
                if not ret:
                    break
                faces, gray = self.face_recognizer.detect_faces(frame)
    
                for (x, y, w, h) in faces:
                    face_img = gray[y:y+h, x:x+w]
                    face_path = os.path.join(faculty_folder, f"face_{face_count + 1}.jpg")
                    cv2.imwrite(face_path, cv2.resize(face_img, (100, 100)))
                    face_count += 1
    
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.imshow("Capture Faces", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    
            cap.release()
            cv2.destroyAllWindows()
    
            if face_count >= 5:
                self.face_recognizer.train_model(faculty_folder)
                self.db_manager.insert_document('faculty', {
                    'faculty_id': faculty_id,
                    'name': name_entry.get(),
                    'email': email_entry.get(),
                    'password': password_entry.get()
                })
                messagebox.showinfo("Success", "Faculty registered successfully!")
                reg_window.destroy()
            else:
                messagebox.showerror("Error", "Not enough face images captured.")
    
        register_btn = tk.Button(
            reg_window, text="Capture and Register Face", font=("Arial", 12),
            bg="#3498db", fg="white", command=capture_and_train_faces
        )
        register_btn.pack(pady=20)

    def _open_faculty_window(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        FacultyWindow(self.parent)
