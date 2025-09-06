# core/video_processor.py
"""
Core video processing operations using FFmpeg
Depends on: temp_manager.py
"""

import subprocess
import os
import json
import logging
from typing import List, Tuple, Dict, Optional
from pathlib import Path

class VideoProcessor:
    """
    Core FFmpeg video processing operations
    """
    
    def __init__(self, temp_manager):
        self.temp_manager = temp_manager
        self.ffmpeg_path = self._detect_ffmpeg()
        self.ffprobe_path = self._detect_ffprobe()
        self.logger = logging.getLogger(__name__)
    
    def _detect_ffmpeg(self) -> str:
        """Auto-detect FFmpeg installation"""
        possible_paths = [
            'ffmpeg',  # System PATH
            'ffmpeg.exe',  # Windows
            './ffmpeg',  # Local directory
            './ffmpeg.exe',  # Local Windows
            '/usr/bin/ffmpeg',  # Linux standard
            '/usr/local/bin/ffmpeg',  # macOS Homebrew
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, '-version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.logger.info(f"FFmpeg found at: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        raise RuntimeError("FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
    
    def _detect_ffprobe(self) -> str:
        """Auto-detect FFprobe installation"""
        # Similar to _detect_ffmpeg but for ffprobe
        ffprobe_path = self.ffmpeg_path.replace('ffmpeg', 'ffprobe')
        try:
            result = subprocess.run([ffprobe_path, '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return ffprobe_path
        except:
            pass
        
        raise RuntimeError("FFprobe not found. Please ensure FFprobe is installed alongside FFmpeg.")
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get comprehensive video information"""
        cmd = [
            self.ffprobe_path, '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise RuntimeError(f"FFprobe failed: {result.stderr}")
            
            info = json.loads(result.stdout)
            
            # Extract useful information
            video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
            audio_stream = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
            
            return {
                'duration': float(info['format'].get('duration', 0)),
                'size': int(info['format'].get('size', 0)),
                'bitrate': int(info['format'].get('bit_rate', 0)),
                'format_name': info['format']['format_name'],
                'video_codec': video_stream['codec_name'] if video_stream else None,
                'audio_codec': audio_stream['codec_name'] if audio_stream else None,
                'width': int(video_stream.get('width', 0)) if video_stream else 0,
                'height': int(video_stream.get('height', 0)) if video_stream else 0,
                'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0,
                'has_audio': audio_stream is not None
            }
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse video info: {e}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Video analysis timed out")
    
    def trim_video(self, input_path: str, start_time: float, end_time: float) -> str:
        """
        Trim video intro/outro - returns temp file path
        
        Args:
            input_path: Path to input video
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Path to trimmed video file
        """
        output_path = self.temp_manager.get_temp_file('_trimmed.mp4')
        
        duration = end_time - start_time
        if duration <= 0:
            raise ValueError("Invalid trim times: end_time must be greater than start_time")
        
        cmd = [
            self.ffmpeg_path,
            '-ss', str(start_time),  # Start time
            '-i', input_path,        # Input file
            '-t', str(duration),     # Duration
            '-c', 'copy',            # Copy streams (fast, no re-encoding)
            '-avoid_negative_ts', 'make_zero',
            '-y',                    # Overwrite output
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Video trimming failed: {result.stderr}")
            
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise RuntimeError("Trimmed video file was not created or is empty")
            
            self.logger.info(f"Video trimmed successfully: {start_time}s to {end_time}s")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Video trimming timed out")
    
    def extract_audio(self, input_path: str) -> str:
        """Extract audio track from video"""
        output_path = self.temp_manager.get_temp_file('_audio.wav')
        
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # Uncompressed audio for analysis
            '-ar', '44100',          # Sample rate
            '-ac', '2',              # Stereo
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Audio extraction failed: {result.stderr}")
            
            self.logger.info(f"Audio extracted successfully")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Audio extraction timed out")

# Test the video_processor
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    from temp_manager import TempManager
    
    # Test video processor
    temp_mgr = TempManager()
    processor = VideoProcessor(temp_mgr)
    
    # Test FFmpeg detection
    print(f"FFmpeg path: {processor.ffmpeg_path}")
    print(f"FFprobe path: {processor.ffprobe_path}")
    
    # Note: Actual video processing tests require a test video file
    print("Video processor initialized successfully")