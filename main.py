# main.py
"""
FFmpeg Editor - Main Application Entry Point
"""

import tkinter as tk
import logging
import json
import os
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from gui.main_window import MainWindow
from core.temp_manager import TempManager

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ffmpeg_editor.log'),
            logging.StreamHandler()
        ]
    )

def load_config() -> dict:
    """Load application configuration"""
    config_path = 'config.json'
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
    
    # Return default config if file doesn't exist or fails to load
    return {
        "app_name": "FFmpeg Editor",
        "version": "1.0.0",
        "license_required": True,
        "temp_dir_prefix": "ffmpeg_editor_",
        "max_temp_files": 100,
        "cleanup_on_exit": True,
        "default_video_quality": "720p",
        "default_audio_threshold": -40.0,
        "min_scene_duration": 3.0,
        "max_cut_duration": 7.0,
        "min_cut_duration": 3.0,
        "panning_interval": 15,
        "supported_platforms": [
            "youtube", "vimeo", "twitter", "instagram", 
            "tiktok", "direct", "gdrive", "dropbox"
        ],
        "performance": {
            "max_memory_usage_mb": 2048,
            "preview_latency_ms": 100,
            "processing_timeout": 300,
            "max_workers": 4
        },
        "theme": {
            "name": "Purple Blackhole",
            "bg_primary": "#1a0d26",
            "bg_secondary": "#2d1b3d",
            "accent_primary": "#6b46c1",
            "accent_secondary": "#a855f7",
            "accent_tertiary": "#ec4899",
            "text_primary": "#f8fafc",
            "text_secondary": "#cbd5e1",
            "border": "#4c1d95",
            "hover": "#7c3aed",
            "success": "#10b981",
            "error": "#ef4444",
            "warning": "#f59e0b"
        }
    }

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import librosa
    except ImportError:
        missing_deps.append("librosa")
    
    try:
        import yt_dlp
    except ImportError:
        missing_deps.append("yt-dlp")
    
    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install missing dependencies with:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    import subprocess
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting FFmpeg Editor")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Missing dependencies. Please install required packages.")
        return
    
    # Check FFmpeg
    if not check_ffmpeg():
        logger.error("FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
        return
    
    # Load configuration
    config = load_config()
    logger.info(f"Loaded configuration: {config['app_name']} v{config['version']}")
    
    # Initialize temporary file manager
    temp_manager = TempManager(config)

    try:
        # Create and run main application
        app = MainWindow(config)
        app.run()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup temporary files
        logger.info("Cleaning up temporary files")
        temp_manager.cleanup_all()
        
        logger.info("Application exited")

if __name__ == "__main__":
    main()