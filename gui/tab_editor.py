# gui/tab_editor.py
"""
Editor tab interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import os
from typing import Dict, Any, Optional

class EditorTab:
    """
    Editor tab interface for video processing
    """
    
    def __init__(self, parent, theme_manager, config: Dict[str, Any] = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Create main frame
        self.frame = self.theme_manager.create_custom_frame(parent, padding=10)

        # Setup UI components
        self.setup_input_section()
        self.setup_timeline_section()
        self.setup_effects_section()
        self.setup_process_section()
        
        self.logger.info("EditorTab initialized")
    
    def setup_input_section(self):
        """Setup input file/URL section"""
        input_frame = self.theme_manager.create_custom_frame(self.frame, padding=5)
        input_frame.pack(fill='x', pady=(0, 10))

        # Title
        title_label = self.theme_manager.create_custom_label(
            input_frame,
            "Input Source",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(anchor='w')
        
        # Button frame
        button_frame = self.theme_manager.create_custom_frame(input_frame)
        button_frame.pack(fill='x', pady=5)
        
        # Local file button
        self.local_file_btn = self.theme_manager.create_custom_button(
            button_frame,
            "Local File",
            command=self.load_local_file
        )
        self.local_file_btn.pack(side='left', padx=(0, 5))
        
        # URL import button
        self.url_btn = self.theme_manager.create_custom_button(
            button_frame,
            "URL Import",
            command=self.show_url_dialog
        )
        self.url_btn.pack(side='left', padx=(0, 5))
        
        # URL entry (hidden by default)
        self.url_frame = self.theme_manager.create_custom_frame(input_frame)
        
        url_label = self.theme_manager.create_custom_label(self.url_frame, "URL:")
        url_label.pack(side='left', padx=(0, 5))

        self.url_entry = self.theme_manager.create_custom_entry(self.url_frame, width=40)
        self.url_entry.pack(side='left', padx=(0, 5))
        
        self.download_btn = self.theme_manager.create_custom_button(
            self.url_frame,
            "Download",
            command=self.download_url
        )
        self.download_btn.pack(side='left')

        # Quality selection
        quality_frame = self.theme_manager.create_custom_frame(input_frame)
        quality_frame.pack(fill='x', pady=5)

        quality_label = self.theme_manager.create_custom_label(quality_frame, "Quality:")
        quality_label.pack(side='left', padx=(0, 5))

        self.quality_var = tk.StringVar(value="720p")
        quality_combo = self.theme_manager.create_custom_combobox(
            quality_frame,
            values=["360p", "480p", "720p", "1080p"],
            width=10
        )
        quality_combo.set("720p")
        quality_combo.pack(side='left')

        # Current file display
        self.file_label = self.theme_manager.create_custom_label(
            input_frame,
            "No file selected",
            font=('Arial', 10, 'italic')
        )
        self.file_label.pack(anchor='w', pady=5)

    def setup_timeline_section(self):
        """Setup timeline controls section"""
        timeline_frame = self.theme_manager.create_custom_frame(self.frame, padding=5)
        timeline_frame.pack(fill='x', pady=(0, 10))

        # Title
        title_label = self.theme_manager.create_custom_label(
            timeline_frame,
            "Timeline Controls",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(anchor='w')
        
        # Trim intro
        intro_frame = self.theme_manager.create_custom_frame(timeline_frame)
        intro_frame.pack(fill='x', pady=5)

        intro_label = self.theme_manager.create_custom_label(intro_frame, "Trim Intro:")
        intro_label.pack(side='left', padx=(0, 5))

        self.intro_var = tk.DoubleVar(value=0.0)
        intro_scale = self.theme_manager.create_custom_scale(
            intro_frame,
            from_=0, to=60, variable=self.intro_var,
            orient='horizontal', length=200
        )
        intro_scale.pack(side='left', padx=(0, 5))

        self.intro_time_label = self.theme_manager.create_custom_label(intro_frame, "00:00")
        self.intro_time_label.pack(side='left')
        
        # Trim outro
        outro_frame = self.theme_manager.create_custom_frame(timeline_frame)
        outro_frame.pack(fill='x', pady=5)

        outro_label = self.theme_manager.create_custom_label(outro_frame, "Trim Outro:")
        outro_label.pack(side='left', padx=(0, 5))

        self.outro_var = tk.DoubleVar(value=180.0)
        outro_scale = self.theme_manager.create_custom_scale(
            outro_frame,
            from_=0, to=300, variable=self.outro_var,
            orient='horizontal', length=200
        )
        outro_scale.pack(side='left', padx=(0, 5))

        self.outro_time_label = self.theme_manager.create_custom_label(outro_frame, "03:00")
        self.outro_time_label.pack(side='left')
        
        # Silent threshold
        silent_frame = self.theme_manager.create_custom_frame(timeline_frame)
        silent_frame.pack(fill='x', pady=5)

        silent_label = self.theme_manager.create_custom_label(silent_frame, "Silent Threshold:")
        silent_label.pack(side='left', padx=(0, 5))

        self.threshold_var = tk.DoubleVar(value=-40.0)
        threshold_scale = self.theme_manager.create_custom_scale(
            silent_frame,
            from_=-60, to=-20, variable=self.threshold_var,
            orient='horizontal', length=200
        )
        threshold_scale.pack(side='left', padx=(0, 5))

        self.threshold_label = self.theme_manager.create_custom_label(silent_frame, "-40dB")
        self.threshold_label.pack(side='left')

    def setup_effects_section(self):
        """Setup effects section"""
        effects_frame = self.theme_manager.create_custom_frame(self.frame, padding=5)
        effects_frame.pack(fill='x', pady=(0, 10))

        # Title
        title_label = self.theme_manager.create_custom_label(
            effects_frame,
            "Effects",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(anchor='w')
        
        # Selective blur
        blur_frame = self.theme_manager.create_custom_frame(effects_frame)
        blur_frame.pack(fill='x', pady=5)

        blur_label = self.theme_manager.create_custom_label(blur_frame, "Selective Blur:")
        blur_label.pack(side='left', padx=(0, 5))

        self.add_region_btn = self.theme_manager.create_custom_button(
            blur_frame,
            "Add Region",
            command=self.add_blur_region
        )
        self.add_region_btn.pack(side='left', padx=(0, 5))

        self.clear_regions_btn = self.theme_manager.create_custom_button(
            blur_frame,
            "Clear All",
            command=self.clear_blur_regions
        )
        self.clear_regions_btn.pack(side='left')
        
        # Color preset
        color_frame = self.theme_manager.create_custom_frame(effects_frame)
        color_frame.pack(fill='x', pady=5)

        color_label = self.theme_manager.create_custom_label(color_frame, "Color Preset:")
        color_label.pack(side='left', padx=(0, 5))

        self.preset_var = tk.StringVar(value="Cinematic")
        preset_combo = self.theme_manager.create_custom_combobox(
            color_frame,
            values=["Cinematic", "Vibrant", "Dramatic", "Natural", "B&W"],
            width=15
        )
        preset_combo.set("Cinematic")
        preset_combo.pack(side='left')
        
        # Scene detection
        scene_frame = self.theme_manager.create_custom_frame(effects_frame)
        scene_frame.pack(fill='x', pady=5)

        self.scene_var = tk.BooleanVar(value=True)
        scene_check = self.theme_manager.create_custom_checkbutton(
            scene_frame,
            "Scene Detection",
            variable=self.scene_var
        )
        scene_check.pack(side='left', padx=(0, 5))
        
        sensitivity_label = self.theme_manager.create_custom_label(scene_frame, "Sensitivity:")
        sensitivity_label.pack(side='left', padx=(0, 5))

        self.sensitivity_var = tk.DoubleVar(value=0.3)
        sensitivity_scale = self.theme_manager.create_custom_scale(
            scene_frame,
            from_=0.1, to=0.8, variable=self.sensitivity_var,
            orient='horizontal', length=150
        )
        sensitivity_scale.pack(side='left')

    def setup_process_section(self):
        """Setup process controls section"""
        process_frame = self.theme_manager.create_custom_frame(self.frame, padding=5)
        process_frame.pack(fill='x', pady=(0, 10))

        # Title
        title_label = self.theme_manager.create_custom_label(
            process_frame,
            "Processing",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(anchor='w')
        
        # Button frame
        button_frame = self.theme_manager.create_custom_frame(process_frame)
        button_frame.pack(fill='x', pady=5)

        self.preview_btn = self.theme_manager.create_custom_button(
            button_frame,
            "SMART PREVIEW",
            command=self.generate_preview,
            width=15
        )
        self.preview_btn.pack(side='left', padx=(0, 5))

        self.process_btn = self.theme_manager.create_custom_button(
            button_frame,
            "START PROCESSING",
            command=self.start_processing,
            width=15
        )
        self.process_btn.pack(side='left')
        
        # Options frame
        options_frame = self.theme_manager.create_custom_frame(process_frame)
        options_frame.pack(fill='x', pady=5)

        self.fair_use_var = tk.BooleanVar(value=True)
        fair_use_check = self.theme_manager.create_custom_checkbutton(
            options_frame,
            "Fair Use Mode",
            variable=self.fair_use_var
        )
        fair_use_check.pack(side='left', padx=(0, 10))

        self.auto_effects_var = tk.BooleanVar(value=True)
        auto_effects_check = self.theme_manager.create_custom_checkbutton(
            options_frame,
            "Auto Effects",
            variable=self.auto_effects_var
        )
        auto_effects_check.pack(side='left')

    def load_local_file(self):
        """Load local video file"""
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
            self.file_label.config(text=f"Loaded: {os.path.basename(filename)}")
            self.logger.info(f"Loaded local file: {filename}")
    
    def show_url_dialog(self):
        """Show URL input dialog"""
        if self.url_frame.winfo_ismapped():
            self.url_frame.pack_forget()
        else:
            self.url_frame.pack(fill='x', pady=5)
    
    def download_url(self):
        """Download video from URL"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a URL")
            return

        # TODO: Implement URL download
        self.logger.info(f"Downloading from URL: {url}")
        messagebox.showinfo("Download", f"Downloading from: {url}")
    
    def add_blur_region(self):
        """Add blur region"""
        # TODO: Implement blur region selection
        self.logger.info("Add blur region clicked")
        messagebox.showinfo("Blur Region", "Click and drag on video to select blur region")
    
    def clear_blur_regions(self):
        """Clear all blur regions"""
        # TODO: Implement clear blur regions
        self.logger.info("Clear blur regions clicked")
        messagebox.showinfo("Clear Regions", "All blur regions cleared")
    
    def generate_preview(self):
        """Generate smart preview"""
        if not hasattr(self, 'current_file') or not self.current_file:
            messagebox.showwarning("No File", "Please load a video file first")
            return

        # TODO: Implement preview generation
        self.logger.info("Generating preview")
        messagebox.showinfo("Preview", "Generating smart preview...")
    
    def start_processing(self):
        """Start video processing"""
        if not hasattr(self, 'current_file') or not self.current_file:
            messagebox.showwarning("No File", "Please load a video file first")
            return

        # TODO: Implement processing
        self.logger.info("Starting processing")
        messagebox.showinfo("Processing", "Starting video processing...")
    
    def update_time_labels(self):
        """Update time display labels"""
        # Update intro time
        intro_time = self.intro_var.get()
        minutes = int(intro_time // 60)
        seconds = int(intro_time % 60)
        self.intro_time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
        # Update outro time
        outro_time = self.outro_var.get()
        minutes = int(outro_time // 60)
        seconds = int(outro_time % 60)
        self.outro_time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
        # Update threshold label
        threshold = self.threshold_var.get()
        self.threshold_label.config(text=f"{threshold:.0f}dB")
        
        # Schedule next update
        self.frame.after(100, self.update_time_labels)

