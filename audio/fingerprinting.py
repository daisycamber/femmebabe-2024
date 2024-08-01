import numpy as np
from django.conf import settings
import librosa, uuid, os

def fingerprint(audio_file):
  """Generates a fingerprint for an audio file.

  Args:
    audio_file: The path to the audio file.

  Returns:
    A numpy array containing the fingerprint.
  """

  # Load the audio file.
  y, sr = librosa.load(audio_file)
  # Compute the spectrogram.
  S = librosa.stft(y)
  # Compute the magnitude spectrogram.
  mag_spectrogram = np.abs(S)
  # Compute the fingerprint.
  fingerprint = np.mean(mag_spectrogram, axis=1)
  return fingerprint

fingerprint_database = os.path.join(settings.BASE_DIR, 'media/audio/fingerprints')

# Generate a fingerprint for the audio file.
def save_fingerprint(file):
    fingerprint = fingerprint(file)
    print_file = os.path.join(fingerprint_database, '{}.npy'.format(str(uuid.uuid4())))
    # Save the fingerprint to a file.
    np.save(print_file, fingerprint)
    return print_file

def is_in_database(path_load):
    op = []
    for file in os.listdir(fingerprint_database):
        if load_fingerprint(path_load, file): op = op + [file]
    return False if len(op) == 0 else op

fidelity = settings.AUDIO_FINGERPRINT_FIDELITY

def load_fingerprint(path_load, known_path):
    known_fingerprint = np.load(known_path)
    # Load the fingerprint from a file.
    fingerprint = fingerprint(path_load)

    score = 0
    # Compare the fingerprint to a known fingerprint.
    for x in range(len(fingerprint)/fidelity):
        for y in range(len(known_fingerprint)/fidelity):
            if np.dot(numpy.split(fingerprint, fidelity)[x], numpy.split(known_fingerprint, fidelity)[y]) > 0.9:
                score = score + 1
    return score > 5
    # Compute the similarity between the two fingerprints.
#    similarity = np.dot(fingerprint, known_fingerprint)

    # If the similarity is high, then the two audio files are likely the same.
    return similarity > 0.9
    if similarity > 0.9:
        print("The two audio files are likely the same.")
    else:
        print("The two audio files are likely different.")
