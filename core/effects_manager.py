# core/effects_manager.py
"""
Color grading and effects management
Depends on: temp_manager.py
"""

import subprocess
import logging
from typing import List, Dict, Any, Optional, Tuple

class EffectsManager:
    """
    Manages color grading and video effects
    """
    
    def __init__(self, temp_manager):
        self.temp_manager = temp_manager
        self.logger = logging.getLogger(__name__)
        
        # Color grading presets
        self.color_presets = {
            'Cinematic': {
                'contrast': 1.2,
                'brightness': 0.9,
                'saturation': 0.8,
                'gamma': 1.1,
                'filter': 'colorchannelmixer=0.3:0.7:0.1:0:0.2:0.8:0:0:0.1:0.9:0:0:0:0:1'
            },
            'Vibrant': {
                'contrast': 1.1,
                'brightness': 1.0,
                'saturation': 1.3,
                'gamma': 1.0,
                'filter': 'eq=contrast=1.1:brightness=0:saturation=1.3'
            },
            'Dramatic': {
                'contrast': 1.4,
                'brightness': 0.8,
                'saturation': 0.9,
                'gamma': 1.2,
                'filter': 'colorchannelmixer=0.4:0.6:0:0:0.3:0.7:0:0:0.2:0.8:0:0:0:0:1'
            },
            'Natural': {
                'contrast': 1.0,
                'brightness': 1.0,
                'saturation': 1.0,
                'gamma': 1.0,
                'filter': ''
            },
            'B&W': {
                'contrast': 1.2,
                'brightness': 1.0,
                'saturation': 0.0,
                'gamma': 1.0,
                'filter': 'hue=s=0'
            }
        }
    
    def apply_color_grading(self, input_path: str, preset: str = 'Cinematic') -> str:
        """
        Apply color grading preset to video
        
        Args:
            input_path: Path to input video
            preset: Color grading preset name
            
        Returns:
            Path to graded video file
        """
        if preset not in self.color_presets:
            self.logger.warning(f"Unknown preset: {preset}, using Natural")
            preset = 'Natural'
        
        preset_config = self.color_presets[preset]
        output_path = self.temp_manager.get_temp_file('_graded.mp4')
        
        # Build FFmpeg filter
        filters = []
        
        if preset_config['filter']:
            filters.append(preset_config['filter'])
        
        # Add basic adjustments
        eq_params = []
        if preset_config['contrast'] != 1.0:
            eq_params.append(f"contrast={preset_config['contrast']}")
        if preset_config['brightness'] != 1.0:
            eq_params.append(f"brightness={preset_config['brightness']}")
        if preset_config['saturation'] != 1.0:
            eq_params.append(f"saturation={preset_config['saturation']}")
        
        if eq_params:
            filters.append(f"eq={':'.join(eq_params)}")
        
        if preset_config['gamma'] != 1.0:
            filters.append(f"gamma={preset_config['gamma']}")
        
        filter_complex = ','.join(filters) if filters else None
        
        cmd = ['ffmpeg', '-i', input_path]
        
        if filter_complex:
            cmd.extend(['-vf', filter_complex])
        
        cmd.extend(['-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-y', output_path])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Color grading failed: {result.stderr}")
            
            self.logger.info(f"Applied color grading preset: {preset}")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Color grading timed out")
    
    def apply_selective_blur(self, input_path: str, blur_regions: List[Dict]) -> str:
        """
        Apply selective blur to specified regions
        
        Args:
            input_path: Path to input video
            blur_regions: List of blur region dictionaries
            
        Returns:
            Path to blurred video file
        """
        if not blur_regions:
            return input_path
        
        output_path = self.temp_manager.get_temp_file('_blurred.mp4')
        
        # Build FFmpeg filter for selective blur
        filters = []
        
        for i, region in enumerate(blur_regions):
            x, y, w, h = region.get('x', 0), region.get('y', 0), region.get('width', 100), region.get('height', 100)
            blur_strength = region.get('strength', 10)
            
            # Create blur filter for this region
            blur_filter = f"boxblur={blur_strength}:1"
            if i == 0:
                filters.append(f"[0:v]{blur_filter}[blurred{i}]")
            else:
                filters.append(f"[blurred{i-1}]{blur_filter}[blurred{i}]")
        
        # Overlay blurred regions on original video
        if filters:
            filters.append(f"[0:v][blurred{len(blur_regions)-1}]overlay=format=auto")
            filter_complex = ','.join(filters)
        else:
            filter_complex = None
        
        cmd = ['ffmpeg', '-i', input_path]
        
        if filter_complex:
            cmd.extend(['-filter_complex', filter_complex])
        
        cmd.extend(['-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-y', output_path])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Selective blur failed: {result.stderr}")
            
            self.logger.info(f"Applied selective blur to {len(blur_regions)} regions")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Selective blur timed out")
    
    def add_panning_effects(self, input_path: str, intervals: int = 15) -> str:
        """
        Add panning/zoom effects at regular intervals
        
        Args:
            input_path: Path to input video
            intervals: Interval in seconds between effects
            
        Returns:
            Path to video with panning effects
        """
        output_path = self.temp_manager.get_temp_file('_panning.mp4')
        
        # Get video duration
        duration = self.get_video_duration(input_path)
        
        # Generate zoom/pan keyframes
        zoom_params = []
        current_time = 0
        
        while current_time < duration:
            # Random zoom effect
            zoom_scale = 1.0 + (0.1 * (current_time % 2))  # Varying zoom
            pan_x = 50 + 30 * (1 if int(current_time) % 2 == 0 else -1)  # Panning left/right
            pan_y = 50 + 20 * (1 if int(current_time) % 3 == 0 else -1)  # Panning up/down
            
            zoom_params.append(f"zoom='{zoom_scale}':x='{pan_x}':y='{pan_y}':enable='between(t,{current_time},{current_time + 2})'")
            
            current_time += intervals
        
        filter_complex = f"zoompan='{':'.join(zoom_params)}'"
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', filter_complex,
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-y', output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Panning effects failed: {result.stderr}")
            
            self.logger.info(f"Added panning effects every {intervals} seconds")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Panning effects timed out")
    
    def get_video_duration(self, video_path: str) -> float:
        """Get video duration using FFprobe"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                return float(info['format']['duration'])
        except:
            pass
        
        return 0.0
    
    def get_available_presets(self) -> List[str]:
        """Get list of available color presets"""
        return list(self.color_presets.keys())
    
    def get_preset_info(self, preset: str) -> Optional[Dict[str, Any]]:
        """Get information about a color preset"""
        return self.color_presets.get(preset)

# Test the effects_manager
if __name__ == "__main__":
    import logging
    
    logging.basicConfig(level=logging.DEBUG)
    
    from temp_manager import TempManager
    
    # Test effects manager
    temp_mgr = TempManager()
    effects_manager = EffectsManager(temp_mgr)
    
    # Test available presets
    presets = effects_manager.get_available_presets()
    print(f"Available presets: {presets}")
    
    # Test preset info
    for preset in presets:
        info = effects_manager.get_preset_info(preset)
        print(f"{preset}: {info}")
    
    print("Effects manager initialized successfully")