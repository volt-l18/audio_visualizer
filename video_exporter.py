import subprocess
import config


class VideoExporter:
    """Handles video exporting using ffmpeg."""

    def __init__(self, width, height, audio_file):
        """
        Initializes the VideoExporter.

        Args:
            width (int): The width of the video.
            height (int): The height of the video.
            audio_file (str): The path to the audio file to be included in the video.
        """
        if config.EXPORT_VIDEO:
            command = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
                "-f",
                "rawvideo",
                "-vcodec",
                "rawvideo",
                "-s",
                f"{width}x{height}",
                "-pix_fmt",
                "rgba",
                "-r",
                str(config.EXPORT_FPS),
                "-i",
                "-",  # Input from stdin
                "-i",
                audio_file,
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                config.EXPORT_FILENAME,
            ]
            self.ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE)
        else:
            self.ffmpeg_process = None

    def write_frame(self, frame_data):
        """
        Writes a frame to the ffmpeg process.

        Args:
            frame_data (bytes): The raw frame data.
        """
        if self.ffmpeg_process:
            self.ffmpeg_process.stdin.write(frame_data)

    def close(self):
        """Closes the ffmpeg process."""
        if self.ffmpeg_process:
            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait()
