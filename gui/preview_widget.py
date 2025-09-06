# gui/preview_widget.py (IMPROVED VERSION)
"""
Video preview widget with improved error handling and performance
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
    Enhanced video preview widget with better error handling
    """
    
    def __init__(self, parent, theme_manager: ThemeManager, config: Dict[str, Any] = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Check PIL availability
        if not PIL_AVAILABLE:
            self.logger.error("PIL/Pillow is required for video preview. Install with: pip install Pillow")

        # Video state
        self.video_path = None
        self.cap = None
        self.current_frame = None
        self.is_playing = False
        self.current_time = 0.0
        self.total_duration = 0.0
        self.fps = 30.0
        self.playback_speed = 1.0
        
        # Playback thread
        self.playback_thread = None
        self.stop_playback = False
        self.thread_lock = threading.Lock()

        # Markers
        self.markers = []
        
        # Create UI
        self.create_ui()
        
        self.logger.info("Enhanced PreviewWidget initialized")
    
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
        self.show_placeholder("No video loaded")
        
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
        
        # Bind canvas events
        self.canvas.bind('<Configure>', self.on_canvas_resize)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
    
    def show_placeholder(self, text: str):
        """Show placeholder text on canvas"""
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width() or 400
        canvas_height = self.canvas.winfo_height() or 300
        
        self.canvas.create_text(
            canvas_width // 2,
            canvas_height // 2,
            text=text,
            fill=self.theme_manager.get_color('text_secondary'),
            font=('Arial', 14)
        )

    def load_video(self, video_path: str) -> bool:
        """Load video file for preview with enhanced error handling"""
        try:
            # Check PIL availability
            if not PIL_AVAILABLE:
                self.show_placeholder("PIL/Pillow required for video preview\nInstall with: pip install Pillow")
                return False

            # Check if file exists
            if not os.path.exists(video_path):
                self.logger.error(f"Video file not found: {video_path}")
                self.show_placeholder("Video file not found")
                return False

            # Close existing video
            if self.cap:
                self.cap.release()
            
            # Stop any existing playback
            self.stop_playback_thread()

            # Open new video
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                self.logger.error(f"Could not open video: {video_path}")
                self.show_placeholder("Could not open video file")
                return False
            
            # Get video properties
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            if self.fps <= 0:
                self.fps = 30.0  # Default fallback

            frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.total_duration = frame_count / self.fps if self.fps > 0 else 0
            self.video_path = video_path
            
            # Reset playback state
            self.current_time = 0.0
            self.seek_var.set(0.0)
            
            # Clear markers
            self.markers.clear()

            # Update UI
            self.update_time_display()
            self.show_placeholder("Loading first frame...")
            
            # Load first frame
            self.load_frame(0)
            
            self.logger.info(f"Loaded video: {video_path} ({self.total_duration:.2f}s, {self.fps:.1f} fps)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load video: {e}")
            self.show_placeholder(f"Error loading video:\n{str(e)}")
            return False
    
    def load_frame(self, frame_number: int):
        """Load specific frame with error handling"""
        if not self.cap or not self.cap.isOpened():
            return
        
        try:
            with self.thread_lock:
                # Set frame position
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                
                # Read frame
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.current_frame = frame
                    # Schedule display on main thread
                    self.canvas.after_idle(lambda: self.display_frame(frame))

                    # Update current time
                    self.current_time = frame_number / self.fps
                    if self.total_duration > 0:
                        seek_percent = (self.current_time / self.total_duration) * 100
                        # Schedule UI update on main thread
                        self.canvas.after_idle(lambda: self.seek_var.set(seek_percent))
                        self.canvas.after_idle(self.update_time_display)
                else:
                    self.logger.warning(f"Could not read frame {frame_number}")
            
        except Exception as e:
            self.logger.error(f"Failed to load frame {frame_number}: {e}")
    
    def display_frame(self, frame):
        """Display frame on canvas with improved error handling"""
        try:
            if not PIL_AVAILABLE:
                return

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get canvas dimensions
            self.canvas.update_idletasks()  # Ensure accurate dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas not ready yet, try again later
                self.canvas.after(100, lambda: self.display_frame(frame))
                return
            
            # Calculate aspect ratio
            frame_height, frame_width = frame.shape[:2]
            if frame_width <= 0 or frame_height <= 0:
                return

            aspect_ratio = frame_width / frame_height
            
            # Calculate display dimensions
            if canvas_width / canvas_height > aspect_ratio:
                display_height = canvas_height
                display_width = int(display_height * aspect_ratio)
            else:
                display_width = canvas_width
                display_height = int(display_width / aspect_ratio)
            
            # Ensure minimum size
            display_width = max(1, display_width)
            display_height = max(1, display_height)

            # Resize frame
            resized_frame = cv2.resize(frame_rgb, (display_width, display_height))
            
            # Convert to PhotoImage
            image = Image.fromarray(resized_frame)
            photo = ImageTk.PhotoImage(image=image)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width // 2, 
                canvas_height // 2, 
                image=photo, 
                anchor='center',
                tags='video_frame'
            )
            
            # Draw markers
            self.draw_markers()

            # Keep reference to prevent garbage collection
            self.canvas.image = photo
            
        except Exception as e:
            self.logger.error(f"Failed to display frame: {e}")
            self.show_placeholder(f"Display error: {str(e)}")

    def draw_markers(self):
        """Draw timeline markers on canvas"""
        if not self.markers or self.total_duration <= 0:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        for marker_time, marker_label in self.markers:
            # Calculate marker position
            marker_x = (marker_time / self.total_duration) * canvas_width

            # Draw marker line
            self.canvas.create_line(
                marker_x, 0, marker_x, canvas_height,
                fill=self.theme_manager.get_color('accent_tertiary'),
                width=2,
                tags='marker'
            )

            # Draw marker label
            if marker_label:
                self.canvas.create_text(
                    marker_x, 20,
                    text=marker_label,
                    fill=self.theme_manager.get_color('text_primary'),
                    font=('Arial', 8),
                    tags='marker_label'
                )
    
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
        self.playback_thread = threading.Thread(target=self.playback_worker, daemon=True)
        self.playback_thread.start()
    
    def stop_playback_thread(self):
        """Stop video playback thread"""
        self.stop_playback = True
        if self.playback_thread:
            self.playback_thread.join(timeout=1.0)
    
    def playback_worker(self):
        """Playback worker thread with improved timing"""
        if not self.cap or not self.cap.isOpened():
            return
        
        last_time = time.time()
        frame_duration = 1.0 / (self.fps * self.playback_speed)
        
        while not self.stop_playback:
            try:
                # Calculate current frame number
                current_frame = int(self.current_time * self.fps)
                
                # Check if reached end
                total_frames = int(self.total_duration * self.fps)
                if current_frame >= total_frames:
                    # Loop or stop
                    self.current_time = 0.0
                    current_frame = 0

                # Load and display frame
                self.load_frame(current_frame)
                
                # Update time
                self.current_time += frame_duration
                
                # Maintain playback speed
                elapsed = time.time() - last_time
                sleep_time = max(0, frame_duration - elapsed)
                time.sleep(sleep_time)
                last_time = time.time()
                
            except Exception as e:
                self.logger.error(f"Playback error: {e}")
                break
        
        # Reset play button on main thread
        self.canvas.after_idle(lambda: self.play_btn.config(text="▶"))
        self.is_playing = False
    
    def on_seek(self, value):
        """Handle seek slider change"""
        if not self.cap or not self.cap.isOpened() or self.total_duration <= 0:
            return

        # Don't seek while playing to avoid conflicts
        if self.is_playing:
            return
        
        # Calculate new time
        seek_percent = float(value)
        new_time = (seek_percent / 100.0) * self.total_duration
        
        # Load frame at new time
        frame_number = int(new_time * self.fps)
        self.load_frame(frame_number)
    
    def on_volume_change(self, value):
        """Handle volume change"""
        # TODO: Implement volume control if audio playback is added
        pass
    
    def on_canvas_resize(self, event):
        """Handle canvas resize"""
        if self.current_frame is not None:
            self.display_frame(self.current_frame)
        else:
            self.show_placeholder("No video loaded")

    def on_canvas_click(self, event):
        """Handle canvas click"""
        # Placeholder for future functionality (e.g., setting blur regions)
        pass
    
    def update_time_display(self):
        """Update time display label"""
        current_str = time.strftime('%M:%S', time.gmtime(self.current_time))
        total_str = time.strftime('%M:%S', time.gmtime(self.total_duration))
        self.time_label.config(text=f"{current_str} / {total_str}")
    
    def set_playback_speed(self, speed: float):
        """Set playback speed"""
        self.playback_speed = max(0.1, speed)
    
    def add_marker(self, marker_time: float, label: str = ""):
        """Add a marker to the timeline"""
        self.markers.append((marker_time, label))
        self.draw_markers()
    
    def clear_markers(self):
        """Clear all markers"""
        self.markers.clear()
        self.canvas.delete("marker", "marker_label")
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_playback_thread()
        if self.cap:
            self.cap.release()
        self.logger.info("PreviewWidget cleaned up")
