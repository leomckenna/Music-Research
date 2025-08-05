import librosa
import numpy as np
import pandas as pd
import os
import csv
from scipy.stats import entropy

# Define the directory containing the audio files
directory = '/Users/leomckenna/Desktop/Music Research/wav_files_control'

# Define the output CSV filep
output_csv = '/Users/leomckenna/Desktop/Music Research/audio_metrics_control.csv'

# Initialize a list to store the metrics for each file
audio_data = []

for filename in os.listdir(directory):
    if filename.endswith(('.m4a', '.wav', '.mp3', '.flac')):
        file_path = os.path.join(directory, filename)
        y, sr = librosa.load(file_path)

        # TEMPO AND RHYTHM METRICS
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        tempo = tempo.item() if isinstance(tempo, np.ndarray) else tempo

        # Estimate an alternative tempo using predominant local pulse (PLP)
        plp = librosa.beat.plp(y=y, sr=sr)
        plp_beats = np.where(plp > 0.5)[0]  # Extract strong pulses
        if len(plp_beats) > 1:
            inter_beat_intervals = np.diff(librosa.frames_to_time(plp_beats, sr=sr))
            estimated_tempo_plp = 60 / np.median(inter_beat_intervals)
        else:
            estimated_tempo_plp = tempo  # Fallback if no strong PLP estimate

        # Use the closer of the two estimates (account for possible octave errors)
        if abs(estimated_tempo_plp - 2 * tempo) < abs(estimated_tempo_plp - tempo):
            tempo = tempo * 2
        elif abs(estimated_tempo_plp - 0.5 * tempo) < abs(estimated_tempo_plp - tempo):
            tempo = tempo / 2
        else:
            tempo = tempo  # Keep original if no octave issue detected

        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        total_duration = librosa.get_duration(y=y, sr=sr)
        clock_density = len(onset_times) / total_duration
        beat_density = len(beat_times) / total_duration
        onsets_per_beat = len(onset_times) / len(beat_times) if len(beat_times) > 0 else np.nan

        # PITCH METRICS
        D = librosa.stft(y)
        frequencies = librosa.fft_frequencies(sr=sr)
        magnitude = np.abs(D)
        dominant_freq_indices = np.argmax(magnitude, axis=0)
        dominant_frequencies = frequencies[dominant_freq_indices]
        dominant_frequencies[dominant_frequencies == 0] = np.nan
        frame_times = librosa.frames_to_time(np.arange(len(dominant_frequencies)), sr=sr)
        interval = tempo / 60
        selected_times = np.arange(0, frame_times[-1], interval) if len(frame_times) > 0 else []
        selected_indices = np.searchsorted(frame_times, selected_times) if len(frame_times) > 0 else []
        dominant_notes = [librosa.hz_to_note(freq) if not np.isnan(freq) else "Invalid" for freq in dominant_frequencies]
        selected_notes = [dominant_notes[idx] for idx in selected_indices if dominant_notes[idx] != "Invalid"]
        valid_midi = [librosa.note_to_midi(note) % 12 for note in selected_notes]
        pitch_sd = np.std(valid_midi)
        pitch_mean = np.mean(valid_midi)
        pitch_median = np.median(valid_midi)
        unique_midi, counts = np.unique(valid_midi, return_counts=True)
        probabilities = counts / counts.sum()
        pitch_entropy = entropy(probabilities, base=2)
        midi_series = pd.Series(valid_midi)
        pitch_intervals = midi_series.diff().dropna()
        intervallic_variability = np.std(pitch_intervals)

        # Store metrics
        audio_data.append([
            filename, tempo, clock_density, beat_density, onsets_per_beat,
            pitch_sd, pitch_mean, pitch_median, pitch_entropy, intervallic_variability
        ])

# Write the metrics to a CSV file
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        'Filename', 'Tempo (BPM)', 'Clock Density (Onsets/Sec)', 'Beat Density (Beats/Sec)', 'Onsets per Beat',
        'Pitch SD', 'Pitch Mean', 'Pitch Median', 'Pitch Entropy', 'Intervallic Variability'
    ])
    writer.writerows(audio_data)

print(f'Audio metrics have been saved to {output_csv}')
