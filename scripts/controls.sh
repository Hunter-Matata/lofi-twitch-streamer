#!/bin/bash

cd "$(dirname "$0")/.."

SERVICE_NAME="stream"
SYSTEMD_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
LOCAL_SERVICE_FILE="./stream.service"

show_menu() {
    clear
    echo "=================================="
    echo "    Lofi Stream Control Panel"
    echo "=================================="
    echo ""
    echo "1) Start Stream"
    echo "2) Stop Stream"
    echo "3) Restart Stream"
    echo "4) Show Status"
    echo "5) Show Logs (Live)"
    echo "6) Show Recent Logs"
    echo "7) Install/Update Service"
    echo "8) Exit"
    echo ""
}

install_service() {
    if [ -f "$LOCAL_SERVICE_FILE" ]; then
        echo "[INFO] Installing systemd service..."
        sudo cp "$LOCAL_SERVICE_FILE" "$SYSTEMD_PATH"
        sudo systemctl daemon-reload
        sudo systemctl enable "$SERVICE_NAME"
        echo "[INFO] Service installed and enabled"
    else
        echo "[ERROR] $SERVICE_NAME.service not found in current directory."
        return 1
    fi
}

start_stream() {
    echo "[INFO] Starting stream service..."
    sudo systemctl start "$SERVICE_NAME"
    sleep 2
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
}

stop_stream() {
    echo "[INFO] Stopping stream service..."
    sudo systemctl stop "$SERVICE_NAME"
    sleep 2
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
}

restart_stream() {
    echo "[INFO] Restarting stream service..."
    sudo systemctl restart "$SERVICE_NAME"
    sleep 2
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
}

show_status() {
    echo "[INFO] Current service status:"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
}

show_live_logs() {
    echo "[INFO] Showing live logs (Ctrl+C to exit):"
    sudo journalctl -u "$SERVICE_NAME" -f
}

show_recent_logs() {
    echo "[INFO] Recent logs:"
    sudo journalctl -u "$SERVICE_NAME" --no-pager -l -n 50
    echo ""
    echo "Press Enter to continue..."
    read
}

# Check if service exists
check_service() {
    if [ ! -f "$SYSTEMD_PATH" ]; then
        echo "[WARNING] Service not installed. Would you like to install it? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            install_service
        else
            echo "[INFO] You can install it later with option 7"
        fi
    fi
}

# Main loop
while true; do
    show_menu
    read -rp "Choose an option (1-8): " choice
    
    case $choice in
        1)
            check_service
            start_stream
            echo ""
            echo "Press Enter to continue..."
            read
            ;;
        2)
            stop_stream
            echo ""
            echo "Press Enter to continue..."
            read
            ;;
        3)
            check_service
            restart_stream
            echo ""
            echo "Press Enter to continue..."
            read
            ;;
        4)
            show_status
            echo ""
            echo "Press Enter to continue..."
            read
            ;;
        5)
            show_live_logs
            ;;
        6)
            show_recent_logs
            ;;
        7)
            install_service
            echo ""
            echo "Press Enter to continue..."
            read
            ;;
        8)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option. Please choose 1-8."
            sleep 2
            ;;
    esac
done