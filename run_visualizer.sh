#!/bin/bash

# This script sets environment variables to encourage the use of the NVIDIA discrete GPU
# for OpenGL applications on systems with PRIME render offloading (e.g., NVIDIA Optimus).
# Then, it runs the audio visualizer Python script.

# Specify the SDL video driver to use
export SDL_VIDEODRIVER=x11

# Enable NVIDIA PRIME render offloading
export __NV_PRIME_RENDER_OFFLOAD=1
# Specify NVIDIA as the GLX vendor library
export __GLX_VENDOR_LIBRARY_NAME=nvidia

# Execute the main.py script using the python interpreter from the virtual environment
./.env/bin/python main.py

# To verify that your NVIDIA GPU is being used, you can run 'nvidia-smi' in a separate terminal
# while the visualizer is running. Look for processes utilizing the GPU.