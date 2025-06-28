# Lofi 24/7 Twitch Streamer (Python + FFmpeg)

A lightweight and reliable solution for streaming a 24/7 lofi music channel to Twitch using FFmpeg and Python.

This project:
- Shuffles audio files randomly without repeating until all are played
- Streams with a video background (looped)
- Automatically stops after 47 hours (Twitch streams should stay below 48h)
- Can be managed via systemd or manually via script

---

## Requirements

- Python 3
- FFmpeg
- `python-dotenv` package
- **INFO**: You need to clone the repo into `/opt/` otherwise you need to update the `stream.service` paths to your directory

Install dependencies:

```bash
sudo apt update && sudo apt install python3 python3-pip ffmpeg
pip3 install python-dotenv
```

## Installation
Clone the repo in your designated folder and run the `start.sh`:
```bash
git clone git@github.com:Hunter-Matata/lofi-twitch-streamer.git
chmod +x start.sh setup.sh
./setup.sh
```
After that, you can run the start sh in your terminal to start the stream:
```bash
./start.sh
```

## How to Restart/Stop the Stream?
If you want to **restart** or **stop** the stream you can use the `systemd` CLIs below:
```bash
sudo systemctl stop stream.service
sudo systemctl restart stream.service
```
