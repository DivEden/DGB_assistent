#!/usr/bin/env python3
"""
Main entry point for the Python Desktop Application
This app is designed to be packaged into a standalone executable
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from gui.main_window import MainWindow


def main():
    """Main application function"""
    try:
        # Create the main tkinter root
        root = tk.Tk()
        
        # Create and configure the main window
        app = MainWindow(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        # Show error dialog if something goes wrong
        messagebox.showerror("Application Error", f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()