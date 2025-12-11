# --- Configuration ---

# The path to the audio file to be visualized.
# Ensure this path is correct for your system.
AUDIO_FILE = "audio_file/audio.mp3"

# --- Window Settings ---
# The initial width and height of the application window.
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 1920
MIN_WINDOW_WIDTH = 400
MIN_WINDOW_HEIGHT = 300

# --- Visualizer Settings ---
# The number of frequency bins (bars) to display in the visualizer.
BINS = 128

# The radius of the inner circle of the visualizer. This is the starting point for the bars.
MIN_RADIUS = 150

# A multiplier for the height of the bars to make the visualization more or less dramatic.
BAR_HEIGHT_MULTIPLIER = 10

# A smoothing factor for bar height changes. The value should be between 0.0 (no smoothing)
# and 1.0 (no change). A higher value results in smoother transitions between heights.
SMOOTHING = 0.95

# The background color of the visualizer window.
BACKGROUND_COLOR = (5, 5, 25)

# The starting and ending colors for the bar gradient.
BAR_COLOR_START = (20, 50, 255)
BAR_COLOR_END = (220, 50, 105)

# --- Audio Analysis Settings ---
# The Fast Fourier Transform (FFT) size. This determines the resolution of the frequency analysis.
# It should be a power of 2 for optimal performance.
FFT_SIZE = 1024 * 2

# The frame rate at which the visualization updates.
FRAME_RATE = 30

# --- Export Settings ---
# Set to True to export the visualization as a video.
EXPORT_VIDEO = True
# The width and height of the exported video.
EXPORT_WIDTH = 1080
EXPORT_HEIGHT = 1920
# The filename of the exported video.
EXPORT_FILENAME = "output.mp4"
# The frame rate of the exported video.
EXPORT_FPS = 30.0
# The temporary filename for the video without audio.
TEMP_VIDEO_FILENAME = "temp_video.mp4"
# Number of seconds to continue recording frames after End Of Song (EOS) is detected.
EXPORT_EOS_BUFFER_SECONDS = 2
