# gui/main_window.py (IMPROVED VERSION)
"""
Main application window with integrated preview widget
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import threading
import os
from typing import Dict, Any, Optional, Callable

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.theme_manager import ThemeManager
from gui.tab_editor import EditorTab
from gui.tab_compiler import CompilerTab
from gui.preview_widget import PreviewWidget  # Import preview widget
from utils.progress_tracker import ProgressTracker

class MainWindow:
    """
    Main application window with integrated preview and tabbed interface
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("FFmpeg Editor")
        self.root.geometry("1400x900")  # Increased size for preview
        self.root.minsize(1200, 700)
        
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
        
        self.logger.info("Main window initialized with preview integration")
    
    def setup_ui(self):
        """Setup the main UI layout with integrated preview"""
        # Create main paned window for layout
        main_paned = ttk.PanedWindow(self.root, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel for tabs
        left_frame = self.theme_manager.create_custom_frame(main_paned)
        left_frame.configure(width=600)
        main_paned.add(left_frame, weight=1)
        
        # Right panel for preview
        right_frame = self.theme_manager.create_custom_frame(main_paned)
        right_frame.configure(width=700)
        main_paned.add(right_frame, weight=1)

        # Setup left panel with tabs
        self.setup_left_panel(left_frame)

        # Setup right panel with preview
        self.setup_right_panel(right_frame)
        
        # Bottom status bar
        self.setup_status_bar()

    def setup_left_panel(self, parent):
        """Setup left panel with editor tabs"""
        # Notebook for tabs
        self.notebook = self.theme_manager.create_custom_notebook(parent)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create tabs
        self.editor_tab = EditorTab(self.notebook, self.theme_manager, self.config)
        self.compiler_tab = CompilerTab(self.notebook, self.theme_manager, self.config)
        
        self.notebook.add(self.editor_tab.frame, text="Editor")
        self.notebook.add(self.compiler_tab.frame, text="Compiler")
        
        # Connect editor tab file loading to preview
        original_load_file = self.editor_tab.load_local_file
        def enhanced_load_file():
            original_load_file()
            if hasattr(self.editor_tab, 'current_file') and self.editor_tab.current_file:
                self.load_video_to_preview(self.editor_tab.current_file)

        self.editor_tab.load_local_file = enhanced_load_file

    def setup_right_panel(self, parent):
        """Setup right panel with preview widget"""
        # Preview title
        preview_title = self.theme_manager.create_custom_label(
            parent,
            "Live Preview",
            font=('Arial', 14, 'bold')
        )
        preview_title.pack(anchor='w', pady=(0, 10))

        # Create preview widget
        self.preview_widget = PreviewWidget(parent, self.theme_manager, self.config)
        self.preview_widget.frame.pack(fill='both', expand=True)

        # Add preview controls
        self.setup_preview_controls(parent)

    def setup_preview_controls(self, parent):
        """Setup additional preview controls"""
        control_frame = self.theme_manager.create_custom_frame(parent)
        control_frame.pack(fill='x', pady=(10, 0))

        # Speed control
        speed_label = self.theme_manager.create_custom_label(control_frame, "Speed:")
        speed_label.pack(side='left', padx=(0, 5))

        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = self.theme_manager.create_custom_scale(
            control_frame,
            from_=0.25, to=2.0, variable=self.speed_var,
            orient='horizontal', length=100
        )
        speed_scale.pack(side='left', padx=(0, 5))
        speed_scale.configure(command=self.on_speed_change)

        self.speed_label = self.theme_manager.create_custom_label(control_frame, "1.0x")
        self.speed_label.pack(side='left', padx=(0, 10))

        # Marker controls
        marker_btn = self.theme_manager.create_custom_button(
            control_frame, "Add Marker", command=self.add_marker, width=10
        )
        marker_btn.pack(side='left', padx=(0, 5))

        clear_markers_btn = self.theme_manager.create_custom_button(
            control_frame, "Clear Markers", command=self.clear_markers, width=10
        )
        clear_markers_btn.pack(side='left')

    def setup_status_bar(self):
        """Setup bottom status bar"""
        status_frame = self.theme_manager.create_custom_frame(self.root)
        status_frame.pack(fill='x', padx=10, pady=(0, 10))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = self.theme_manager.create_custom_progressbar(
            status_frame,
            variable=self.progress_var,
            length=300
        )
        self.progress_bar.pack(side='left', padx=(0, 10))
        
        # Status label
        self.status_label = self.theme_manager.create_custom_label(
            status_frame,
            "Ready",
            font=('Arial', 10)
        )
        self.status_label.pack(side='left')

        # File info
        self.file_info_label = self.theme_manager.create_custom_label(
            status_frame,
            "",
            font=('Arial', 9, 'italic')
        )
        self.file_info_label.pack(side='right')

    def load_video_to_preview(self, video_path: str):
        """Load video into preview widget"""
        try:
            if self.preview_widget.load_video(video_path):
                self.current_file = video_path
                filename = os.path.basename(video_path)
                self.update_status(f"Loaded: {filename}")

                # Update file info
                file_size = os.path.getsize(video_path) / (1024*1024)  # MB
                self.file_info_label.config(text=f"{filename} ({file_size:.1f} MB)")

                self.logger.info(f"Successfully loaded video: {video_path}")
            else:
                self.update_status("Failed to load video")
                messagebox.showerror("Error", "Failed to load video file")
        except Exception as e:
            self.logger.error(f"Error loading video: {e}")
            messagebox.showerror("Error", f"Error loading video: {str(e)}")

    def on_speed_change(self, value):
        """Handle playback speed change"""
        speed = float(value)
        self.speed_label.config(text=f"{speed:.1f}x")
        if hasattr(self.preview_widget, 'set_playback_speed'):
            self.preview_widget.set_playback_speed(speed)

    def add_marker(self):
        """Add marker at current time"""
        if self.preview_widget and hasattr(self.preview_widget, 'current_time'):
            current_time = self.preview_widget.current_time
            label = f"Marker {int(current_time)}s"
            self.preview_widget.add_marker(current_time, label)
            self.update_status(f"Added marker at {current_time:.1f}s")

    def clear_markers(self):
        """Clear all markers"""
        if self.preview_widget:
            self.preview_widget.clear_markers()
            self.update_status("Cleared all markers")
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # File operations
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

        # Preview focus
        self.root.bind('<Control-p>', lambda e: self.focus_preview())
    
    def open_file(self):
        """Open file dialog"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Open Video File",
            filetypes=filetypes
        )
        
        if filename:
            self.load_video_to_preview(filename)
    
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
            # Cleanup preview widget
            if hasattr(self, 'preview_widget'):
                self.preview_widget.cleanup()
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

Preview Controls:
  Ctrl+P - Focus preview window

Other:
  F1 - Show this help
"""
        messagebox.showinfo("Help", help_text)
    
    def toggle_play_pause(self):
        """Toggle video play/pause"""
        if self.preview_widget:
            self.preview_widget.toggle_playback()
    
    def frame_backward(self):
        """Go one frame backward"""
        if self.preview_widget and self.preview_widget.cap:
            current_frame = int(self.preview_widget.current_time * self.preview_widget.fps)
            new_frame = max(0, current_frame - 1)
            self.preview_widget.load_frame(new_frame)
    
    def frame_forward(self):
        """Go one frame forward"""
        if self.preview_widget and self.preview_widget.cap:
            current_frame = int(self.preview_widget.current_time * self.preview_widget.fps)
            total_frames = int(self.preview_widget.total_duration * self.preview_widget.fps)
            new_frame = min(total_frames - 1, current_frame + 1)
            self.preview_widget.load_frame(new_frame)
    
    def goto_beginning(self):
        """Go to beginning of video"""
        if self.preview_widget and self.preview_widget.cap:
            self.preview_widget.load_frame(0)
    
    def goto_end(self):
        """Go to end of video"""
        if self.preview_widget and self.preview_widget.cap:
            total_frames = int(self.preview_widget.total_duration * self.preview_widget.fps)
            self.preview_widget.load_frame(max(0, total_frames - 1))

    def focus_preview(self):
        """Focus on preview widget"""
        if hasattr(self, 'preview_widget'):
            self.preview_widget.canvas.focus_set()
    
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
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
        self.root.mainloop()
