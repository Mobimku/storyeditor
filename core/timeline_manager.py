# core/timeline_manager.py
"""
Timeline and cuts management
Depends on: temp_manager.py
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import json
import os

class TimelineCut:
    """
    Represents a single cut in the timeline
    """
    
    def __init__(self, cut_id: int, start_time: float, end_time: float, scene_id: int = -1):
        self.cut_id = cut_id
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.scene_id = scene_id
        self.order_index = cut_id
        
        # Additional properties
        self.selected = False
        self.enabled = True
        self.effects = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cut to dictionary"""
        return {
            'cut_id': self.cut_id,
            'start': self.start_time,
            'end': self.end_time,
            'duration': self.duration,
            'scene_id': self.scene_id,
            'order_index': self.order_index,
            'selected': self.selected,
            'enabled': self.enabled,
            'effects': self.effects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimelineCut':
        """Create cut from dictionary"""
        cut = cls(
            cut_id=data['cut_id'],
            start_time=data['start'],
            end_time=data['end'],
            scene_id=data.get('scene_id', -1)
        )
        cut.selected = data.get('selected', False)
        cut.enabled = data.get('enabled', True)
        cut.effects = data.get('effects', [])
        return cut
    
    def __repr__(self):
        return f"TimelineCut(id={self.cut_id}, start={self.start_time:.2f}, end={self.end_time:.2f})"

class TimelineScene:
    """
    Represents a scene in the timeline
    """
    
    def __init__(self, scene_id: int, start_time: float, end_time: float):
        self.scene_id = scene_id
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.cuts = []
        
        # Additional properties
        self.selected = False
        self.color = "#6b46c1"  # Default purple color
    
    def add_cut(self, cut: TimelineCut):
        """Add a cut to this scene"""
        self.cuts.append(cut.cut_id)
    
    def remove_cut(self, cut_id: int):
        """Remove a cut from this scene"""
        if cut_id in self.cuts:
            self.cuts.remove(cut_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scene to dictionary"""
        return {
            'scene_id': self.scene_id,
            'start': self.start_time,
            'end': self.end_time,
            'duration': self.duration,
            'cuts': self.cuts,
            'selected': self.selected,
            'color': self.color
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimelineScene':
        """Create scene from dictionary"""
        scene = cls(
            scene_id=data['scene_id'],
            start_time=data['start'],
            end_time=data['end']
        )
        scene.cuts = data.get('cuts', [])
        scene.selected = data.get('selected', False)
        scene.color = data.get('color', "#6b46c1")
        return scene
    
    def __repr__(self):
        return f"TimelineScene(id={self.scene_id}, start={self.start_time:.2f}, end={self.end_time:.2f})"

class TimelineManager:
    """
    Manages video timeline, cuts, and sequences
    """
    
    def __init__(self, temp_manager):
        self.temp_manager = temp_manager
        self.logger = logging.getLogger(__name__)
        
        # Timeline data
        self.cuts = []  # List of TimelineCut objects
        self.scenes = []  # List of TimelineScene objects
        self.timeline_duration = 0.0
        
        # Timeline settings
        self.min_cut_duration = 3.0
        self.max_cut_duration = 7.0
        self.min_scene_duration = 3.0
    
    def add_cut(self, start_time: float, end_time: float, scene_id: int = -1) -> Optional[TimelineCut]:
        """
        Add a cut to the timeline
        
        Args:
            start_time: Start time of cut
            end_time: End time of cut
            scene_id: Associated scene ID
            
        Returns:
            TimelineCut object or None if invalid
        """
        duration = end_time - start_time
        
        # Validate cut duration
        if duration < self.min_cut_duration:
            self.logger.warning(f"Cut too short ({duration:.2f}s), minimum is {self.min_cut_duration}s")
            return None
        
        if duration > self.max_cut_duration:
            self.logger.warning(f"Cut too long ({duration:.2f}s), maximum is {self.max_cut_duration}s")
            return None
        
        cut = TimelineCut(
            cut_id=len(self.cuts),
            start_time=start_time,
            end_time=end_time,
            scene_id=scene_id
        )
        
        self.cuts.append(cut)
        
        # Add cut to scene if scene_id is valid
        if 0 <= scene_id < len(self.scenes):
            self.scenes[scene_id].add_cut(cut)
        
        self.update_timeline_duration()
        
        self.logger.info(f"Added cut: {start_time:.2f}s - {end_time:.2f}s (duration: {duration:.2f}s)")
        return cut
    
    def remove_cut(self, cut_id: int) -> bool:
        """
        Remove a cut from the timeline
        
        Args:
            cut_id: ID of cut to remove
            
        Returns:
            True if cut was removed
        """
        for i, cut in enumerate(self.cuts):
            if cut.cut_id == cut_id:
                # Remove cut from scene
                if 0 <= cut.scene_id < len(self.scenes):
                    self.scenes[cut.scene_id].remove_cut(cut_id)
                
                self.cuts.pop(i)
                self.update_timeline_duration()
                self.logger.info(f"Removed cut with ID: {cut_id}")
                return True
        
        self.logger.warning(f"Cut with ID {cut_id} not found")
        return False
    
    def add_scene(self, start_time: float, end_time: float) -> Optional[TimelineScene]:
        """
        Add a scene to the timeline
        
        Args:
            start_time: Start time of scene
            end_time: End time of scene
            
        Returns:
            TimelineScene object or None if invalid
        """
        duration = end_time - start_time
        
        if duration < self.min_scene_duration:
            self.logger.warning(f"Scene too short ({duration:.2f}s), minimum is {self.min_scene_duration}s")
            return None
        
        scene = TimelineScene(
            scene_id=len(self.scenes),
            start_time=start_time,
            end_time=end_time
        )
        
        self.scenes.append(scene)
        self.logger.info(f"Added scene: {start_time:.2f}s - {end_time:.2f}s (duration: {duration:.2f}s)")
        return scene
    
    def generate_cuts_from_scenes(self) -> List[TimelineCut]:
        """
        Generate cuts from existing scenes
        
        Returns:
            List of TimelineCut objects
        """
        import random
        
        cuts = []
        
        for scene in self.scenes:
            scene_duration = scene.duration
            
            # Skip scenes that are too short
            if scene_duration < self.min_cut_duration:
                continue
            
            # Generate random cut within the scene
            cut_duration = random.uniform(self.min_cut_duration, 
                                        min(self.max_cut_duration, scene_duration))
            cut_start = random.uniform(scene.start_time, scene.end_time - cut_duration)
            cut_end = cut_start + cut_duration
            
            cut = TimelineCut(
                cut_id=len(cuts),
                start_time=cut_start,
                end_time=cut_end,
                scene_id=scene.scene_id
            )
            
            cuts.append(cut)
            scene.add_cut(cut)
        
        self.cuts = cuts
        self.update_timeline_duration()
        
        self.logger.info(f"Generated {len(cuts)} cuts from {len(self.scenes)} scenes")
        return cuts
    
    def create_zigzag_sequence(self) -> List[int]:
        """
        Create zigzag compilation order: 0,2,1,3,5,4,7,6...
        
        Returns:
            List of cut indices in zigzag order
        """
        sequence = []
        n = len(self.cuts)
        
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
    
    def get_cuts_in_sequence(self, sequence: List[int] = None) -> List[TimelineCut]:
        """
        Get cuts in specified sequence order
        
        Args:
            sequence: List of cut indices (uses zigzag if None)
            
        Returns:
            List of ordered TimelineCut objects
        """
        if sequence is None:
            sequence = self.create_zigzag_sequence()
        
        ordered_cuts = []
        for cut_id in sequence:
            if 0 <= cut_id < len(self.cuts):
                ordered_cuts.append(self.cuts[cut_id])
        
        return ordered_cuts
    
    def update_timeline_duration(self):
        """Update total timeline duration"""
        if self.cuts:
            self.timeline_duration = sum(cut.duration for cut in self.cuts)
        else:
            self.timeline_duration = 0.0
    
    def get_timeline_info(self) -> Dict[str, Any]:
        """
        Get comprehensive timeline information
        
        Returns:
            Dictionary with timeline information
        """
        return {
            'total_duration': self.timeline_duration,
            'num_cuts': len(self.cuts),
            'num_scenes': len(self.scenes),
            'cuts': [cut.to_dict() for cut in self.cuts],
            'scenes': [scene.to_dict() for scene in self.scenes],
            'settings': {
                'min_cut_duration': self.min_cut_duration,
                'max_cut_duration': self.max_cut_duration,
                'min_scene_duration': self.min_scene_duration
            }
        }
    
    def clear_timeline(self):
        """Clear all cuts and scenes from timeline"""
        self.cuts.clear()
        self.scenes.clear()
        self.timeline_duration = 0.0
        self.logger.info("Timeline cleared")
    
    def save_timeline(self, filepath: str) -> bool:
        """
        Save timeline to JSON file
        
        Args:
            filepath: Path to save file
            
        Returns:
            True if save successful
        """
        try:
            timeline_data = {
                'cuts': [cut.to_dict() for cut in self.cuts],
                'scenes': [scene.to_dict() for scene in self.scenes],
                'settings': {
                    'min_cut_duration': self.min_cut_duration,
                    'max_cut_duration': self.max_cut_duration,
                    'min_scene_duration': self.min_scene_duration
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(timeline_data, f, indent=2)
            
            self.logger.info(f"Timeline saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save timeline: {e}")
            return False
    
    def load_timeline(self, filepath: str) -> bool:
        """
        Load timeline from JSON file
        
        Args:
            filepath: Path to load file
            
        Returns:
            True if load successful
        """
        try:
            if not os.path.exists(filepath):
                self.logger.error(f"Timeline file not found: {filepath}")
                return False
            
            with open(filepath, 'r') as f:
                timeline_data = json.load(f)
            
            # Load cuts
            self.cuts = [TimelineCut.from_dict(cut_data) for cut_data in timeline_data.get('cuts', [])]
            
            # Load scenes
            self.scenes = [TimelineScene.from_dict(scene_data) for scene_data in timeline_data.get('scenes', [])]
            
            # Load settings
            settings = timeline_data.get('settings', {})
            self.min_cut_duration = settings.get('min_cut_duration', 3.0)
            self.max_cut_duration = settings.get('max_cut_duration', 7.0)
            self.min_scene_duration = settings.get('min_scene_duration', 3.0)
            
            self.update_timeline_duration()
            
            self.logger.info(f"Timeline loaded from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load timeline: {e}")
            return False
    
    def validate_timeline(self) -> List[str]:
        """
        Validate timeline and return list of issues
        
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Check for overlapping cuts
        for i, cut1 in enumerate(self.cuts):
            for j, cut2 in enumerate(self.cuts[i+1:], i+1):
                if (cut1.start_time < cut2.end_time and cut1.end_time > cut2.start_time):
                    issues.append(f"Cuts {i} and {j} overlap")
        
        # Check cut durations
        for i, cut in enumerate(self.cuts):
            if cut.duration < self.min_cut_duration:
                issues.append(f"Cut {i} is too short: {cut.duration:.2f}s")
            if cut.duration > self.max_cut_duration:
                issues.append(f"Cut {i} is too long: {cut.duration:.2f}s")
        
        # Check scene durations
        for i, scene in enumerate(self.scenes):
            if scene.duration < self.min_scene_duration:
                issues.append(f"Scene {i} is too short: {scene.duration:.2f}s")
        
        return issues

# Test the timeline_manager
if __name__ == "__main__":
    import logging
    
    logging.basicConfig(level=logging.DEBUG)
    
    from temp_manager import TempManager
    
    # Test timeline manager
    temp_mgr = TempManager()
    timeline_manager = TimelineManager(temp_mgr)
    
    # Test adding scenes
    scene1 = timeline_manager.add_scene(0.0, 30.0)
    scene2 = timeline_manager.add_scene(30.0, 60.0)
    scene3 = timeline_manager.add_scene(60.0, 90.0)
    
    # Test generating cuts from scenes
    cuts = timeline_manager.generate_cuts_from_scenes()
    print(f"Generated {len(cuts)} cuts")
    
    # Test zigzag sequence
    sequence = timeline_manager.create_zigzag_sequence()
    print(f"Zigzag sequence: {sequence}")
    
    # Test timeline info
    info = timeline_manager.get_timeline_info()
    print(f"Timeline info: {info}")
    
    # Test validation
    issues = timeline_manager.validate_timeline()
    print(f"Validation issues: {issues}")
    
    print("Timeline manager initialized successfully")