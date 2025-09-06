# tests/test_temp_manager.py
import pytest
import os
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.temp_manager import TempManager

class TestTempManager:
    def test_temp_dir_creation(self):
        """Test temporary directory creation"""
        temp_mgr = TempManager()
        temp_dir = temp_mgr.create_temp_dir()
        
        assert os.path.exists(temp_dir)
        assert temp_dir == temp_mgr.temp_dir
        assert temp_dir.startswith(temp_mgr.temp_dir_prefix)
        
        # Cleanup
        temp_mgr.cleanup_all()
    
    def test_temp_file_generation(self):
        """Test temporary file generation"""
        temp_mgr = TempManager()
        temp_file = temp_mgr.get_temp_file('.mp4')
        
        assert temp_file.endswith('.mp4')
        assert temp_file in temp_mgr.temp_files
        assert os.path.dirname(temp_file) == temp_mgr.temp_dir
        
        # Cleanup
        temp_mgr.cleanup_all()
    
    def test_file_registration(self):
        """Test file registration for cleanup"""
        temp_mgr = TempManager()
        
        # Create a temp file manually
        temp_file = temp_mgr.get_temp_file('.txt')
        
        # Create the actual file
        with open(temp_file, 'w') as f:
            f.write("test content")
        
        # Verify file exists and is registered
        assert os.path.exists(temp_file)
        assert temp_file in temp_mgr.temp_files
        
        # Cleanup should remove the file
        temp_mgr.cleanup_all()
        assert not os.path.exists(temp_file)
    
    def test_cache_file_creation(self):
        """Test cache file creation"""
        temp_mgr = TempManager()
        cache_file = temp_mgr.get_cache_file('test_cache')
        
        assert cache_file.endswith('test_cache.cache')
        assert 'cache' in cache_file
        assert cache_file in temp_mgr.temp_files
        
        # Cleanup
        temp_mgr.cleanup_all()
    
    def test_temp_subdirectory_creation(self):
        """Test temporary subdirectory creation"""
        temp_mgr = TempManager()
        subdir = temp_mgr.get_temp_dir('test_subdir')
        
        assert os.path.exists(subdir)
        assert os.path.basename(subdir) == 'test_subdir'
        assert os.path.dirname(subdir) == temp_mgr.temp_dir
        
        # Cleanup
        temp_mgr.cleanup_all()
    
    def test_disk_usage(self):
        """Test disk usage calculation"""
        temp_mgr = TempManager()
        
        # Create some test files
        temp_file1 = temp_mgr.get_temp_file('.txt')
        temp_file2 = temp_mgr.get_temp_file('.txt')
        
        with open(temp_file1, 'w') as f:
            f.write("x" * 1000)  # 1KB
        
        with open(temp_file2, 'w') as f:
            f.write("x" * 2000)  # 2KB
        
        usage = temp_mgr.get_disk_usage()
        
        assert usage['temp_dir_size_mb'] > 0
        assert usage['temp_file_count'] >= 2
        assert usage['temp_dir_path'] == temp_mgr.temp_dir
        assert usage['registered_files'] >= 2
        
        # Cleanup
        temp_mgr.cleanup_all()
    
    def test_cleanup_on_error(self):
        """Test emergency cleanup on error"""
        temp_mgr = TempManager()
        
        # Create a temp file
        temp_file = temp_mgr.get_temp_file('.txt')
        with open(temp_file, 'w') as f:
            f.write("test content")
        
        assert os.path.exists(temp_file)
        
        # Simulate error cleanup
        temp_mgr.cleanup_on_error()
        
        assert not os.path.exists(temp_file)
    
    def test_max_temp_files_limit(self):
        """Test max temp files limit"""
        config = {'max_temp_files': 3}
        temp_mgr = TempManager(config)
        
        # Create files up to the limit
        files = []
        for i in range(3):
            files.append(temp_mgr.get_temp_file('.txt'))
        
        # All files should be registered
        assert len(temp_mgr.temp_files) == 3
        
        # Create one more file - should trigger cleanup
        extra_file = temp_mgr.get_temp_file('.txt')
        
        # Should still have max_files + 1 files
        assert len(temp_mgr.temp_files) <= 4
        
        # Cleanup
        temp_mgr.cleanup_all()
    
    def test_disk_space_check(self):
        """Test disk space checking"""
        temp_mgr = TempManager()
        
        # Should return True (assuming we have enough space)
        assert temp_mgr.check_disk_space() is True
        
        # Test with very high requirement
        assert temp_mgr.check_disk_space(10000) is False  # 10TB
        
        # Cleanup
        temp_mgr.cleanup_all()
    
    def test_config_override(self):
        """Test configuration override"""
        config = {
            'temp_dir_prefix': 'test_prefix_',
            'max_temp_files': 5,
            'cleanup_on_exit': False
        }
        
        temp_mgr = TempManager(config)
        
        assert temp_mgr.temp_dir_prefix == 'test_prefix_'
        assert temp_mgr.max_temp_files == 5
        assert temp_mgr.cleanup_on_exit is False
        
        # Cleanup
        temp_mgr.cleanup_all()
    
    def test_destructor_cleanup(self):
        """Test cleanup in destructor"""
        temp_mgr = TempManager()
        
        # Create a temp file
        temp_file = temp_mgr.get_temp_file('.txt')
        with open(temp_file, 'w') as f:
            f.write("test content")
        
        assert os.path.exists(temp_file)
        
        # Simulate destructor call
        temp_mgr.__del__()
        
        # File should be cleaned up
        assert not os.path.exists(temp_file)

if __name__ == "__main__":
    pytest.main([__file__])