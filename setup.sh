#!/bin/bash

# Note: This script currently only supports Debian-based systems (it uses sudo apt-get)
# This script is untested with MacOS

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Update package manager 
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew update
else
    echo "Unsupported OS type: $OSTYPE"
    exit 1
fi

# Install Python 3 if not installed
if ! command_exists python3; then
    echo "Python3 is not installed. Installing Python3..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
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

# Install tkinter
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "Tkinter is not installed. Installing Tkinter..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y python3-tk
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python-tk
    else
        echo "Please install Tkinter manually for your OS."
        exit 1
    fi
else
    echo "Tkinter is already installed."
fi

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
    ./models/download-ggml-model.sh small.en
    make small.en
    cd ..
else
    echo "Whisper.cpp is already set up."
fi

# Create launch.sh with the absolute path to main.py
echo "Creating launch.sh..."
main_py_path=$(pwd)/main.py

cat <<EOL > launch.sh
#!/bin/bash

APP_NAME="main.py"

# Check if the application is already running
if pgrep -f "\$APP_NAME" > /dev/null; then
    echo "\$APP_NAME is already running."
else
    python3 "$main_py_path"
fi
EOL

# Make launch.sh executable
chmod +x launch.sh

# Create a .desktop file for the application
# Note it's important Exec is wrapped in quotes & Icon isn't
DESKTOP_ENTRY="[Desktop Entry]
Version=1.0
Name=MP3ScriptRoller
Comment=Transcribe MP3 Files
Exec=\"$(pwd)/launch.sh\"
Icon=$(pwd)/data/OlaAki.png
Terminal=false
Type=Application"

echo "$DESKTOP_ENTRY" | sudo tee /usr/share/applications/MP3ScriptRoller.desktop > /dev/null

echo "Setup finished."
echo "---python3 & pip3 locations (for verifying environment):"
which python3
which pip3

# Wait for user input to keep the terminal open
echo "Press any key to exit..."
read -n 1 -s