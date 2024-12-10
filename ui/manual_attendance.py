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
        self.window = tk.Toplevel(self.parent)
        self.window.title("Manual Attendance")
        self.window.geometry("600x400")

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
        # Fetch subjects from the database (mocked for now)
        return ["Mathematics", "Science", "History", "Literature"]

    def _submit_attendance(self):
        student_id = self.student_id_entry.get()
        subject = self.subject_var.get()

        if not student_id or not subject:
            messagebox.showwarning("Input Error", "Please enter Student ID and select a subject.")
            return

        # Save attendance to the database
        attendance_record = {
            'student_id': student_id,
            'subject': subject,
            'timestamp': datetime.datetime.now()
        }
        self.db_manager.insert_document('attendance', attendance_record)
        messagebox.showinfo("Attendance", "Attendance submitted successfully!")
        self.student_id_entry.delete(0, tk.END)