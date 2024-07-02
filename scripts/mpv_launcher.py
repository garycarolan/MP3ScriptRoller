import os
import sys
import subprocess

def launch_mpv(mp3_filename, transcripts_dir):
    if not mp3_filename:
        print("Usage: python script.py \"mp3_filename\" \"transcripts_dir\"")
        sys.exit(1)

    # Get the full path of the MP3 file
    audio_file = os.path.abspath(mp3_filename)

    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(audio_file))[0]

    # Set the path to the main subtitle file (xyz.ass)
    main_sub_file = os.path.join(transcripts_dir, base_filename + '.ass')

    # Construct the command
    command = [
        'mpv',
        '--sub-files=' + main_sub_file,
        '--sid=1',
        audio_file
    ]

    # Run the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py \"mp3_filename\" \"transcripts_dir\"")
        sys.exit(1)

    mp3_filename = sys.argv[1]
    transcripts_dir = sys.argv[2]

    launch_mpv(mp3_filename, transcripts_dir)