# FFmpeg Editor - Phase 2 Implementation Plan

## STEP 1: Project Structure Creation (15 minutes)

### 1.1 Create Directory Structure
```bash
# Create main project structure
mkdir ffmpeg_editor
cd ffmpeg_editor

# Create core directories
mkdir core gui utils assets tests

# Create subdirectories
mkdir assets/icons assets/presets assets/themes
mkdir tests/unit tests/integration

# Create __init__.py files for Python packages
touch __init__.py
touch core/__init__.py
touch gui/__init__.py  
touch utils/__init__.py
```

### 1.2 Create Initial Files
```bash
# Core module files
touch core/temp_manager.py
touch core/video_processor.py
touch core/audio_processor.py
touch core/scene_detector.py
touch core/effects_manager.py
touch core/timeline_manager.py

# GUI module files  
touch gui/main_window.py
touch gui/preview_widget.py
touch gui/timeline_widget.py
touch gui/tab_editor.py
touch gui/tab_compiler.py
touch gui/theme_manager.py

# Utility files
touch utils/url_downloader.py
touch utils/file_handler.py
touch utils/progress_tracker.py
touch utils/keyboard_handler.py

# Main application file
touch main.py

# Configuration files
touch config.json
touch requirements.txt
touch README.md
```

### 1.3 Basic requirements.txt
```txt
# Core Dependencies - Phase 2 Focus
opencv-python==4.8.1
numpy==1.24.3
Pillow==10.0.0
psutil==5.9.5

# Audio Processing
librosa==0.10.1
soundfile==0.12.1

# URL Download (for future phases)
yt-dlp==2023.7.6
requests==2.31.0

# Development & Testing
pytest==7.4.0
pytest-cov==4.1.0
```

---

## STEP 2: Phase 2 Implementation Priority

### 2.1 Module Implementation Order

#### **WEEK 1: Foundation (Priority 1)**
1. **`temp_manager.py`** - CRITICAL FIRST
2. **`video_processor.py`** - Core operations
3. **Basic testing framework**

#### **WEEK 2: Processing Engine (Priority 2)**  
4. **`audio_processor.py`** - Audio analysis
5. **`scene_detector.py`** - AI scene detection
6. **Integration testing**

### 2.2 Implementation Strategy

#### **Day 1-2: temp_manager.py**
```python
"""
CRITICAL MODULE - Must be implemented first
All other modules depend on this
"""

import tempfile
import shutil
import os
import atexit
import logging
from pathlib import Path
from typing import List, Optional

class TempManager:
    """
    PRIORITY: HIGHEST
    Manages all temporary files and cleanup
    """
    
    def __init__(self):
        self.temp_dir: Optional[str] = None
        self.temp_files: List[str] = []
        self.cleanup_on_exit: bool = True
        self.logger = logging.getLogger(__name__)
        
        # Register cleanup on exit
        atexit.register(self.cleanup_all)
    
    def create_temp_dir(self) -> str:
        """Create main temporary directory"""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix='ffmpeg_editor_')
            self.logger.info(f"Created temp directory: {self.temp_dir}")
        return self.temp_dir
    
    def get_temp_file(self, suffix: str = '.mp4') -> str:
        """Generate unique temp file path"""
        if not self.temp_dir:
            self.create_temp_dir()
        
        temp_file = tempfile.mktemp(suffix=suffix, dir=self.temp_dir)
        self.register_temp_file(temp_file)
        return temp_file
    
    def register_temp_file(self, filepath: str):
        """Register file for cleanup"""
        if filepath not in self.temp_files:
            self.temp_files.append(filepath)
            self.logger.debug(f"Registered temp file: {filepath}")
    
    def cleanup_all(self):
        """Clean all temporary files and directories"""
        cleaned_count = 0
        
        # Clean individual files
        for temp_file in self.temp_files[:]:  # Copy list to avoid modification during iteration
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    cleaned_count += 1
                    self.logger.debug(f"Cleaned temp file: {temp_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean temp file {temp_file}: {e}")
                finally:
                    self.temp_files.remove(temp_file)
        
        # Clean main temp directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"Cleaned temp directory: {self.temp_dir}")
                cleaned_count += 1
            except Exception as e:
                self.logger.error(f"Failed to clean temp directory {self.temp_dir}: {e}")
        
        self.logger.info(f"Cleanup completed. {cleaned_count} items cleaned.")
    
    def cleanup_on_error(self):
        """Emergency cleanup on errors"""
        self.logger.warning("Emergency cleanup initiated")
        self.cleanup_all()
    
    def get_cache_file(self, identifier: str) -> str:
        """Get cacheable temp file with identifier"""
        cache_dir = os.path.join(self.temp_dir or self.create_temp_dir(), 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{identifier}.cache")
        self.register_temp_file(cache_file)
        return cache_file
    
    def get_temp_dir(self, subdir_name: str) -> str:
        """Create and return temporary subdirectory"""
        if not self.temp_dir:
            self.create_temp_dir()
        
        subdir_path = os.path.join(self.temp_dir, subdir_name)
        os.makedirs(subdir_path, exist_ok=True)
        return subdir_path
    
    def get_disk_usage(self) -> dict:
        """Get current disk usage info"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.temp_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            
            return {
                'temp_dir_size_mb': total_size / (1024 * 1024),
                'temp_file_count': len(self.temp_files),
                'temp_dir_path': self.temp_dir
            }
        
        return {'temp_dir_size_mb': 0, 'temp_file_count': 0, 'temp_dir_path': None}

# Test the temp_manager
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    # Test temp manager functionality
    temp_mgr = TempManager()
    
    # Test temp file creation
    temp_file1 = temp_mgr.get_temp_file('.mp4')
    temp_file2 = temp_mgr.get_temp_file('.wav')
    
    # Create actual files for testing
    with open(temp_file1, 'w') as f:
        f.write("test video file")
    with open(temp_file2, 'w') as f:
        f.write("test audio file")
    
    # Test cache file
    cache_file = temp_mgr.get_cache_file('test_cache')
    
    # Test disk usage
    usage = temp_mgr.get_disk_usage()
    print(f"Disk usage: {usage}")
    
    # Test cleanup (will be called automatically on exit)
    print("Temp manager test completed. Files will be cleaned up on exit.")
```

#### **Day 3-5: video_processor.py Foundation**
```python
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
```

---

## STEP 3: Development Workflow

### 3.1 Daily Development Process
1. **Morning**: Review previous day's work, run tests
2. **Implementation**: Focus on single module/function
3. **Testing**: Unit tests for each implemented function
4. **Integration**: Test with other modules
5. **Documentation**: Update code comments and docs

### 3.2 Testing Strategy
```python
# tests/test_temp_manager.py
import pytest
import os
import tempfile
from core.temp_manager import TempManager

class TestTempManager:
    def test_temp_dir_creation(self):
        temp_mgr = TempManager()
        temp_dir = temp_mgr.create_temp_dir()
        
        assert os.path.exists(temp_dir)
        assert temp_dir == temp_mgr.temp_dir
        
        # Cleanup
        temp_mgr.cleanup_all()
    
    def test_temp_file_generation(self):
        temp_mgr = TempManager()
        temp_file = temp_mgr.get_temp_file('.mp4')
        
        assert temp_file.endswith('.mp4')
        assert temp_file in temp_mgr.temp_files
        
        # Cleanup
        temp_mgr.cleanup_all()
```

### 3.3 Progress Milestones

#### **Week 1 Milestones:**
- [ ] Project structure created
- [ ] `temp_manager.py` fully implemented and tested
- [ ] `video_processor.py` basic functions working
- [ ] FFmpeg integration confirmed
- [ ] Basic video trim and info extraction working

#### **Week 2 Milestones:**
- [ ] `audio_processor.py` implemented
- [ ] `scene_detector.py` basic implementation
- [ ] Integration tests between modules passing
- [ ] Performance benchmarks established
- [ ] Error handling comprehensive

---

## STEP 4: Implementation Guidelines

### 4.1 Code Quality Standards
- **Type hints** for all function parameters and returns
- **Comprehensive logging** for debugging
- **Error handling** with specific exception types
- **Unit tests** for every public method
- **Documentation strings** following Google style

### 4.2 Performance Considerations
- **Timeout handling** for all subprocess calls
- **Resource cleanup** in finally blocks
- **Progress callbacks** for long operations
- **Memory usage monitoring**

### 4.3 Dependencies Management
- **Lazy imports** for heavy libraries
- **Version pinning** for stability
- **Fallback strategies** for missing dependencies
- **Cross-platform compatibility**

---

## Next Steps for Coder:

1. **Create project structure** (15 minutes)
2. **Implement `temp_manager.py`** (Day 1-2)
3. **Start `video_processor.py`** (Day 3-5)
4. **Regular testing and validation**
5. **Weekly progress review**

This plan provides **concrete, actionable steps** while maintaining the flexibility to adapt as development progresses.