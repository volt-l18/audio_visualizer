import pyglet
import librosa
import numpy as np
import config


class AudioProcessor:
    """
    Handles loading, playback, and analysis of the audio file.
    """

    def __init__(self, audio_file):
        """
        Initializes the AudioProcessor.

        Args:
            audio_file (str): The path to the audio file.

        Raises:
            Exception: If there is an error loading the audio file.
        """
        try:
            # Load with pyglet for playback
            self.song = pyglet.media.load(audio_file)
            self.duration = self.song.duration
            self.player = pyglet.media.Player()
            self.player.queue(self.song)

            # Store audio file path
            self.audio_file = audio_file

            # Load with librosa for analysis
            # Note: This loads the entire audio file into memory.
            # For very large files, a streaming approach would be more memory-efficient.
            self.y, self.sr = librosa.load(audio_file)
            self.fft_size = config.FFT_SIZE

        except Exception as e:
            print(f"Error loading audio: {e}")
            print(
                f"Please make sure the audio file path is correct in config.py: {audio_file}"
            )
            raise

    def play(self):
        """Starts audio playback."""
        self.player.play()

    def get_audio_features(self):
        """
        Performs FFT on the current audio chunk and returns binned magnitudes.

        Returns:
            list: A list of processed frequency magnitudes for each bin.
        """
        if self.player.time >= self.duration:
            return None

        # Get current audio position and corresponding sample
        current_sample = int(self.player.time * self.sr)

        # Get chunk of audio data
        chunk = self.y[current_sample : current_sample + self.fft_size]
        if len(chunk) < self.fft_size:
            chunk = np.pad(chunk, (0, self.fft_size - len(chunk)), "constant")

        # Perform FFT
        fft_result = np.fft.fft(chunk)
        magnitudes = np.abs(fft_result)
        frequencies = np.fft.fftfreq(len(magnitudes), 1 / self.sr)

        # Binning the frequencies
        num_bins = config.BINS
        log_freq_axis = np.logspace(np.log10(20), np.log10(self.sr / 2), num_bins + 1)
        binned_magnitudes = np.zeros(num_bins)
        for i in range(num_bins):
            start_freq = log_freq_axis[i]
            end_freq = log_freq_axis[i + 1]
            bin_indices = (frequencies >= start_freq) & (frequencies < end_freq)
            if np.any(bin_indices):
                binned_magnitudes[i] = magnitudes[bin_indices].max()

        return binned_magnitudes
