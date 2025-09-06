# gui/tab_compiler.py
"""
Compiler tab interface for final output
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from typing import Dict, Any, Optional

class CompilerTab:
    """
    Compiler tab interface for final video compilation
    """
    
    def __init__(self, parent, theme_manager, config: Dict[str, Any] = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Create main frame
        self.frame = self.theme_manager.create_custom_frame(parent, padding=10)
        
        # Setup UI components
        self.setup_audio_section()
        self.setup_video_section()
        self.setup_render_section()
        
        self.logger.info("CompilerTab initialized")
    
    def setup_audio_section(self):
        """Setup audio mixing section"""
        audio_frame = self.theme_manager.create_custom_frame(self.frame, padding=5)
        audio_frame.pack(fill='x', pady=(0, 10))
        
        # Title
        title_label = self.theme_manager.create_custom_label(
            audio_frame, 
            "Audio Mixing",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(anchor='w')
        
        # Original audio
        original_frame = self.theme_manager.create_custom_frame(audio_frame)
        original_frame.pack(fill='x', pady=5)
        
        self.original_var = tk.BooleanVar(value=True)
        original_check = self.theme_manager.create_custom_checkbutton(
            original_frame,
            "Original Audio",
            variable=self.original_var
        )
        original_check.pack(side='left', padx=(0, 5))
        
        vol_label = self.theme_manager.create_custom_label(original_frame, "Vol:")
        vol_label.pack(side='left', padx=(0, 5))
        
        self.original_vol_var = tk.DoubleVar(value=80.0)
        original_vol_scale = self.theme_manager.create_custom_scale(
            original_frame,
            from_=0, to=100, variable=self.original_vol_var,
            orient='horizontal', length=150
        )
        original_vol_scale.pack(side='left', padx=(0, 5))
        
        self.original_vol_label = self.theme_manager.create_custom_label(original_frame, "80%")
        self.original_vol_label.pack(side='left')
        
        # Background music
        bgm_frame = self.theme_manager.create_custom_frame(audio_frame)
        bgm_frame.pack(fill='x', pady=5)
        
        bgm_label = self.theme_manager.create_custom_label(bgm_frame, "Background Music:")
        bgm_label.pack(side='left', padx=(0, 5))
        
        self.add_bgm_btn = self.theme_manager.create_custom_button(
            bgm_frame,
            "+Add",
            command=self.add_background_music,
            width=8
        )
        self.add_bgm_btn.pack(side='left', padx=(0, 5))
        
        self.bgm_file_label = self.theme_manager.create_custom_label(
            bgm_frame,
            "No background music",
            font=('Arial', 10, 'italic')
        )
        self.bgm_file_label.pack(side='left', padx=(0, 5))
        
        vol_label2 = self.theme_manager.create_custom_label(bgm_frame, "Vol:")
        vol_label2.pack(side='left', padx=(0, 5))
        
        self.bgm_vol_var = tk.DoubleVar(value=40.0)
        bgm_vol_scale = self.theme_manager.create_custom_scale(
            bgm_frame,
            from_=0, to=100, variable=self.bgm_vol_var,
            orient='horizontal', length=150
        )
        bgm_vol_scale.pack(side='left', padx=(0, 5))
        
        self.bgm_vol_label = self.theme_manager.create_custom_label(bgm_frame, "40%")
        self.bgm_vol_label.pack(side='left')
        
        # Output format
        format_frame = self.theme_manager.create_custom_frame(audio_frame)
        format_frame.pack(fill='x', pady=5)
        
        format_label = self.theme_manager.create_custom_label(format_frame, "Output Format:")
        format_label.pack(side='left', padx=(0, 5))
        
        self.audio_format_var = tk.StringVar(value="MP3")
        format_combo = self.theme_manager.create_custom_combobox(
            format_frame,
            values=["MP3", "WAV", "AAC"],
            width=10
        )
        format_combo.set("MP3")
        format_combo.pack(side='left')
    
    def setup_video_section(self):
        """Setup video settings section"""
        video_frame = self.theme_manager.create_custom_frame(self.frame, padding=5)
        video_frame.pack(fill='x', pady=(0, 10))
        
        # Title
        title_label = self.theme_manager.create_custom_label(
            video_frame, 
            "Video Settings",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(anchor='w')
        
        # Watermark
        watermark_frame = self.theme_manager.create_custom_frame(video_frame)
        watermark_frame.pack(fill='x', pady=5)
        
        watermark_label = self.theme_manager.create_custom_label(watermark_frame, "Watermark:")
        watermark_label.pack(side='left', padx=(0, 5))
        
        self.add_watermark_btn = self.theme_manager.create_custom_button(
            watermark_frame,
            "+Add",
            command=self.add_watermark,
            width=8
        )
        self.add_watermark_btn.pack(side='left', padx=(0, 5))
        
        self.watermark_file_label = self.theme_manager.create_custom_label(
            watermark_frame,
            "No watermark",
            font=('Arial', 10, 'italic')
        )
        self.watermark_file_label.pack(side='left', padx=(0, 5))
        
        pos_label = self.theme_manager.create_custom_label(watermark_frame, "Position:")
        pos_label.pack(side='left', padx=(0, 5))
        
        self.position_var = tk.StringVar(value="Bottom Right")
        pos_combo = self.theme_manager.create_custom_combobox(
            watermark_frame,
            values=["Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center"],
            width=12
        )
        pos_combo.set("Bottom Right")
        pos_combo.pack(side='left')
        
        # Output quality
        quality_frame = self.theme_manager.create_custom_frame(video_frame)
        quality_frame.pack(fill='x', pady=5)
        
        quality_label = self.theme_manager.create_custom_label(quality_frame, "Output Quality:")
        quality_label.pack(side='left', padx=(0, 5))
        
        self.quality_var = tk.StringVar(value="1080p")
        quality_combo = self.theme_manager.create_custom_combobox(
            quality_frame,
            values=["720p", "1080p", "4K"],
            width=8
        )
        quality_combo.set("1080p")
        quality_combo.pack(side='left', padx=(0, 5))
        
        codec_label = self.theme_manager.create_custom_label(quality_frame, "Codec:")
        codec_label.pack(side='left', padx=(0, 5))
        
        self.codec_var = tk.StringVar(value="H.264")
        codec_combo = self.theme_manager.create_custom_combobox(
            quality_frame,
            values=["H.264", "H.265", "VP9"],
            width=8
        )
        codec_combo.set("H.264")
        codec_combo.pack(side='left')
        
        # Advanced settings
        advanced_frame = self.theme_manager.create_custom_frame(video_frame)
        advanced_frame.pack(fill='x', pady=5)
        
        fps_label = self.theme_manager.create_custom_label(advanced_frame, "FPS:")
        fps_label.pack(side='left', padx=(0, 5))
        
        self.fps_var = tk.StringVar(value="30")
        fps_combo = self.theme_manager.create_custom_combobox(
            advanced_frame,
            values=["24", "30", "60"],
            width=6
        )
        fps_combo.set("30")
        fps_combo.pack(side='left', padx=(0, 10))
        
        bitrate_label = self.theme_manager.create_custom_label(advanced_frame, "Bitrate:")
        bitrate_label.pack(side='left', padx=(0, 5))
        
        self.bitrate_var = tk.StringVar(value="5000")
        bitrate_entry = self.theme_manager.create_custom_entry(advanced_frame, width=8)
        bitrate_entry.insert(0, "5000")
        bitrate_entry.pack(side='left', padx=(0, 5))
        
        kbps_label = self.theme_manager.create_custom_label(advanced_frame, "kbps")
        kbps_label.pack(side='left')
    
    def setup_render_section(self):
        """Setup render section"""
        render_frame = self.theme_manager.create_custom_frame(self.frame, padding=5)
        render_frame.pack(fill='x', pady=(0, 10))
        
        # Title
        title_label = self.theme_manager.create_custom_label(
            render_frame, 
            "Render Settings",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(anchor='w')
        
        # Output directory
        output_frame = self.theme_manager.create_custom_frame(render_frame)
        output_frame.pack(fill='x', pady=5)
        
        output_label = self.theme_manager.create_custom_label(output_frame, "Output Directory:")
        output_label.pack(side='left', padx=(0, 5))
        
        self.output_dir_var = tk.StringVar(value="")
        self.output_dir_entry = self.theme_manager.create_custom_entry(output_frame, width=40)
        self.output_dir_entry.pack(side='left', padx=(0, 5))
        self.output_dir_entry.config(state='readonly')
        
        self.browse_btn = self.theme_manager.create_custom_button(
            output_frame,
            "Browse...",
            command=self.browse_output_dir
        )
        self.browse_btn.pack(side='left')
        
        # Filename
        filename_frame = self.theme_manager.create_custom_frame(render_frame)
        filename_frame.pack(fill='x', pady=5)
        
        filename_label = self.theme_manager.create_custom_label(filename_frame, "Filename:")
        filename_label.pack(side='left', padx=(0, 5))
        
        self.filename_var = tk.StringVar(value="video_edit")
        self.filename_entry = self.theme_manager.create_custom_entry(filename_frame, width=30)
        self.filename_entry.pack(side='left', padx=(0, 5))
        
        # Progress
        progress_frame = self.theme_manager.create_custom_frame(render_frame)
        progress_frame.pack(fill='x', pady=5)
        
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = self.theme_manager.create_custom_progressbar(
            progress_frame,
            variable=self.progress_var,
            length=300
        )
        self.progress_bar.pack(side='left', padx=(0, 5))
        
        self.progress_label = self.theme_manager.create_custom_label(progress_frame, "0%")
        self.progress_label.pack(side='left')
        
        # Render button
        self.render_btn = self.theme_manager.create_custom_button(
            render_frame,
            "RENDER FINAL",
            command=self.start_render,
            width=15
        )
        self.render_btn.pack(pady=10)
    
    def add_background_music(self):
        """Add background music file"""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.aac *.flac"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Background Music",
            filetypes=filetypes
        )
        
        if filename:
            self.bgm_file = filename
            self.bgm_file_label.config(text=f"Loaded: {os.path.basename(filename)}")
            self.logger.info(f"Loaded background music: {filename}")
    
    def add_watermark(self):
        """Add watermark file"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Watermark",
            filetypes=filetypes
        )
        
        if filename:
            self.watermark_file = filename
            self.watermark_file_label.config(text=f"Loaded: {os.path.basename(filename)}")
            self.logger.info(f"Loaded watermark: {filename}")
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            self.output_dir_entry.config(state='normal')
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)
            self.output_dir_entry.config(state='readonly')
            self.logger.info(f"Output directory: {directory}")
    
    def start_render(self):
        """Start rendering process"""
        if not self.output_dir_var.get():
            messagebox.showwarning("No Output Directory", "Please select an output directory")
            return
        
        if not self.filename_var.get().strip():
            messagebox.showwarning("No Filename", "Please enter a filename")
            return
        
        # TODO: Implement rendering process
        self.logger.info("Starting render process")
        messagebox.showinfo("Render", "Starting render process...")
    
    def update_volume_labels(self):
        """Update volume display labels"""
        # Update original audio volume
        orig_vol = self.original_vol_var.get()
        self.original_vol_label.config(text=f"{orig_vol:.0f}%")
        
        # Update BGM volume
        bgm_vol = self.bgm_vol_var.get()
        self.bgm_vol_label.config(text=f"{bgm_vol:.0f}%")
        
        # Schedule next update
        self.frame.after(100, self.update_volume_labels)

# Test the compiler tab
if __name__ == "__main__":
    import logging
    import os
    
    logging.basicConfig(level=logging.INFO)
    
    root = tk.Tk()
    root.title("Compiler Tab Test")
    root.geometry("600x600")
    
    # Mock theme manager
    class MockThemeManager:
        def create_custom_frame(self, parent, style='TFrame', padding=0):
            return ttk.Frame(parent)
        
        def create_custom_label(self, parent, text, font=None):
            return ttk.Label(parent, text=text, font=font)
        
        def create_custom_button(self, parent, text, command=None, width=None):
            return ttk.Button(parent, text=text, command=command, width=width)
        
        def create_custom_entry(self, parent, width=None):
            return ttk.Entry(parent, width=width)
        
        def create_custom_combobox(self, parent, values=None, width=None):
            return ttk.Combobox(parent, values=values, width=width)
        
        def create_custom_scale(self, parent, from_=0, to=100, variable=None, orient='horizontal', length=200):
            return ttk.Scale(parent, from_=from_, to=to, variable=variable, orient=orient, length=length)
        
        def create_custom_checkbutton(self, parent, text, variable=None):
            return ttk.Checkbutton(parent, text=text, variable=variable)
        
        def create_custom_progressbar(self, parent, variable=None, length=200):
            return ttk.Progressbar(parent, variable=variable, length=length)
    
    theme_manager = MockThemeManager()
    compiler_tab = CompilerTab(root, theme_manager)
    
    # Start volume updates
    compiler_tab.update_volume_labels()
    
    root.mainloop()