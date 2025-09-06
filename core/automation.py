import logging
from .temp_manager import TempManager
from .video_processor import VideoProcessor
from .scene_detector import SceneDetector

class AutomationPipeline:
    """
    Orchestrates the entire automated video editing pipeline.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.temp_manager = TempManager()
        self.video_processor = VideoProcessor(self.temp_manager)
        # Access the scene_detector from the video_processor to avoid redundancy
        self.scene_detector = self.video_processor.scene_detector
        self.logger.info("AutomationPipeline initialized.")

    def execute_full_pipeline(self, input_source: str, settings: dict) -> tuple:
        """
        Runs the complete video processing pipeline from start to finish.

        Args:
            input_source: The path to the source video file.
            settings: A dictionary of processing settings.

        Returns:
            A tuple containing the path to the final video and final audio file.
        """
        self.logger.info(f"--- Starting Full Automation Pipeline for {input_source} ---")

        # For now, we assume input_source is a local file path.
        # A future implementation would handle URL downloads here.

        # Step 1: Preprocessing Phase (e.g., Trim)
        # Use get_video_info to find duration if trim_end is not provided.
        video_info = self.video_processor.get_video_info(input_source)
        trim_end = settings.get('trim_end', video_info['duration'])

        trimmed_video = self.video_processor.trim_video(
            input_source,
            settings.get('trim_start', 0),
            trim_end
        )
        self.logger.info(f"1. Preprocessing: Video trimmed to {trimmed_video}")

        # Step 2: Audio Analysis Phase (Remove Silence)
        (video_no_silence, _) = self.video_processor.remove_silent_parts(
            trimmed_video,
            audio_threshold=settings.get('silence_threshold', -40.0)
        )
        self.logger.info(f"2. Audio Analysis: Silent parts removed, new video at {video_no_silence}")

        # Step 3: Scene Detection Phase
        scenes = self.scene_detector.detect_scenes(video_no_silence)
        filtered_scenes = self.scene_detector.filter_scene_breaks(scenes)
        self.logger.info(f"3. Scene Detection: Found {len(filtered_scenes)} scenes after filtering.")

        # Step 4: Fair Use Cut Generation
        video_duration = self.video_processor.get_video_info(video_no_silence)['duration']
        cuts = self.scene_detector.generate_fair_use_cuts(filtered_scenes, video_duration)

        if not cuts:
            self.logger.error("No cuts were generated from the scenes. Aborting pipeline.")
            raise RuntimeError("Could not generate any cuts from the provided video.")

        # Step 5: Fair Use Sequencing (Zigzag)
        zigzag_cuts_definitions = self.scene_detector.create_zigzag_sequence(cuts)
        self.logger.info(f"4 & 5. Fair Use: Generated {len(zigzag_cuts_definitions)} cuts and applied zigzag sequence.")

        # Create the actual video clips for each cut definition
        cut_files = []
        for i, cut_def in enumerate(zigzag_cuts_definitions):
            self.logger.debug(f"Creating clip {i} from {cut_def['start']:.2f}s for {cut_def['duration']:.2f}s")
            clip = self.video_processor.trim_video(
                video_no_silence,
                cut_def['start'],
                cut_def['start'] + cut_def['duration']
            )
            cut_files.append(clip)
        self.logger.info(f"   - Created {len(cut_files)} video clip files from definitions.")

        # Step 6: Compile the sequence
        compiled_video = self.video_processor.compile_zigzag_sequence(cut_files)
        self.logger.info(f"6. Compilation: Compiled final video at {compiled_video}")

        # Step 7: Effects Application (Placeholder)
        # A real implementation would apply color grading/panning here based on settings.
        final_video = compiled_video
        self.logger.info("7. Effects: Skipping final effects application for this pipeline version.")

        # As per the original spec, return both video and a separate audio file.
        final_audio = self.video_processor.extract_audio(final_video)

        self.logger.info(f"--- Pipeline Finished ---")
        self.logger.info(f"Final Video: {final_video}")
        self.logger.info(f"Final Audio: {final_audio}")

        return (final_video, final_audio)
