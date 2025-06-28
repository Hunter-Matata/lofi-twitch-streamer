#!/bin/bash

cd "$(dirname "$0")"

SERVICE_NAME="stream"
SYSTEMD_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
LOCAL_SERVICE_FILE="./stream.service"

echo "[INFO] Checking for systemd service: $SERVICE_NAME"

if [ ! -f "$SYSTEMD_PATH" ]; then
    if [ -f "$LOCAL_SERVICE_FILE" ]; then
        echo "[INFO] Installing systemd service from local file..."
        sudo cp "$LOCAL_SERVICE_FILE" "$SYSTEMD_PATH"
        sudo systemctl daemon-reexec
        sudo systemctl enable "$SERVICE_NAME"
    else
        echo "[ERROR] $SERVICE_NAME.service not found in system or local directory."
        exit 1
    fi
fi

# Restart service
echo "[INFO] Restarting systemd service: $SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

# Show status
sudo systemctl status "$SERVICE_NAME" --no-pager
