#!/bin/bash

cd "$(dirname "$0")"

echo "=== 24/7 Lofi Stream Setup ==="

# Create audio directory if missing
if [ ! -d "audio" ]; then
    mkdir -p audio
    echo "[INFO] Created ./audio/ directory – place your .mp3 files here."
fi

# Ask for stream key
read -rp "Enter your Twitch Stream Key: " stream_key
if [[ -z "$stream_key" ]]; then
    echo "[ERROR] Stream key is required."
    exit 1
fi

# Ask for background video path (optional)
read -rp "Enter the path to your background video (press Enter to skip): " background
if [[ -z "$background" ]]; then
    background="NONE"
    echo "[INFO] No background file will be used."
else
    if [[ ! -f "$background" ]]; then
        echo "[ERROR] File '$background' not found. Please provide a valid file path or leave empty."
        exit 1
    fi
fi

# Ask for duration (default = 169200s = 47h)
read -rp "Enter stream max duration in seconds (default 169200 = 47h): " duration
duration=${duration:-169200}

# Validate duration
if (( duration > 172800 )); then
    echo "[WARNING] Duration is over 48h – Twitch may auto-flag your stream."
    echo "[ERROR] Please choose a value less than or equal to 172800 seconds (48h)."
    exit 1
fi

# Create .env
cat <<EOF > .env
STREAM_KEY=$stream_key
RTMP_URL=rtmp://live.twitch.tv/app
BACKGROUND=$background
MAX_DURATION=$duration
EOF

echo "[INFO] .env created."

# Create requirements.txt if missing
if [ ! -f "requirements.txt" ]; then
    echo "python-dotenv" > requirements.txt
    echo "[INFO] Created default requirements.txt"
fi

# Ensure venv is available
if ! python3 -m venv .venv 2>/dev/null; then
    echo "[WARNING] python3-venv not found – trying to install it..."
    sudo apt update && sudo apt install -y python3-venv
    echo "[INFO] Retrying virtual environment creation..."
    python3 -m venv .venv || {
        echo "[ERROR] Failed to create virtual environment even after installing python3-venv."
        exit 1
    }
else
    echo "[INFO] Virtual environment created in .venv/"
fi

# Activate venv and install deps
echo "[INFO] Activating virtual environment..."
source .venv/bin/activate

echo "[INFO] Installing Python dependencies..."
pip install -r requirements.txt

# Check for FFmpeg
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "[ERROR] FFmpeg is not installed. Please install it with:"
    echo "sudo apt install ffmpeg"
    exit 1
fi

echo ""
echo "Setup complete!"
echo "- Place your MP3 files in ./audio/"
echo "- Start the stream with: ./start.sh"