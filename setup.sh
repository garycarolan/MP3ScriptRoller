#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Python 3 if not installed
if ! command_exists python3; then
    echo "Python3 is not installed. Installing Python3..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python3
    else
        echo "Please install Python3 manually for your OS."
        exit 1
    fi
else
    echo "Python3 is already installed."
fi

# Install pip3 if not installed
if ! command_exists pip3; then
    echo "pip3 is not installed. Installing pip3..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y python3-pip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        sudo easy_install pip
    else
        echo "Please install pip3 manually for your OS."
        exit 1
    fi
else
    echo "pip3 is already installed."
fi

# Install required Python packages
echo "Installing required Python packages..."
pip3 install -r data/requirements.txt

# Install MPV
if ! command_exists mpv; then
    echo "Installing MPV..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y mpv
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install mpv
    else
        echo "Please install MPV manually for your OS."
        exit 1
    fi
else
    echo "MPV is already installed."
fi

# Install FFmpeg
if ! command_exists ffmpeg; then
    echo "Installing FFmpeg..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y ffmpeg
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ffmpeg
    else
        echo "Please install FFmpeg manually for your OS."
        exit 1
    fi
else
    echo "FFmpeg is already installed."
fi

# Install git if not installed
if ! command_exists git; then
    echo "Git is not installed. Installing git..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y git
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install git
    else
        echo "Please install git manually for your OS."
        exit 1
    fi
else
    echo "Git is already installed."
fi

# Clone Whisper.cpp and set up models
if [ ! -d "whisper.cpp" ]; then
    echo "Cloning Whisper.cpp repository..."
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd whisper.cpp
    echo "Downloading Whisper models..."
    ./models/download-ggml-model.sh small
    cd ..
else
    echo "Whisper.cpp is already set up."
fi

echo "Setup completed successfully."
echo "---python3 & pip3 locations:"
which python3
which pip3

# Wait for user input to keep the terminal open
echo "Press any key to exit..."
read -n 1 -s