from flask import Flask, request, jsonify
from music21 import key as music21_key, scale, pitch
import librosa
import numpy as np  # Add this import statement
import madmom
import aubio
import os
import logging
from pydub import AudioSegment

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return "Librosa, MADMOM, and Aubio API"

# Endpoint to extract chroma features using librosa
@app.route('/librosa/chroma', methods=['POST'])
def chroma():
    if 'file' not in request.files:
        app.logger.debug("No file part in request")
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        app.logger.debug("No selected file")
        return "No selected file", 400
    
    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)
    app.logger.debug(f"File saved to {file_path}")
    
    try:
        y, sr = librosa.load(file_path)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        return jsonify(chroma=chroma.tolist())
    finally:
        os.remove(file_path)
        app.logger.debug(f"File deleted: {file_path}")

def get_scale_chords(key_str, mode_str):
    # Create a key object
    key_obj = music21_key.Key(key_str, mode_str)
    
    # Get the scale
    if mode_str == 'major':
        scale_obj = scale.MajorScale(key_obj.tonic)
    elif mode_str == 'minor':
        scale_obj = scale.MinorScale(key_obj.tonic)
    elif mode_str == 'mixolydian':
        scale_obj = scale.MixolydianScale(key_obj.tonic)
    else:
        raise ValueError(f"Unsupported mode: {mode_str}")
    
    # Generate chords for each degree of the scale
    chords = []
    for degree in range(1, 8):
        chord_obj = scale_obj.getChord(degree=degree, minPitch=pitch.Pitch('C4'))
        chords.append(chord_obj.pitchedCommonName)
    
    return chords

@app.route('/scale/chords', methods=['POST'])
def scale_chords():
    data = request.get_json()
    key_str = data.get('key')
    mode = data.get('mode')
    
    logging.debug(f"Received request with key: {key_str}, mode: {mode}")
    
    if not key_str or not mode:
        logging.error("Key and mode are required but not provided")
        return jsonify({"error": "Key and mode are required"}), 400
    
    try:
        chords = get_scale_chords(key_str, mode)
        logging.debug(f"Generated chords: {chords}")
        return jsonify({"chords": chords})
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Endpoint to detect beats using madmom
@app.route('/madmom/beats', methods=['POST'])
def beats():
    if 'file' not in request.files:
        app.logger.debug("No file part in request")
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        app.logger.debug("No selected file")
        return "No selected file", 400
    
    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)
    app.logger.debug(f"File saved to {file_path}")
    
    try:
        proc = madmom.features.beats.RNNBeatProcessor()
        beats = madmom.features.beats.DBNBeatTrackingProcessor()(proc(file_path))
        return jsonify(beats=beats.tolist())
    finally:
        os.remove(file_path)
        app.logger.debug(f"File deleted: {file_path}")

# Endpoint to extract tempo using librosa
@app.route('/librosa/tempo', methods=['POST'])
def tempo_librosa():
    if 'file' not in request.files:
        app.logger.debug("No file part in request")
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        app.logger.debug("No selected file")
        return "No selected file", 400
    
    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)
    app.logger.debug(f"File saved to {file_path}")
    
    try:
        y, sr = librosa.load(file_path)
        
        # Calculate the number of samples to trim (15 seconds)
        trim_samples = 15 * sr
        
        # Use a longer segment from the middle of the audio
        if len(y) > 4 * trim_samples:
            y_trimmed = y[trim_samples:-trim_samples]
        else:
            y_trimmed = y  # If the audio is too short, don't trim
        
        # Refine the onset envelope
        onset_env = librosa.onset.onset_strength(y=y_trimmed, sr=sr, hop_length=512)
        
        # Estimate tempo using beat_track
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        
        # Extract the first element if tempo is an array
        if isinstance(tempo, np.ndarray):
            tempo = tempo[0]
        
        # Apply a correction factor if needed
        correction_factor = 1.006  # Adjust this factor based on observed bias
        corrected_tempo = tempo * correction_factor
        
        # Round the tempo to the nearest whole number
        rounded_tempo = round(corrected_tempo)
        
        return jsonify(tempo=int(rounded_tempo))
    finally:
        os.remove(file_path)
        app.logger.debug(f"File deleted: {file_path}")


# Endpoint to extract tempo using aubio
@app.route('/aubio/tempo', methods=['POST'])
def tempo_aubio():
    if 'file' not in request.files:
        app.logger.debug("No file part in request")
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        app.logger.debug("No selected file")
        return "No selected file", 400
    
    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)
    app.logger.debug(f"File saved to {file_path}")
    
    try:
        # Convert MP3 to WAV
        try:
            audio = AudioSegment.from_file(file_path)
            wav_path = file_path.replace('.mp3', '.wav')
            audio.export(wav_path, format='wav')
            app.logger.debug(f"File converted to WAV: {wav_path}")
        except Exception as e:
            app.logger.error(f"Error converting file to WAV: {e}")
            return f"Error converting file to WAV: {e}", 500
        
        # Use aubio to calculate tempo
        try:
            win_s = 1024                 # fft size
            hop_s = win_s // 2           # hop size
            samplerate = 0               # use original sample rate
            s = aubio.source(wav_path, samplerate, hop_s)
            samplerate = s.samplerate
            o = aubio.tempo("default", win_s, hop_s, samplerate)
            
            while True:
                samples, read = s()
                o(samples)
                if read < hop_s:
                    break
            
            bpm = o.get_bpm()
            return jsonify(tempo=bpm)
        except Exception as e:
            app.logger.error(f"Error processing file with aubio: {e}")
            return f"Error processing file with aubio: {e}", 500
        finally:
            os.remove(wav_path)
            app.logger.debug(f"File deleted: {wav_path}")
    finally:
        os.remove(file_path)
        app.logger.debug(f"File deleted: {file_path}")

# Function to estimate key and mode
def estimate_key_and_mode(y, sr):
    harmonic = librosa.effects.harmonic(y)
    chroma = librosa.feature.chroma_cqt(y=harmonic, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    
    # Define the key names
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Find the key with the highest mean chroma value
    key_index = chroma_mean.argmax()
    pitch = keys[key_index]
    
    # Determine the mode (major, minor, or Mixolydian)
    mode = 'major'  # Default to major
    if chroma_mean[(key_index + 9) % 12] > chroma_mean[(key_index + 8) % 12]:
        mode = 'minor'
    if chroma_mean[(key_index + 10) % 12] > chroma_mean[(key_index + 11) % 12]:
        mode = 'mixolydian'
    
    return pitch, mode

# Endpoint to extract key using librosa
@app.route('/librosa/key', methods=['POST'])
def key():
    if 'file' not in request.files:
        app.logger.debug("No file part in request")
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        app.logger.debug("No selected file")
        return "No selected file", 400
    
    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)
    app.logger.debug(f"File saved to {file_path}")
    
    try:
        y, sr = librosa.load(file_path)
        pitch, mode = estimate_key_and_mode(y, sr)
        
        return jsonify(key=pitch, mode=mode)
    finally:
        os.remove(file_path)
        app.logger.debug(f"File deleted: {file_path}")



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)