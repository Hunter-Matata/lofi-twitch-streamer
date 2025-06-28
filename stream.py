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

def get_shuffled_playlist():
    tracks = [os.path.join(AUDIO_DIR, f) for f in os.listdir(AUDIO_DIR) if f.endswith('.mp3')]
    random.shuffle(tracks)
    return tracks

def build_ffmpeg_command(track):
    base_command = [
        "ffmpeg",
        "-re"
    ]

    if BACKGROUND != "NONE":
        base_command += ["-stream_loop", "-1", "-i", BACKGROUND]
    else:
        base_command += ["-loop", "1", "-f", "lavfi", "-i", "color=c=black:s=1280x720"]

    base_command += [
        "-i", track,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", "2500k",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-f", "flv",
        f"{RTMP_URL}/{STREAM_KEY}"
    ]

    return base_command

def main():
    playlist = get_shuffled_playlist()
    start_time = time.time()

    for track in playlist:
        elapsed = time.time() - start_time
        if elapsed >= MAX_DURATION:
            print("[INFO] Maximum stream duration reached. Exiting.")
            break

        print(f"[INFO] Streaming: {track}")
        try:
            cmd = build_ffmpeg_command(track)

            remaining_time = MAX_DURATION - int(elapsed)
            subprocess.run(cmd + ["-t", str(remaining_time)], check=True)
        except subprocess.CalledProcessError:
            print("[WARNING] FFmpeg crashed. Retrying in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    main()
