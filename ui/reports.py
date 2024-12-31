import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from models.database import MongoDBManager
import datetime
import logging
from tkcalendar import DateEntry

class ReportsWindow:
    def __init__(self, parent):
        # Initialize database and logging
        self.db_manager = MongoDBManager()
        self.logger = logging.getLogger(__name__)

        # Create top-level window
        self.window = tk.Toplevel(parent)
        self.window.title("Attendance Reports Dashboard")
        self.window.geometry("1200x800")
        self.window.configure(background='#f0f0f0')

        # Create notebook for different report types
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create report tabs
        self._create_overall_report_tab()
        self._create_subject_report_tab()
        self._create_student_report_tab()
        self._create_visualization_tab()

    def _create_overall_report_tab(self):
        # Overall Attendance Report Tab
        overall_frame = ttk.Frame(self.notebook)
        self.notebook.add(overall_frame, text="Overall Attendance")

        # Date Range Selection
        date_frame = ttk.Frame(overall_frame)
        date_frame.pack(pady=10)

        ttk.Label(date_frame, text="From Date:").pack(side=tk.LEFT)
        self.from_date = tk.StringVar()
        from_entry = DateEntry(date_frame, textvariable=self.from_date, date_pattern='yyyy-mm-dd')
        from_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(date_frame, text="To Date:").pack(side=tk.LEFT)
        self.to_date = tk.StringVar()
        to_entry = DateEntry(date_frame, textvariable=self.to_date, date_pattern='yyyy-mm-dd')
        to_entry.pack(side=tk.LEFT, padx=5)

        # Generate Report Button
        generate_btn = ttk.Button(
            overall_frame, 
            text="Generate Overall Report", 
            command=self._generate_overall_report
        )
        generate_btn.pack(pady=10)

        # Report Display Tree
        self.overall_tree = ttk.Treeview(
            overall_frame, 
            columns=("Date", "Total Students", "Present", "Percentage"),
            show="headings"
        )
        self.overall_tree.heading("Date", text="Date")
        self.overall_tree.heading("Total Students", text="Total Students")
        self.overall_tree.heading("Present", text="Present")
        self.overall_tree.heading("Percentage", text="Percentage")
        self.overall_tree.pack(expand=True, fill='both', padx=10, pady=10)

    def _create_subject_report_tab(self):
        # Subject-wise Attendance Report Tab
        subject_frame = ttk.Frame(self.notebook)
        self.notebook.add(subject_frame, text="Subject Attendance")

        # Subject Selection
        subject_select_frame = ttk.Frame(subject_frame)
        subject_select_frame.pack(pady=10)

        ttk.Label(subject_select_frame, text="Select Subject:").pack(side=tk.LEFT)
        self.subject_var = tk.StringVar()
        subjects = self._get_subjects()
        subject_dropdown = ttk.Combobox(
            subject_select_frame, 
            textvariable=self.subject_var, 
            values=subjects
        )
        subject_dropdown.pack(side=tk.LEFT, padx=5)

        # Generate Subject Report Button
        generate_subject_btn = ttk.Button(
            subject_frame, 
            text="Generate Subject Report", 
            command=self._generate_subject_report
        )
        generate_subject_btn.pack(pady=10)

        # Subject Report Tree
        self.subject_tree = ttk.Treeview(
            subject_frame, 
            columns=("Student ID", "Name", "Total Classes", "Attended", "Percentage", "Time"),
            show="headings"
        )
        self.subject_tree.heading("Student ID", text="Student ID")
        self.subject_tree.heading("Name", text="Name")
        self.subject_tree.heading("Total Classes", text="Total Classes")
        self.subject_tree.heading("Attended", text="Attended")
        self.subject_tree.heading("Percentage", text="Percentage")
        self.subject_tree.heading("Time", text="Time")
        self.subject_tree.pack(expand=True, fill='both', padx=10, pady=10)

    def _create_student_report_tab(self):
        # Individual Student Report Tab
        student_frame = ttk.Frame(self.notebook)
        self.notebook.add(student_frame, text="Student Report")

        # Student ID Entry
        student_id_frame = ttk.Frame(student_frame)
        student_id_frame.pack(pady=10)

        ttk.Label(student_id_frame, text="Enter Student ID:").pack(side=tk.LEFT)
        self.student_id_var = tk.StringVar()
        student_id_entry = ttk.Entry(student_id_frame, textvariable=self.student_id_var)
        student_id_entry.pack(side=tk.LEFT, padx=5)

        # Generate Student Report Button
        generate_student_btn = ttk.Button(
            student_frame, 
            text="Generate Student Report", 
            command=self._generate_student_report
        )
        generate_student_btn.pack(pady=10)

        # Student Report Tree
        self.student_tree = ttk.Treeview(
            student_frame, 
            columns=("Subject", "Total Classes", "Attended", "Percentage"),
            show="headings"
        )
        self.student_tree.heading("Subject", text="Subject")
        self.student_tree.heading("Total Classes", text="Total Classes")
        self.student_tree.heading("Attended", text="Attended")
        self.student_tree.heading("Percentage", text="Percentage")
        self.student_tree.pack(expand=True, fill='both', padx=10, pady=10)

    def _create_visualization_tab(self):
        # Visualization Tab
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualizations")

        # Visualization Type Selection
        viz_type_frame = ttk.Frame(viz_frame)
        viz_type_frame.pack(pady=10)

        ttk.Label(viz_type_frame, text="Select Visualization:").pack(side=tk.LEFT)
        self.viz_var = tk.StringVar()
        viz_types = [
            "Attendance by Subject", 
            "Student Attendance Distribution", 
            "Monthly Attendance Trend"
        ]
        viz_dropdown = ttk.Combobox(
            viz_type_frame, 
            textvariable=self.viz_var, 
            values=viz_types
        )
        viz_dropdown.pack(side=tk.LEFT, padx=5)

        # Generate Visualization Button
        generate_viz_btn = ttk.Button(
            viz_frame, 
            text="Generate Visualization", 
            command=self._generate_visualization
        )
        generate_viz_btn.pack(pady=10)

        # Visualization Canvas
        self.viz_canvas_frame = ttk.Frame(viz_frame)
        self.viz_canvas_frame.pack(expand=True, fill='both', padx=10, pady=10)

    def _get_subjects(self):
        # Fetch subjects from database
        try:
            subjects = self.db_manager.find_documents('subjects', {}, {'name': 1})
            return [subject['name'] for subject in subjects]
        except Exception as e:
            self.logger.error(f"Error fetching subjects: {e}")
            messagebox.showerror("Error", "Could not retrieve subjects from the database")
            return []

    def _generate_overall_report(self):
        # Generate overall attendance report based on date range
        from_date = self.from_date.get()
        to_date = self.to_date.get()
        try:
            report_data = self.db_manager.get_overall_attendance(from_date, to_date)
            self.overall_tree.delete(*self.overall_tree.get_children())  # Clear previous data
            for row in report_data:
                self.overall_tree.insert("", "end", values=row)
            self.logger.info("Overall attendance report generated successfully")
        except Exception as e:
            self.logger.error(f"Error generating overall report: {e}")
            messagebox.showerror("Error", "Could not generate overall report")

    def _generate_subject_report(self):
        # Generate subject-wise attendance report
        subject = self.subject_var.get()
        try:
            report_data = self.db_manager.get_subject_attendance(subject)
            self.subject_tree.delete(*self.subject_tree.get_children())  # Clear previous data
            for row in report_data:
                self.subject_tree.insert("", "end", values=row)
            self.logger.info(f"Subject attendance report for {subject} generated successfully")
        except Exception as e:
            self.logger.error(f"Error generating subject report: {e}")
            messagebox.showerror("Error", "Could not generate subject report")

    def _generate_student_report(self):
        # Generate individual student attendance report
        student_id = self.student_id_var.get()
        try:
            report_data = self.db_manager.get_student_attendance(student_id)
            for row in report_data:
                self.student_tree.insert("", "end", values=row)
            self.logger.info(f"Student attendance report for ID {student_id} generated successfully")
        except Exception as e:
            self.logger.error(f"Error generating student report: {e}")
            messagebox.showerror("Error", "Could not generate student report")

    def _generate_visualization(self):
        # Generate visualizations based on selected type
        viz_type = self.viz_var.get()
        try:
            if viz_type == "Attendance by Subject":
                self._visualize_attendance_by_subject()
            elif viz_type == "Student Attendance Distribution":
                self._visualize_student_attendance_distribution()
            elif viz_type == "Monthly Attendance Trend":
                self._visualize_monthly_attendance_trend()
            self.logger.info(f"Visualization for {viz_type} generated successfully")
        except Exception as e:
            self.logger.error(f"Error generating visualization: {e}")
            messagebox.showerror("Error", "Could not generate visualization")

    def _visualize_attendance_by_subject(self):
        # Logic to visualize attendance by subject
        data = self.db_manager.get_attendance_by_subject()
        subjects = [item['subject'] for item in data]
        attendance_counts = [item['attendance_count'] for item in data]

        plt.figure(figsize=(10, 6))
        sns.barplot(x=subjects, y=attendance_counts)
        plt.title("Attendance by Subject")
        plt.xlabel("Subjects")
        plt.ylabel("Attendance Count")
        plt.xticks(rotation=45)
        self._show_plot()

    def _visualize_student_attendance_distribution(self):
        # Logic to visualize student attendance distribution
        data = self.db_manager.get_student_attendance_distribution()
        students = [item['student_name'] for item in data]
        attendance_percentages = [item['attendance_percentage'] for item in data]

        plt.figure(figsize=(10, 6))
        sns.histplot(attendance_percentages, bins=10, kde=True)
        plt.title("Student Attendance Distribution")
        plt.xlabel("Attendance Percentage")
        plt.ylabel("Number of Students")
        self._show_plot()

    def _visualize_monthly_attendance_trend(self):
        # Logic to visualize monthly attendance trend
        data = self.db_manager.get_monthly_attendance_trend()
        months = [item['month'] for item in data]
        attendance_counts = [item['attendance_count'] for item in data]

        plt.figure(figsize=(10, 6))
        sns.lineplot(x=months, y=attendance_counts, marker='o')
        plt.title("Monthly Attendance Trend")
        plt.xlabel("Months")
        plt.ylabel("Attendance Count")
        self._show_plot()

    def _show_plot(self):
        # Display the plot in the Tkinter window
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.viz_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')

# Note: Ensure that the MongoDBManager class has the necessary methods to fetch data for reports.