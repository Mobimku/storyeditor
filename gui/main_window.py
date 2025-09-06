# gui/main_window.py
"""
Main application window with tabbed interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import threading
import os  # Tambahkan import ini
from typing import Dict, Any, Optional, Callable

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.theme_manager import ThemeManager
from gui.tab_editor import EditorTab
from gui.tab_compiler import CompilerTab
from utils.progress_tracker import ProgressTracker

class MainWindow:
    """
    Main application window with tabbed interface
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("FFmpeg Editor")
        self.root.geometry("1200x800")
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.config)
        self.theme_manager.apply_theme(self.root)
        
        # Initialize progress tracker
        self.progress_tracker = ProgressTracker()
        
        # Setup UI components
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        
        # Application state
        self.current_file = None
        self.is_processing = False
        
        self.logger.info("Main window initialized")
    
# gui/main_window.py (bagian setup_ui yang perlu diperbaiki)

    def setup_ui(self):
        """Setup the main UI layout"""
        # Main container
        main_container = self.theme_manager.create_custom_frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Preview area (placeholder)
        preview_frame = self.theme_manager.create_custom_frame(main_container, 'Preview.TFrame')
        preview_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        preview_label = self.theme_manager.create_custom_label(
            preview_frame, 
            "Video Preview Area\n(Will be implemented in preview_widget.py)",
            font=('Arial', 12)
        )
        preview_label.pack(expand=True)
        
        # Notebook for tabs
        self.notebook = self.theme_manager.create_custom_notebook(main_container)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create tabs
        self.editor_tab = EditorTab(self.notebook, self.theme_manager, self.config)
        self.compiler_tab = CompilerTab(self.notebook, self.theme_manager, self.config)
        
        self.notebook.add(self.editor_tab.frame, text="Editor")
        self.notebook.add(self.compiler_tab.frame, text="Compiler")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = self.theme_manager.create_custom_progressbar(
            main_container, 
            variable=self.progress_var,
            length=400
        )
        self.progress_bar.pack(fill='x', pady=(0, 5))
        
        # Status label
        self.status_label = self.theme_manager.create_custom_label(
            main_container, 
            "Ready",
            font=('Arial', 9)
        )
        self.status_label.pack()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_project())
        self.root.bind('<Control-q>', lambda e: self.quit_application())
        self.root.bind('<F1>', lambda e: self.show_help())
        
        # Playback controls
        self.root.bind('<space>', lambda e: self.toggle_play_pause())
        self.root.bind('<Left>', lambda e: self.frame_backward())
        self.root.bind('<Right>', lambda e: self.frame_forward())
        self.root.bind('<Home>', lambda e: self.goto_beginning())
        self.root.bind('<End>', lambda e: self.goto_end())
    
    def open_file(self):
        """Open file dialog"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Open Video File",
            filetypes=filetypes
        )
        
        if filename:
            self.current_file = filename
            self.update_status(f"Loaded: {os.path.basename(filename)}")
            # TODO: Load video in preview widget
    
    def save_project(self):
        """Save project dialog"""
        if not self.current_file:
            messagebox.showwarning("No Project", "No project to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Project",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            # TODO: Implement project saving
            self.update_status(f"Project saved: {os.path.basename(filename)}")
    
    def quit_application(self):
        """Quit application with confirmation"""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.quit()
    
    def show_help(self):
        """Show help dialog"""
        help_text = """FFmpeg Editor - Keyboard Shortcuts

File Operations:
  Ctrl+O - Open file
  Ctrl+S - Save project
  Ctrl+Q - Quit application

Playback Controls:
  Space - Toggle play/pause
  Left Arrow - Frame backward
  Right Arrow - Frame forward
  Home - Go to beginning
  End - Go to end

Other:
  F1 - Show this help
"""
        messagebox.showinfo("Help", help_text)
    
    def toggle_play_pause(self):
        """Toggle video play/pause"""
        # TODO: Implement play/pause functionality
        self.update_status("Play/Pause (not implemented)")
    
    def frame_backward(self):
        """Go one frame backward"""
        # TODO: Implement frame navigation
        self.update_status("Frame backward (not implemented)")
    
    def frame_forward(self):
        """Go one frame forward"""
        # TODO: Implement frame navigation
        self.update_status("Frame forward (not implemented)")
    
    def goto_beginning(self):
        """Go to beginning of video"""
        # TODO: Implement navigation
        self.update_status("Go to beginning (not implemented)")
    
    def goto_end(self):
        """Go to end of video"""
        # TODO: Implement navigation
        self.update_status("Go to end (not implemented)")
    
    def update_status(self, message: str):
        """Update status message"""
        self.status_label.config(text=message)
        self.logger.info(f"Status: {message}")
    
    def update_progress(self, value: float):
        """Update progress bar"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def start_processing(self, operation: str, callback: Callable):
        """Start processing operation in separate thread"""
        if self.is_processing:
            messagebox.showwarning("Processing", "Already processing another operation.")
            return
        
        self.is_processing = True
        self.update_status(f"Processing: {operation}...")
        
        # Run in separate thread to keep UI responsive
        thread = threading.Thread(target=callback)
        thread.daemon = True
        thread.start()
    
    def finish_processing(self, success: bool = True, message: str = ""):
        """Finish processing operation"""
        self.is_processing = False
        self.update_progress(0.0)
        
        if success:
            self.update_status(f"Completed: {message}")
        else:
            self.update_status(f"Failed: {message}")
            messagebox.showerror("Error", message)
    
    def run(self):
        """Start the application main loop"""
        self.root.mainloop()

# Test the main_window
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and run main window
    app = MainWindow()
    app.run()