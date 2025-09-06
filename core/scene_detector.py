# core/scene_detector.py
"""
AI scene detection using OpenCV
Depends on: temp_manager.py
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Dict, Optional
import os

class SceneDetector:
    """
    Scene detection using OpenCV histogram analysis
    """
    
    def __init__(self, temp_manager):
        self.temp_manager = temp_manager
        self.sensitivity = 0.3
        self.min_scene_duration = 3.0
        self.logger = logging.getLogger(__name__)
    
    def detect_scenes(self, video_path: str) -> List[Tuple[float, float]]:
        """
        Detect scene changes using histogram analysis
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of (start_time, end_time) tuples for each scene
        """
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError(f"Cannot open video file: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            scenes = []
            prev_hist = None
            scene_start = 0.0
            
            for frame_idx in range(frame_count):
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to HSV for better histogram analysis
                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                # Calculate histogram
                hist = cv2.calcHist([hsv_frame], [0, 1, 2], None, [50, 60, 60], 
                                  [0, 180, 0, 256, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                
                if prev_hist is not None:
                    # Compare histograms
                    correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    
                    # If correlation is low, it's a scene change
                    if correlation < (1.0 - self.sensitivity):
                        current_time = frame_idx / fps
                        
                        # Only add scene if it's long enough
                        if current_time - scene_start >= self.min_scene_duration:
                            scenes.append((scene_start, current_time))
                            scene_start = current_time
                
                prev_hist = hist
            
            # Add the last scene
            total_duration = frame_count / fps
            if total_duration - scene_start >= self.min_scene_duration:
                scenes.append((scene_start, total_duration))
            
            cap.release()
            self.logger.info(f"Detected {len(scenes)} scenes")
            return scenes
            
        except Exception as e:
            self.logger.error(f"Scene detection failed: {e}")
            raise RuntimeError(f"Scene detection failed: {e}")
    
    def generate_fair_use_cuts(self, scenes: List[Tuple[float, float]], 
                              min_duration: float = 3.0, 
                              max_duration: float = 7.0) -> List[Dict]:
        """
        Generate fair-use compliant random cuts from scenes
        
        Args:
            scenes: List of (start_time, end_time) tuples
            min_duration: Minimum cut duration
            max_duration: Maximum cut duration
            
        Returns:
            List of cut dictionaries with scene info
        """
        import random
        
        cuts = []
        
        for scene_idx, (start, end) in enumerate(scenes):
            scene_duration = end - start
            
            # Skip scenes that are too short
            if scene_duration < min_duration:
                continue
            
            # Generate random cut within the scene
            cut_duration = random.uniform(min_duration, min(max_duration, scene_duration))
            cut_start = random.uniform(start, end - cut_duration)
            cut_end = cut_start + cut_duration
            
            cuts.append({
                'scene_id': scene_idx,
                'start': cut_start,
                'end': cut_end,
                'duration': cut_duration,
                'cut_id': len(cuts)
            })
        
        self.logger.info(f"Generated {len(cuts)} fair-use cuts")
        return cuts
    
    def create_zigzag_sequence(self, cuts: List[Dict]) -> List[int]:
        """
        Create zigzag compilation order: 0,2,1,3,5,4,7,6...
        
        Args:
            cuts: List of cut dictionaries
            
        Returns:
            List of cut indices in zigzag order
        """
        sequence = []
        n = len(cuts)
        
        for i in range(n):
            if i % 2 == 0:
                # Even indices: 0, 1, 2, 3...
                if i < n:
                    sequence.append(i)
            else:
                # Odd indices: reverse order
                reverse_index = n - 1 - (i // 2)
                if reverse_index > i and reverse_index < n:
                    sequence.append(reverse_index)
        
        # Remove duplicates and ensure all cuts are included
        sequence = list(dict.fromkeys(sequence))
        
        # Add any missing cuts
        for i in range(n):
            if i not in sequence:
                sequence.append(i)
        
        self.logger.info(f"Created zigzag sequence: {sequence}")
        return sequence

# Test the scene_detector
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    from temp_manager import TempManager
    
    # Test scene detector
    temp_mgr = TempManager()
    detector = SceneDetector(temp_mgr)
    
    # Note: Actual scene detection tests require a test video file
    print("Scene detector initialized successfully")