import os
import librosa
import numpy as np
import scipy.stats
import pandas as pd


# Analysis functions
def onset_density(y, sr):
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
    return len(onsets) / (len(y) / sr)


def clock_density(y, sr):
    _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beats = len(beat_frames)
    duration = librosa.get_duration(y=y, sr=sr)
    return beats / duration


def tempo_estimates(y, sr):
    tempos = librosa.beat.tempo(y=y, sr=sr)
    return tempos[0]


def dominant_frequencies_and_notes(y, sr, interval=0.5):
    # Compute the Short-Time Fourier Transform (STFT)
    D = librosa.stft(y)

    # Convert the STFT into frequencies
    frequencies = librosa.fft_frequencies(sr=sr)

    # Get the magnitude spectrum (energy at each frequency)
    magnitude = np.abs(D)

    # Find the dominant frequency (highest energy) in each frame
    dominant_freq_indices = np.argmax(magnitude, axis=0)
    dominant_frequencies = frequencies[dominant_freq_indices]

    # Replace zero frequencies with NaN for invalid frames
    dominant_frequencies[dominant_frequencies == 0] = np.nan

    # Convert frame indices to time
    frame_times = librosa.frames_to_time(np.arange(len(dominant_frequencies)), sr=sr)

    # Select data at regular intervals
    selected_times = np.arange(0, frame_times[-1], interval)  # Interval in seconds
    selected_indices = np.searchsorted(frame_times, selected_times)

    # Convert dominant frequencies to notes
    dominant_notes = []
    for freq in dominant_frequencies:
        if np.isnan(freq):  # Handle NaN
            dominant_notes.append("Invalid")
        else:
            dominant_notes.append(librosa.hz_to_note(freq))

    # Collect results at selected intervals
    results = []
    for t, idx in zip(selected_times, selected_indices):
        freq = dominant_frequencies[idx]
        note = dominant_notes[idx]
        if not np.isnan(freq):
            results.append({"time": t, "frequency": freq, "note": note})
        else:
            results.append({"time": t, "frequency": None, "note": "Invalid"})

    return results


# Main analysis function
def analyze_audio(file):
    y, sr = librosa.load(file)

    # Perform analyses
    return {
        "file_name": os.path.basename(file),
        "onset_density": onset_density(y, sr),
        "clock_density": clock_density(y, sr),
        "tempo_estimates": tempo_estimates(y, sr),
        "dominant_notes": dominant_frequencies_and_notes(y, sr),
    }


# Directory containing your WAV files
wav_dir = "wav_files"
output_file = "complete_audio_features_with_notes.csv"

# Get all WAV files
audio_files = [os.path.join(wav_dir, f) for f in os.listdir(wav_dir) if f.endswith(".wav")]

# Analyze each file and save results
results = []
for file in audio_files:
    analysis = analyze_audio(file)

    # Flatten dominant notes into a string for CSV storage
    dominant_notes_summary = "; ".join(
        f"{note['time']:.2f}s: {note['note']}" for note in analysis["dominant_notes"]
    )
    analysis["dominant_notes_summary"] = dominant_notes_summary

    # Remove raw dominant notes from the main output (optional)
    del analysis["dominant_notes"]

    results.append(analysis)

# Save results to a CSV file
df = pd.DataFrame(results)
df.to_csv(output_file, index=False)

print(f"Results saved to {output_file}")
