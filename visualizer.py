import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
import numpy as np
import math
import config
from audio import AudioProcessor
from video_exporter import VideoExporter


class VisualizerWindow:
    """
    The main window for the audio visualizer, handling rendering and updates using pygame.
    """

    def __init__(self, audio_processor: AudioProcessor, *args, **kwargs):
        """
        Initializes the VisualizerWindow.

        Args:
            audio_processor (AudioProcessor): An instance of the audio processor.
        """
        pygame.init()
        self.width = kwargs.get("width", config.WINDOW_WIDTH)
        self.height = kwargs.get("height", config.WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Audio Visualizer")

        self.audio_processor = audio_processor
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio_ended = False

        # Visualizer state
        self.smoothed_magnitudes = np.zeros(config.BINS)

        # Video export setup
        self.video_exporter = None
        self.eos_frames = 0
        if config.EXPORT_VIDEO:
            self.video_exporter = VideoExporter(
                config.EXPORT_WIDTH,
                config.EXPORT_HEIGHT,
                self.audio_processor.audio_file,
            )

    def run(self):
        """
        Starts the main event loop for the visualizer.
        """
        self.audio_processor.play()
        while self.running:  # Loop continues as long as self.running is True
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.w, event.h
                    self.screen = pygame.display.set_mode(
                        (self.width, self.height), pygame.RESIZABLE
                    )

            self.update()
            self.draw()
            self.clock.tick(config.FRAME_RATE)

        self.quit()

    def update(self):
        """
        Updates the visualizer state.
        """
        # Check if audio has ended
        if not self.audio_processor.player.playing and not self.audio_ended:
            self.audio_ended = True
            self.eos_frames = int(config.EXPORT_FPS * config.EXPORT_EOS_BUFFER_SECONDS)

        # Get audio features
        magnitudes = self.audio_processor.get_audio_features()

        if magnitudes is not None:
            # Smooth the magnitudes
            self.smoothed_magnitudes = (
                self.smoothed_magnitudes * config.SMOOTHING
                + magnitudes * (1 - config.SMOOTHING)
            )

    def draw(self):
        """
        Draws the visualizer on the screen.
        """
        self.screen.fill(config.BACKGROUND_COLOR)
        self._draw_bars(self.smoothed_magnitudes)
        pygame.display.flip()

        # Capture frame for video export
        if self.video_exporter:
            if not self.audio_ended or self.eos_frames > 0:
                frame_data = pygame.image.tostring(self.screen, "RGBA")
                self.video_exporter.write_frame(frame_data)
                if self.audio_ended:
                    self.eos_frames -= 1
            else:
                self.running = False

    def _draw_bars(self, magnitudes):
        """
        Draws the visualizer bars.

        Args:
            magnitudes (list): A list of frequency magnitudes.
        """
        center_x, center_y = self.width // 2, self.height // 2
        num_bars = len(magnitudes)

        # Create a logarithmic frequency axis for better distribution of bars
        log_freq_axis = np.logspace(0, np.log10(num_bars), num_bars)
        log_freq_axis = (log_freq_axis - 1) / (
            log_freq_axis[-1] - 1
        )  # Normalize to 0-1

        for i in range(num_bars):
            # Bar angle and position
            angle = (i / num_bars) * 2 * math.pi
            start_radius = config.MIN_RADIUS
            end_radius = start_radius + magnitudes[i] * config.BAR_HEIGHT_MULTIPLIER
            start_pos = (
                center_x + start_radius * math.cos(angle),
                center_y + start_radius * math.sin(angle),
            )
            end_pos = (
                center_x + end_radius * math.cos(angle),
                center_y + end_radius * math.sin(angle),
            )

            # Bar color interpolation
            color = tuple(
                int(c1 + (c2 - c1) * (i / num_bars))
                for c1, c2 in zip(config.BAR_COLOR_START, config.BAR_COLOR_END)
            )

            # Bar width
            # Make bars at the beginning and end of the circle thinner
            width_factor = 1 - abs(i - num_bars / 2) / (num_bars / 2)
            bar_width = int(2 + width_factor * 5)
            pygame.draw.line(self.screen, color, start_pos, end_pos, bar_width)

    def quit(self):
        """
        Cleans up and exits the application.
        """
        if self.video_exporter:
            self.video_exporter.close()
        pygame.quit()
