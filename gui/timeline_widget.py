# gui/timeline_widget.py
"""
Timeline widget with visual representation of cuts and scenes
"""

import tkinter as tk
from tkinter import ttk, Canvas
import logging
from typing import Dict, Any, Optional, List, Tuple, Callable

from core.timeline_manager import TimelineCut, TimelineScene, TimelineManager

class TimelineWidget:
    """
    Visual timeline widget for displaying and manipulating cuts and scenes
    """
    
    def __init__(self, parent, timeline_manager: TimelineManager, theme_manager, 
                 width: int = 800, height: int = 200):
        self.parent = parent
        self.timeline_manager = timeline_manager
        self.theme_manager = theme_manager
        self.logger = logging.getLogger(__name__)
        
        # Widget dimensions
        self.width = width
        self.height = height
        self.timeline_height = height - 50  # Leave space for controls
        
        # Timeline properties
        self.zoom_level = 1.0
        self.scroll_position = 0.0
        self.total_duration = 0.0
        self.pixels_per_second = 50.0  # Default zoom level
        
        # Selection and interaction
        self.selected_cut = None
        self.selected_scene = None
        self.drag_start_x = 0
        self.is_dragging = False
        
        # Callbacks
        self.on_cut_selected: Optional[Callable[[TimelineCut], None]] = None
        self.on_scene_selected: Optional[Callable[[TimelineScene], None]] = None
        self.on_cut_moved: Optional[Callable[[TimelineCut, float], None]] = None
        
        # Create widget
        self.create_widget()
        
        # Bind events
        self.bind_events()
        
        # Initial render
        self.update_timeline()
    
    def create_widget(self):
        """Create the timeline widget"""
        # Main frame
        self.frame = self.theme_manager.create_custom_frame(self.parent, padding=5)
        
        # Canvas for timeline visualization
        self.canvas = Canvas(
            self.frame,
            width=self.width,
            height=self.timeline_height,
            bg=self.theme_manager.get_color('bg_secondary'),
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Control frame
        control_frame = self.theme_manager.create_custom_frame(self.frame)
        control_frame.pack(fill='x', pady=(5, 0))
        
        # Zoom controls
        zoom_label = self.theme_manager.create_custom_label(control_frame, "Zoom:")
        zoom_label.pack(side='left', padx=(0, 5))
        
        self.zoom_in_btn = self.theme_manager.create_custom_button(
            control_frame, "+", command=self.zoom_in, width=3
        )
        self.zoom_in_btn.pack(side='left', padx=(0, 2))
        
        self.zoom_out_btn = self.theme_manager.create_custom_button(
            control_frame, "-", command=self.zoom_out, width=3
        )
        self.zoom_out_btn.pack(side='left', padx=(0, 10))
        
        # Time display
        self.time_label = self.theme_manager.create_custom_label(control_frame, "00:00")
        self.time_label.pack(side='left', padx=(0, 10))
        
        # Duration display
        self.duration_label = self.theme_manager.create_custom_label(control_frame, "/ 00:00")
        self.duration_label.pack(side='left')
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.frame,
            orient='horizontal',
            command=self.on_scroll
        )
        self.scrollbar.pack(fill='x', pady=(5, 0))
        
        # Configure canvas to use scrollbar
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
    
    def bind_events(self):
        """Bind mouse and keyboard events"""
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.canvas.bind('<Motion>', self.on_canvas_motion)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        self.canvas.bind('<Button-4>', self.on_mouse_wheel)  # Linux
        self.canvas.bind('<Button-5>', self.on_mouse_wheel)  # Linux
    
    def update_timeline(self):
        """Update timeline visualization"""
        # Clear canvas
        self.canvas.delete('all')
        
        # Get timeline data
        self.total_duration = self.timeline_manager.timeline_duration
        
        # Update scrollbar
        if self.total_duration > 0:
            canvas_width = self.total_duration * self.pixels_per_second * self.zoom_level
            self.canvas.configure(scrollregion=(0, 0, canvas_width, self.timeline_height))
            self.scrollbar.configure(to=canvas_width - self.width)
        
        # Draw time markers
        self.draw_time_markers()
        
        # Draw scenes
        self.draw_scenes()
        
        # Draw cuts
        self.draw_cuts()
        
        # Update labels
        self.update_labels()
    
    def draw_time_markers(self):
        """Draw time markers on timeline"""
        if self.total_duration == 0:
            return
        
        # Calculate marker interval based on zoom
        if self.zoom_level > 2.0:
            interval = 1.0  # 1 second markers
        elif self.zoom_level > 1.0:
            interval = 5.0  # 5 second markers
        else:
            interval = 10.0  # 10 second markers
        
        # Draw markers
        current_time = 0.0
        while current_time <= self.total_duration:
            x = self.time_to_x(current_time)
            
            # Draw marker line
            self.canvas.create_line(
                x, 0, x, self.timeline_height,
                fill=self.theme_manager.get_color('border'),
                width=1,
                tags='time_marker'
            )
            
            # Draw time label
            time_text = self.format_time(current_time)
            self.canvas.create_text(
                x, self.timeline_height - 5,
                text=time_text,
                fill=self.theme_manager.get_color('text_secondary'),
                font=('Arial', 8),
                anchor='s',
                tags='time_label'
            )
            
            current_time += interval
    
    def draw_scenes(self):
        """Draw scenes on timeline"""
        for scene in self.timeline_manager.scenes:
            x1 = self.time_to_x(scene.start_time)
            x2 = self.time_to_x(scene.end_time)
            
            # Draw scene background
            self.canvas.create_rectangle(
                x1, 0, x2, self.timeline_height,
                fill=scene.color,
                outline='',
                tags=('scene', f'scene_{scene.scene_id}')
            )
            
            # Draw scene label
            if x2 - x1 > 50:  # Only show label if scene is wide enough
                center_x = (x1 + x2) / 2
                self.canvas.create_text(
                    center_x, 15,
                    text=f"Scene {scene.scene_id + 1}",
                    fill=self.theme_manager.get_color('text_primary'),
                    font=('Arial', 10, 'bold'),
                    tags=('scene_label', f'scene_label_{scene.scene_id}')
                )
    
    def draw_cuts(self):
        """Draw cuts on timeline"""
        for cut in self.timeline_manager.cuts:
            x1 = self.time_to_x(cut.start_time)
            x2 = self.time_to_x(cut.end_time)
            
            # Determine cut color based on selection and state
            if cut.selected:
                fill_color = self.theme_manager.get_color('accent_secondary')
                outline_color = self.theme_manager.get_color('text_primary')
            elif cut.enabled:
                fill_color = self.theme_manager.get_color('accent_primary')
                outline_color = self.theme_manager.get_color('border')
            else:
                fill_color = self.theme_manager.get_color('bg_secondary')
                outline_color = self.theme_manager.get_color('text_secondary')
            
            # Draw cut rectangle
            self.canvas.create_rectangle(
                x1, 30, x2, self.timeline_height - 30,
                fill=fill_color,
                outline=outline_color,
                width=2,
                tags=('cut', f'cut_{cut.cut_id}')
            )
            
            # Draw cut label
            if x2 - x1 > 30:  # Only show label if cut is wide enough
                center_x = (x1 + x2) / 2
                center_y = (30 + self.timeline_height - 30) / 2
                
                duration_text = self.format_duration(cut.duration)
                self.canvas.create_text(
                    center_x, center_y,
                    text=duration_text,
                    fill=self.theme_manager.get_color('text_primary'),
                    font=('Arial', 9),
                    tags=('cut_label', f'cut_label_{cut.cut_id}')
                )
    
    def time_to_x(self, time: float) -> float:
        """Convert time to x coordinate"""
        return time * self.pixels_per_second * self.zoom_level
    
    def x_to_time(self, x: float) -> float:
        """Convert x coordinate to time"""
        return x / (self.pixels_per_second * self.zoom_level)
    
    def format_time(self, time_seconds: float) -> str:
        """Format time as MM:SS"""
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def format_duration(self, duration_seconds: float) -> str:
        """Format duration as X.Xs"""
        return f"{duration_seconds:.1f}s"
    
    def update_labels(self):
        """Update time and duration labels"""
        # Update duration label
        duration_text = self.format_time(self.total_duration)
        self.duration_label.config(text=f"/ {duration_text}")
    
    def zoom_in(self):
        """Zoom in timeline"""
        self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        self.update_timeline()
    
    def zoom_out(self):
        """Zoom out timeline"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.2)
        self.update_timeline()
    
    def on_scroll(self, *args):
        """Handle scrollbar scroll"""
        self.canvas.xview(*args)
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        # Convert click coordinates to timeline coordinates
        canvas_x = self.canvas.canvasx(event.x)
        click_time = self.x_to_time(canvas_x)
        
        # Check if clicking on a cut
        clicked_cut = self.get_cut_at_position(canvas_x, event.y)
        if clicked_cut:
            self.select_cut(clicked_cut)
            if self.on_cut_selected:
                self.on_cut_selected(clicked_cut)
            self.drag_start_x = canvas_x
            return
        
        # Check if clicking on a scene
        clicked_scene = self.get_scene_at_position(canvas_x, event.y)
        if clicked_scene:
            self.select_scene(clicked_scene)
            if self.on_scene_selected:
                self.on_scene_selected(clicked_scene)
            return
        
        # Clear selection if clicking empty space
        self.clear_selection()
    
    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        if self.selected_cut and self.is_dragging:
            canvas_x = self.canvas.canvasx(event.x)
            drag_delta = canvas_x - self.drag_start_x
            time_delta = self.x_to_time(drag_delta)
            
            # Move the cut
            new_start_time = self.selected_cut.start_time + time_delta
            new_end_time = self.selected_cut.end_time + time_delta
            
            # Validate new position
            if self.is_valid_cut_position(self.selected_cut, new_start_time, new_end_time):
                self.selected_cut.start_time = new_start_time
                self.selected_cut.end_time = new_end_time
                self.drag_start_x = canvas_x
                
                if self.on_cut_moved:
                    self.on_cut_moved(self.selected_cut, time_delta)
                
                self.update_timeline()
    
    def on_canvas_release(self, event):
        """Handle canvas release"""
        self.is_dragging = False
    
    def on_canvas_motion(self, event):
        """Handle canvas motion"""
        canvas_x = self.canvas.canvasx(event.x)
        click_time = self.x_to_time(canvas_x)
        
        # Update time label
        time_text = self.format_time(click_time)
        self.time_label.config(text=time_text)
        
        # Change cursor if hovering over draggable element
        if self.get_cut_at_position(canvas_x, event.y):
            self.canvas.configure(cursor="hand2")
        else:
            self.canvas.configure(cursor="")
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        if event.delta > 0 or event.num == 4:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def get_cut_at_position(self, x: float, y: float) -> Optional[TimelineCut]:
        """Get cut at given position"""
        for cut in self.timeline_manager.cuts:
            x1 = self.time_to_x(cut.start_time)
            x2 = self.time_to_x(cut.end_time)
            
            if x1 <= x <= x2 and 30 <= y <= self.timeline_height - 30:
                return cut
        return None
    
    def get_scene_at_position(self, x: float, y: float) -> Optional[TimelineScene]:
        """Get scene at given position"""
        for scene in self.timeline_manager.scenes:
            x1 = self.time_to_x(scene.start_time)
            x2 = self.time_to_x(scene.end_time)
            
            if x1 <= x <= x2 and 0 <= y <= self.timeline_height:
                return scene
        return None
    
    def select_cut(self, cut: TimelineCut):
        """Select a cut"""
        # Clear previous selection
        self.clear_selection()
        
        # Select new cut
        cut.selected = True
        self.selected_cut = self.selected_cut
        self.is_dragging = True
        
        self.update_timeline()
    
    def select_scene(self, scene: TimelineScene):
        """Select a scene"""
        # Clear previous selection
        self.clear_selection()
        
        # Select new scene
        scene.selected = True
        self.selected_scene = scene
        
        self.update_timeline()
    
    def clear_selection(self):
        """Clear all selections"""
        for cut in self.timeline_manager.cuts:
            cut.selected = False
        
        for scene in self.timeline_manager.scenes:
            scene.selected = False
        
        self.selected_cut = None
        self.selected_scene = None
        self.is_dragging = False
        
        self.update_timeline()
    
    def is_valid_cut_position(self, cut: TimelineCut, start_time: float, end_time: float) -> bool:
        """Check if cut position is valid"""
        # Check duration constraints
        duration = end_time - start_time
        if duration < self.timeline_manager.min_cut_duration:
            return False
        if duration > self.timeline_manager.max_cut_duration:
            return False
        
        # Check for overlaps with other cuts
        for other_cut in self.timeline_manager.cuts:
            if other_cut.cut_id != cut.cut_id:
                if (start_time < other_cut.end_time and end_time > other_cut.start_time):
                    return False
        
        return True
    
    def set_cut_selected_callback(self, callback: Callable[[TimelineCut], None]):
        """Set callback for cut selection"""
        self.on_cut_selected = callback
    
    def set_scene_selected_callback(self, callback: Callable[[TimelineScene], None]):
        """Set callback for scene selection"""
        self.on_scene_selected = callback
    
    def set_cut_moved_callback(self, callback: Callable[[TimelineCut, float], None]):
        """Set callback for cut movement"""
        self.on_cut_moved = callback

# Test the timeline_widget
if __name__ == "__main__":
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    root = tk.Tk()
    root.title("Timeline Widget Test")
    root.geometry("1000x300")
    
    # Mock theme manager
    class MockThemeManager:
        def create_custom_frame(self, parent, style='TFrame', padding=0):
            return ttk.Frame(parent)
        
        def create_custom_label(self, parent, text, font=None):
            return ttk.Label(parent, text=text, font=font)
        
        def create_custom_button(self, parent, text, command=None, width=None):
            return ttk.Button(parent, text=text, command=command, width=width)
        
        def get_color(self, color_name):
            colors = {
                'bg_primary': '#1a0d26',
                'bg_secondary': '#2d1b3d',
                'accent_primary': '#6b46c1',
                'accent_secondary': '#a855f7',
                'text_primary': '#f8fafc',
                'text_secondary': '#cbd5e1',
                'border': '#4c1d95'
            }
            return colors.get(color_name, '#000000')
    
    # Mock timeline manager
    class MockTimelineManager:
        def __init__(self):
            self.cuts = []
            self.scenes = []
            self.timeline_duration = 0.0
            self.min_cut_duration = 3.0
            self.max_cut_duration = 7.0
        
        def add_scene(self, start, end):
            from core.timeline_manager import TimelineScene
            scene = TimelineScene(len(self.scenes), start, end)
            self.scenes.append(scene)
            return scene
        
        def add_cut(self, start, end, scene_id=-1):
            from core.timeline_manager import TimelineCut
            cut = TimelineCut(len(self.cuts), start, end, scene_id)
            self.cuts.append(cut)
            self.timeline_duration += cut.duration
            return cut
    
    # Create test data
    theme_manager = MockThemeManager()
    timeline_manager = MockTimelineManager()
    
    # Add test scenes and cuts
    scene1 = timeline_manager.add_scene(0, 30)
    scene2 = timeline_manager.add_scene(30, 60)
    scene3 = timeline_manager.add_scene(60, 90)
    
    timeline_manager.add_cut(2, 8, 0)
    timeline_manager.add_cut(12, 18, 0)
    timeline_manager.add_cut(32, 38, 1)
    timeline_manager.add_cut(42, 48, 1)
    timeline_manager.add_cut(62, 68, 2)
    timeline_manager.add_cut(72, 78, 2)
    
    # Create timeline widget
    timeline_widget = TimelineWidget(root, timeline_manager, theme_manager)
    timeline_widget.frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    root.mainloop()