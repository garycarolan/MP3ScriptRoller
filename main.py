import os
import psutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import shutil  # For copying files
import platform

# Define the paths to the data and scripts directories
data_dir = os.path.join(os.path.dirname(__file__), 'data')
mp3_list = os.path.join(data_dir, 'mp3_list.json')
scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
transcripts_dir = os.path.join(os.path.dirname(__file__), 'transcripts')

# Ensure the data and transcripts directories exist
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
if not os.path.exists(transcripts_dir):
    os.makedirs(transcripts_dir)

added_files = set()
file_lines_per_frame = {}

def get_python_executable():
    if platform.system() == "Windows":
        return "python"
    else:
        return "python3"

def check_ass_file_exists(base_filename):
    return os.path.isfile(os.path.join(transcripts_dir, base_filename + '.ass'))

def check_srt_file_exists(base_filename):
    return os.path.isfile(os.path.join(transcripts_dir, base_filename + '.srt'))

def call_mp3_to_srt(mp3_filename, threads):
    script_path = os.path.join(scripts_dir, 'mp3_to_srt.py')
    subprocess.run([get_python_executable(), script_path, mp3_filename, str(threads), transcripts_dir], check=True)

def call_create_transcript(srt_filename, added_lines, filename=None):
    script_path = os.path.join(scripts_dir, 'create_transcript.py')
    subprocess.run([get_python_executable(), script_path, srt_filename, str(added_lines), transcripts_dir], check=True)
    file_lines_per_frame[filename or srt_filename] = added_lines + 1  # Store the number of lines per frame
    save_files()  # Save the updated information
    update_file_list()  # Reload the file list after creating a transcript

def call_mpv_launcher(mp3_filename):
    script_path = os.path.join(scripts_dir, 'mpv_launcher.py')
    subprocess.run([get_python_executable(), script_path, mp3_filename, transcripts_dir], check=True)

def add_file():
    filenames = filedialog.askopenfilenames(filetypes=[("MP3 files", "*.mp3")])
    for filename in filenames:
        if filename not in added_files:
            added_files.add(filename)
            add_file_to_list(filename)
            save_files()
        else:
            print(f"{filename} is already in the list")

def delete_file(filename):
    def on_confirm():
        if confirm_var.get():
            base_filename = os.path.splitext(os.path.basename(filename))[0]
            srt_file = os.path.join(transcripts_dir, base_filename + '.srt')
            ass_file = os.path.join(transcripts_dir, base_filename + '.ass')
            if os.path.exists(srt_file):
                os.remove(srt_file)
            if os.path.exists(ass_file):
                os.remove(ass_file)
        if filename in added_files:
            added_files.remove(filename)
            file_lines_per_frame.pop(filename, None)
            save_files()
            update_file_list()
        confirm_dialog.destroy()

    confirm_dialog = tk.Toplevel(root)
    confirm_dialog.title("Confirm Deletion")
    
    tk.Label(confirm_dialog, text="Are you sure you want to remove this file from the list?\nThe MP3 itself will not be deleted. \n\n"
             "LPF will display incorrectly if you keep associated files and re-add the mp3 later, "
             "but you can fix LPF display by using the 'Change LPF' button.\n\n"
             "⚠ Deleting transcript files means you will have to rerun Whisper.cpp if you did not have an original srt "
             "and want to re-add this MP3 to the list later. ", wraplength=350, justify='left').pack(pady=10, padx=10)
    
    confirm_var = tk.BooleanVar()
    confirm_checkbox = tk.Checkbutton(confirm_dialog, text="Delete associated SRT & ASS (transcript) files", variable=confirm_var)
    confirm_checkbox.pack(pady=5, padx=10)
    
    tk.Button(confirm_dialog, text="Cancel", command=confirm_dialog.destroy).pack(side=tk.RIGHT, padx=10, pady=10)
    tk.Button(confirm_dialog, text="Confirm", command=on_confirm).pack(side=tk.RIGHT, padx=10, pady=10)

def truncate_filename(filename, length=30):
    if len(filename) > length:
        return filename[:length - 3] + "..."
    return filename

def add_file_to_list(filename):
    base_filename = os.path.splitext(os.path.basename(filename))[0]
    
    frame = tk.Frame(files_frame)
    frame.pack(fill='x', pady=2)
    
    # Use the truncate_filename function to limit the filename length
    truncated_filename = truncate_filename(os.path.basename(filename), length=30)
    label = tk.Label(frame, text=truncated_filename, anchor='w', width=30)  # Fixed width for filenames
    label.grid(row=0, column=0, padx=0, sticky='w')
    
    play_button = tk.Button(frame, text="Play", bg="purple", fg="white", command=lambda: play_file(filename))
    play_button.grid(row=0, column=1, padx=3, sticky='e')

    change_lpf_button = tk.Button(frame, text="Change LPF", command=lambda: open_change_lpf_dialog(filename))
    change_lpf_button.grid(row=0, column=2, padx=3, sticky='e')
    if not check_srt_file_exists(base_filename):
        change_lpf_button.config(state=tk.DISABLED)
    
    delete_button = tk.Button(frame, text="Delete", bg="lightgrey", fg="black", command=lambda: delete_file(filename))
    delete_button.grid(row=0, column=3, padx=3, sticky='e')

    lpf_value = file_lines_per_frame.get(filename, 0)
    lpf_label = tk.Label(frame, text=f"LPF: {lpf_value}")
    lpf_label.grid(row=0, column=4, padx=3, sticky='e')

    ass_icon = tk.Label(frame, text="ASS: ✔️" if check_ass_file_exists(base_filename) else "ASS: ❌", fg="green" if check_ass_file_exists(base_filename) else "red")
    ass_icon.grid(row=0, column=5, padx=3, sticky='e')

    srt_icon = tk.Label(frame, text="SRT: ✔️" if check_srt_file_exists(base_filename) else "SRT: ❌", fg="green" if check_srt_file_exists(base_filename) else "red")
    srt_icon.grid(row=0, column=6, padx=3, sticky='e')

def play_file(filename):
    base_filename = os.path.splitext(os.path.basename(filename))[0]
    srt_exists = check_srt_file_exists(base_filename)
    ass_exists = check_ass_file_exists(base_filename)

    if not srt_exists and not ass_exists:
        if messagebox.askyesno("No Transcript Detected",
                               "No .srt or .ass file found. Would you like to browse for an .srt file on your system?\n\n"
                               "(Select no for prompt to convert from mp3)"):
            srt_path = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt")])
            if srt_path:
                lines_per_frame = simpledialog.askinteger("SRT to Transcript", "Set LPF - Lines Per Frame, default of 5 is recommended:", initialvalue=5)
                if lines_per_frame:
                    added_lines = lines_per_frame - 1
                    shutil.copyfile(srt_path, os.path.join(transcripts_dir, base_filename + '.srt'))
                    call_create_transcript(os.path.join(transcripts_dir, base_filename + '.srt'), added_lines, filename)
                    call_mpv_launcher(filename)
        else:
            open_threads_and_lines_dialog(filename)
    elif srt_exists and not ass_exists:
        lines_per_frame = simpledialog.askinteger("SRT to Transcript", "Set LPF - Lines Per Frame, default of 5 is recommended:", initialvalue=5)
        if lines_per_frame:
            added_lines = lines_per_frame - 1
            call_create_transcript(os.path.join(transcripts_dir, base_filename + '.srt'), added_lines, filename)
            call_mpv_launcher(filename)
    elif ass_exists:
        call_mpv_launcher(filename)

def open_change_lpf_dialog(filename):
    base_filename = os.path.splitext(os.path.basename(filename))[0]
    srt_file = os.path.join(transcripts_dir, base_filename + '.srt')

    if not check_srt_file_exists(base_filename):
        messagebox.showerror("Error", "No SRT file found for this MP3.")
        return

    def on_confirm():
        try:
            lines_per_frame = int(lines_entry.get())
            added_lines = lines_per_frame - 1
            call_create_transcript(srt_file, added_lines, filename)
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Lines per frame must be an integer")

    dialog = tk.Toplevel(root)
    dialog.title("Change Lines Per Frame")
    
    tk.Label(dialog, text="Enter the number of lines to be shown at a given time:").pack(pady=10)
    lines_entry = tk.Entry(dialog, width=5)
    lines_entry.pack(pady=5)
    lines_entry.insert(0, "5")  # Default value

    tk.Button(dialog, text="Confirm", command=on_confirm).pack(pady=10)

def open_threads_and_lines_dialog(filename):
    dialog = tk.Toplevel(root)
    dialog.title("MP3 to Transcript Settings")
    
    # Set the size of the dialog box
    explanation_label = tk.Label(dialog, text="Whisper.cpp is an optimised port of OpenAI's 'Whisper' speech recognition system. "
                             "You can use it to create a reasonably accurate transcript from an mp3. "
                             "However, it takes a while.\n\n⚠ Expect this to take about as long as half the runtime of the file. "
                             "This varies by computer and number of threads allocated.\n"
                             "⚠ This may use a lot of resources and slow down your computer, "
                             "close and restart the application and reduce the number of threads in this case.", wraplength=350, justify='left')
    explanation_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

    # Additional information for threads
    threads_info_label = tk.Label(dialog, text="Below decides how many CPU cores are used. It is recommended to use the number of physical cores on your CPU. "
                                  "This is the default number entered below.", wraplength=350, justify='left')
    threads_info_label.grid(row=1, column=0, columnspan=2, pady=5, padx=10)

    # Get the number of physical cores
    physical_cores = psutil.cpu_count(logical=False)

    # Label and entry for threads
    tk.Label(dialog, text="Number of threads:").grid(row=2, column=0, pady=5, padx=10, sticky='e')
    threads_entry = tk.Entry(dialog, width=3)
    threads_entry.insert(0, str(physical_cores))  # Set default value to the number of physical cores
    threads_entry.grid(row=2, column=1, pady=5, padx=10, sticky='w')

    # Additional information for lines per frame
    lines_info_label = tk.Label(dialog, text="Below is the number of previous lines of dialogue shown at a given time, 5 is recommended and entered by default, "
                                "you can change this quickly at any time without re-running Whisper.cpp. ", wraplength=350, justify='left')
    lines_info_label.grid(row=3, column=0, columnspan=2, pady=5, padx=10)

    # Label and entry for lines per frame
    tk.Label(dialog, text="Lines per frame:").grid(row=4, column=0, pady=5, padx=10, sticky='e')
    lines_entry = tk.Entry(dialog, width=3)
    lines_entry.grid(row=4, column=1, pady=5, padx=10, sticky='w')
    lines_entry.insert(0, "5")  # Set default value to 5

    def on_confirm():
        try:
            threads = int(threads_entry.get())
            lines_per_frame = int(lines_entry.get())
            added_lines = lines_per_frame - 1
            call_mp3_to_srt(filename, threads)
            call_create_transcript(os.path.join(transcripts_dir, os.path.splitext(os.path.basename(filename))[0] + '.srt'), added_lines, filename)
            call_mpv_launcher(filename)
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Number of threads and lines per frame input invalid")

    tk.Button(dialog, text="Confirm", command=on_confirm).grid(row=5, column=0, columnspan=2, pady=10)

def save_files():
    config = {
        'files': list(added_files),
        'lpf': {file: file_lines_per_frame.get(file, 0) for file in added_files}
    }
    with open(mp3_list, 'w') as f:
        json.dump(config, f)

def load_files():
    if os.path.exists(mp3_list):
        with open(mp3_list, 'r') as f:
            config = json.load(f)
            for file in config.get('files', []):
                added_files.add(file)
                file_lines_per_frame[file] = config.get('lpf', {}).get(file, 0)
                add_file_to_list(file)

def update_file_list():
    # Clear existing entries
    for widget in files_frame.winfo_children():
        widget.destroy()
    
    # Re-add files to the list
    for file in added_files:
        add_file_to_list(file)

# Create the main application window
root = tk.Tk()
root.title("MP3ScriptRoller")
root.geometry("800x600")

# Create a canvas with a scrollbar
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
files_frame = tk.Frame(canvas)

# Configure the canvas and the scrollbar
files_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)
canvas.create_window((0, 0), window=files_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Pack the canvas and the scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Create a button to add files
add_button = tk.Button(root, text="Add MP3 Files", bg="purple", fg="white", command=add_file)
add_button.pack(pady=10)

# Load files on startup
load_files()

# Run the main application loop
root.mainloop()
