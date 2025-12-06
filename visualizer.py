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
        # Get audio features
        magnitudes = self.audio_processor.get_audio_features()

        if magnitudes is None:
            if not self.audio_ended:
                self.audio_ended = True
                if config.EXPORT_VIDEO:
                    self.eos_frames = int(
                        config.EXPORT_FPS * config.EXPORT_EOS_BUFFER_SECONDS
                    )
            return

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

        if self.audio_ended:
            if self.video_exporter:
                if self.eos_frames > 0:
                    frame_data = pygame.image.tostring(self.screen, "RGBA")
                    self.video_exporter.write_frame(frame_data)
                    self.eos_frames -= 1
                else:
                    self.running = False
            else:
                self.running = False
        elif self.video_exporter:
            frame_data = pygame.image.tostring(self.screen, "RGBA")
            self.video_exporter.write_frame(frame_data)

    def _draw_bars(self, magnitudes):
        """
        Draws the visualizer bars.

        Args:
            magnitudes (np.ndarray): A numpy array of frequency magnitudes.
        """
        center_x, center_y = self.width // 2, self.height // 2
        num_bars = len(magnitudes)

        # Vectorized calculations
        angles = (np.arange(num_bars) / num_bars) * 2 * np.pi
        start_radius = config.MIN_RADIUS
        end_radii = start_radius + magnitudes * config.BAR_HEIGHT_MULTIPLIER

        cos_angles = np.cos(angles)
        sin_angles = np.sin(angles)

        start_pos_x = center_x + start_radius * cos_angles
        start_pos_y = center_y + start_radius * sin_angles

        end_pos_x = center_x + end_radii * cos_angles
        end_pos_y = center_y + end_radii * sin_angles

        # Color interpolation
        c1 = np.array(config.BAR_COLOR_START)
        c2 = np.array(config.BAR_COLOR_END)
        i_array = np.arange(num_bars) / num_bars
        colors = c1 + (c2 - c1) * i_array[:, np.newaxis]
        colors = colors.astype(int)

        # Bar width
        width_factors = 1 - np.abs(np.arange(num_bars) - num_bars / 2) / (
            num_bars / 2
        )
        bar_widths = (1 + width_factors * 2).astype(int)

        for i in range(num_bars):
            start_pos = (start_pos_x[i], start_pos_y[i])
            end_pos = (end_pos_x[i], end_pos_y[i])
            color = tuple(colors[i])
            bar_width = bar_widths[i]
            pygame.draw.line(self.screen, color, start_pos, end_pos, bar_width)

    def quit(self):
        """
        Cleans up and exits the application.
        """
        if self.video_exporter:
            self.video_exporter.close()
        pygame.quit()
