# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Cython first
RUN pip install --no-cache-dir Cython

# Install the dependencies
RUN pip install --no-cache-dir numpy==1.19.5
RUN pip install --no-cache-dir Flask==2.0.1
RUN pip install --no-cache-dir librosa==0.9.2
RUN pip install --no-cache-dir madmom
RUN pip install --no-cache-dir aubio==0.4.9
RUN pip install --no-cache-dir pydub==0.25.1
RUN pip install --no-cache-dir gunicorn==20.1.0
RUN pip install --no-cache-dir werkzeug==2.0.1
RUN pip install --no-cache-dir music21

# Copy the patch script into the container
COPY patch_madmom.py /app/patch_madmom.py
COPY patch_librosa.py /app/patch_librosa.py

# Run the patch scripts
RUN python /app/patch_madmom.py
RUN python /app/patch_librosa.py

# Explicitly copy the Python application files
COPY bandbridge_audio.py /app/bandbridge_audio.py
COPY wsgi.py /app/wsgi.py

# Set the PYTHONPATH
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 6000

# Command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:6000", "wsgi:app"]