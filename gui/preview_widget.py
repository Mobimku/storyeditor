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
import os  # Tambahkan import ini
from typing import Optional, Callable, Dict, Any

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
        
        # Video state
        self.video_path = None
        self.cap = None
        self.current_frame = None
        self.is_playing = False
        self.current_time = 0.0
        self.total_duration = 0.0
        self.fps = 30.0
        
        # Playback thread
        self.playback_thread = None
        self.stop_playback = False
        
        # Create UI
        self.create_ui()
        
        self.logger.info("PreviewWidget initialized")
    
    def create_ui(self):
        """Create the preview widget UI"""
        # Main container
        self.frame = self.theme_manager.create_custom_frame(self.parent)
        
        # Video display area
        self.video_frame = self.theme_manager.create_custom_frame(
            self.frame, 
            'VideoFrame.TFrame'
        )
        self.video_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create canvas for video display
        self.canvas = tk.Canvas(
            self.video_frame, 
            bg=self.theme_manager.get_color('bg_secondary'),
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Placeholder text
        self.placeholder_text = self.canvas.create_text(
            400, 300,
            text="No video loaded",
            fill=self.theme_manager.get_color('text_secondary'),
            font=('Arial', 14)
        )
        
        # Controls frame
        controls_frame = self.theme_manager.create_custom_frame(self.frame)
        controls_frame.pack(fill='x')
        
        # Playback controls
        self.play_btn = self.theme_manager.create_custom_button(
            controls_frame, 
            "▶", 
            command=self.toggle_playback,
            width=3
        )
        self.play_btn.pack(side='left', padx=(0, 5))
        
        # Time display
        self.time_label = self.theme_manager.create_custom_label(
            controls_frame, 
            "00:00 / 00:00",
            font=('Arial', 10)
        )
        self.time_label.pack(side='left', padx=(0, 10))
        
        # Seek slider
        self.seek_var = tk.DoubleVar()
        self.seek_slider = self.theme_manager.create_custom_scale(
            controls_frame,
            from_=0,
            to=100,
            variable=self.seek_var,
            orient='horizontal',
            length=300,
            command=self.on_seek
        )
        self.seek_slider.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Volume control
        volume_frame = self.theme_manager.create_custom_frame(controls_frame)
        volume_frame.pack(side='right')
        
        volume_label = self.theme_manager.create_custom_label(volume_frame, "🔊")
        volume_label.pack(side='left')
        
        self.volume_var = tk.DoubleVar(value=100.0)
        self.volume_slider = self.theme_manager.create_custom_scale(
            volume_frame,
            from_=0,
            to=100,
            variable=self.volume_var,
            orient='horizontal',
            length=100,
            command=self.on_volume_change
        )
        self.volume_slider.pack(side='left')
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self.on_canvas_resize)
    
    def load_video(self, video_path: str) -> bool:
        """
        Load video file for preview

        Args:
            video_path: Path to video file

        Returns:
            True if video loaded successfully
        """
        try:
            # Close existing video
            if self.cap:
                self.cap.release()
            
            # Open new video
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                self.logger.error(f"Could not open video: {video_path}")
                return False
            
            # Get video properties
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_duration = self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.fps
            self.video_path = video_path
            
            # Reset playback state
            self.current_time = 0.0
            self.seek_var.set(0.0)
            
            # Update UI
            self.update_time_display()
            self.placeholder_text = self.canvas.create_text(
                400, 300,
                text="Loading video...",
                fill=self.theme_manager.get_color('text_secondary'),
                font=('Arial', 14)
            )
            
            # Load first frame
            self.load_frame(0)
            
            self.logger.info(f"Loaded video: {video_path} ({self.total_duration:.2f}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load video: {e}")
            return False
    
    def load_frame(self, frame_number: int):
        """Load specific frame"""
        if not self.cap or not self.cap.isOpened():
            return
        
        try:
            # Set frame position
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

            # Read frame
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.display_frame(frame)
                
                # Update current time
                self.current_time = frame_number / self.fps
                self.seek_var.set((self.current_time / self.total_duration) * 100)
                self.update_time_display()
            
        except Exception as e:
            self.logger.error(f"Failed to load frame: {e}")
    
    def display_frame(self, frame):
        """Display frame on canvas"""
        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Calculate aspect ratio
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_width / frame_height
            
            # Calculate display dimensions
            if canvas_width / canvas_height > aspect_ratio:
                display_height = canvas_height
                display_width = int(display_height * aspect_ratio)
            else:
                display_width = canvas_width
                display_height = int(display_width / aspect_ratio)
            
            # Resize frame
            resized_frame = cv2.resize(frame_rgb, (display_width, display_height))
            
            # Convert to PhotoImage
            from PIL import Image, ImageTk
            image = Image.fromarray(resized_frame)
            photo = ImageTk.PhotoImage(image=image)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width // 2, 
                canvas_height // 2, 
                image=photo, 
                anchor='center'
            )
            
            # Keep reference to prevent garbage collection
            self.canvas.image = photo
            
        except Exception as e:
            self.logger.error(f"Failed to display frame: {e}")
    
    def toggle_playback(self):
        """Toggle video playback"""
        if not self.cap or not self.cap.isOpened():
            return
        
        if self.is_playing:
            self.stop_playback_thread()
            self.play_btn.config(text="▶")
        else:
            self.start_playback_thread()
            self.play_btn.config(text="⏸")
        
        self.is_playing = not self.is_playing
    
    def start_playback_thread(self):
        """Start video playback thread"""
        if self.playback_thread and self.playback_thread.is_alive():
            return
        
        self.stop_playback = False
        self.playback_thread = threading.Thread(target=self.playback_worker)
        self.playback_thread.daemon = True
        self.playback_thread.start()
    
    def stop_playback_thread(self):
        """Stop video playback thread"""
        self.stop_playback = True
        if self.playback_thread:
            self.playback_thread.join(timeout=1.0)
    
    def playback_worker(self):
        """Playback worker thread"""
        if not self.cap or not self.cap.isOpened():
            return
        
        last_time = time.time()
        
        while not self.stop_playback:
            try:
                # Calculate current frame number
                current_frame = int(self.current_time * self.fps)
                
                # Load and display frame
                self.load_frame(current_frame)
                
                # Update time
                self.current_time += 1.0 / self.fps

                # Check if reached end
                if self.current_time >= self.total_duration:
                    self.current_time = 0.0
                
                # Maintain playback speed
                elapsed = time.time() - last_time
                sleep_time = max(0, (1.0 / self.fps) - elapsed)
                time.sleep(sleep_time)
                last_time = time.time()
                
            except Exception as e:
                self.logger.error(f"Playback error: {e}")
                break
        
        # Reset play button
        self.is_playing = False
        self.play_btn.config(text="▶")
    
    def on_seek(self, value):
        """Handle seek slider change"""
        if not self.cap or not self.cap.isOpened():
            return
        
        # Calculate new time
        seek_percent = float(value)
        new_time = (seek_percent / 100.0) * self.total_duration
        
        # Load frame at new time
        frame_number = int(new_time * self.fps)
        self.load_frame(frame_number)
    
    def on_volume_change(self, value):
        """Handle volume slider change"""
        volume = float(value)
        self.logger.debug(f"Volume changed to: {volume}%")
        # TODO: Implement volume control
    
    def on_canvas_resize(self, event):
        """Handle canvas resize"""
        if self.current_frame is not None:
            self.display_frame(self.current_frame)
    
    def update_time_display(self):
        """Update time display label"""
        current_str = self.format_time(self.current_time)
        total_str = self.format_time(self.total_duration)
        self.time_label.config(text=f"{current_str} / {total_str}")
    
    def format_time(self, seconds: float) -> str:
        """Format time in MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def set_playback_speed(self, speed: float):
        """Set playback speed"""
        self.logger.info(f"Playback speed set to: {speed}x")
        # TODO: Implement playback speed control
    
    def add_marker(self, time: float, label: str = ""):
        """Add marker to timeline"""
        self.logger.info(f"Added marker at {time:.2f}s: {label}")
        # TODO: Implement marker functionality
    
    def clear_markers(self):
        """Clear all markers"""
        self.logger.info("Cleared all markers")
        # TODO: Implement marker clearing
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_playback_thread()
        if self.cap:
            self.cap.release()
        self.logger.info("PreviewWidget cleaned up")

# Test the preview_widget
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Preview Widget Test")
    root.geometry("800x600")

    theme_manager = ThemeManager()
    theme_manager.apply_theme(root)

    preview = PreviewWidget(root, theme_manager)
    preview.frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Test with a sample video path (uncomment to test)
    # preview.load_video("sample.mp4")

    root.protocol("WM_DELETE_WINDOW", lambda: (preview.cleanup(), root.destroy()))
    root.mainloop()