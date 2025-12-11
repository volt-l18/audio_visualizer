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
            self.y, self.sr = librosa.load(audio_file, sr=None)
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

    def get_audio_features(self, timestamp=None):
        """
        Performs FFT on the current audio chunk and returns binned magnitudes.

        Args:
            timestamp (float, optional): The time in seconds to analyze. 
                                         If None, uses the current player time.

        Returns:
            list: A list of processed frequency magnitudes for each bin.
        """
        if timestamp is None:
            current_time = self.player.time
        else:
            current_time = timestamp

        if current_time >= self.duration:
            return None

        # Get current audio position and corresponding sample
        current_sample = int(current_time * self.sr)

        # Get chunk of audio data
        chunk = self.y[current_sample : current_sample + self.fft_size]
        if len(chunk) < self.fft_size:
            chunk = np.pad(chunk, (0, self.fft_size - len(chunk)), "constant")

        # Perform FFT
        fft_result = np.fft.fft(chunk)
        magnitudes = np.abs(fft_result)

        # Binning the frequencies
        num_bins = config.BINS
        bin_boundaries = self._create_log_bins(
            num_bins, 20, self.sr / 2, self.fft_size, self.sr
        )
        binned_magnitudes = np.zeros(num_bins)
        for i in range(num_bins):
            start_index = bin_boundaries[i]
            end_index = bin_boundaries[i + 1]
            if start_index < end_index:
                binned_magnitudes[i] = magnitudes[start_index:end_index].max()

        return binned_magnitudes

    def _create_log_bins(self, num_bins, min_freq, max_freq, fft_size, sr):
        """
        Creates logarithmically spaced bins and returns their start and end indices
        in the FFT result array.
        """
        freq_res = sr / fft_size
        log_min = np.log10(min_freq)
        log_max = np.log10(max_freq)

        # Create logarithmically spaced frequencies
        log_freqs = np.logspace(log_min, log_max, num_bins + 1)

        # Convert frequencies to FFT bin indices
        bin_indices = (log_freqs / freq_res).astype(int)

        # Ensure that each bin has at least one FFT bin
        for i in range(len(bin_indices) - 1):
            if bin_indices[i + 1] <= bin_indices[i]:
                bin_indices[i + 1] = bin_indices[i] + 1

        return bin_indices
