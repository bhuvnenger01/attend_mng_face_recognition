import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from ui.faculty_login import FacultyLoginWindow
from ui.student_attendance import StudentAttendanceWindow
from ui.manual_attendance import ManualAttendanceWindow
from ui.reports import ReportsWindow
from config import LOGGING_CONFIG

# Theme configurations
themes = {
    "light": {
        "bg": "#f0f0f0",
        "fg": "black",
        "button_bg": "#3498db",
        "button_fg": "white",
        "button_hover_bg": "#2980b9",  # Added hover color for light theme
        "title_fg": "black",
        "desc_fg": "#7f8c8d"
    },
    "dark": {
        "bg": "#121212",
        "fg": "#e0e0e0",
        "button_bg": "#1f1f1f",
        "button_fg": "#bb86fc",
        "button_hover_bg": "#3700b3",  # Hover color for dark theme
        "title_fg": "#bb86fc",
        "desc_fg": "#a0a0a0",
        "entry_bg": "#1f1f1f",
        "entry_fg": "#e0e0e0",
        "border_color": "#3c3c3c"
    }
}


class MainWindow:
    def __init__(self, root):
        # Configure logging
        logging.basicConfig(**LOGGING_CONFIG)
        self.logger = logging.getLogger(__name__)
        
        # Root window configuration
        self.root = root
        self.root.title("Attendance Management System")
        self.root.geometry("1280x720")
        self.current_theme = "light"  # Default theme
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Set up the UI
        self._create_main_window()

    def _create_main_window(self):
        # Create notebook for different functionalities
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create tabs
        self._create_faculty_login_tab()
        self._create_student_attendance_tab()
        self._create_reports_tab()
        self._create_manual_attendance_tab()

    def _create_faculty_login_tab(self):
        faculty_login_frame = ttk.Frame(self.notebook)
        self.notebook.add(faculty_login_frame, text="Faculty Login")
        self.faculty_login_window = FacultyLoginWindow(faculty_login_frame)

    def _create_student_attendance_tab(self):
        student_attendance_frame = ttk.Frame(self.notebook)
        self.notebook.add(student_attendance_frame, text="Student Attendance")
        self.student_attendance_window = StudentAttendanceWindow(student_attendance_frame)

    def _create_reports_tab(self):
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        self.reports_window = ReportsWindow(reports_frame)

    def _create_manual_attendance_tab(self):
        manual_attendance_frame = ttk.Frame(self.notebook)
        self.notebook.add(manual_attendance_frame, text="Manual Attendance")
        self.manual_attendance_window = ManualAttendanceWindow(manual_attendance_frame)

    def apply_theme(self, theme_name):
        """Apply the selected theme to the application."""
        theme = themes[theme_name]
        self.root.configure(bg=theme["bg"])
        self.main_container.configure(style='TFrame')
        self.title.configure(foreground=theme["title_fg"], background=theme["bg"])

        for child in self.button_frame.winfo_children():
            for widget in child.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.configure(style="TButton")
                elif isinstance(widget, ttk.Label):
                    widget.configure(foreground=theme["desc_fg"], background=theme["bg"])

        # Update ttk styles for dark mode
        if theme_name == "dark":
            self.style.configure(
                "TButton",
                background=theme["button_bg"],
                foreground=theme["button_fg"],
                borderwidth=1,
                relief="flat"
            )
            self.style.map(
                "TButton",
                background=[("active", theme["button_hover_bg"])],
                relief=[("pressed", "groove")]
            )
        else:
            self.style.configure(
                "TButton",
                background=theme["button_bg"],
                foreground=theme["button_fg"]
            )
            self.style.map(
                "TButton",
                background=[("active", theme["button_hover_bg"])]
            )

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(self.current_theme)

    def faculty_login(self):
        """Open Faculty Login Window."""
        try:
            FacultyLoginWindow(self.root)
            self.logger.info("Faculty Login window opened")
        except Exception as e:
            self.logger.error(f"Error opening Faculty Login window: {e}")
            messagebox.showerror("Error", "Could not open Faculty Login window")

    def student_attendance(self):
        """Open Student Attendance Window."""
        try:
            StudentAttendanceWindow(self.root)
            self.logger.info("Student Attendance window opened")
        except Exception as e:
            self.logger.error(f"Error opening Student Attendance window: {e}")
            messagebox.showerror("Error", "Could not open Student Attendance window")

    def manual_attendance(self):
        """Open Manual Attendance Window."""
        try:
            ManualAttendanceWindow(self.root)
            self.logger.info("Manual Attendance window opened")
        except Exception as e:
            self.logger.error(f"Error opening Manual Attendance window: {e}")
            messagebox.showerror("Error", "Could not open Manual Attendance window")

    def view_reports(self):
        """Open Reports Window."""
        try:
            ReportsWindow(self.root)
            self.logger.info("Reports window opened")
        except Exception as e:
            self.logger.error(f"Error opening Reports window: {e}")
            messagebox.showerror("Error", "Could not open Reports window")
