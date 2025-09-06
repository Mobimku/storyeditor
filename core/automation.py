# core/automation.py
"""
Automation pipeline for the FFmpeg Editor
"""

import logging
from typing import Dict, Any

from .temp_manager import TempManager
from .video_processor import VideoProcessor
from .scene_detector import SceneDetector

class AutomationPipeline:
    """
    Orchestrates the entire automated video editing workflow.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the automation pipeline with all necessary components.

        Args:
            config: The application configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize core components correctly
        self.temp_manager = TempManager(self.config)
        self.video_processor = VideoProcessor(self.temp_manager)
        self.scene_detector = SceneDetector(self.temp_manager)

        self.logger.info("AutomationPipeline initialized correctly")

    def execute_full_pipeline(self, input_source: str, settings: Dict[str, Any]) -> str:
        """
        Runs the complete video processing pipeline from start to finish.
        This is a refactored version that uses the high-level methods
        from the other core modules.

        Args:
            input_source: The path to the source video file.
            settings: A dictionary of processing settings.

        Returns:
            The path to the final edited video file.
        """
        self.logger.info(f"--- Starting Refactored Automation Pipeline for {input_source} ---")

        # Step 1: Scene Detection
        self.logger.info("Step 1: Detecting scenes...")
        scenes = self.scene_detector.detect_scenes(input_source)
        if not scenes:
            self.logger.error("No scenes were detected. Aborting pipeline.")
            raise RuntimeError("Could not detect any scenes in the provided video.")
        self.logger.info(f"Detected {len(scenes)} scenes.")

        # Step 2: Generate Cut Definitions
        # This method exists in scene_detector, so we use it.
        self.logger.info("Step 2: Generating fair use cut definitions...")
        cut_definitions = self.scene_detector.generate_fair_use_cuts(
            scenes,
            min_duration=settings.get('min_cut_duration', 3.0),
            max_duration=settings.get('max_cut_duration', 7.0)
        )
        if not cut_definitions:
            self.logger.error("No cut definitions were generated. Aborting pipeline.")
            raise RuntimeError("Could not generate any cut definitions from the scenes.")
        self.logger.info(f"Generated {len(cut_definitions)} cut definitions.")

        # Step 3: Create Video Clips from Definitions
        # This uses the method I implemented in video_processor
        self.logger.info("Step 3: Creating video clips from definitions...")
        # Note: The test for create_random_cuts implies it takes scene_data, not cut_definitions.
        # I will use the `create_random_cuts` method as it is implemented in video_processor.py
        # which takes scene data and returns a list of file paths.
        cut_files = self.video_processor.create_random_cuts(input_source, scenes)
        if not cut_files:
             self.logger.error("Failed to create video clips. Aborting pipeline.")
             raise RuntimeError("Failed to create video clips.")
        self.logger.info(f"Created {len(cut_files)} video clip files.")

        # Step 4: Compile the sequence in zigzag order
        # This uses the method I implemented in video_processor, which handles the
        # file list creation and zigzag logic internally.
        self.logger.info("Step 4: Compiling clips into zigzag sequence...")
        final_video_path = self.video_processor.compile_zigzag_sequence(cut_files)
        self.logger.info(f"Compilation complete. Final video at: {final_video_path}")

        # Step 5: (Future) Apply effects, mixing, etc.
        # For now, the pipeline stops here as per the core task.

        self.logger.info(f"--- Pipeline Finished Successfully ---")
        return final_video_path
