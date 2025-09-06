# core/audio_processor.py
"""
Audio analysis and processing using librosa and FFmpeg
Depends on: temp_manager.py
"""

import librosa
import soundfile as sf
import numpy as np
import subprocess
import os
import logging
from typing import List, Tuple, Dict, Optional, Any, Callable

from .temp_manager import TempManager

class AudioProcessor:
    """
    Audio analysis and processing operations
    """
    
    def __init__(self, temp_manager: TempManager, config: Dict[str, Any] = None):
        self.temp_manager = temp_manager
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Default settings
        self.default_sample_rate = 22050
        self.default_threshold = self.config.get('default_audio_threshold', -40.0)
        
        self.logger.info("AudioProcessor initialized")
    
    def analyze_audio(self, audio_path: str, 
                     progress_callback: Optional[Callable[[float], None]] = None) -> Dict[str, Any]:
        """
        Analyze audio file for silent parts and other characteristics
        
        Args:
            audio_path: Path to audio file
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.default_sample_rate)
            
            if progress_callback:
                progress_callback(25.0)
            
            # Detect silent parts
            silent_parts = self._detect_silent_parts(y, sr, self.default_threshold)
            
            if progress_callback:
                progress_callback(50.0)
            
            # Calculate RMS energy
            rms = librosa.feature.rms(y=y)[0]
            
            if progress_callback:
                progress_callback(75.0)
            
            # Calculate spectral centroid
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # Calculate zero crossing rate
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            
            if progress_callback:
                progress_callback(100.0)
            
            analysis_result = {
                'duration': len(y) / sr,
                'sample_rate': sr,
                'silent_parts': silent_parts,
                'rms_energy': float(np.mean(rms)),
                'spectral_centroid': float(np.mean(spectral_centroid)),
                'zero_crossing_rate': float(np.mean(zero_crossing_rate)),
                'max_amplitude': float(np.max(np.abs(y)))
            }
            
            self.logger.info(f"Audio analysis completed: {analysis_result['duration']:.2f}s")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Audio analysis failed: {e}")
            raise RuntimeError(f"Audio analysis failed: {e}")
    
    def _detect_silent_parts(self, y: np.ndarray, sr: int, threshold_db: float) -> List[Tuple[float, float]]:
        """
        Detect silent parts in audio
        
        Args:
            y: Audio signal
            sr: Sample rate
            threshold_db: Threshold in dB to consider as silent
            
        Returns:
            List of (start_time, end_time) tuples for silent parts
        """
        # Calculate RMS energy
        rms = librosa.feature.rms(y=y)[0]
        
        # Convert threshold from dB to linear scale
        threshold_linear = 10 ** (threshold_db / 20)
        
        # Find silent parts
        silent_frames = np.where(rms < threshold_linear)[0]
        
        if len(silent_frames) == 0:
            return []
        
        # Group consecutive silent frames
        silent_parts = []
        start_frame = silent_frames[0]
        
        for i in range(1, len(silent_frames)):
            if silent_frames[i] - silent_frames[i-1] > 1:
                # End of silent part
                end_frame = silent_frames[i-1]
                start_time = librosa.frames_to_time(start_frame, sr=sr)
                end_time = librosa.frames_to_time(end_frame, sr=sr)
                
                # Only include silent parts longer than 0.5 seconds
                if end_time - start_time > 0.5:
                    silent_parts.append((start_time, end_time))
                
                start_frame = silent_frames[i]
        
        # Add the last silent part
        end_frame = silent_frames[-1]
        start_time = librosa.frames_to_time(start_frame, sr=sr)
        end_time = librosa.frames_to_time(end_frame, sr=sr)
        
        if end_time - start_time > 0.5:
            silent_parts.append((start_time, end_time))
        
        return silent_parts
    
    def remove_silent_parts(self, audio_path: str, threshold_db: float = -40.0,
                           progress_callback: Optional[Callable[[float], None]] = None) -> str:
        """
        Remove silent parts from audio file
        
        Args:
            audio_path: Path to input audio file
            threshold_db: Threshold in dB to consider as silent
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to audio file without silent parts
        """
        output_path = self.temp_manager.get_temp_file('_no_silence.wav')
        
        # Use FFmpeg for efficient silent parts removal
        cmd = [
            'ffmpeg',
            '-i', audio_path,
            '-af', f'silenceremove=start_periods=1:start_duration=1:start_threshold={threshold_db}dB:stop_duration=1:stop_threshold={threshold_db}dB:detection=peak',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Silent parts removal failed: {result.stderr}")
            
            if progress_callback:
                progress_callback(100.0)
            
            self.logger.info(f"Silent parts removed from audio")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Silent parts removal timed out")
    
    def normalize_audio(self, audio_path: str, target_level_db: float = -16.0,
                       progress_callback: Optional[Callable[[float], None]] = None) -> str:
        """
        Normalize audio to target level
        
        Args:
            audio_path: Path to input audio file
            target_level_db: Target level in dB LUFS
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to normalized audio file
        """
        output_path = self.temp_manager.get_temp_file('_normalized.wav')
        
        # Use FFmpeg for audio normalization
        cmd = [
            'ffmpeg',
            '-i', audio_path,
            '-af', f'loudnorm=I={target_level_db}:TP=-1.5:LRA=11',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Audio normalization failed: {result.stderr}")
            
            if progress_callback:
                progress_callback(100.0)
            
            self.logger.info(f"Audio normalized to {target_level_db} dB LUFS")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Audio normalization timed out")
    
    def apply_fade_effects(self, audio_path: str, fade_in_duration: float = 0.5, 
                          fade_out_duration: float = 0.5,
                          progress_callback: Optional[Callable[[float], None]] = None) -> str:
        """
        Apply fade in/out effects to audio
        
        Args:
            audio_path: Path to input audio file
            fade_in_duration: Fade in duration in seconds
            fade_out_duration: Fade out duration in seconds
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to audio file with fade effects
        """
        output_path = self.temp_manager.get_temp_file('_faded.wav')
        
        # Get audio duration
        y, sr = librosa.load(audio_path, sr=None)
        duration = len(y) / sr
        
        # Use FFmpeg for fade effects
        cmd = [
            'ffmpeg',
            '-i', audio_path,
            '-af', f'afade=t=in:st=0:d={fade_in_duration},afade=t=out:st={duration-fade_out_duration}:d={fade_out_duration}',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Fade effects failed: {result.stderr}")
            
            if progress_callback:
                progress_callback(100.0)
            
            self.logger.info(f"Fade effects applied: in={fade_in_duration}s, out={fade_out_duration}s")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Fade effects timed out")
    
    def mix_audio(self, audio_path1: str, audio_path2: str, volume1: float = 1.0, 
                 volume2: float = 1.0, 
                 progress_callback: Optional[Callable[[float], None]] = None) -> str:
        """
        Mix two audio files with specified volumes
        
        Args:
            audio_path1: Path to first audio file
            audio_path2: Path to second audio file
            volume1: Volume for first audio (0.0 to 1.0)
            volume2: Volume for second audio (0.0 to 1.0)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to mixed audio file
        """
        output_path = self.temp_manager.get_temp_file('_mixed.wav')
        
        # Use FFmpeg for audio mixing
        cmd = [
            'ffmpeg',
            '-i', audio_path1,
            '-i', audio_path2,
            '-filter_complex', f'[0:a]volume={volume1}[a1];[1:a]volume={volume2}[a2];[a1][a2]amix=inputs=2:duration=longest',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise RuntimeError(f"Audio mixing failed: {result.stderr}")
            
            if progress_callback:
                progress_callback(100.0)
            
            self.logger.info(f"Audio mixed: volume1={volume1}, volume2={volume2}")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Audio mixing timed out")
    
    def extract_audio_features(self, audio_path: str, 
                             progress_callback: Optional[Callable[[float], None]] = None) -> Dict[str, Any]:
        """
        Extract advanced audio features
        
        Args:
            audio_path: Path to audio file
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with audio features
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.default_sample_rate)
            
            if progress_callback:
                progress_callback(20.0)
            
            # Extract MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfccs_mean = np.mean(mfccs, axis=1)
            
            if progress_callback:
                progress_callback(40.0)
            
            # Extract Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)
            
            if progress_callback:
                progress_callback(60.0)
            
            # Extract Tonnetz features
            tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
            tonnetz_mean = np.mean(tonnetz, axis=1)
            
            if progress_callback:
                progress_callback(80.0)
            
            # Extract Tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            if progress_callback:
                progress_callback(100.0)
            
            features = {
                'mfccs': mfccs_mean.tolist(),
                'chroma': chroma_mean.tolist(),
                'tonnetz': tonnetz_mean.tolist(),
                'tempo': float(tempo),
                'duration': len(y) / sr
            }
            
            self.logger.info(f"Audio features extracted: {len(features['mfccs'])} MFCCs, tempo={features['tempo']:.1f}")
            return features
            
        except Exception as e:
            self.logger.error(f"Audio feature extraction failed: {e}")
            raise RuntimeError(f"Audio feature extraction failed: {e}")

# Test the audio_processor
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    from temp_manager import TempManager
    
    # Test audio processor
    temp_mgr = TempManager()
    processor = AudioProcessor(temp_mgr)
    
    # Note: Actual audio processing tests require a test audio file
    print("Audio processor initialized successfully")