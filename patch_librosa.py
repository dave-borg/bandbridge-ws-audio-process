import os

librosa_beat_path = '/usr/local/lib/python3.9/site-packages/librosa/beat.py'

# Read the original file
with open(librosa_beat_path, 'r') as file:
    data = file.read()

# Replace scipy.signal.hann with scipy.signal.windows.hann
data = data.replace('scipy.signal.hann', 'scipy.signal.windows.hann')

# Write the modified file
with open(librosa_beat_path, 'w') as file:
    file.write(data)