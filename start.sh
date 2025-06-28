#!/bin/bash

cd "$(dirname "$0")"

SERVICE_NAME="stream"

echo "[INFO] Restarting systemd service: $SERVICE_NAME"

# Reload systemd just in case
sudo systemctl daemon-reload

# Restart the stream service
sudo systemctl restart "$SERVICE_NAME"

# Show status
sudo systemctl status "$SERVICE_NAME" --no-pager