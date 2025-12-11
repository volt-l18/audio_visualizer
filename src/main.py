import sys
import os
import config
from audio import AudioProcessor
from visualizer import VisualizerWindow


def get_first_audio_file():
    """
    Finds the first supported audio file in the configured directory.
    """
    if not os.path.exists(config.AUDIO_DIR):
        raise FileNotFoundError(f"Audio directory not found: {config.AUDIO_DIR}")

    for file in os.listdir(config.AUDIO_DIR):
        if file.lower().endswith(config.SUPPORTED_EXTENSIONS):
            return os.path.join(config.AUDIO_DIR, file)
    
    raise FileNotFoundError(f"No supported audio files found in {config.AUDIO_DIR}")


def main():
    """
    The main function to set up and run the audio visualizer application.
    """
    try:
        # 1. Find audio file
        audio_file = get_first_audio_file()
        print(f"Using audio file: {audio_file}")

        # 2. Initialize the audio processor
        audio_processor = AudioProcessor(audio_file)

        # 3. Determine window settings
        width = config.WINDOW_WIDTH
        height = config.WINDOW_HEIGHT

        # 3. Create the visualizer window
        window = VisualizerWindow(
            audio_processor=audio_processor,
            width=width,
            height=height,
        )

        # 4. Run the visualizer
        window.run()

    except Exception as e:
        print(f"Failed to start the application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
