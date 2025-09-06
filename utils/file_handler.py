# utils/file_handler.py
"""
File I/O operations utility
"""

import os
import shutil
import json
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

class FileHandler:
    """
    Handles file I/O operations
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Supported video formats
        self.video_formats = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        
        # Supported audio formats
        self.audio_formats = {'.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'}
        
        # Supported image formats
        self.image_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        
        self.logger.info("FileHandler initialized")
    
    def ensure_directory(self, directory: str) -> bool:
        """
        Ensure directory exists, create if necessary
        
        Args:
            directory: Directory path
            
        Returns:
            True if directory exists or was created
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create directory {directory}: {e}")
            return False
    
    def get_file_size(self, filepath: str) -> int:
        """
        Get file size in bytes
        
        Args:
            filepath: File path
            
        Returns:
            File size in bytes, or 0 if file doesn't exist
        """
        try:
            return os.path.getsize(filepath)
        except OSError:
            return 0
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """
        Get comprehensive file information
        
        Args:
            filepath: File path
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = os.stat(filepath)
            path_obj = Path(filepath)
            
            return {
                'name': path_obj.name,
                'stem': path_obj.stem,
                'suffix': path_obj.suffix,
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'is_video': path_obj.suffix.lower() in self.video_formats,
                'is_audio': path_obj.suffix.lower() in self.audio_formats,
                'is_image': path_obj.suffix.lower() in self.image_formats,
                'exists': True
            }
        except OSError:
            return {
                'name': os.path.basename(filepath),
                'stem': '',
                'suffix': '',
                'size': 0,
                'size_mb': 0,
                'created_time': 0,
                'modified_time': 0,
                'is_video': False,
                'is_audio': False,
                'is_image': False,
                'exists': False
            }
    
    def copy_file(self, src: str, dst: str, overwrite: bool = False) -> bool:
        """
        Copy file from source to destination
        
        Args:
            src: Source file path
            dst: Destination file path
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if copy successful
        """
        try:
            if os.path.exists(dst) and not overwrite:
                self.logger.warning(f"Destination file exists: {dst}")
                return False
            
            shutil.copy2(src, dst)
            self.logger.info(f"Copied file: {src} -> {dst}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to copy file {src} to {dst}: {e}")
            return False
    
    def move_file(self, src: str, dst: str, overwrite: bool = False) -> bool:
        """
        Move file from source to destination
        
        Args:
            src: Source file path
            dst: Destination file path
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if move successful
        """
        try:
            if os.path.exists(dst) and not overwrite:
                self.logger.warning(f"Destination file exists: {dst}")
                return False
            
            shutil.move(src, dst)
            self.logger.info(f"Moved file: {src} -> {dst}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to move file {src} to {dst}: {e}")
            return False
    
    def delete_file(self, filepath: str) -> bool:
        """
        Delete file
        
        Args:
            filepath: File path
            
        Returns:
            True if deletion successful
        """
        try:
            os.remove(filepath)
            self.logger.info(f"Deleted file: {filepath}")
            return True
        except OSError as e:
            self.logger.error(f"Failed to delete file {filepath}: {e}")
            return False
    
    def delete_directory(self, directory: str, recursive: bool = True) -> bool:
        """
        Delete directory
        
        Args:
            directory: Directory path
            recursive: Whether to delete recursively
            
        Returns:
            True if deletion successful
        """
        try:
            if recursive:
                shutil.rmtree(directory)
            else:
                os.rmdir(directory)
            self.logger.info(f"Deleted directory: {directory}")
            return True
        except OSError as e:
            self.logger.error(f"Failed to delete directory {directory}: {e}")
            return False
    
    def read_text_file(self, filepath: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read text file content
        
        Args:
            filepath: File path
            encoding: File encoding
            
        Returns:
            File content as string, or None if failed
        """
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to read text file {filepath}: {e}")
            return None
    
    def write_text_file(self, filepath: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        Write text file
        
        Args:
            filepath: File path
            content: Content to write
            encoding: File encoding
            
        Returns:
            True if write successful
        """
        try:
            # Ensure directory exists
            self.ensure_directory(os.path.dirname(filepath))
            
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(content)
            
            self.logger.info(f"Wrote text file: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write text file {filepath}: {e}")
            return False
    
    def read_json_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Read JSON file
        
        Args:
            filepath: File path
            
        Returns:
            JSON data as dictionary, or None if failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to read JSON file {filepath}: {e}")
            return None
    
    def write_json_file(self, filepath: str, data: Dict[str, Any], indent: int = 2) -> bool:
        """
        Write JSON file
        
        Args:
            filepath: File path
            data: Data to write
            indent: JSON indentation
            
        Returns:
            True if write successful
        """
        try:
            # Ensure directory exists
            self.ensure_directory(os.path.dirname(filepath))
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            self.logger.info(f"Wrote JSON file: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write JSON file {filepath}: {e}")
            return False
    
    def list_files(self, directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """
        List files in directory
        
        Args:
            directory: Directory path
            pattern: File pattern to match
            recursive: Whether to search recursively
            
        Returns:
            List of file paths
        """
        try:
            if recursive:
                return [str(p) for p in Path(directory).rglob(pattern) if p.is_file()]
            else:
                return [str(p) for p in Path(directory).glob(pattern) if p.is_file()]
        except Exception as e:
            self.logger.error(f"Failed to list files in {directory}: {e}")
            return []
    
    def find_files_by_extension(self, directory: str, extension: str, recursive: bool = False) -> List[str]:
        """
        Find files by extension
        
        Args:
            directory: Directory path
            extension: File extension (e.g., '.mp4')
            recursive: Whether to search recursively
            
        Returns:
            List of file paths
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        
        pattern = f"*{extension}"
        return self.list_files(directory, pattern, recursive)
    
    def get_unique_filename(self, filepath: str) -> str:
        """
        Get unique filename by adding number suffix if file exists
        
        Args:
            filepath: Original file path
            
        Returns:
            Unique file path
        """
        if not os.path.exists(filepath):
            return filepath
        
        path_obj = Path(filepath)
        stem = path_obj.stem
        suffix = path_obj.suffix
        parent = path_obj.parent
        
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            
            if not new_path.exists():
                return str(new_path)
            
            counter += 1
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing invalid characters
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Invalid characters for most file systems
        invalid_chars = '<>:"/\\|?*'
        
        # Replace invalid characters with underscore
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    def calculate_directory_size(self, directory: str) -> int:
        """
        Calculate total size of directory
        
        Args:
            directory: Directory path
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
        except OSError:
            pass
        
        return total_size
    
    def get_disk_usage(self, path: str = None) -> Dict[str, int]:
        """
        Get disk usage information
        
        Args:
            path: Path to check (uses current directory if None)
            
        Returns:
            Dictionary with disk usage info
        """
        try:
            if path is None:
                path = os.getcwd()
            
            usage = shutil.disk_usage(path)
            
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'total_gb': usage.total / (1024**3),
                'used_gb': usage.used / (1024**3),
                'free_gb': usage.free / (1024**3),
                'percent_used': (usage.used / usage.total) * 100
            }
        except Exception:
            return {
                'total': 0,
                'used': 0,
                'free': 0,
                'total_gb': 0,
                'used_gb': 0,
                'free_gb': 0,
                'percent_used': 0
            }
    
    def is_file_readable(self, filepath: str) -> bool:
        """
        Check if file is readable
        
        Args:
            filepath: File path
            
        Returns:
            True if file is readable
        """
        try:
            return os.access(filepath, os.R_OK)
        except OSError:
            return False
    
    def is_file_writable(self, filepath: str) -> bool:
        """
        Check if file is writable
        
        Args:
            filepath: File path
            
        Returns:
            True if file is writable
        """
        try:
            # If file doesn't exist, check if directory is writable
            if not os.path.exists(filepath):
                return os.access(os.path.dirname(filepath), os.W_OK)
            
            return os.access(filepath, os.W_OK)
        except OSError:
            return False

# Test the file_handler
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    # Test file handler
    file_handler = FileHandler()
    
    # Test file info
    test_file = __file__  # Use this file for testing
    info = file_handler.get_file_info(test_file)
    print(f"File info: {info}")
    
    # Test unique filename
    unique_name = file_handler.get_unique_filename("test.txt")
    print(f"Unique filename: {unique_name}")
    
    # Test sanitize filename
    sanitized = file_handler.sanitize_filename("file<>name?.txt")
    print(f"Sanitized filename: {sanitized}")
    
    # Test disk usage
    disk_usage = file_handler.get_disk_usage()
    print(f"Disk usage: {disk_usage['free_gb']:.2f} GB free")
    
    print("File handler test completed")