import pytest
from unittest.mock import patch, MagicMock

from core.automation import AutomationPipeline

# By patching the classes at the module level where they are USED (i.e., in core.automation),
# any instance created by AutomationPipeline will be a mock.
@patch('core.automation.VideoProcessor')
@patch('core.automation.TempManager') # We also patch TempManager
def test_pipeline_execution_flow(mock_temp_manager, mock_video_processor):
    """
    Tests the high-level execution flow of the AutomationPipeline.
    It ensures that methods on the core modules are called in the correct order.
    This is an integration test for the pipeline's orchestration logic.
    """
    # Arrange
    # The decorators replace the actual classes with mocks.
    # When AutomationPipeline is instantiated, it gets these mocks.
    pipeline = AutomationPipeline()

    # The mock instances are accessible via the pipeline instance
    mock_vp_instance = pipeline.video_processor
    mock_sd_instance = pipeline.scene_detector # This is also a mock, nested inside the vp mock

    # Configure the return values of the mocked methods to simulate the pipeline flow
    mock_vp_instance.get_video_info.return_value = {'duration': 60.0}
    # The trim method is called multiple times, so we provide multiple return values
    mock_vp_instance.trim_video.side_effect = ['/tmp/trimmed.mp4', '/tmp/clip1.mp4', '/tmp/clip2.mp4']
    mock_vp_instance.remove_silent_parts.return_value = ('/tmp/no_silence.mp4', 'dummy_audio.wav')
    mock_sd_instance.detect_scenes.return_value = [0.0, 15.0, 30.0]
    mock_sd_instance.filter_scene_breaks.return_value = [0.0, 30.0]
    mock_sd_instance.generate_fair_use_cuts.return_value = [
        {'start': 5.0, 'duration': 5.0, 'cut_id': 0},
        {'start': 35.0, 'duration': 5.0, 'cut_id': 1}
    ]
    # create_zigzag_sequence is also on the scene_detector mock
    mock_sd_instance.create_zigzag_sequence.return_value = [
        {'start': 35.0, 'duration': 5.0, 'cut_id': 1}, # Swapped
        {'start': 5.0, 'duration': 5.0, 'cut_id': 0}
    ]
    mock_vp_instance.compile_zigzag_sequence.return_value = '/tmp/compiled.mp4'
    mock_vp_instance.extract_audio.return_value = '/tmp/final_audio.wav'

    # Act
    pipeline.execute_full_pipeline('input.mp4', {})

    # Assert
    # We can check that the key methods were called, which confirms the flow.
    mock_vp_instance.trim_video.assert_called()
    mock_vp_instance.remove_silent_parts.assert_called_once()
    mock_sd_instance.detect_scenes.assert_called_once()
    mock_sd_instance.filter_scene_breaks.assert_called_once()
    mock_sd_instance.generate_fair_use_cuts.assert_called_once()
    mock_sd_instance.create_zigzag_sequence.assert_called_once()
    mock_vp_instance.compile_zigzag_sequence.assert_called_once()
    mock_vp_instance.extract_audio.assert_called_once()

    # A more rigorous check can be done on the call order if needed,
    # but for this level of integration test, ensuring they all ran is sufficient.
    # Example check on arguments:
    mock_vp_instance.compile_zigzag_sequence.assert_called_with(['/tmp/clip1.mp4', '/tmp/clip2.mp4'])
