import librosa, queue, pyflac
import soundfile as sf
from pedalboard.io import AudioFile
from pedalboard import Pedalboard, Chorus, Reverb, Compressor, HighpassFilter, Gain



def adjust_pitch(path, semitones):
    y, sr = librosa.load(path, sr=None)
    steps = float(semitones)
    new_y = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)
    sf.write(path, new_y, 44100)
    return path

def add_reverb(path, new_path, size=0.25):
    # Make a Pedalboard object, containing multiple audio plugins:
    board = Pedalboard([Reverb(room_size=size)])

    # Open an audio file for reading, just like a regular file:
    with AudioFile(path) as f:
        # Open an audio file to write to:
        with AudioFile(new_path, 'w', f.samplerate, f.num_channels) as o:
            # Read one second of audio at a time, until the file is empty:
            while f.tell() < f.frames:
                chunk = f.read(int(f.samplerate))
                # Run the audio through our pedalboard:
                effected = board(chunk, f.samplerate, reset=False)
                # Write the output to our output file:
                o.write(effected)

def compressor(path, new_path, threshold=-50, ratio=25):
    # Make a Pedalboard object, containing multiple audio plugins:
    board = Pedalboard([Compressor(threshold_db=threshold, ratio=ratio)])

    # Open an audio file for reading, just like a regular file:
    with AudioFile(path) as f:
        # Open an audio file to write to:
        with AudioFile(new_path, 'w', f.samplerate, f.num_channels) as o:
            # Read one second of audio at a time, until the file is empty:
            while f.tell() < f.frames:
                chunk = f.read(int(f.samplerate))
                # Run the audio through our pedalboard:
                effected = board(chunk, f.samplerate, reset=False)
                # Write the output to our output file:
                o.write(effected)

def highpass_filter(path, new_path, cutoff=900):
    # Make a Pedalboard object, containing multiple audio plugins:
    board = Pedalboard([HighpassFilter(cutoff_frequency_hz=cutoff)])

    # Open an audio file for reading, just like a regular file:
    with AudioFile(path) as f:
        # Open an audio file to write to:
        with AudioFile(new_path, 'w', f.samplerate, f.num_channels) as o:
            # Read one second of audio at a time, until the file is empty:
            while f.tell() < f.frames:
                chunk = f.read(int(f.samplerate))
                # Run the audio through our pedalboard:
                effected = board(chunk, f.samplerate, reset=False)
                # Write the output to our output file:
                o.write(effected)

def lowpass_filter(path, new_path, cutoff=500):
    # Make a Pedalboard object, containing multiple audio plugins:
    board = Pedalboard([LowpassFilter(cutoff_frequency_hz=cutoff)])

    # Open an audio file for reading, just like a regular file:
    with AudioFile(path) as f:
        # Open an audio file to write to:
        with AudioFile(new_path, 'w', f.samplerate, f.num_channels) as o:
            # Read one second of audio at a time, until the file is empty:
            while f.tell() < f.frames:
                chunk = f.read(int(f.samplerate))
                # Run the audio through our pedalboard:
                effected = board(chunk, f.samplerate, reset=False)
                # Write the output to our output file:
                o.write(effected)

def gain(path, new_path, gain_db=30):
    # Make a Pedalboard object, containing multiple audio plugins:
    board = Pedalboard([Gain(gain_db=gain_db)])

    # Open an audio file for reading, just like a regular file:
    with AudioFile(path) as f:
        # Open an audio file to write to:
        with AudioFile(new_path, 'w', f.samplerate, f.num_channels) as o:
            # Read one second of audio at a time, until the file is empty:
            while f.tell() < f.frames:
                chunk = f.read(int(f.samplerate))
                # Run the audio through our pedalboard:
                effected = board(chunk, f.samplerate, reset=False)
                # Write the output to our output file:
                o.write(effected)



