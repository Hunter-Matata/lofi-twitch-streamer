import os
import random
import subprocess
import time
from dotenv import load_dotenv

load_dotenv()

AUDIO_DIR = "audio"
RTMP_URL = os.getenv("RTMP_URL")
STREAM_KEY = os.getenv("STREAM_KEY")
BACKGROUND = os.getenv("BACKGROUND")
MAX_DURATION = int(os.getenv("MAX_DURATION", 169200))  # 47h

CONCAT_FILE = "playlist.txt"

def get_shuffled_tracks():
    tracks = [
        os.path.join(AUDIO_DIR, f)
        for f in os.listdir(AUDIO_DIR)
        if f.endswith(".mp3")
    ]
    if not tracks:
        print("[ERROR] No MP3 files found in ./audio/")
        exit(1)
    random.shuffle(tracks)
    return tracks

def write_concat_file(tracks):
    with open(CONCAT_FILE, "w") as f:
        for track in tracks:
            f.write(f"file '{os.path.abspath(track)}'\n")

def build_ffmpeg_command():
    cmd = ["ffmpeg", "-re"]

    # Audio playlist
    cmd += ["-f", "concat", "-safe", "0", "-i", CONCAT_FILE]

    # Background
    if BACKGROUND and BACKGROUND != "NONE":
        cmd += ["-stream_loop", "-1", "-i", BACKGROUND]
    else:
        cmd += ["-loop", "1", "-f", "lavfi", "-i", "color=c=black:s=1280x720"]

    # Output
    cmd += [
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", "2500k",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-f", "flv",
        f"{RTMP_URL}/{STREAM_KEY}"
    ]

    return cmd

def run_stream_loop():
    start = time.time()
    elapsed = 0

    while elapsed < MAX_DURATION:
        print(f"[INFO] Shuffling playlist... {int(elapsed)}s elapsed / {MAX_DURATION}s max")

        tracks = get_shuffled_tracks()
        write_concat_file(tracks)

        cmd = build_ffmpeg_command()

        # Estimate track total duration, fallback to 1h if unknown
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[WARNING] FFmpeg crashed: {e}")
            time.sleep(5)

        elapsed = time.time() - start

    print("[INFO] Max duration reached, stopping stream.")
    if os.path.exists(CONCAT_FILE):
        os.remove(CONCAT_FILE)

if __name__ == "__main__":
    run_stream_loop()