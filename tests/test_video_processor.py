# tests/test_video_processor.py
import pytest
import os
import tempfile
import subprocess
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.temp_manager import TempManager
from core.video_processor import VideoProcessor

class TestVideoProcessor:
    @pytest.fixture
    def temp_manager(self):
        """Create a temporary manager for testing"""
        return TempManager()
    
    @pytest.fixture
    def video_processor(self, temp_manager):
        """Create a video processor for testing"""
        with patch('subprocess.run') as mock_run:
            # Mock FFmpeg detection
            mock_run.return_value = Mock(returncode=0, stdout='ffmpeg version 4.4')
            return VideoProcessor(temp_manager)
    
    def test_ffmpeg_detection_success(self, temp_manager):
        """Test successful FFmpeg detection"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='ffmpeg version 4.4')
            
            processor = VideoProcessor(temp_manager)
            assert processor.ffmpeg_path == 'ffmpeg'
            assert processor.ffprobe_path == 'ffprobe'
    
    def test_ffmpeg_detection_failure(self, temp_manager):
        """Test FFmpeg detection failure"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            
            with pytest.raises(RuntimeError, match="FFmpeg not found"):
                VideoProcessor(temp_manager)
    
    def test_get_video_info_success(self, video_processor):
        """Test successful video info extraction"""
        mock_info = {
            'format': {
                'duration': '60.0',
                'size': '1048576',
                'bit_rate': '1000000',
                'format_name': 'mp4'
            },
            'streams': [
                {
                    'codec_type': 'video',
                    'codec_name': 'h264',
                    'width': 1920,
                    'height': 1080,
                    'r_frame_rate': '30/1'
                },
                {
                    'codec_type': 'audio',
                    'codec_name': 'aac'
                }
            ]
        }
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='{"streams": [], "format": {}}')
            mock_run.return_value.stdout = str(mock_info).replace("'", '"')
            
            info = video_processor.get_video_info('test.mp4')
            
            assert info['duration'] == 60.0
            assert info['size'] == 1048576
            assert info['bitrate'] == 1000000
            assert info['video_codec'] == 'h264'
            assert info['audio_codec'] == 'aac'
            assert info['width'] == 1920
            assert info['height'] == 1080
            assert info['fps'] == 30.0
            assert info['has_audio'] is True
    
    def test_get_video_info_timeout(self, video_processor):
        """Test video info extraction timeout"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('ffprobe', 30)
            
            with pytest.raises(RuntimeError, match="Video analysis timed out"):
                video_processor.get_video_info('test.mp4')
    
    def test_trim_video_success(self, video_processor):
        """Test successful video trimming"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            # Mock file creation
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = True
                with patch('os.path.getsize') as mock_getsize:
                    mock_getsize.return_value = 1024
                    
                    result = video_processor.trim_video('input.mp4', 10.0, 20.0)
                    
                    assert result.endswith('_trimmed.mp4')
                    mock_run.assert_called_once()
    
    def test_trim_video_invalid_times(self, video_processor):
        """Test video trimming with invalid times"""
        with pytest.raises(ValueError, match="Invalid trim times"):
            video_processor.trim_video('input.mp4', 20.0, 10.0)
    
    def test_trim_video_timeout(self, video_processor):
        """Test video trimming timeout"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('ffmpeg', 300)
            
            with pytest.raises(RuntimeError, match="Video trimming timed out"):
                video_processor.trim_video('input.mp4', 10.0, 20.0)
    
    def test_extract_audio_success(self, video_processor):
        """Test successful audio extraction"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            result = video_processor.extract_audio('input.mp4')
            
            assert result.endswith('_audio.wav')
            mock_run.assert_called_once()
    
    def test_extract_audio_timeout(self, video_processor):
        """Test audio extraction timeout"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('ffmpeg', 300)
            
            with pytest.raises(RuntimeError, match="Audio extraction timed out"):
                video_processor.extract_audio('input.mp4')
    
    def test_apply_selective_blur_no_regions(self, video_processor):
        """Test selective blur with no regions"""
        result = video_processor.apply_selective_blur('input.mp4', [])
        assert result == 'input.mp4'
    
    def test_apply_selective_blur_with_regions(self, video_processor):
        """Test selective blur with regions"""
        blur_regions = [
            {'x': 100, 'y': 100, 'width': 200, 'height': 200}
        ]
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            result = video_processor.apply_selective_blur('input.mp4', blur_regions)
            
            assert result.endswith('_blurred.mp4')
            mock_run.assert_called_once()
    
    def test_remove_silent_parts(self, video_processor):
        """Test silent parts removal"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            with patch.object(video_processor, 'extract_audio') as mock_extract:
                mock_extract.return_value = 'audio.wav'
                
                video_path, audio_path = video_processor.remove_silent_parts('input.mp4')
                
                assert video_path.endswith('_no_silence.mp4')
                assert audio_path == 'audio.wav'
                mock_run.assert_called_once()
    
    def test_create_random_cuts(self, video_processor):
        """Test random cuts creation"""
        scene_data = [
            {'start': 0.0, 'end': 30.0, 'duration': 30.0},
            {'start': 30.0, 'end': 60.0, 'duration': 30.0}
        ]
        
        with patch.object(video_processor, 'trim_video') as mock_trim:
            mock_trim.return_value = 'cut.mp4'
            
            cuts = video_processor.create_random_cuts('input.mp4', scene_data)
            
            assert len(cuts) == 2
            mock_trim.assert_called()
    
    def test_compile_zigzag_sequence(self, video_processor):
        """Test zigzag sequence compilation"""
        cuts_list = ['cut1.mp4', 'cut2.mp4', 'cut3.mp4']
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            with patch('builtins.open') as mock_open:
                mock_open.return_value.__enter__.return_value.write = Mock()
                
                result = video_processor.compile_zigzag_sequence(cuts_list)
                
                assert result.endswith('_zigzag.mp4')
                mock_run.assert_called_once()
    
    def test_apply_color_grading(self, video_processor):
        """Test color grading application"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            result = video_processor.apply_color_grading('input.mp4', 'cinematic')
            
            assert result.endswith('_graded_cinematic.mp4')
            mock_run.assert_called_once()
    
    def test_add_panning_effects(self, video_processor):
        """Test panning effects addition"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            with patch.object(video_processor, 'get_video_info') as mock_info:
                mock_info.return_value = {'duration': 60.0}
                
                result = video_processor.add_panning_effects('input.mp4')
                
                assert result.endswith('_panning.mp4')
                mock_run.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])