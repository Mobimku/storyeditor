# core/temp_manager.py
"""
CRITICAL MODULE - Must be implemented first
All other modules depend on this
"""

import tempfile
import shutil
import os
import atexit
import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

class TempManager:
    """
    PRIORITY: HIGHEST
    Manages all temporary files and cleanup
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.temp_dir: Optional[str] = None
        self.temp_files: List[str] = []
        self.cleanup_on_exit: bool = True
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Register cleanup on exit
        atexit.register(self.cleanup_all)
        
        # Initialize with config values
        self.max_temp_files = self.config.get('max_temp_files', 100)
        self.temp_dir_prefix = self.config.get('temp_dir_prefix', 'ffmpeg_editor_')
        self.cleanup_on_exit = self.config.get('cleanup_on_exit', True)
        
        self.logger.info("TempManager initialized")
    
    def create_temp_dir(self) -> str:
        """Create main temporary directory"""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix=self.temp_dir_prefix)
            self.logger.info(f"Created temp directory: {self.temp_dir}")
        return self.temp_dir
    
    def get_temp_file(self, suffix: str = '.mp4') -> str:
        """Generate unique temp file path"""
        if not self.temp_dir:
            self.create_temp_dir()
        
        # Check if we have too many temp files
        if len(self.temp_files) >= self.max_temp_files:
            self.logger.warning(f"Too many temp files ({len(self.temp_files)}), forcing cleanup")
            self.cleanup_old_files()
        
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
        if not self.cleanup_on_exit:
            self.logger.info("Cleanup on exit disabled, skipping")
            return
            
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
                    if temp_file in self.temp_files:
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
    
    def cleanup_old_files(self):
        """Clean oldest temp files when limit is reached"""
        if len(self.temp_files) < self.max_temp_files:
            return
            
        # Sort files by modification time (oldest first)
        sorted_files = sorted(
            [f for f in self.temp_files if os.path.exists(f)],
            key=lambda x: os.path.getmtime(x)
        )
        
        # Remove oldest 20% of files
        files_to_remove = sorted_files[:max(1, len(sorted_files) // 5)]
        
        for file_path in files_to_remove:
            try:
                os.remove(file_path)
                self.temp_files.remove(file_path)
                self.logger.debug(f"Removed old temp file: {file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to remove old temp file {file_path}: {e}")
    
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
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get current disk usage info"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            total_size = 0
            file_count = 0
            
            for dirpath, dirnames, filenames in os.walk(self.temp_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                        file_count += 1
                    except OSError:
                        continue
            
            return {
                'temp_dir_size_mb': total_size / (1024 * 1024),
                'temp_file_count': file_count,
                'temp_dir_path': self.temp_dir,
                'registered_files': len(self.temp_files)
            }
        
        return {'temp_dir_size_mb': 0, 'temp_file_count': 0, 'temp_dir_path': None}
    
    def check_disk_space(self, min_free_space_gb: float = 5.0) -> bool:
        """Check if there's enough disk space"""
        try:
            stat = shutil.disk_usage(self.temp_dir or tempfile.gettempdir())
            free_gb = stat.free / (1024 ** 3)
            return free_gb >= min_free_space_gb
        except Exception:
            return True  # Assume OK if we can't check
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        if hasattr(self, 'cleanup_on_exit') and self.cleanup_on_exit:
            try:
                self.cleanup_all()
            except:
                pass  # Ignore errors during cleanup

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