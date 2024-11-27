# MP3ScriptRoller

This project is for automating the use of other open source software to subtitle MP3 audio files.

The software used includes:
* "Whisper.cpp" https://github.com/ggerganov/whisper.cpp is an optimised port of OpenAI's "whisper". This is used to create transcripts from audio files, the small model is installed by default in the setup.sh script.
* MPV https://github.com/mpv-player/mpv is a video player used to show the transcript in time with MP3 audio.
* Python is used for scripting with "tkinter" providing a basic GUI.

## Installation (As of November 2024)

**Linux** (recommended) - "setup.sh" script is tested and working on Debian based Linux operating systems. It is recommended you review the "setup.sh" script before running it. 
A desktop entry called "MP3ScriptRoller" should be created allowing you to find and launch the application from wherever your other applications are accessed.

*Note* - If you want to test this on a virtual machine, VirtualBox will not work. I believe this is because whisper.cpp requires "FMA" CPU instructions, which currently don't work on virtualbox https://www.virtualbox.org/ticket/15471
The setup and program have been tested with Ubuntu on Hyper-V on Windows 10.

**Windows** - This project can be set up to work on windows with wsl, but an automated installer script has not been made.

**MacOS** - Neither the project itself nor the setup script has been tested for macOS, although some code for macOS exists in the setup.sh file, it is not recommended to run this script on macOS.

