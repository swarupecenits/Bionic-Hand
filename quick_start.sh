#!/bin/bash

echo "================================================"
echo "Robot Hand Controller - Quick Start"
echo "================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python detected:"
python3 --version
echo

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import mediapipe" &> /dev/null; then
    echo
    echo "MediaPipe not found. Installing dependencies..."
    echo "This may take a few minutes..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
else
    echo "Dependencies already installed!"
fi

echo
echo "================================================"
echo "Choose an option:"
echo "================================================"
echo
echo "1. List available serial ports"
echo "2. Run robot controller"
echo "3. Run web interface (local network)"
echo "4. Exit"
echo

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo
        echo "================================================"
        echo "Available Serial Ports:"
        echo "================================================"
        python3 local_client.py --list-ports
        echo
        read -p "Press Enter to continue..."
        ;;
    2)
        echo
        read -p "Enter serial port (e.g., /dev/ttyUSB0): " port
        if [ -z "$port" ]; then
            echo "ERROR: No port specified!"
            exit 1
        fi
        
        echo
        read -p "Enable serial communication? (y/n): " enableserial
        
        serialflag=""
        if [ "$enableserial" = "y" ] || [ "$enableserial" = "Y" ]; then
            serialflag="--enable-serial"
        fi
        
        echo
        echo "Starting robot controller..."
        echo "Press ESC in the video window to stop"
        echo
        python3 local_client.py --serial-port "$port" $serialflag
        ;;
    3)
        echo
        echo "Starting web interface..."
        echo "Access from other devices at: http://YOUR-IP:8501"
        echo "Press Ctrl+C to stop"
        echo
        streamlit run streamlit_app.py --server.address 0.0.0.0
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac
