import sys
import config
from audio import AudioProcessor
from visualizer import VisualizerWindow


def main():
    """
    The main function to set up and run the audio visualizer application.
    """
    try:
        # 1. Initialize the audio processor
        audio_processor = AudioProcessor(config.AUDIO_FILE)

        # 2. Determine window settings
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
