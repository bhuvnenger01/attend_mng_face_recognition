import logging
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import datetime

import pymongo
from models.database import MongoDBManager
from models.face_recognition import FaceRecognition
from config import MONGODB_CONFIG

MONGO_URL = MONGODB_CONFIG['url']
MONGO_DB = MONGODB_CONFIG['database']

class StudentAttendanceWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db_manager = MongoDBManager()
        self.face_recognizer = FaceRecognition()

        # Setup logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        self._create_attendance_window()

    def _create_attendance_window(self):
        self.window = tk.Frame(self.parent)
        self.window.pack(expand=True, fill='both')

        # Subject Selection
        tk.Label(self.window, text="Select Subject", font=("Arial", 16)).pack(pady=10)
        self.subject_var = tk.StringVar()
        subjects = self._get_subjects()
        subject_dropdown = ttk.Combobox(
            self.window, 
            textvariable=self.subject_var, 
            values=subjects,
            font=("Arial", 14)
        )
        subject_dropdown.pack(pady=10)

        # Attendance Capture Button
        capture_btn = tk.Button(
            self.window, 
            text="Capture Attendance", 
            command=self._capture_attendance,
            font=("Arial", 16),
            bg="#3498db",
            fg="white"
        )
        capture_btn.pack(pady=20)

        # Attendance List
        self.attendance_tree = ttk.Treeview(
            self.window, 
            columns=("Student ID", "Name", "Time"), 
            show='headings', 
            height=15
        )
        self.attendance_tree.heading("Student ID", text="Student ID")
        self.attendance_tree.heading("Name", text="Name")
        self.attendance_tree.heading("Time", text="Time")
        self.attendance_tree.pack(pady=20)

    def _get_subjects(self):
        """
        Fetch subjects from the database with comprehensive error handling
        and fallback mechanism.
        """
        try:
            # Attempt to fetch subjects from subjects collection
            subjects_cursor = self.db_manager.get_collection('subjects').find({}, {'name': 1})
            subjects = [subject.get('name', 'Unknown Subject') for subject in subjects_cursor]
            
            # If no subjects found, try alternative collections
            if not subjects:
                # Attempt to extract unique subjects from attendance records
                subjects_cursor = self.db_manager.get_collection('attendance').distinct('subject')
                subjects = list(subjects_cursor)
            
            # Fallback to predefined list if still no subjects
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
                
                # Optional: Insert fallback subjects into database
                self._insert_default_subjects(subjects)
            
            return subjects
        
        except Exception as e:
            # Comprehensive logging
            self.logger.error(f"Error retrieving subjects: {e}")
            
            # User-friendly error handling
            messagebox.showwarning(
                "Subject Retrieval Error", 
                "Could not fetch subjects. Using default list."
            )
            
            # Return predefined list as last resort
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
    
    # Enhanced Subject Management Method
    def manage_subjects(self):
        """
        Provide a UI for managing subjects in the database
        """
        subject_window = tk.Toplevel(self.window)
        subject_window.title("Manage Subjects")
        subject_window.geometry("600x400")
    
        # Subject List
        subject_frame = ttk.Frame(subject_window)
        subject_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
        # Treeview to display subjects
        subject_tree = ttk.Treeview(
            subject_frame, 
            columns=('Name', 'Code', 'Created At'), 
            show='headings'
        )
        subject_tree.heading('Name', text='Subject Name')
        subject_tree.heading('Code', text='Subject Code')
        subject_tree.heading('Created At', text='Created Date')
    
        # Populate subjects
        subjects = self.db_manager.collection['subjects'].find()
        for subject in subjects:
            subject_tree.insert('', 'end', values=(
                subject.get('name', 'N/A'),
                subject.get('code', 'N/A'),
                subject.get('created_at', 'N/A')
            ))
    
        subject_tree.pack(fill=tk.BOTH, expand=True)
    
        # Add Subject Section
        add_frame = ttk.Frame(subject_window)
        add_frame.pack(padx=10, pady=10, fill=tk.X)
    
        ttk.Label(add_frame, text="Subject Name:").pack(side=tk.LEFT)
        subject_name_entry = ttk.Entry(add_frame)
        subject_name_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
        def add_subject():
            subject_name = subject_name_entry.get().strip()
            if subject_name:
                try:
                    # Insert new subject
                    self.db_manager.collection['subjects'].insert_one({
                        'name': subject_name,
                        'code': subject_name[:3].upper(),
                        'created_at': datetime.datetime.now()
                    })
                    
                    # Refresh subject list
                    subject_tree.delete(*subject_tree.get_children())
                    subjects = self.db_manager.collection['subjects'].find()
                    for subject in subjects:
                        subject_tree.insert('', 'end', values=(
                            subject.get('name', 'N/A'),
                            subject.get('code', 'N/A'),
                            subject.get('created_at', 'N/A')
                        ))
                    
                    subject_name_entry.delete(0, tk.END)
                    messagebox.showinfo("Success", "Subject added successfully")
                
                except Exception as e:
                    messagebox.showerror("Error", f"Could not add subject: {e}")
    
        add_button = ttk.Button(add_frame, text="Add Subject", command=add_subject)
        add_button.pack(side=tk.RIGHT)
        

    def _capture_attendance(self):
        # Open camera for face recognition
        cap = cv2.VideoCapture(0)
        recognized_students = set()
        today_date = datetime.datetime.now().date()
        subject = self.subject_var.get()

        while True:
            ret, frame = cap.read()
            faces, gray = self.face_recognizer.detect_faces(frame)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                face_img = gray[y:y+h, x:x+w]

                # Attempt to recognize
                student_id, confidence = self.face_recognizer.recognize_face(face_img)

                if student_id and student_id not in recognized_students:
                    # Verify student in database
                    student_cursor = self.db_manager.find_documents(
                        'students', 
                        {'student_id': student_id}
                    )

                    for student in student_cursor:
                        student_name = student['name']
                        # Check if attendance already recorded for this student, subject, and date
                        existing_attendance = self.db_manager.find_documents(
                            'attendance', 
                            {'student_id': student_id, 'subject': subject, 'date': datetime.datetime.combine(today_date, datetime.datetime.min.time())}
                        )
                        if len(list(existing_attendance)) == 0:
                            recognized_students.add(student_id)
                            self.attendance_tree.insert('', 'end', values=(student_id, student_name, datetime.datetime.now()))
                            
                            # Log attendance in the database
                            self.db_manager.insert_document('attendance', {
                                'student_id': student_id,
                                'name': student_name,
                                'subject': subject,
                                'date': datetime.datetime.combine(today_date, datetime.datetime.min.time()),  # Convert to datetime
                                'time': datetime.datetime.now()
                            })
                            messagebox.showinfo("Attendance", f"Attendance for {student_name} captured successfully!")
                        else:
                            messagebox.showinfo("Attendance", f"Attendance for {student_name} already recorded for today.")
                            cap.release()
                            cv2.destroyAllWindows()
                            self.window.destroy()
                            return

            cv2.imshow("Face Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord('q') or len(recognized_students) > 0:
                break

        cap.release()
        cv2.destroyAllWindows()
        if not recognized_students:
            messagebox.showinfo("Attendance", "No new attendance captured.")
        self.window.destroy()
