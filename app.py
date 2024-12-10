import tkinter as tk
import logging
from ui.main_window import MainWindow
from config import LOGGING_CONFIG

def main():
    logging.basicConfig(**LOGGING_CONFIG)
    try:
        root = tk.Tk()
        app = MainWindow(root)
        app.apply_theme("light")  # Set initial theme to light
        root.mainloop()
    except Exception as e:
        logging.critical(f"Application startup error: {e}")

if __name__ == "__main__":
    main()
