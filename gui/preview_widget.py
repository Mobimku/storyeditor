# gui/preview_widget.py
"""
Video preview widget with playback controls
"""

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import threading
import time
import logging
import os
from typing import Optional, Callable, Dict, Any

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL/Pillow not available. Preview functionality will be limited.")

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.theme_manager import ThemeManager

class PreviewWidget:
    """
    Video preview widget with playback controls
    """
    
    def __init__(self, parent, theme_manager: ThemeManager, config: Dict[str, Any] = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        if not PIL_AVAILABLE:
            self.logger.error("PIL/Pillow is required for video preview. Install with: pip install Pillow")

        # Video state
        self.video_path = None
        self.cap = None
        self.current_frame_image = None
        self.is_playing = False
        self.total_duration = 0.0
        self.fps = 30.0
        
        # Playback loop
        self.after_id = None

        # Create UI
        self.create_ui()
        
        self.logger.info("PreviewWidget initialized")
    
    def create_ui(self):
        """Create the preview widget UI"""
        self.frame = self.theme_manager.create_custom_frame(self.parent)
        self.frame.pack(fill='both', expand=True)

        self.video_frame = self.theme_manager.create_custom_frame(self.frame, 'VideoFrame.TFrame')
        self.video_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.canvas = tk.Canvas(
            self.video_frame, 
            bg=self.theme_manager.get_color('bg_secondary'),
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        self.placeholder_text = self.canvas.create_text(
            400, 300, text="No video loaded",
            fill=self.theme_manager.get_color('text_secondary'), font=('Arial', 14))
        
        controls_frame = self.theme_manager.create_custom_frame(self.frame)
        controls_frame.pack(fill='x')
        
        self.play_btn = self.theme_manager.create_custom_button(
            controls_frame, "▶", command=self.toggle_playback, width=3)
        self.play_btn.pack(side='left', padx=(0, 5))
        
        self.time_label = self.theme_manager.create_custom_label(
            controls_frame, "00:00 / 00:00", font=('Arial', 10))
        self.time_label.pack(side='left', padx=(0, 10))
        
        self.seek_var = tk.DoubleVar()
        self.seek_slider = self.theme_manager.create_custom_scale(
            controls_frame, from_=0, to=100, variable=self.seek_var,
            orient='horizontal', command=self.on_seek)
        self.seek_slider.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.canvas.bind('<Configure>', self.on_canvas_resize)
    
    def load_video(self, video_path: str) -> bool:
        if not PIL_AVAILABLE:
            self.show_placeholder("PIL/Pillow is required for preview.")
            return False

        try:
            if self.cap:
                self.cap.release()
            
            if not os.path.exists(video_path):
                self.logger.error(f"Video file not found: {video_path}")
                self.show_placeholder("Video file not found.")
                return False

            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                self.logger.error(f"Could not open video: {video_path}")
                self.show_placeholder("Could not open video.")
                return False
            
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            if self.fps == 0: self.fps = 30

            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.total_duration = frame_count / self.fps
            self.video_path = video_path
            
            self.seek_var.set(0.0)
            self.update_time_display(0)
            
            self.show_frame(0)
            self.logger.info(f"Loaded video: {video_path} ({self.total_duration:.2f}s)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load video: {e}")
            self.show_placeholder("Failed to load video.")
            return False

    def show_frame(self, frame_num):
        if not self.cap: return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)

    def display_frame(self, frame):
        if not PIL_AVAILABLE: return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1: return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_height, frame_width, _ = frame_rgb.shape
        aspect_ratio = frame_width / frame_height
        
        if canvas_width / canvas_height > aspect_ratio:
            display_height = canvas_height
            display_width = int(display_height * aspect_ratio)
        else:
            display_width = canvas_width
            display_height = int(display_width / aspect_ratio)

        resized_frame = cv2.resize(frame_rgb, (display_width, display_height))
        
        self.current_frame_image = ImageTk.PhotoImage(image=Image.fromarray(resized_frame))
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=self.current_frame_image, anchor='center')
    
    def toggle_playback(self):
        if not self.cap: return
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_btn.config(text="⏸")
            self.playback_loop()
        else:
            self.play_btn.config(text="▶")
            if self.after_id:
                self.frame.after_cancel(self.after_id)
                self.after_id = None

    def playback_loop(self):
        if not self.is_playing or not self.cap:
            return

        current_frame_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

        if current_frame_pos >= total_frames:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop

        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)
            current_time = self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.fps
            self.update_time_display(current_time)
            self.seek_var.set((current_time / self.total_duration) * 100)

        frame_delay = int(1000 / self.fps)
        self.after_id = self.frame.after(frame_delay, self.playback_loop)

    def on_seek(self, value):
        if self.is_playing: return
        
        seek_percent = float(value)
        frame_num = int((seek_percent / 100.0) * self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.show_frame(frame_num)
        current_time = frame_num / self.fps
        self.update_time_display(current_time)

    def on_canvas_resize(self, event):
        if self.cap:
            current_frame_num = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.show_frame(current_frame_num)
        else:
            self.show_placeholder("No video loaded")
    
    def show_placeholder(self, text):
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2,
            text=text, fill=self.theme_manager.get_color('text_secondary'), font=('Arial', 14))

    def update_time_display(self, current_time):
        current_str = time.strftime('%M:%S', time.gmtime(current_time))
        total_str = time.strftime('%M:%S', time.gmtime(self.total_duration))
        self.time_label.config(text=f"{current_str} / {total_str}")
    
    def cleanup(self):
        self.is_playing = False
        if self.after_id:
            self.frame.after_cancel(self.after_id)
        if self.cap:
            self.cap.release()
        self.logger.info("PreviewWidget cleaned up")
