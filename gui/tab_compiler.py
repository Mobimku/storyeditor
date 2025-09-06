# gui/tab_compiler.py
"""
Compiler tab interface for final output
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import os
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
        self.frame.grid_columnconfigure(0, weight=1)

        # Setup UI components
        self.setup_audio_section()
        self.setup_video_section()
        self.setup_render_section()
        
        self.logger.info("CompilerTab initialized")
    
    def setup_audio_section(self):
        """Setup audio mixing section using .grid()"""
        audio_frame = self.theme_manager.create_custom_frame(self.frame, padding=5)
        audio_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        audio_frame.grid_columnconfigure(1, weight=1)

        title_label = self.theme_manager.create_custom_label(
            audio_frame, "Audio Mixing", font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, sticky='w')
        
        # Original audio
        self.original_var = tk.BooleanVar(value=True)
        original_check = self.theme_manager.create_custom_checkbutton(
            audio_frame, "Original Audio", variable=self.original_var)
        original_check.grid(row=1, column=0, sticky='w', pady=5)

        original_vol_frame = self.theme_manager.create_custom_frame(audio_frame)
        original_vol_frame.grid(row=1, column=1, sticky='ew')
        original_vol_frame.grid_columnconfigure(1, weight=1)
        vol_label = self.theme_manager.create_custom_label(original_vol_frame, "Vol:")
        vol_label.grid(row=0, column=0, sticky='w', padx=5)
        self.original_vol_var = tk.DoubleVar(value=80.0)
        original_vol_scale = self.theme_manager.create_custom_scale(
            original_vol_frame, from_=0, to=100, variable=self.original_vol_var, orient='horizontal')
        original_vol_scale.grid(row=0, column=1, sticky='ew', padx=5)
        self.original_vol_label = self.theme_manager.create_custom_label(original_vol_frame, "80%")
        self.original_vol_label.grid(row=0, column=2, sticky='w')
        
        # Background music
        bgm_label = self.theme_manager.create_custom_label(audio_frame, "Background Music:")
        bgm_label.grid(row=2, column=0, sticky='w', pady=5)
        bgm_frame = self.theme_manager.create_custom_frame(audio_frame)
        bgm_frame.grid(row=2, column=1, sticky='ew')
        bgm_frame.grid_columnconfigure(1, weight=1)
        self.add_bgm_btn = self.theme_manager.create_custom_button(
            bgm_frame, "+Add", command=self.add_background_music, width=8)
        self.add_bgm_btn.grid(row=0, column=0, sticky='w')
        self.bgm_file_label = self.theme_manager.create_custom_label(
            bgm_frame, "No background music", font=('Arial', 10, 'italic'))
        self.bgm_file_label.grid(row=0, column=1, sticky='w', padx=5)

        bgm_vol_frame = self.theme_manager.create_custom_frame(bgm_frame)
        bgm_vol_frame.grid(row=0, column=2, sticky='e')
        bgm_vol_frame.grid_columnconfigure(1, weight=1)
        vol_label2 = self.theme_manager.create_custom_label(bgm_vol_frame, "Vol:")
        vol_label2.grid(row=0, column=0, sticky='w', padx=5)
        self.bgm_vol_var = tk.DoubleVar(value=40.0)
        bgm_vol_scale = self.theme_manager.create_custom_scale(
            bgm_vol_frame, from_=0, to=100, variable=self.bgm_vol_var, orient='horizontal')
        bgm_vol_scale.grid(row=0, column=1, sticky='ew', padx=5)
        self.bgm_vol_label = self.theme_manager.create_custom_label(bgm_vol_frame, "40%")
        self.bgm_vol_label.grid(row=0, column=2, sticky='w')

    def setup_video_section(self):
        """Setup video settings section using .grid()"""
        video_frame = self.theme_manager.create_custom_frame(self.frame, padding=5)
        video_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        video_frame.grid_columnconfigure(1, weight=1)

        title_label = self.theme_manager.create_custom_label(
            video_frame, "Video Settings", font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, sticky='w')

        # Watermark
        watermark_label = self.theme_manager.create_custom_label(video_frame, "Watermark:")
        watermark_label.grid(row=1, column=0, sticky='w', pady=5)
        watermark_controls_frame = self.theme_manager.create_custom_frame(video_frame)
        watermark_controls_frame.grid(row=1, column=1, sticky='ew')
        self.add_watermark_btn = self.theme_manager.create_custom_button(
            watermark_controls_frame, "+Add", command=self.add_watermark, width=8)
        self.add_watermark_btn.grid(row=0, column=0)
        self.watermark_file_label = self.theme_manager.create_custom_label(
            watermark_controls_frame, "No watermark", font=('Arial', 10, 'italic'))
        self.watermark_file_label.grid(row=0, column=1, padx=5)
        pos_label = self.theme_manager.create_custom_label(watermark_controls_frame, "Position:")
        pos_label.grid(row=0, column=2, padx=5)
        self.position_var = tk.StringVar(value="Bottom Right")
        pos_combo = self.theme_manager.create_custom_combobox(
            watermark_controls_frame, values=["Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center"], width=12)
        pos_combo.set("Bottom Right")
        pos_combo.grid(row=0, column=3)

        # Output quality
        quality_label = self.theme_manager.create_custom_label(video_frame, "Output Quality:")
        quality_label.grid(row=2, column=0, sticky='w', pady=5)
        quality_controls_frame = self.theme_manager.create_custom_frame(video_frame)
        quality_controls_frame.grid(row=2, column=1, sticky='w')
        self.quality_var = tk.StringVar(value="1080p")
        quality_combo = self.theme_manager.create_custom_combobox(
            quality_controls_frame, values=["720p", "1080p", "4K"], width=8)
        quality_combo.set("1080p")
        quality_combo.grid(row=0, column=0, padx=(0,5))
        codec_label = self.theme_manager.create_custom_label(quality_controls_frame, "Codec:")
        codec_label.grid(row=0, column=1, padx=(0,5))
        self.codec_var = tk.StringVar(value="H.264")
        codec_combo = self.theme_manager.create_custom_combobox(
            quality_controls_frame, values=["H.264", "H.265", "VP9"], width=8)
        codec_combo.set("H.264")
        codec_combo.grid(row=0, column=2)

    def setup_render_section(self):
        """Setup render section using .grid()"""
        render_frame = self.theme_manager.create_custom_frame(self.frame, padding=5)
        render_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        render_frame.grid_columnconfigure(1, weight=1)

        title_label = self.theme_manager.create_custom_label(
            render_frame, "Render Settings", font=('Arial', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, sticky='w')
        
        # Output directory
        output_label = self.theme_manager.create_custom_label(render_frame, "Output Directory:")
        output_label.grid(row=1, column=0, sticky='w', pady=5)
        self.output_dir_var = tk.StringVar(value="")
        self.output_dir_entry = self.theme_manager.create_custom_entry(render_frame)
        self.output_dir_entry.grid(row=1, column=1, sticky='ew', padx=5)
        self.output_dir_entry.config(state='readonly')
        self.browse_btn = self.theme_manager.create_custom_button(
            render_frame, "Browse...", command=self.browse_output_dir)
        self.browse_btn.grid(row=1, column=2)
        
        # Filename
        filename_label = self.theme_manager.create_custom_label(render_frame, "Filename:")
        filename_label.grid(row=2, column=0, sticky='w', pady=5)
        self.filename_var = tk.StringVar(value="video_edit")
        self.filename_entry = self.theme_manager.create_custom_entry(render_frame)
        self.filename_entry.grid(row=2, column=1, sticky='w', padx=5)
        
        # Render button
        self.render_btn = self.theme_manager.create_custom_button(
            render_frame, "RENDER FINAL", command=self.start_render, width=20)
        self.render_btn.grid(row=3, column=0, columnspan=3, pady=10)

    def add_background_music(self):
        """Add background music file"""
        filetypes = [("Audio files", "*.mp3 *.wav *.aac *.flac"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(
            title="Select Background Music", filetypes=filetypes)
        if filename:
            self.bgm_file = filename
            self.bgm_file_label.config(text=f"Loaded: {os.path.basename(filename)}")
            self.logger.info(f"Loaded background music: {filename}")
    
    def add_watermark(self):
        """Add watermark file"""
        filetypes = [("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(
            title="Select Watermark", filetypes=filetypes)
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
        self.logger.info("Starting render process")
        messagebox.showinfo("Render", "Starting render process...")
    
    def update_volume_labels(self):
        """Update volume display labels"""
        orig_vol = self.original_vol_var.get()
        self.original_vol_label.config(text=f"{orig_vol:.0f}%")
        
        bgm_vol = self.bgm_vol_var.get()
        self.bgm_vol_label.config(text=f"{bgm_vol:.0f}%")
        
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
            return ttk.Frame(parent, padding=padding)
        
        def create_custom_label(self, parent, text, font=None):
            return ttk.Label(parent, text=text, font=font)
        
        def create_custom_button(self, parent, text, command=None, width=None):
            return ttk.Button(parent, text=text, command=command, width=width)
        
        def create_custom_entry(self, parent, width=None):
            return ttk.Entry(parent, width=width)
        
        def create_custom_combobox(self, parent, values=None, width=None):
            return ttk.Combobox(parent, values=values, width=width)
        
        def create_custom_scale(self, parent, from_=0, to=100, variable=None, orient='horizontal', length=200):
            return ttk.Scale(parent, from_=from_, to=to, variable=variable, orient=orient)
        
        def create_custom_checkbutton(self, parent, text, variable=None):
            return ttk.Checkbutton(parent, text=text, variable=variable)
        
        def create_custom_progressbar(self, parent, variable=None, length=200):
            return ttk.Progressbar(parent, variable=variable, length=length)
    
    theme_manager = MockThemeManager()
    compiler_tab = CompilerTab(root, theme_manager)
    compiler_tab.frame.pack(fill='both', expand=True) # Use pack here for simple test window
    
    compiler_tab.update_volume_labels()
    
    root.mainloop()
