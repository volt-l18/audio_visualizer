# Audio Visualizer

A Python-based audio visualizer that generates reactive graphics from audio files. It supports real-time visualization and rendering to video files.

## Features

- **Audio Analysis:** Uses `librosa` and `numpy` for FFT-based frequency analysis.
- **Visuals:** Renders a circular bar visualizer with smooth gradients and customizable aesthetics using `pygame` / `pyglet`.
- **Configuration:** Fully configurable via `src/config.py` (resolution, colors, smoothing, FFT size, etc.).
- **Video Export:** Capability to render the visualization to an MP4 video file.
- **GPU Acceleration:** Includes a helper script for NVIDIA PRIME offloading on Linux.

## Prerequisites

- Python 3.x
- FFmpeg (required for video export audio merging)

## Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .env
    source .env/bin/activate  # On Linux/macOS
    # .env\Scripts\activate   # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install FFmpeg:**
    *   **Linux (Arch):** `sudo pacman -S ffmpeg`
    *   **Linux (Debian/Ubuntu):** `sudo apt install ffmpeg`
    *   **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## Usage

1.  **Add Audio:**
    Place your audio files (mp3, wav, flac, etc.) in the `assets/audio/` directory. The application will automatically pick the first supported file found.

2.  **Configuration:**
    Edit `src/config.py` to adjust settings:
    *   `EXPORT_VIDEO`: Set to `True` to save an MP4, `False` for real-time window only.
    *   `WINDOW_WIDTH` / `WINDOW_HEIGHT`: Set render resolution.
    *   `BAR_COLOR_START` / `BAR_COLOR_END`: Change color gradients.

3.  **Run:**
    
    **Standard run:**
    ```bash
    python src/main.py
    ```

    **On Linux with NVIDIA GPU (PRIME offloading):**
    ```bash
    ./run_visualizer.sh
    ```

## Output

If video export is enabled, the resulting video will be saved to `outputs/output.mp4`.
