# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for aubio and librosa (libsndfile, ffmpeg, gcc, pkg-config)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    aubio-tools \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Cython and numpy first
RUN pip install cython numpy

# Install Python libraries: librosa, madmom, aubio, flask
RUN pip install librosa madmom aubio flask pydub

# Copy your Flask app into the container
COPY bandbridge-audio.py /app/bandbridge-audio.py

# Copy the patch script into the container
COPY patch_madmom.py /app/patch_madmom.py

# Run the patch script
RUN python /app/patch_madmom.py

# Expose the new port
EXPOSE 6000

# Run the Flask app
CMD ["python", "bandbridge-audio.py"]