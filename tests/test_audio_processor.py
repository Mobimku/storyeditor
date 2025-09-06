import pytest
from unittest.mock import patch, MagicMock

from core.audio_processor import AudioProcessor

# Mock FFmpeg stderr output for silence detection
MOCK_FFMPEG_SILENCE_OUTPUT = """
[silencedetect @ 0x12345] silence_start: 10.123
[silencedetect @ 0x12345] silence_end: 12.456 | silence_duration: 2.333
[silencedetect @ 0x67890] silence_start: 30.5
[silencedetect @ 0x67890] silence_end: 33.0 | silence_duration: 2.5
"""

@pytest.fixture
def audio_processor():
    """Provides an AudioProcessor instance with a dummy ffmpeg path."""
    return AudioProcessor(ffmpeg_path='dummy_ffmpeg')

@patch('subprocess.run')
def test_detect_silence_parses_output_correctly(mock_run, audio_processor):
    """
    Tests if the detect_silence method correctly parses the stderr
    output from a successful ffmpeg silencedetect run.
    """
    # Arrange: Configure the mock to return our fake ffmpeg output
    mock_result = MagicMock()
    mock_result.stderr = MOCK_FFMPEG_SILENCE_OUTPUT
    mock_result.returncode = 0  # Even though ffmpeg might return 1, we test for 0
    mock_run.return_value = mock_result

    # Act
    silent_segments = audio_processor.detect_silence('dummy_audio.wav')

    # Assert
    mock_run.assert_called_once()
    expected_segments = [
        {'start': 10.123, 'end': 12.456},
        {'start': 30.5, 'end': 33.0}
    ]
    assert silent_segments == expected_segments

@patch('subprocess.run')
def test_detect_silence_handles_no_silence_output(mock_run, audio_processor):
    """
    Tests if detect_silence returns an empty list when ffmpeg does not
    report any silence.
    """
    # Arrange: Configure mock for no silence output
    mock_result = MagicMock()
    mock_result.stderr = "some other ffmpeg output without the silencedetect string"
    mock_result.returncode = 0
    mock_run.return_value = mock_result

    # Act
    silent_segments = audio_processor.detect_silence('dummy_audio.wav')

    # Assert
    assert silent_segments == []

@patch('subprocess.run')
def test_detect_silence_builds_correct_command(mock_run, audio_processor):
    """
    Tests if the correct FFmpeg command is constructed based on the
    method parameters.
    """
    # Arrange
    mock_run.return_value = MagicMock(stderr="[silencedetect]", returncode=0)

    # Act
    audio_processor.detect_silence(
        'input.wav',
        threshold_db=-50.5,
        min_duration=2.5
    )

    # Assert
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    ffmpeg_command = args[0]

    expected_command = [
        'dummy_ffmpeg',
        '-i', 'input.wav',
        '-af', 'silencedetect=noise=-50.5dB:d=2.5',
        '-f', 'null',
        '-'
    ]
    assert ffmpeg_command == expected_command
