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
        self._setup_ui()

    def _setup_ui(self):
        # Menu for dark mode toggle
        menu_bar = tk.Menu(self.root)
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_command(label="Toggle Dark Mode", command=self.toggle_theme)
        menu_bar.add_cascade(label="Options", menu=theme_menu)
        self.root.config(menu=menu_bar)

        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Title
        self.title = ttk.Label(
            self.main_container,
            text="Intelligent Attendance Management System",
            font=("Arial", 24, "bold")
        )
        self.title.pack(pady=20, fill=tk.X)

        # Button frame
        self.button_frame = ttk.Frame(self.main_container)
        self.button_frame.pack(expand=True)

        # Define buttons
        self.buttons = [
            {
                "text": "Faculty Login",
                "command": self.faculty_login,
                "description": "Authenticate and manage faculty access"
            },
            {
                "text": "Student Attendance",
                "command": self.student_attendance,
                "description": "Capture student attendance"
            },
            {
                "text": "Manual Attendance",
                "command": self.manual_attendance,
                "description": "Manually enter attendance records"
            },
            {
                "text": "View Reports",
                "command": self.view_reports,
                "description": "Generate and view attendance reports"
            }
        ]

        # Create buttons
        for button_info in self.buttons:
            btn_container = ttk.Frame(self.button_frame)
            btn_container.pack(pady=10, padx=20, fill="x")

            # Create button
            btn = ttk.Button(
                btn_container,
                text=button_info["text"],
                command=button_info["command"]
            )
            btn.pack(side=tk.LEFT, expand=True, fill="x")

            # Description label
            desc_label = ttk.Label(
                btn_container,
                text=button_info["description"],
                font=("Arial", 10)
            )
            desc_label.pack(side=tk.RIGHT, padx=10)

        # Apply the default theme
        self.apply_theme(self.current_theme)

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
