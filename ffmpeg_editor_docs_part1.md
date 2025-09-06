# FFmpeg Video Editor - Development Documentation

## 1. PROJECT OVERVIEW

### 1.1 Application Description
Advanced FFmpeg-based video editor with automated fair-use content processing, featuring real-time preview, smart scene detection, and automated editing workflows.

### 1.2 Key Features
- **Real-time video preview** with timeline controls
- **URL import** from multiple platforms (YouTube, Vimeo, etc.)
- **Smart scene detection** for fair-use editing
- **Automated silent audio removal** with video sync
- **Random sequence generation** with zigzag compilation
- **Color grading presets** and effects
- **Audio mixing** with BGM support
- **Watermark integration**
- **Professional tabbed interface**

### 1.3 Target Output
- Standalone executable (.exe) with licensing system
- Clean temp file management
- Professional-grade editing results

---

## 2. TECHNICAL ARCHITECTURE

### 2.1 Project Structure
```
ffmpeg_editor/
├── main.py                     # Application entry point
├── requirements.txt            # Dependencies
├── config.json                # App configuration
├── LICENSE                     # License file
│
├── core/                      # Core processing modules
│   ├── __init__.py
│   ├── video_processor.py     # FFmpeg video operations
│   ├── audio_processor.py     # Audio analysis & processing
│   ├── scene_detector.py      # AI scene detection
│   ├── effects_manager.py     # Color grading & effects
│   ├── timeline_manager.py    # Timeline & cuts management
│   └── temp_manager.py        # Temporary file management
│
├── gui/                       # User interface
│   ├── __init__.py
│   ├── main_window.py         # Main application window
│   ├── preview_widget.py      # Video preview component
│   ├── timeline_widget.py     # Timeline with sliders
│   ├── tab_editor.py          # Tab 1: Editor interface
│   ├── tab_compiler.py        # Tab 2: Compiler interface
│   └── theme_manager.py       # Purple Blackhole theme
│
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── url_downloader.py      # URL import functionality
│   ├── file_handler.py        # File I/O operations
│   ├── progress_tracker.py    # Progress bar management
│   └── keyboard_handler.py    # Keyboard shortcuts
│
├── assets/                    # Static resources
│   ├── icons/                 # UI icons
│   ├── presets/              # Color grading presets
│   └── themes/               # Theme configurations
│
└── tests/                     # Unit tests
    ├── test_video_processor.py
    ├── test_scene_detector.py
    └── test_temp_manager.py
```

### 2.2 Dependencies
```txt
# Core Dependencies
tkinter                 # GUI framework (built-in Python)
opencv-python==4.8.1   # Computer vision
numpy==1.24.3          # Numerical operations
Pillow==10.0.0         # Image processing
threading              # Async operations (built-in)
tempfile               # Temp file management (built-in)
subprocess             # FFmpeg execution (built-in)
json                   # Configuration (built-in)

# URL Download
yt-dlp==2023.7.6       # Video platform downloads
requests==2.31.0       # HTTP requests

# Audio Processing
librosa==0.10.1        # Audio analysis
soundfile==0.12.1      # Audio file handling

# GUI Enhancements
tkinter.ttk            # Modern widgets (built-in)
matplotlib==3.7.2      # Waveform visualization

# Build & Distribution
pyinstaller==5.13.0    # Executable creation
```

---

## 3. CORE MODULES SPECIFICATION

### 3.1 temp_manager.py - Critical Module
```python
"""
PRIORITY: HIGH - All processing uses temporary files
"""

class TempManager:
    def __init__(self):
        self.temp_dir = None
        self.temp_files = []
        self.cleanup_on_exit = True
    
    def create_temp_dir(self) -> str:
        """Create main temporary directory"""
        
    def get_temp_file(self, suffix='.mp4') -> str:
        """Generate unique temp file path"""
        
    def register_temp_file(self, filepath: str):
        """Register file for cleanup"""
        
    def cleanup_all(self):
        """Clean all temporary files"""
        
    def cleanup_on_error(self):
        """Emergency cleanup on errors"""
        
    def get_cache_file(self, identifier: str) -> str:
        """Get cacheable temp file"""
```

### 3.2 video_processor.py - FFmpeg Operations
```python
class VideoProcessor:
    def __init__(self, temp_manager: TempManager):
        self.temp_manager = temp_manager
        self.ffmpeg_path = self._detect_ffmpeg()
    
    def trim_video(self, input_path: str, start_time: float, 
                   end_time: float) -> str:
        """Trim video intro/outro - returns temp file path"""
        
    def apply_selective_blur(self, input_path: str, 
                           blur_regions: list) -> str:
        """Apply blur to specified regions"""
        
    def remove_silent_parts(self, input_path: str, 
                          audio_threshold: float = -40.0) -> tuple:
        """Remove silent parts, return (video_path, audio_path)"""
        
    def create_random_cuts(self, input_path: str, 
                          scene_data: list) -> list:
        """Generate random 3-7 second cuts per scene"""
        
    def compile_zigzag_sequence(self, cuts_list: list) -> str:
        """Compile video with zigzag pattern"""
        
    def apply_color_grading(self, input_path: str, 
                          preset: str) -> str:
        """Apply color grading preset"""
        
    def add_panning_effects(self, input_path: str, 
                          intervals: int = 15) -> str:
        """Add panning/zoom effects every 15-20 seconds"""
```

### 3.3 scene_detector.py - AI Scene Detection
```python
class SceneDetector:
    def __init__(self, temp_manager: TempManager):
        self.temp_manager = temp_manager
        self.sensitivity = 0.3
    
    def detect_scenes(self, video_path: str) -> list:
        """
        Detect scene changes using OpenCV histogram analysis
        Returns: [(timestamp, confidence), ...]
        """
        
    def analyze_frame_difference(self, frame1, frame2) -> float:
        """Calculate histogram correlation between frames"""
        
    def filter_scene_breaks(self, raw_scenes: list, 
                          min_scene_duration: float = 3.0) -> list:
        """Filter out too-short scenes"""
        
    def generate_fair_use_cuts(self, scenes: list) -> list:
        """
        Generate fair-use compliant random cuts
        Returns: [{'scene_id', 'start', 'duration', 'cut_id'}, ...]
        """
        
    def create_zigzag_sequence(self, cuts: list) -> list:
        """Create zigzag compilation order: 0,2,1,3,5,4,7,6..."""
```

### 3.4 url_downloader.py - Platform Support
```python
class URLDownloader:
    def __init__(self, temp_manager: TempManager):
        self.temp_manager = temp_manager
        self.supported_platforms = [
            'youtube', 'vimeo', 'twitter', 'instagram', 
            'tiktok', 'direct', 'gdrive', 'dropbox'
        ]
    
    def detect_platform(self, url: str) -> str:
        """Auto-detect video platform"""
        
    def download_video(self, url: str, quality: str = '720p', 
                      progress_callback=None) -> tuple:
        """
        Download video from URL
        Returns: (temp_file_path, duration, title)
        """
        
    def download_playlist(self, url: str, max_videos: int = 10) -> list:
        """Download multiple videos from playlist"""
        
    def validate_url(self, url: str) -> bool:
        """Validate URL accessibility"""
```

---

## 4. GUI ARCHITECTURE

### 4.1 Theme System - Purple Blackhole
```python
# theme_manager.py
PURPLE_BLACKHOLE_THEME = {
    'bg_primary': '#1a0d26',      # Deep purple-black
    'bg_secondary': '#2d1b3d',    # Lighter purple-black
    'accent_primary': '#6b46c1',  # Purple
    'accent_secondary': '#a855f7', # Light purple
    'accent_tertiary': '#ec4899',  # Pink-purple
    'text_primary': '#f8fafc',     # Light gray
    'text_secondary': '#cbd5e1',   # Medium gray
    'border': '#4c1d95',          # Purple border
    'hover': '#7c3aed',           # Hover purple
    'success': '#10b981',         # Green
    'error': '#ef4444',           # Red
    'warning': '#f59e0b'          # Orange
}
```

### 4.2 Main Window Layout
```python
class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_theme()
        self.setup_layout()
        self.setup_keyboard_shortcuts()
    
    def setup_layout(self):
        """
        Layout Structure:
        ┌─────────────────────────────────────────┐
        │           Video Preview Area            │
        │                                         │
        ├─────────────────────────────────────────┤
        │  Tab1: Editor  │  Tab2: Compiler        │
        ├─────────────────────────────────────────┤
        │              Progress Bar               │
        └─────────────────────────────────────────┘
        """
```

### 4.3 Tab 1: Editor Interface
```python
class EditorTab:
    def setup_ui(self):
        """
        Editor Layout:
        ├── Input Section
        │   ├── [Local File] [URL Import]
        │   ├── URL Entry: _________________ [Download]
        │   └── Quality: [720p ▼]
        │
        ├── Timeline Section  
        │   ├── Trim Intro:  [====|========] 00:15
        │   ├── Trim Outro:  [========|====] 02:45
        │   └── Silent Threshold: [-40dB ====|==]
        │
        ├── Effects Section
        │   ├── Selective Blur: [Add Region] [Clear All]
        │   ├── Color Preset: [Cinematic ▼]
        │   └── Scene Detection: [Auto ✓] Sensitivity: [===|=]
        │
        └── Process Section
            ├── [SMART PREVIEW] [START PROCESSING]
            └── ☑️ Fair Use Mode  ☑️ Auto Effects
        """
```

### 4.4 Tab 2: Compiler Interface  
```python
class CompilerTab:
    def setup_ui(self):
        """
        Compiler Layout:
        ├── Audio Mixing
        │   ├── Original Audio: [■] Vol: [====|====] 80%
        │   ├── Background Music: [+Add] Vol: [===|=====] 40%  
        │   └── Output Format: [MP3 ▼] [WAV ▼]
        │
        ├── Video Settings
        │   ├── Watermark: [+Add] Position: [Bottom Right ▼]
        │   ├── Output Quality: [1080p ▼] [H.264 ▼]
        │   └── FPS: [30 ▼] Bitrate: [5000 kbps]
        │
        └── Render Section  
            ├── Output Directory: [Browse...]
            ├── Filename: video_edit_[timestamp]
            └── [RENDER FINAL] Progress: [████████░░] 80%
        """
```

---

## 5. WORKFLOW AUTOMATION

### 5.1 Complete Processing Pipeline
```python
class AutomationPipeline:
    def __init__(self):
        self.temp_manager = TempManager()
        self.video_processor = VideoProcessor(self.temp_manager)
        self.scene_detector = SceneDetector(self.temp_manager)
        
    def execute_full_pipeline(self, input_source: str, settings: dict) -> tuple:
        """
        Complete automation workflow:
        
        1. Import Phase
           ├── URL download OR local file copy to temp
           └── Basic validation
        
        2. Preprocessing Phase  
           ├── Apply trim settings (intro/outro)
           ├── Apply selective blur regions
           └── Extract initial audio track
        
        3. Audio Analysis Phase
           ├── Detect silent parts (<-40dB)  
           ├── Generate cut timestamps
           └── Remove silent parts from video + audio
        
        4. Scene Detection Phase
           ├── Analyze remaining video for scene changes
           ├── Filter scenes (min 3 seconds)
           └── Generate random cuts per scene (3-7 sec)
        
        5. Fair Use Sequencing
           ├── Create zigzag pattern: 0,2,1,3,5,4,7,6...
           ├── Compile video sequence (no audio)
           └── Keep original audio intact
        
        6. Effects Application  
           ├── Auto-select color grading preset
           ├── Apply panning effects (every 15-20 sec)
           └── Add subtle variations
        
        7. Output Generation
           ├── Render final video (silent)
           ├── Process final audio
           └── Cleanup all temp files
        
        Returns: (final_video_path, final_audio_path)
        """
```

### 5.2 Error Handling & Recovery
```python
class ErrorHandler:
    def __init__(self, temp_manager: TempManager):
        self.temp_manager = temp_manager
        self.error_log = []
    
    def handle_ffmpeg_error(self, error: Exception, context: str):
        """Handle FFmpeg-related errors"""
        
    def handle_download_error(self, error: Exception, url: str):
        """Handle URL download errors"""
        
    def emergency_cleanup(self):
        """Emergency cleanup on critical errors"""
        
    def log_error(self, error: Exception, context: str):
        """Log errors for debugging"""
```

---

## 6. PERFORMANCE OPTIMIZATION

### 6.1 Threading Strategy
```python
class ThreadManager:
    def __init__(self):
        self.max_workers = 4
        self.current_tasks = []
    
    def run_ffmpeg_async(self, command: list, callback=None):
        """Run FFmpeg operations in separate thread"""
        
    def run_download_async(self, url: str, callback=None):
        """Run URL downloads in separate thread"""
        
    def update_progress(self, task_id: str, progress: float):
        """Thread-safe progress updates"""
```

### 6.2 Caching System
```python
class CacheManager:
    def __init__(self, temp_manager: TempManager):
        self.temp_manager = temp_manager
        self.cache = {}
    
    def cache_scene_analysis(self, video_path: str, scenes: list):
        """Cache scene detection results"""
        
    def get_cached_preview(self, video_path: str, timestamp: float):
        """Get cached preview frames"""
        
    def cache_audio_analysis(self, audio_path: str, silent_parts: list):
        """Cache audio silent detection"""
```

### 6.3 Memory Management
```python
class MemoryManager:
    def __init__(self):
        self.max_memory_usage = 2048  # MB
        self.current_usage = 0
    
    def monitor_memory(self):
        """Monitor application memory usage"""
        
    def optimize_opencv_usage(self):
        """Optimize OpenCV memory usage"""
        
    def garbage_collect(self):
        """Force garbage collection when needed"""
```

---

## 7. KEYBOARD SHORTCUTS

### 7.1 Standard Shortcuts
```python
KEYBOARD_SHORTCUTS = {
    # Playback Controls
    'Space': 'toggle_play_pause',
    'Left Arrow': 'frame_backward',  
    'Right Arrow': 'frame_forward',
    'Home': 'goto_beginning',
    'End': 'goto_end',
    
    # Editing
    'I': 'set_in_point',
    'O': 'set_out_point', 
    'Ctrl+Z': 'undo',
    'Ctrl+Y': 'redo',
    'Delete': 'delete_selected',
    
    # Application  
    'Ctrl+O': 'open_file',
    'Ctrl+S': 'save_project',
    'Ctrl+Q': 'quit_application',
    'F1': 'show_help'
}
```

---

## 8. TESTING STRATEGY

### 8.1 Unit Tests Priority
1. **temp_manager.py** - Critical for cleanup
2. **video_processor.py** - Core functionality  
3. **scene_detector.py** - AI accuracy
4. **url_downloader.py** - Platform compatibility

### 8.2 Integration Tests
1. **Full pipeline test** with sample video
2. **URL download test** for major platforms
3. **Error recovery test** with corrupted files
4. **Memory stress test** with large files

### 8.3 User Acceptance Tests
1. **Complete workflow** from URL to final output
2. **Performance benchmarks** with various file sizes
3. **UI responsiveness** during processing
4. **Cross-platform compatibility**

---

## 9. BUILD & DISTRIBUTION

### 9.1 PyInstaller Configuration
```python
# build.spec
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[('ffmpeg.exe', '.')],  # Include FFmpeg
    datas=[('assets/', 'assets/'), ('config.json', '.')],
    hiddenimports=['cv2', 'numpy', 'yt_dlp'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FFmpegEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows app
    icon='assets/icons/app_icon.ico'
)
```

### 9.2 Licensing Integration
```python
class LicenseManager:
    def __init__(self):
        self.license_file = 'license.key'
        self.is_licensed = False
    
    def validate_license(self) -> bool:
        """Validate license key on startup"""
        
    def show_license_dialog(self):
        """Show license input dialog"""
        
    def encrypt_license_key(self, key: str) -> str:
        """Encrypt license for storage"""
```

---

## 10. DEVELOPMENT PHASES

### Phase 1: Core Foundation (Week 1-2)
- [x] Project structure setup
- [x] temp_manager.py implementation  
- [x] Basic GUI with theme
- [x] FFmpeg integration
- [x] File import functionality

### Phase 2: Processing Engine (Week 3-4)  
- [ ] video_processor.py full implementation
- [ ] audio_processor.py implementation
- [ ] scene_detector.py with OpenCV
- [ ] Basic automation pipeline

### Phase 3: Advanced Features (Week 5-6)
- [ ] URL downloading with yt-dlp
- [ ] Color grading presets
- [ ] Effects and panning
- [ ] Audio mixing capabilities

### Phase 4: UI/UX Polish (Week 7-8)
- [ ] Complete tabbed interface
- [ ] Real-time preview
- [ ] Progress tracking
- [ ] Keyboard shortcuts

### Phase 5: Testing & Build (Week 9-10)
- [ ] Comprehensive testing
- [ ] Performance optimization  
- [ ] PyInstaller build
- [ ] License integration

---

## 11. CRITICAL NOTES FOR DEVELOPERS

### 11.1 MANDATORY Requirements
1. **ALL processing uses temporary files** - Never modify original files
2. **Automatic cleanup** on application exit or error
3. **Thread-safe operations** for GUI responsiveness  
4. **Progress callbacks** for all long-running operations
5. **Error handling** with user-friendly messages

### 11.2 Performance Targets
- **Preview latency**: < 100ms for seeking
- **Processing speed**: Real-time for 720p video
- **Memory usage**: < 2GB for 1-hour video
- **Startup time**: < 5 seconds

### 11.3 Platform Compatibility
- **Primary**: Windows 10/11
- **Secondary**: macOS, Linux
- **FFmpeg**: Auto-detect or bundle executable
- **Dependencies**: Minimize external requirements

### 11.4 Fair Use Compliance
- **Random sequencing**: Essential for fair use
- **Scene disruption**: Break narrative continuity  
- **Duration limits**: 3-7 second cuts maximum
- **Transformation**: Substantial alteration of original

---

## 12. CONTACT & SUPPORT

### 12.1 Development Team Roles
- **Lead Developer**: Core engine implementation
- **GUI Developer**: Interface and user experience
- **QA Engineer**: Testing and optimization
- **Build Engineer**: Distribution and deployment

### 12.2 Documentation Updates
This document should be updated with:
- Implementation progress
- Architecture changes  
- Performance benchmarks
- User feedback integration

---

*Document Version: 1.0*
*Last Updated: September 2025*
*Next Review: After Phase 2 completion*