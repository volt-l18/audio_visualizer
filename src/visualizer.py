import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
import numpy as np
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

        # Determine render resolution
        if config.EXPORT_VIDEO:
            self.render_width = config.EXPORT_WIDTH
            self.render_height = config.EXPORT_HEIGHT
        else:
            self.render_width = self.width
            self.render_height = self.height
        
        self.render_surface = pygame.Surface((self.render_width, self.render_height))

        self.audio_processor = audio_processor
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio_ended = False

        # Visualizer state
        self.smoothed_magnitudes = np.zeros(config.BINS)
        self.current_frame = 0

        # Video export setup
        self.video_exporter = None
        self.eos_frames = 0
        if config.EXPORT_VIDEO:
            self.video_exporter = VideoExporter(
                config.EXPORT_WIDTH,
                config.EXPORT_HEIGHT,
                self.audio_processor.audio_file,
                self.audio_processor.duration,
            )

        self._precalculate_visuals()

    def _precalculate_visuals(self):
        """Pre-calculates static visual elements."""
        num_bars = config.BINS

        # Angles
        self.angles = (np.arange(num_bars) / num_bars) * 2 * np.pi
        self.cos_angles = np.cos(self.angles)
        self.sin_angles = np.sin(self.angles)

        # Colors
        c1 = np.array(config.BAR_COLOR_START)
        c2 = np.array(config.BAR_COLOR_END)
        i_array = np.arange(num_bars) / num_bars
        self.bar_colors = c1 + (c2 - c1) * i_array[:, np.newaxis]
        self.bar_colors = self.bar_colors.astype(int)

        # Bar widths
        width_factors = 1 - np.abs(np.arange(num_bars) - num_bars / 2) / (
            num_bars / 2
        )
        self.bar_widths = (1 + width_factors * 2).astype(int)

    def run(self):
        """
        Starts the main event loop for the visualizer.
        """
        if not config.EXPORT_VIDEO:
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
        if config.EXPORT_VIDEO:
            timestamp = self.current_frame / config.EXPORT_FPS
            magnitudes = self.audio_processor.get_audio_features(timestamp=timestamp)
            self.current_frame += 1
        else:
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
        # 1. Draw to the internal render surface (at full resolution)
        self.render_surface.fill(config.BACKGROUND_COLOR)
        self._draw_bars(self.smoothed_magnitudes, self.render_surface)

        # 2. Scale and draw to the display window
        scaled_surface = pygame.transform.scale(self.render_surface, (self.width, self.height))
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

        if self.audio_ended:
            if self.video_exporter:
                if self.eos_frames > 0:
                    frame_data = pygame.image.tostring(self.render_surface, "RGBA")
                    self.video_exporter.write_frame(frame_data)
                    self.eos_frames -= 1
                else:
                    self.running = False
            else:
                self.running = False
        elif self.video_exporter:
            frame_data = pygame.image.tostring(self.render_surface, "RGBA")
            self.video_exporter.write_frame(frame_data)

    def _draw_bars(self, magnitudes, surface):
        """
        Draws the visualizer bars.

        Args:
            magnitudes (np.ndarray): A numpy array of frequency magnitudes.
            surface (pygame.Surface): The surface to draw onto.
        """
        surface_width = surface.get_width()
        surface_height = surface.get_height()
        center_x, center_y = surface_width // 2, surface_height // 2
        num_bars = len(magnitudes)

        # Vectorized calculations
        start_radius = config.MIN_RADIUS
        end_radii = start_radius + magnitudes * config.BAR_HEIGHT_MULTIPLIER

        # Use pre-calculated cos/sin
        # Ensure we don't go out of bounds if magnitudes has different length (unlikely but safe)
        n = min(num_bars, len(self.cos_angles))
        
        start_pos_x = center_x + start_radius * self.cos_angles[:n]
        start_pos_y = center_y + start_radius * self.sin_angles[:n]

        end_pos_x = center_x + end_radii[:n] * self.cos_angles[:n]
        end_pos_y = center_y + end_radii[:n] * self.sin_angles[:n]

        for i in range(n):
            start_pos = (start_pos_x[i], start_pos_y[i])
            end_pos = (end_pos_x[i], end_pos_y[i])
            color = tuple(self.bar_colors[i])
            bar_width = self.bar_widths[i]
            pygame.draw.line(surface, color, start_pos, end_pos, bar_width)

    def quit(self):
        """
        Cleans up and exits the application.
        """
        if self.video_exporter:
            self.video_exporter.close()
        pygame.quit()
