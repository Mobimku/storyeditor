# tests/test_scene_detector.py
import pytest
import numpy as np
import cv2
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.temp_manager import TempManager
from core.scene_detector import SceneDetector

class TestSceneDetector:
    @pytest.fixture
    def temp_manager(self):
        """Create a temporary manager for testing"""
        return TempManager()
    
    @pytest.fixture
    def scene_detector(self, temp_manager):
        """Create a scene detector for testing"""
        return SceneDetector(temp_manager)
    
    @pytest.fixture
    def mock_video_capture(self):
        """Create a mock video capture"""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 900
        }.get(prop, 0)
        return mock_cap
    
    def test_scene_detector_initialization(self, temp_manager):
        """Test scene detector initialization"""
        detector = SceneDetector(temp_manager)
        
        assert detector.temp_manager == temp_manager
        assert detector.sensitivity == 0.3
        assert detector.min_scene_duration == 3.0
        assert detector.max_cut_duration == 7.0
        assert detector.min_cut_duration == 3.0
    
    def test_detect_scenes_success(self, scene_detector, mock_video_capture):
        """Test successful scene detection"""
        # Mock video frames
        mock_frames = [
            np.ones((480, 640, 3), dtype=np.uint8) * 100,  # Similar frame
            np.ones((480, 640, 3), dtype=np.uint8) * 100,  # Similar frame
            np.ones((480, 640, 3), dtype=np.uint8) * 200,  # Different frame (scene change)
            np.ones((480, 640, 3), dtype=np.uint8) * 200,  # Similar frame
        ]
        
        mock_video_capture.read.side_effect = [
            (True, frame) for frame in mock_frames
        ] + [(False, None)]  # End of video
        
        with patch('cv2.VideoCapture') as mock_cv_capture:
            mock_cv_capture.return_value = mock_video_capture
            
            scenes = scene_detector.detect_scenes('test.mp4')
            
            assert len(scenes) >= 1
            assert all('start' in scene for scene in scenes)
            assert all('end' in scene for scene in scenes)
            assert all('duration' in scene for scene in scenes)
    
    def test_detect_scenes_no_video(self, scene_detector):
        """Test scene detection with non-existent video"""
        with patch('cv2.VideoCapture') as mock_cv_capture:
            mock_cv_capture.return_value.isOpened.return_value = False
            
            with pytest.raises(RuntimeError, match="Could not open video file"):
                scene_detector.detect_scenes('nonexistent.mp4')
    
    def test_analyze_frame_difference(self, scene_detector):
        """Test frame difference analysis"""
        # Create two similar frames
        frame1 = np.ones((480, 640, 3), dtype=np.uint8) * 100
        frame2 = np.ones((480, 640, 3), dtype=np.uint8) * 100
        
        correlation = scene_detector.analyze_frame_difference(frame1, frame2)
        assert correlation > 0.9  # Should be very similar
        
        # Create two different frames
        frame3 = np.ones((480, 640, 3), dtype=np.uint8) * 200
        
        correlation2 = scene_detector.analyze_frame_difference(frame1, frame3)
        assert correlation2 < correlation  # Should be less similar
    
    def test_filter_scene_breaks(self, scene_detector):
        """Test scene break filtering"""
        raw_scenes = [
            {'start': 0.0, 'end': 2.0, 'duration': 2.0},   # Too short
            {'start': 2.0, 'end': 8.0, 'duration': 6.0},   # Valid
            {'start': 8.0, 'end': 9.0, 'duration': 1.0},   # Too short
            {'start': 9.0, 'end': 15.0, 'duration': 6.0},  # Valid
        ]
        
        filtered = scene_detector.filter_scene_breaks(raw_scenes, min_scene_duration=3.0)
        
        assert len(filtered) == 2
        assert filtered[0]['start'] == 2.0
        assert filtered[1]['start'] == 9.0
    
    def test_generate_fair_use_cuts(self, scene_detector):
        """Test fair use cuts generation"""
        scenes = [
            {'start': 0.0, 'end': 30.0, 'duration': 30.0},
            {'start': 30.0, 'end': 60.0, 'duration': 30.0},
            {'start': 60.0, 'end': 90.0, 'duration': 30.0}
        ]
        
        cuts = scene_detector.generate_fair_use_cuts(scenes)
        
        assert len(cuts) == 3
        assert all('scene_id' in cut for cut in cuts)
        assert all('start' in cut for cut in cuts)
        assert all('end' in cut for cut in cuts)
        assert all('duration' in cut for cut in cuts)
        assert all('cut_id' in cut for cut in cuts)
        
        # Check cut durations are within limits
        for cut in cuts:
            assert scene_detector.min_cut_duration <= cut['duration'] <= scene_detector.max_cut_duration
    
    def test_generate_fair_use_cuts_short_scene(self, scene_detector):
        """Test fair use cuts with scenes too short"""
        scenes = [
            {'start': 0.0, 'end': 2.0, 'duration': 2.0},   # Too short
            {'start': 2.0, 'end': 8.0, 'duration': 6.0},   # Valid
        ]
        
        cuts = scene_detector.generate_fair_use_cuts(scenes)
        
        assert len(cuts) == 1
        assert cuts[0]['scene_id'] == 1
    
    def test_create_zigzag_sequence(self, scene_detector):
        """Test zigzag sequence creation"""
        cuts = [
            {'id': 'cut0', 'start': 0.0, 'end': 5.0},
            {'id': 'cut1', 'start': 5.0, 'end': 10.0},
            {'id': 'cut2', 'start': 10.0, 'end': 15.0},
            {'id': 'cut3', 'start': 15.0, 'end': 20.0},
        ]
        
        zigzag_indices = scene_detector.create_zigzag_sequence(cuts)
        
        # Expected pattern: 0, 2, 1, 3
        expected = [0, 2, 1, 3]
        assert zigzag_indices == expected
    
    def test_create_zigzag_sequence_odd_count(self, scene_detector):
        """Test zigzag sequence with odd number of cuts"""
        cuts = [
            {'id': 'cut0', 'start': 0.0, 'end': 5.0},
            {'id': 'cut1', 'start': 5.0, 'end': 10.0},
            {'id': 'cut2', 'start': 10.0, 'end': 15.0},
        ]
        
        zigzag_indices = scene_detector.create_zigzag_sequence(cuts)
        
        # Expected pattern: 0, 2, 1
        expected = [0, 2, 1]
        assert zigzag_indices == expected
    
    def test_create_zigzag_sequence_empty(self, scene_detector):
        """Test zigzag sequence with empty cuts"""
        zigzag_indices = scene_detector.create_zigzag_sequence([])
        assert zigzag_indices == []
    
    def test_detect_keyframes(self, scene_detector, mock_video_capture):
        """Test keyframe detection"""
        mock_video_capture.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 900
        }.get(prop, 0)
        
        mock_video_capture.read.side_effect = [
            (True, np.ones((480, 640, 3), dtype=np.uint8))
        ] * 10 + [(False, None)]
        
        with patch('cv2.VideoCapture') as mock_cv_capture:
            mock_cv_capture.return_value = mock_video_capture
            
            keyframes = scene_detector.detect_keyframes('test.mp4', interval=1.0)
            
            assert len(keyframes) > 0
            assert all(isinstance(kf, (int, float)) for kf in keyframes)
    
    def test_export_scene_frames(self, scene_detector, mock_video_capture):
        """Test scene frame export"""
        scenes = [
            {'start_frame': 0, 'end_frame': 30},
            {'start_frame': 30, 'end_frame': 60}
        ]
        
        mock_video_capture.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 900
        }.get(prop, 0)
        
        mock_video_capture.read.side_effect = [
            (True, np.ones((480, 640, 3), dtype=np.uint8))
        ] * 3 + [(False, None)]
        
        with patch('cv2.VideoCapture') as mock_cv_capture:
            mock_cv_capture.return_value = mock_video_capture
            with patch('cv2.imwrite') as mock_imwrite:
                mock_imwrite.return_value = True
                
                frame_paths = scene_detector.export_scene_frames('test.mp4', scenes)
                
                assert len(frame_paths) == 2
                mock_imwrite.assert_called()
    
    def test_export_scene_frames_no_output_dir(self, scene_detector, mock_video_capture):
        """Test scene frame export with no output directory"""
        scenes = [{'start_frame': 0, 'end_frame': 30}]
        
        mock_video_capture.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 900
        }.get(prop, 0)
        
        mock_video_capture.read.side_effect = [
            (True, np.ones((480, 640, 3), dtype=np.uint8))
        ] + [(False, None)]
        
        with patch('cv2.VideoCapture') as mock_cv_capture:
            mock_cv_capture.return_value = mock_video_capture
            with patch('cv2.imwrite') as mock_imwrite:
                mock_imwrite.return_value = True
                
                frame_paths = scene_detector.export_scene_frames('test.mp4', scenes, None)
                
                assert len(frame_paths) == 1
                # Check that temp directory was used
                assert 'scene_frames' in frame_paths[0]

if __name__ == "__main__":
    pytest.main([__file__])