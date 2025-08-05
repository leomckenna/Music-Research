import librosa
import numpy as np
import os
import csv

# Define the directory containing the audio files
directory = '/Users/khoile/Desktop/Updated Project/practice_recordings'

# Define the output CSV file for key profile
output_csv = '/Users/khoile/Desktop/Updated Project/practice_results/key_profile.csv'

# Initialize a dictionary to store aggregate pitch counts
pitch_counts = {i: 0 for i in range(12)}  # MIDI pitch class (0-11, representing C-B)
total_notes = 0

for filename in os.listdir(directory):
    if filename.endswith(('.m4a', '.wav', '.mp3', '.flac')):
        file_path = os.path.join(directory, filename)
        try:
            y, sr = librosa.load(file_path)

            # Compute STFT and extract dominant frequencies
            D = librosa.stft(y)
            frequencies = librosa.fft_frequencies(sr=sr)
            magnitude = np.abs(D)
            dominant_freq_indices = np.argmax(magnitude, axis=0)
            dominant_frequencies = frequencies[dominant_freq_indices]

            # Remove invalid frequencies
            valid_frequencies = [freq for freq in dominant_frequencies if not np.isnan(freq) and freq > 0]

            # Convert valid frequencies to MIDI pitch class (0-11)
            valid_midi = [int(librosa.hz_to_midi(freq)) % 12 for freq in valid_frequencies]

            # Count occurrences of each pitch class
            for midi in valid_midi:
                pitch_counts[midi] += 1
                total_notes += 1

        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Normalize to get the average pitch distribution
if total_notes > 0:
    pitch_distribution = {pitch: count / total_notes for pitch, count in pitch_counts.items()}
else:
    pitch_distribution = {pitch: 0 for pitch in pitch_counts.keys()}

# Write the key profile to a CSV file
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Pitch Class (MIDI)', 'Average Proportion'])
    for pitch, proportion in pitch_distribution.items():
        writer.writerow([pitch, proportion])

print(f'Key profile has been saved to {output_csv}')
