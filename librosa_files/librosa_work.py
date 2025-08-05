import os
import scipy.spip3tats
import re
import librosa
import numpy as np
import pandas as pd

# Directory containing WAV files
wav_dir = "wav_files"

# Output file for audio features
output_file = "complete_audio_features.csv"

# Function to extract all available audio features using librosa
def extract_all_audio_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=None)  # Load audio file

        # Core audio features
        features = {
            "filename": os.path.basename(file_path),
            "duration": librosa.get_duration(y=y, sr=sr),
            "zero_crossing_rate": np.mean(librosa.feature.zero_crossing_rate(y=y).flatten()),
            "energy": np.mean(librosa.feature.rms(y=y).flatten()),
            "spectral_centroid": np.mean(librosa.feature.spectral_centroid(y=y, sr=sr).flatten()),
            "spectral_bandwidth": np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr).flatten()),
            "spectral_contrast": np.mean(librosa.feature.spectral_contrast(y=y, sr=sr), axis=1).tolist(),
            "spectral_flatness": np.mean(librosa.feature.spectral_flatness(y=y).flatten()),
            "spectral_rolloff": np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr).flatten()),
            "chroma_stft": np.mean(librosa.feature.chroma_stft(y=y, sr=sr), axis=1).tolist(),
            "chroma_cqt": np.mean(librosa.feature.chroma_cqt(y=y, sr=sr), axis=1).tolist(),
            "chroma_cens": np.mean(librosa.feature.chroma_cens(y=y, sr=sr), axis=1).tolist(),
            "tonnetz": np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr), axis=1).tolist(),
            "mfcc": np.mean(librosa.feature.mfcc(y=y, sr=sr), axis=1).tolist(),
            "tempo": librosa.beat.tempo(y=y, sr=sr)[0],
        }

        return features
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Analyze all WAV files in the directory
audio_features = []
for wav_file in os.listdir(wav_dir):
    if wav_file.endswith(".wav"):
        file_path = os.path.join(wav_dir, wav_file)
        features = extract_all_audio_features(file_path)
        if features:
            audio_features.append(features)

# Convert results to a DataFrame
features_df = pd.DataFrame(audio_features)

# Expand list-based features (e.g., spectral contrast, chroma, tonnetz, mfcc) into individual columns
def expand_feature_column(df, column_name, prefix, count):
    expanded_columns = pd.DataFrame(df[column_name].tolist(), columns=[f"{prefix}_{i+1}" for i in range(count)])
    return pd.concat([df.drop(columns=[column_name]), expanded_columns], axis=1)

features_df = expand_feature_column(features_df, "spectral_contrast", "spectral_contrast", 7)  # 7 spectral contrast bands
features_df = expand_feature_column(features_df, "chroma_stft", "chroma_stft", 12)  # 12 chroma bins
features_df = expand_feature_column(features_df, "chroma_cqt", "chroma_cqt", 12)  # 12 chroma bins
features_df = expand_feature_column(features_df, "chroma_cens", "chroma_cens", 12)  # 12 chroma bins
features_df = expand_feature_column(features_df, "tonnetz", "tonnetz", 6)  # 6 tonnetz dimensions
features_df = expand_feature_column(features_df, "mfcc", "mfcc", 20)  # Default 20 MFCC coefficients

# Save features to a CSV file
features_df.to_csv(output_file, index=False)

print(f"All audio features saved to {output_file}")