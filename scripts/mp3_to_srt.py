import os
import sys
import subprocess
import platform

def read_whisper_cpp_path():
    with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'whisper_cpp_path.txt'), 'r') as file:
        return file.read().strip()

def convert_mp3_to_srt(mp3_filename, threads, transcripts_dir):
    if len(sys.argv) != 4:
        print("Usage: python script.py mp3_filename number_of_threads transcripts_dir")
        sys.exit(1)

    # Get the input MP3 filename and number of threads from command-line arguments
    mp3_filename = sys.argv[1]
    threads = sys.argv[2]
    transcripts_dir = sys.argv[3]

    # Get the directory of the MP3 file
    mp3_dir = os.path.dirname(os.path.abspath(mp3_filename))
    
    # Remove the file extension and get the base name
    basename = os.path.splitext(os.path.basename(mp3_filename))[0]

    # Full path for the WAV and SRT files
    wav_filename = os.path.join(transcripts_dir, basename + '.wav')
    srt_filename = os.path.join(transcripts_dir, basename)

    # Convert MP3 to WAV using ffmpeg
    ffmpeg_command = ['ffmpeg', '-i', mp3_filename, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', wav_filename]
    subprocess.run(ffmpeg_command, check=True)

    # Read the whisper.cpp path from the .txt file
    whisper_cpp_path = read_whisper_cpp_path()

    # Detect the operating system
    os_type = platform.system()
    
    # The following whisper commands are set to output to srt and each line has a max of 45 characters
    if os_type == 'Windows':
        # Manually convert Windows path to WSL path
        wav_filename_wsl = '/mnt/' + wav_filename.replace(':', '').replace('\\', '/').replace('C', 'c').replace('c', 'c')
        srt_filename_wsl = '/mnt/' + srt_filename.replace(':', '').replace('\\', '/').replace('C', 'c').replace('c', 'c')
        whisper_cpp_path_wsl = '/mnt/' + whisper_cpp_path.replace(':', '').replace('\\', '/').replace('C', 'c').replace('c', 'c')

        # Run whisper.cpp using WSL
        whisper_command = ['wsl', whisper_cpp_path_wsl + '/main', '-t', threads, '-m', whisper_cpp_path_wsl + '/models/ggml-small.en.bin', '-f', wav_filename_wsl, '-osrt', '-of', srt_filename_wsl, '-ml', '45']
    elif os_type == 'Linux':
        # Run whisper.cpp directly on Linux
        whisper_command = [os.path.join(whisper_cpp_path, 'main'), '-t', threads, '-m', os.path.join(whisper_cpp_path, 'models/ggml-small.en.bin'), '-f', wav_filename, '-osrt', '-of', srt_filename, '-ml', '45']
    else:
        print("Unsupported operating system")
        sys.exit(1)

    subprocess.run(whisper_command, check=True)

    # Delete the WAV file
    os.remove(wav_filename)

if __name__ == "__main__":
    convert_mp3_to_srt(sys.argv[1], sys.argv[2], sys.argv[3])
