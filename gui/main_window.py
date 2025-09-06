# gui/main_window.py
"""
Main application window with a modern, multi-panel layout.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import threading
import os
from typing import Dict, Any, Optional, Callable

# Add project root to sys.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.theme_manager import ThemeManager
from gui.tab_editor import EditorTab
from gui.tab_compiler import CompilerTab
from gui.preview_widget import PreviewWidget
from gui.timeline_widget import TimelineWidget
from core.temp_manager import TempManager
from core.scene_detector import SceneDetector
from core.timeline_manager import TimelineManager
from utils.progress_tracker import ProgressTracker

class MainWindow:
    """
    Main application window with a resizable 3-panel layout.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        self.root = tk.Tk()
        self.root.title("FFmpeg Editor - Modern UI")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)
        
        self.theme_manager = ThemeManager(self.config)
        self.theme_manager.apply_theme(self.root)
        
        # Core components
        self.temp_manager = TempManager(self.config)
        self.scene_detector = SceneDetector(self.temp_manager)
        self.timeline_manager = TimelineManager(self.temp_manager)
        self.progress_tracker = ProgressTracker()
        
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        
        self.current_file = None
        self.is_processing = False
        
        self.logger.info("MainWindow with 3-panel layout initialized")
    
    def setup_ui(self):
        """Setup the main UI layout using a PanedWindow."""
        # Main PanedWindow for resizable panels
        main_paned = ttk.PanedWindow(self.root, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=10, pady=10)

        # Left panel (for editor tabs)
        left_panel = self.create_left_panel(main_paned)
        main_paned.add(left_panel, weight=1, minsize=300)

        # Center panel (for preview and timeline)
        center_panel = self.create_center_panel(main_paned)
        main_paned.add(center_panel, weight=3, minsize=600)

        # Right panel (placeholder for effects/properties)
        right_panel = self.create_right_panel(main_paned)
        main_paned.add(right_panel, weight=1, minsize=250)

        # Status Bar at the bottom
        self.setup_status_bar()

    def create_left_panel(self, parent):
        """Creates the left panel containing the editor and compiler tabs."""
        left_frame = self.theme_manager.create_custom_frame(parent)

        self.notebook = self.theme_manager.create_custom_notebook(left_frame)
        self.notebook.pack(fill='both', expand=True)

        self.editor_tab = EditorTab(self.notebook, self.theme_manager, self.config)
        self.compiler_tab = CompilerTab(self.notebook, self.theme_manager, self.config)
        
        self.notebook.add(self.editor_tab.frame, text="Editor")
        self.notebook.add(self.compiler_tab.frame, text="Compiler")
        
        # Monkey-patch the file loading to link it to the preview widget
        original_load_file = self.editor_tab.load_local_file
        def enhanced_load_file():
            original_load_file()
            if hasattr(self.editor_tab, 'current_file') and self.editor_tab.current_file:
                self.load_video_to_preview(self.editor_tab.current_file)
        self.editor_tab.load_local_file = enhanced_load_file

        return left_frame

    def create_center_panel(self, parent):
        """Creates the center panel containing the preview and timeline."""
        center_frame = self.theme_manager.create_custom_frame(parent)
        
        # Use a PanedWindow for vertical resizing
        center_paned = ttk.PanedWindow(center_frame, orient='vertical')
        center_paned.pack(fill='both', expand=True)

        # Preview Widget (top)
        self.preview_widget = PreviewWidget(center_paned, self.theme_manager, self.config)
        center_paned.add(self.preview_widget.frame, weight=3, minsize=400)
        
        # Timeline Widget (bottom)
        self.timeline_widget = TimelineWidget(center_paned, self.timeline_manager, self.theme_manager)
        center_paned.add(self.timeline_widget.frame, weight=1, minsize=200)

        return center_frame

    def create_right_panel(self, parent):
        """Creates a placeholder for the right panel."""
        right_frame = self.theme_manager.create_custom_frame(parent, padding=5)

        label = self.theme_manager.create_custom_label(right_frame, "Effects & Properties\n(To be implemented)")
        label.pack(expand=True)

        return right_frame

    def setup_status_bar(self):
        """Creates the status bar at the bottom of the window."""
        status_frame = self.theme_manager.create_custom_frame(self.root, padding=5)
        status_frame.pack(fill='x', side='bottom', padx=10, pady=(0, 10))

        self.status_label = self.theme_manager.create_custom_label(status_frame, "Ready")
        self.status_label.pack(side='left')

        self.progress_bar = self.theme_manager.create_custom_progressbar(status_frame, length=200)
        self.progress_bar.pack(side='right')

    def load_video_to_preview(self, video_path: str):
        """Loads a video into the preview and timeline widgets."""
        self.current_file = video_path
        self.update_status(f"Loading: {os.path.basename(video_path)}")

        # Load into preview
        if not self.preview_widget.load_video(video_path):
            messagebox.showerror("Load Error", "Failed to load video into preview.")
            self.update_status("Error loading video.")
            return
        
        # Run scene detection and timeline population in a separate thread
        threading.Thread(target=self.populate_timeline, args=(video_path,), daemon=True).start()
        
    def populate_timeline(self, video_path: str):
        """Detects scenes and populates the timeline."""
        try:
            self.update_status("Detecting scenes...")
            self.timeline_manager.clear_timeline()

            scenes = self.scene_detector.detect_scenes(video_path)
            for start, end in scenes:
                self.timeline_manager.add_scene(start, end)

            self.update_status("Generating cuts...")
            self.timeline_manager.generate_cuts_from_scenes()

            self.timeline_widget.update_timeline()
            self.update_status(f"Loaded: {os.path.basename(video_path)}")
        except Exception as e:
            self.logger.error(f"Failed to populate timeline: {e}")
            messagebox.showerror("Timeline Error", f"Could not populate timeline: {e}")
            self.update_status("Error populating timeline.")

    def setup_keyboard_shortcuts(self):
        """Binds all application keyboard shortcuts."""
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-q>', lambda e: self.quit_application())
        self.root.bind('<space>', lambda e: self.preview_widget.toggle_playback())

    def open_file(self):
        """Shows the open file dialog."""
        filetypes = [("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Open Video File", filetypes=filetypes)
        if filename:
            self.load_video_to_preview(filename)

    def quit_application(self):
        """Handles application shutdown."""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.preview_widget.cleanup()
            self.root.destroy()

    def update_status(self, message: str):
        """Updates the status bar message."""
        self.status_label.config(text=message)

    def run(self):
        """Starts the Tkinter main loop."""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
        self.root.mainloop()
