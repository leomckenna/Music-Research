import os
from pytube import YouTube
from pydub import AudioSegment

# === Step 1: Set YouTube URL and Desktop Path ===
youtube_url = "https://www.youtube.com/watch?v=7A1utb0NrHU"  # replace with your URL
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

# === Step 2: Download YouTube Audio as MP3 ===
yt = YouTube(youtube_url)
audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
mp3_path = os.path.join(desktop_path, yt.title + ".mp3")
audio_stream.download(output_path=desktop_path, filename=yt.title + ".mp3")

# === Step 3: Convert MP3 to WAV ===
mp3_audio = AudioSegment.from_file(mp3_path, format="mp3")
wav_path = os.path.join(desktop_path, yt.title + ".wav")
mp3_audio.export(wav_path, format="wav")

# === Step 4: (Optional) Remove the original MP3 ===
os.remove(mp3_path)

print(f"✅ WAV file saved to: {wav_path}")
