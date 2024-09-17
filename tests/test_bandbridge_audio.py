import requests
import os

BASE_URL = "http://localhost:6000"

def test_librosa_tempo():
    file_path = "/app/audio/getback.mp3"
    with open(file_path, 'rb') as f:
        response = requests.post(f"{BASE_URL}/librosa/tempo", files={'file': f})
    assert response.status_code == 200
    json_response = response.json()
    assert 'tempo' in json_response
    assert isinstance(json_response['tempo'], float)  # Ensure tempo is a float
    assert json_response['tempo'] > 123.0
    assert json_response['tempo'] < 124.5

def test_librosa_key():
    file_path = "/app/audio/getback.mp3"
    with open(file_path, 'rb') as f:
        response = requests.post(f"{BASE_URL}/librosa/key", files={'file': f})
    assert response.status_code == 200
    json_response = response.json()
    assert 'key' in json_response
    assert isinstance(json_response['key'], str)  # Ensure key is a string
    assert json_response['key'] == "A"  # Ensure key is valid