```python
"""
ISSUE: Processing large videos can fill up disk space rapidly
SOLUTION: Proactive disk space monitoring and management
"""
class DiskSpaceCrisisManager:
    def __init__(self, temp_manager: TempManager):
        self.temp_manager = temp_manager
        self.min_free_space_gb = 10
        self.warning_threshold_gb = 20
        
    def monitor_disk_space(self):
        """Continuous disk space monitoring"""
        while self.processing_active:
            free_space_gb = self.get_free_space_gb()
            
            if free_space_gb < self.min_free_space_gb:
                self.handle_disk_space_emergency()
            elif free_space_gb < self.warning_threshold_gb:
                self.optimize_disk_usage()
                
            time.sleep(30)  # Check every 30 seconds
    
    def handle_disk_space_emergency(self):
        """Emergency disk space recovery"""
        # 1. Pause all non-critical operations
        self.pause_background_tasks()
        
        # 2. Aggressive cleanup
        self.temp_manager.emergency_cleanup()
        
        # 3. Clear system temp files
        self.clear_system_temp()
        
        # 4. Compress intermediate files
        self.compress_temp_files()
        
        # 5. If still critical, abort processing
        if self.get_free_space_gb() < self.min_free_space_gb:
            raise DiskSpaceError("Critical disk space shortage - processing aborted")
    
    def predict_space_requirements(self, input_file: str) -> int:
        """Predict space requirements before processing"""
        input_size = os.path.getsize(input_file)
        
        # Rough estimation: 3x input size for processing
        estimated_space = input_size * 3
        
        return estimated_space
```

### 13.2 GPU Hardware Acceleration Critical Points

#### 13.2.1 NVIDIA GPU Acceleration
```python
class NVIDIAAcceleration:
    def __init__(self):
        self.cuda_available = self.check_cuda_support()
        self.nvenc_supported = self.check_nvenc_support()
        self.gpu_memory = self.get_gpu_memory()
    
    def check_cuda_support(self) -> bool:
        """Check if CUDA is available and working"""
        try:
            cmd = ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader']
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0 and result.stdout.strip()
        except FileNotFoundError:
            return False
    
    def get_optimal_nvenc_settings(self, resolution: tuple, bitrate_mbps: int) -> list:
        """Get optimal NVENC encoding settings"""
        width, height = resolution
        
        # Adaptive settings based on resolution
        if height >= 2160:  # 4K
            preset = 'p2'    # Slower but better quality for 4K
            tune = 'hq'
        elif height >= 1440:  # 1440p  
            preset = 'p4'    # Balanced
            tune = 'hq'
        else:  # 1080p and below
            preset = 'p6'    # Faster for lower resolutions
            tune = 'll'      # Low latency
        
        return [
            '-hwaccel', 'cuda',
            '-hwaccel_output_format', 'cuda',
            '-c:v', 'h264_nvenc',
            '-preset', preset,
            '-tune', tune,
            '-rc', 'vbr',
            '-cq', '21',
            '-b:v', f'{bitrate_mbps}M',
            '-maxrate', f'{bitrate_mbps * 1.5}M',
            '-bufsize', f'{bitrate_mbps * 2}M',
            '-spatial_aq', '1',
            '-temporal_aq', '1',
            '-rc-lookahead', '32'
        ]
    
    def handle_gpu_memory_overflow(self):
        """Handle GPU memory issues"""
        # Reduce CUDA memory usage
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Use single GPU
        
        # Enable GPU memory growth
        cmd_prefix = [
            '-hwaccel_device', '0',
            '-extra_hw_frames', '8'  # Limit hardware frame buffer
        ]
        return cmd_prefix
```

#### 13.2.2 Intel QuickSync Acceleration
```python
class IntelQuickSyncAcceleration:
    def __init__(self):
        self.qsv_available = self.check_qsv_support()
        self.supported_codecs = self.get_supported_codecs()
    
    def check_qsv_support(self) -> bool:
        """Check Intel QuickSync Video support"""
        try:
            # Test QSV encoding capability
            cmd = [
                'ffmpeg', '-hide_banner', '-f', 'lavfi', 
                '-i', 'testsrc=duration=1:size=320x240:rate=1',
                '-c:v', 'h264_qsv', '-f', 'null', '-'
            ]
            result = subprocess.run(cmd, capture_output=True, stderr=subprocess.DEVNULL)
            return result.returncode == 0
        except:
            return False
    
    def get_qsv_params(self, quality_preset: str) -> list:
        """Get Intel QSV encoding parameters"""
        presets = {
            'fast': ['-preset', 'veryfast', '-global_quality', '25'],
            'balanced': ['-preset', 'medium', '-global_quality', '23'], 
            'quality': ['-preset', 'slow', '-global_quality', '21']
        }
        
        base_params = [
            '-hwaccel', 'qsv',
            '-c:v', 'h264_qsv',
            '-look_ahead', '1',
            '-look_ahead_depth', '40'
        ]
        
        return base_params + presets.get(quality_preset, presets['balanced'])
```

### 13.3 Additional Performance Optimizations

#### 13.3.1 Smart Preview Generation
```python
class SmartPreviewGenerator:
    """
    Generate efficient previews without processing full video
    """
    def __init__(self):
        self.preview_resolution = (640, 360)  # 360p for preview
        self.preview_fps = 15
        self.keyframe_interval = 30  # Extract keyframes for scrubbing
    
    def generate_smart_preview(self, video_path: str) -> str:
        """Generate lightweight preview for timeline scrubbing"""
        preview_path = self.temp_manager.get_temp_file('_preview.mp4')
        
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vf', f'scale={self.preview_resolution[0]}:{self.preview_resolution[1]}',
            '-r', str(self.preview_fps),
            '-c:v', 'libx264', '-preset', 'ultrafast',
            '-crf', '28',  # Lower quality for preview
            '-an',  # No audio needed for preview
            preview_path
        ]
        
        subprocess.run(cmd, check=True)
        return preview_path
    
    def extract_keyframes(self, video_path: str) -> list:
        """Extract keyframes for instant seeking"""
        keyframes_dir = self.temp_manager.get_temp_dir('keyframes')
        
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vf', 'select=eq(pict_type\\,I)',
            '-fps_mode', 'vfr',
            f'{keyframes_dir}/keyframe_%04d.jpg'
        ]
        
        subprocess.run(cmd, check=True)
        return sorted(os.listdir(keyframes_dir))
```

#### 13.3.2 Intelligent File Format Detection
```python
class FileFormatOptimizer:
    """
    Optimize processing based on input file format
    """
    def __init__(self):
        self.fast_formats = ['mp4', 'mov', 'avi']
        self.slow_formats = ['mkv', 'webm', 'flv']
        self.needs_conversion = ['wmv', 'asf', 'rm', 'rmvb']
    
    def analyze_input_format(self, video_path: str) -> dict:
        """Analyze input file and determine optimal processing strategy"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        
        video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
        
        return {
            'container': info['format']['format_name'],
            'video_codec': video_stream['codec_name'] if video_stream else None,
            'needs_conversion': self.requires_conversion(video_path),
            'hardware_decodable': self.supports_hardware_decode(video_stream),
            'processing_complexity': self.estimate_complexity(info)
        }
    
    def get_optimal_processing_strategy(self, file_info: dict) -> dict:
        """Return optimal processing parameters based on file analysis"""
        if file_info['needs_conversion']:
            return {
                'preprocess': True,
                'conversion_params': ['-c:v', 'libx264', '-preset', 'fast'],
                'processing_mode': 'convert_first'
            }
        elif file_info['hardware_decodable']:
            return {
                'preprocess': False,
                'decode_params': ['-hwaccel', 'auto'],
                'processing_mode': 'direct_hw'
            }
        else:
            return {
                'preprocess': False,
                'decode_params': ['-threads', str(os.cpu_count())],
                'processing_mode': 'direct_sw'
            }
```

---

## 14. ADDITIONAL CRITICAL OPTIMIZATIONS

### 14.1 Real-Time Performance Monitoring
```python
class PerformanceMonitor:
    """
    Real-time performance monitoring and automatic optimization
    """
    def __init__(self):
        self.metrics_history = []
        self.performance_thresholds = {
            'fps_drop_threshold': 0.8,  # Alert if FPS drops below 80%
            'memory_warning': 75,       # Warning at 75% memory usage
            'cpu_warning': 85,          # Warning at 85% CPU usage
            'processing_timeout': 300   # 5 minutes per operation max
        }
    
    def monitor_processing_performance(self, operation_name: str):
        """Monitor performance during processing operations"""
        start_time = time.time()
        start_memory = psutil.virtual_memory().percent
        
        while self.is_processing_active(operation_name):
            current_metrics = {
                'timestamp': time.time(),
                'memory_percent': psutil.virtual_memory().percent,
                'cpu_percent': psutil.cpu_percent(interval=1),
                'disk_io': psutil.disk_io_counters(),
                'network_io': psutil.net_io_counters(),
                'elapsed_time': time.time() - start_time
            }
            
            # Check for performance issues
            self.check_performance_issues(current_metrics, operation_name)
            
            # Auto-optimize if needed
            if self.should_auto_optimize(current_metrics):
                self.apply_auto_optimization(current_metrics)
            
            self.metrics_history.append(current_metrics)
            time.sleep(2)  # Monitor every 2 seconds
    
    def apply_auto_optimization(self, metrics: dict):
        """Automatically apply optimizations based on current performance"""
        if metrics['memory_percent'] > self.performance_thresholds['memory_warning']:
            # Reduce memory usage
            self.reduce_cache_size()
            self.enable_streaming_mode()
            
        if metrics['cpu_percent'] > self.performance_thresholds['cpu_warning']:
            # Reduce CPU load
            self.reduce_thread_count()
            self.lower_processing_quality()
            
        # Adaptive bitrate based on system performance
        if metrics['memory_percent'] > 80 or metrics['cpu_percent'] > 90:
            self.emergency_mode_activate()
```

### 14.2 Advanced Error Recovery System
```python
class AdvancedErrorRecovery:
    """
    Comprehensive error recovery with multiple fallback strategies
    """
    def __init__(self):
        self.recovery_strategies = [
            'retry_with_lower_quality',
            'retry_with_software_encoding',
            'split_processing_into_chunks',
            'emergency_basic_processing'
        ]
        self.max_retry_attempts = 3
        
    def execute_with_recovery(self, operation_func, *args, **kwargs):
        """Execute operation with comprehensive error recovery"""
        last_exception = None
        
        for strategy in self.recovery_strategies:
            for attempt in range(self.max_retry_attempts):
                try:
                    # Apply current recovery strategy
                    modified_kwargs = self.apply_recovery_strategy(strategy, kwargs)
                    
                    # Execute operation
                    result = operation_func(*args, **modified_kwargs)
                    
                    # Success - log recovery info if strategies were used
                    if strategy != self.recovery_strategies[0] or attempt > 0:
                        self.log_recovery_success(strategy, attempt)
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    self.log_recovery_attempt(strategy, attempt, e)
                    
                    # Wait before retry (exponential backoff)
                    if attempt < self.max_retry_attempts - 1:
                        time.sleep(2 ** attempt)
        
        # All recovery strategies failed
        raise ProcessingFailureError(
            f"All recovery strategies exhausted. Last error: {last_exception}"
        )
    
    def apply_recovery_strategy(self, strategy: str, kwargs: dict) -> dict:
        """Apply specific recovery strategy modifications"""
        recovery_modifications = {
            'retry_with_lower_quality': {
                'quality_preset': 'ultrafast',
                'resolution_scale': 0.5,
                'bitrate_reduction': 0.7
            },
            'retry_with_software_encoding': {
                'disable_hardware_acceleration': True,
                'codec': 'libx264',
                'preset': 'fast'
            },
            'split_processing_into_chunks': {
                'enable_chunked_processing': True,
                'chunk_duration': 60,  # 1 minute chunks
                'parallel_chunks': False
            },
            'emergency_basic_processing': {
                'disable_all_effects': True,
                'basic_encoding_only': True,
                'quality_preset': 'ultrafast'
            }
        }
        
        modified_kwargs = kwargs.copy()
        if strategy in recovery_modifications:
            modified_kwargs.update(recovery_modifications[strategy])
        
        return modified_kwargs
```

### 14.3 Smart Resource Allocation
```python
class SmartResourceAllocator:
    """
    Intelligently allocate system resources based on current workload
    """
    def __init__(self):
        self.resource_pools = {
            'cpu_intensive': ThreadPoolExecutor(max_workers=os.cpu_count()),
            'io_intensive': ThreadPoolExecutor(max_workers=4),
            'memory_intensive': ThreadPoolExecutor(max_workers=2)
        }
        self.current_allocations = {}
        
    def allocate_resources(self, task_type: str, estimated_duration: int) -> dict:
        """Allocate optimal resources for specific task types"""
        system_load = self.assess_system_load()
        
        allocation_strategies = {
            'video_encoding': {
                'cpu_priority': 'high',
                'memory_requirement': 'medium',
                'io_requirement': 'low',
                'gpu_acceleration': True
            },
            'scene_detection': {
                'cpu_priority': 'medium', 
                'memory_requirement': 'high',
                'io_requirement': 'medium',
                'gpu_acceleration': False
            },
            'audio_analysis': {
                'cpu_priority': 'medium',
                'memory_requirement': 'low',
                'io_requirement': 'high',
                'gpu_acceleration': False
            },
            'file_download': {
                'cpu_priority': 'low',
                'memory_requirement': 'low', 
                'io_requirement': 'high',
                'gpu_acceleration': False
            }
        }
        
        strategy = allocation_strategies.get(task_type, allocation_strategies['video_encoding'])
        
        # Adjust allocation based on current system load
        if system_load['memory_percent'] > 80:
            strategy['memory_requirement'] = 'low'
            
        if system_load['cpu_percent'] > 85:
            strategy['cpu_priority'] = 'low'
            
        return self.calculate_optimal_allocation(strategy, estimated_duration)
    
    def dynamic_reallocation(self):
        """Dynamically reallocate resources based on changing conditions"""
        while self.processing_active:
            current_load = self.assess_system_load()
            
            # Reallocate if system is under stress
            if current_load['memory_percent'] > 85 or current_load['cpu_percent'] > 90:
                self.emergency_reallocation()
            elif current_load['memory_percent'] < 50 and current_load['cpu_percent'] < 60:
                self.optimize_for_performance()
                
            time.sleep(10)  # Check every 10 seconds
```

### 14.4 Intelligent Preview System
```python
class IntelligentPreviewSystem:
    """
    Smart preview system that adapts to user behavior and system performance
    """
    def __init__(self):
        self.preview_cache = {}
        self.user_behavior_tracker = UserBehaviorTracker()
        self.adaptive_quality = True
        
    def generate_adaptive_preview(self, video_path: str, user_context: dict) -> str:
        """Generate preview adapted to user behavior and system performance"""
        
        # Analyze user behavior patterns
        behavior_analysis = self.user_behavior_tracker.analyze_patterns()
        
        # Determine optimal preview settings
        if behavior_analysis['frequent_scrubbing']:
            # User scrubs frequently - generate high-quality keyframes
            preview_settings = {
                'keyframe_density': 'high',
                'resolution': (854, 480),  # 480p
                'quality': 'medium'
            }
        elif behavior_analysis['mostly_playback']:
            # User mainly plays - optimize for smooth playback
            preview_settings = {
                'keyframe_density': 'low',
                'resolution': (640, 360),  # 360p
                'quality': 'fast'
            }
        else:
            # Balanced approach
            preview_settings = {
                'keyframe_density': 'medium',
                'resolution': (720, 405),  # 405p
                'quality': 'balanced'
            }
        
        # Adjust based on system performance
        system_performance = self.assess_preview_performance()
        if system_performance['can_handle_hq']:
            preview_settings['quality'] = 'high'
        elif system_performance['struggling']:
            preview_settings['resolution'] = (480, 270)  # Lower resolution
            preview_settings['quality'] = 'fast'
        
        return self.generate_optimized_preview(video_path, preview_settings)
    
    def intelligent_caching_strategy(self, video_path: str):
        """Implement intelligent caching based on predicted user needs"""
        
        # Predict which parts of video user is likely to access
        predicted_regions = self.predict_user_interest_regions(video_path)
        
        # Pre-cache high-interest regions
        for region in predicted_regions:
            cache_key = f"{video_path}_{region['start']}_{region['end']}"
            if cache_key not in self.preview_cache:
                self.pre_cache_region(video_path, region)
```

### 14.5 Final Performance Recommendations

```python
"""
CRITICAL PERFORMANCE RECOMMENDATIONS:

1. HARDWARE ACCELERATION PRIORITY:
   - NVIDIA GPU: Up to 10x faster encoding
   - Intel QuickSync: 3-5x faster, lower power
   - AMD VCE: 3-4x faster encoding
   - Apple VideoToolbox: Optimized for M1/M2

2. MEMORY MANAGEMENT:
   - Use streaming processing for files >2GB
   - Implement aggressive garbage collection
   - Monitor memory usage continuously
   - Emergency cleanup procedures

3. DISK I/O OPTIMIZATION:
   - Use SSD for temporary files if available
   - Implement disk space monitoring
   - Compress intermediate files when possible
   - Predict space requirements

4. CPU OPTIMIZATION:
   - Dynamic thread allocation based on system load
   - Process priority management
   - Avoid blocking main UI thread
   - Implement operation timeouts

5. NETWORK OPTIMIZATION (for URL downloads):
   - Concurrent downloads with connection pooling
   - Resume capability for interrupted downloads
   - Bandwidth throttling to prevent system overload
   - Smart retry with exponential backoff

6. USER EXPERIENCE:
   - Real-time progress reporting
   - Cancellation capability for all operations
   - Preview generation without full processing
   - Responsive UI during heavy operations
"""
```

---

## 15. FINAL DEPLOYMENT CHECKLIST

### 15.1 Pre-Release Testing Checklist
- [ ] **Memory leak testing** with 4-hour continuous operation
- [ ] **Large file handling** (test with 8GB+ files)
- [ ] **Hardware acceleration** on NVIDIA, Intel, AMD systems
- [ ] **Error recovery** with corrupted/invalid files
- [ ] **Disk space crisis** simulation and recovery
- [ ] **Network interruption** during URL downloads
- [ ] **System resource exhaustion** scenarios
- [ ] **Cross-platform compatibility** (Windows 10/11, different hardware)

### 15.2 Performance Benchmarks
- [ ] **Encoding speed**: Target 2x real-time for 1080p
- [ ] **Memory usage**: Max 4GB for 1-hour 1080p video
- [ ] **Startup time**: < 5 seconds cold start
- [ ] **Preview generation**: < 3 seconds for any video
- [ ] **Scene detection**: < 30 seconds for 1-hour video
- [ ] **UI responsiveness**: < 100ms for all interactions

---

*Critical Performance Documentation - Version 1.1*
*Hardware Acceleration & Resource Management Added*
*Ready for High-Performance Implementation*# FFmpeg Video Editor - Development Documentation

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