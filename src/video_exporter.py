import subprocess
import os
import config


class VideoExporter:
    """Handles video exporting using ffmpeg."""

    def __init__(self, width, height, audio_file, audio_duration):
        """
        Initializes the VideoExporter.

        Args:
            width (int): The width of the video.
            height (int): The height of the video.
            audio_file (str): The path to the audio file to be included in the video.
            audio_duration (float): The duration of the audio in seconds.
        """
        self.width = width
        self.height = height
        self.audio_file = audio_file
        self.audio_duration = audio_duration
        
        if config.EXPORT_VIDEO:
            # 1. First pass: Generate video only to a temp file
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
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p", # Standard pixel format for compatibility
                config.TEMP_VIDEO_FILENAME,
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
        """Closes the ffmpeg process and merges audio."""
        if self.ffmpeg_process:
            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait()
            
            # 2. Second pass: Merge audio and video
            print("Merging audio and video...")
            temp_merged_filename = "temp_merged.mp4"
            merge_command = [
                "ffmpeg",
                "-y",
                "-i",
                config.TEMP_VIDEO_FILENAME,
                "-i",
                self.audio_file,
                "-c:v",
                "copy", # Copy video stream directly
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                temp_merged_filename
            ]
            subprocess.run(merge_command)

            # 3. Third pass: Trim video to exact audio duration
            print("Trimming video to exact duration...")
            trim_command = [
                "ffmpeg",
                "-y",
                "-ss",
                "00:00:00",
                "-i",
                temp_merged_filename,
                "-t",
                str(self.audio_duration),
                "-c",
                "copy",
                config.EXPORT_FILENAME
            ]
            subprocess.run(trim_command)
            
            # 4. Cleanup
            if os.path.exists(config.TEMP_VIDEO_FILENAME):
                os.remove(config.TEMP_VIDEO_FILENAME)
            if os.path.exists(temp_merged_filename):
                os.remove(temp_merged_filename)
            print(f"Export complete: {config.EXPORT_FILENAME}")
