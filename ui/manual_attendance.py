import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from models.database import MongoDBManager

class ManualAttendanceWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db_manager = MongoDBManager()
        self._create_manual_attendance_window()

    def _create_manual_attendance_window(self):
        self.window = tk.Frame(self.parent)
        self.window.pack(expand=True, fill='both')

        # Student ID Entry
        tk.Label(self.window, text="Enter Student ID", font=("Arial", 16)).pack(pady=10)
        self.student_id_entry = tk.Entry(self.window, font=("Arial", 14))
        self.student_id_entry.pack(pady=10)

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

        # Submit Button
        submit_btn = tk.Button(
            self.window, 
            text="Submit Attendance", 
            command=self._submit_attendance,
            font=("Arial", 16),
            bg="#3498db",
            fg="white"
        )
        submit_btn.pack(pady=20)

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

    def _submit_attendance(self):
        student_id = self.student_id_entry.get()
        subject = self.subject_var.get()

        if not student_id or not subject:
            messagebox.showwarning("Input Error", "Please enter Student ID and select a subject.")
            return

        today_date = datetime.datetime.now().date()

        # Check if attendance already recorded for this student, subject, and date
        existing_attendance = self.db_manager.find_documents(
            'attendance', 
            {'student_id': student_id, 'subject': subject, 'date': datetime.datetime.combine(today_date, datetime.datetime.min.time())}
        )
        if len(list(existing_attendance)) == 0:
            # Save attendance to the database
            attendance_record = {
                'student_id': student_id,
                'name': student_id,  # Assuming student name is same as ID, modify as needed
                'subject': subject,
                'date': datetime.datetime.combine(today_date, datetime.datetime.min.time()),  # Convert to datetime
                'time': datetime.datetime.now()
            }
            self.db_manager.insert_document('attendance', attendance_record)
            messagebox.showinfo("Attendance", "Attendance submitted successfully!")
        else:
            messagebox.showinfo("Attendance", "Attendance already recorded for today.")
        
        self.student_id_entry.delete(0, tk.END)