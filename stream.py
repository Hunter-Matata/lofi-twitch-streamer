# lofi-stream
# Copyright (c) 2025 Hunter-Matata
#
# This code is licensed under the MIT License.
# You are free to use, modify, and distribute this code.
# See the LICENSE file or https://opensource.org/licenses/MIT for details.

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
        if f.endswith(".mp3") and os.path.getsize(os.path.join(AUDIO_DIR, f)) > 0
    ]
    if not tracks:
        raise RuntimeError("[ERROR] No valid MP3 files found in ./audio/")
    random.shuffle(tracks)
    return tracks


def write_concat_file(tracks):
    with open(CONCAT_FILE, "w") as f:
        for track in tracks:
            f.write(f"file '{os.path.abspath(track)}'\n")


def build_ffmpeg_command():
    cmd = ["ffmpeg", "-re"]
    cmd += ["-f", "concat", "-safe", "0", "-i", CONCAT_FILE]
    if BACKGROUND and BACKGROUND != "NONE":
        cmd += ["-stream_loop", "-1", "-i", BACKGROUND]
    else:
        cmd += ["-loop", "1", "-f", "lavfi", "-i", "color=c=black:s=1280x720"]
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
    try:
        while elapsed < MAX_DURATION:
            print(f"[INFO] Shuffling playlist... {int(elapsed)}s elapsed / {MAX_DURATION}s max")
            tracks = get_shuffled_tracks()
            write_concat_file(tracks)
            cmd = build_ffmpeg_command()
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print(f"[WARNING] FFmpeg crashed: {e}")
                time.sleep(5)
            elapsed = time.time() - start
    finally:
        if os.path.exists(CONCAT_FILE):
            os.remove(CONCAT_FILE)
        print("[INFO] Stream loop finished or max duration reached.")


if __name__ == "__main__":
    try:
        run_stream_loop()
    except Exception as e:
        print(f"[FATAL] {e}")
        time.sleep(10)
        raise