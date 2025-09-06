# utils/url_downloader.py
"""
URL downloader for various video platforms
Depends on: temp_manager.py
"""

import os
import logging
import threading
from typing import List, Dict, Any, Optional, Callable

from core.temp_manager import TempManager

# Import yt_dlp secara opsional
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    print("Warning: yt-dlp not available. URL download functionality will be disabled.")

class URLDownloader:
    """
    Downloads videos from various platforms using yt-dlp
    """
    
    def __init__(self, temp_manager: TempManager, config: Dict[str, Any] = None):
        self.temp_manager = temp_manager
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Supported platforms
        self.supported_platforms = self.config.get('supported_platforms', [
            'youtube', 'vimeo', 'twitter', 'instagram', 
            'tiktok', 'direct', 'gdrive', 'dropbox'
        ])
        
        # Download options
        self.default_quality = self.config.get('default_video_quality', '720p')
        
        # Check if yt-dlp is available
        if not YTDLP_AVAILABLE:
            self.logger.warning("yt-dlp not available. URL download functionality disabled.")
        
        # yt-dlp options (hanya jika tersedia)
        if YTDLP_AVAILABLE:
            self.ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': os.path.join(temp_manager.temp_dir or '', '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [],
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
        
        self.logger.info("URLDownloader initialized")
    
    def is_available(self) -> bool:
        """Check if yt-dlp is available"""
        return YTDLP_AVAILABLE
    
    def detect_platform(self, url: str) -> str:
        """
        Auto-detect video platform from URL
        
        Args:
            url: Video URL
            
        Returns:
            Platform name or 'unknown'
        """
        url_lower = url.lower()
        
        platform_patterns = {
            'youtube': ['youtube.com', 'youtu.be'],
            'vimeo': ['vimeo.com'],
            'twitter': ['twitter.com', 'x.com'],
            'instagram': ['instagram.com'],
            'tiktok': ['tiktok.com'],
            'gdrive': ['drive.google.com'],
            'dropbox': ['dropbox.com/s/'],
        }
        
        for platform, patterns in platform_patterns.items():
            for pattern in patterns:
                if pattern in url_lower:
                    self.logger.info(f"Detected platform: {platform}")
                    return platform
        
        # Check if direct URL
        if url_lower.startswith(('http://', 'https://')):
            return 'direct'
        
        return 'unknown'
    
    def validate_url(self, url: str) -> bool:
        """
        Validate URL accessibility
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid and accessible
        """
        if not YTDLP_AVAILABLE:
            self.logger.warning("yt-dlp not available, cannot validate URL")
            return False
        
        try:
            # Quick validation with yt-dlp
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    return info is not None
                except Exception as e:
                    self.logger.warning(f"URL validation failed: {e}")
                    return False
        except Exception as e:
            self.logger.error(f"URL validation error: {e}")
            return False
    
    def download_video(self, url: str, quality: str = None, 
                      progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict[str, Any]:
        """
        Download video from URL
        
        Args:
            url: Video URL
            quality: Video quality (e.g., '720p', '1080p')
            progress_callback: Optional progress callback (progress, status)
            
        Returns:
            Dictionary with download information
        """
        if not YTDLP_AVAILABLE:
            raise RuntimeError("yt-dlp not available. Cannot download videos.")
        
        platform = self.detect_platform(url)
        if platform == 'unknown':
            raise ValueError(f"Unsupported URL: {url}")
        
        if not self.validate_url(url):
            raise ValueError(f"Invalid or inaccessible URL: {url}")
        
        # Set quality
        quality = quality or self.default_quality
        
        # Configure yt-dlp options
        ydl_opts = self.ydl_opts.copy()
        
        # Set format based on quality
        if quality == '1080p':
            ydl_opts['format'] = 'best[height<=1080][ext=mp4]/best[height<=1080]/best[ext=mp4]/best'
        elif quality == '720p':
            ydl_opts['format'] = 'best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best'
        elif quality == '480p':
            ydl_opts['format'] = 'best[height<=480][ext=mp4]/best[height<=480]/best[ext=mp4]/best'
        elif quality == '360p':
            ydl_opts['format'] = 'best[height<=360][ext=mp4]/best[height<=360]/best[ext=mp4]/best'
        
        # Set output template
        output_path = self.temp_manager.get_temp_file('.%(ext)s')
        ydl_opts['outtmpl'] = output_path
        
        # Add progress hook
        if progress_callback:
            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', '0%').replace('%', '')
                    try:
                        progress = float(percent)
                        speed = d.get('_speed_str', 'N/A')
                        eta = d.get('_eta_str', 'N/A')
                        status = f"Downloading: {progress:.1f}% - Speed: {speed} - ETA: {eta}"
                        progress_callback(progress, status)
                    except ValueError:
                        progress_callback(0, "Starting download...")
                elif d['status'] == 'finished':
                    progress_callback(100.0, "Download completed")
                elif d['status'] == 'error':
                    progress_callback(0, "Download error")
            
            ydl_opts['progress_hooks'] = [progress_hook]
        
        try:
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get downloaded file path
                downloaded_file = ydl.prepare_filename(info)
                if not os.path.exists(downloaded_file):
                    # Try to find the actual file
                    base_name = os.path.splitext(downloaded_file)[0]
                    for ext in ['.mp4', '.webm', '.mkv']:
                        test_file = base_name + ext
                        if os.path.exists(test_file):
                            downloaded_file = test_file
                            break
                
                # Register file for cleanup
                self.temp_manager.register_temp_file(downloaded_file)
                
                # Get video info
                video_info = {
                    'platform': platform,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'description': info.get('description', ''),
                    'tags': info.get('tags', []),
                    'thumbnail': info.get('thumbnail', ''),
                    'filepath': downloaded_file,
                    'url': url,
                    'quality': quality
                }
                
                self.logger.info(f"Downloaded video: {video_info['title']} ({video_info['duration']}s)")
                return video_info
                
        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            raise RuntimeError(f"Failed to download video: {e}")
    
    def download_playlist(self, url: str, max_videos: int = 10, quality: str = None,
                          progress_callback: Optional[Callable[[float, str], None]] = None) -> List[Dict[str, Any]]:
        """
        Download multiple videos from playlist
        
        Args:
            url: Playlist URL
            max_videos: Maximum number of videos to download
            quality: Video quality
            progress_callback: Optional progress callback
            
        Returns:
            List of video information dictionaries
        """
        if not YTDLP_AVAILABLE:
            raise RuntimeError("yt-dlp not available. Cannot download playlists.")
        
        platform = self.detect_platform(url)
        if platform == 'unknown':
            raise ValueError(f"Unsupported URL: {url}")
        
        quality = quality or self.default_quality
        
        # Configure yt-dlp options for playlist
        ydl_opts = self.ydl_opts.copy()
        ydl_opts['playlistend'] = max_videos
        ydl_opts['noplaylist'] = False
        
        # Set format based on quality
        if quality == '1080p':
            ydl_opts['format'] = 'best[height<=1080][ext=mp4]/best[height<=1080]/best[ext=mp4]/best'
        elif quality == '720p':
            ydl_opts['format'] = 'best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best'
        elif quality == '480p':
            ydl_opts['format'] = 'best[height<=480][ext=mp4]/best[height<=480]/best[ext=mp4]/best'
        elif quality == '360p':
            ydl_opts['format'] = 'best[height<=360][ext=mp4]/best[height<=360]/best[ext=mp4]/best'
        
        downloaded_videos = []
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' not in info:
                    # Single video, not a playlist
                    video_info = self.download_video(url, quality, progress_callback)
                    return [video_info]
                
                # Process playlist
                total_videos = min(len(info['entries']), max_videos)
                for i, entry in enumerate(info['entries'][:max_videos]):
                    if entry is None:
                        continue
                    
                    try:
                        video_url = entry.get('url') or entry.get('webpage_url')
                        if video_url:
                            video_info = self.download_video(video_url, quality, progress_callback)
                            downloaded_videos.append(video_info)
                            
                            if progress_callback:
                                overall_progress = ((i + 1) / total_videos) * 100
                                progress_callback(overall_progress, f"Downloaded {i + 1}/{total_videos} videos")
                    
                    except Exception as e:
                        self.logger.warning(f"Failed to download video {i+1}: {e}")
                        continue
                
                self.logger.info(f"Downloaded {len(downloaded_videos)} videos from playlist")
                return downloaded_videos
                
        except Exception as e:
            self.logger.error(f"Playlist download failed: {e}")
            raise RuntimeError(f"Failed to download playlist: {e}")
    
    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """
        Get available video formats for URL
        
        Args:
            url: Video URL
            
        Returns:
            List of format information
        """
        if not YTDLP_AVAILABLE:
            self.logger.warning("yt-dlp not available, cannot get formats")
            return []
        
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'listformats': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                formats = []
                if 'formats' in info:
                    for fmt in info['formats']:
                        if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                            formats.append({
                                'format_id': fmt.get('format_id'),
                                'ext': fmt.get('ext'),
                                'resolution': fmt.get('resolution'),
                                'fps': fmt.get('fps'),
                                'filesize': fmt.get('filesize'),
                                'vcodec': fmt.get('vcodec'),
                                'acodec': fmt.get('acodec'),
                                'format_note': fmt.get('format_note')
                            })
                
                return formats
                
        except Exception as e:
            self.logger.error(f"Failed to get formats: {e}")
            return []
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get video information without downloading
        
        Args:
            url: Video URL
            
        Returns:
            Video information dictionary or None
        """
        if not YTDLP_AVAILABLE:
            self.logger.warning("yt-dlp not available, cannot get video info")
            return None
        
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'platform': self.detect_platform(url),
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', 'Unknown'),
                    'description': info.get('description', ''),
                    'tags': info.get('tags', []),
                    'thumbnail': info.get('thumbnail', ''),
                    'url': url
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get video info: {e}")
            return None
    
    def is_supported_platform(self, platform: str) -> bool:
        """
        Check if platform is supported
        
        Args:
            platform: Platform name
            
        Returns:
            True if platform is supported
        """
        return platform.lower() in [p.lower() for p in self.supported_platforms]
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return self.supported_platforms.copy()

# Test the url_downloader
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    from temp_manager import TempManager
    
    # Test URL downloader
    temp_mgr = TempManager()
    downloader = URLDownloader(temp_mgr)
    
    # Check if yt-dlp is available
    print(f"yt-dlp available: {downloader.is_available()}")
    
    # Test platform detection
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://vimeo.com/148751763",
        "https://twitter.com/username/status/123456789",
        "https://www.instagram.com/p/ABC123/",
        "https://www.tiktok.com/@username/video/123456789"
    ]
    
    for url in test_urls:
        platform = downloader.detect_platform(url)
        print(f"URL: {url}")
        print(f"Platform: {platform}")
        print(f"Supported: {downloader.is_supported_platform(platform)}")
        print("---")
    
    # Test supported platforms
    print(f"Supported platforms: {downloader.get_supported_platforms()}")
    
    print("URL downloader test completed")