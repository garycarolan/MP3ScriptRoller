import os
import sys
import pysubs2
import chardet

def offset_dialogue_lines(input_file, added_lines, transcripts_dir):
    input_basename = os.path.splitext(os.path.basename(input_file))[0]
    offset_files = []

    for offset_number in range(1, added_lines + 1):
        output_file = os.path.join(transcripts_dir, f"{input_basename}+{offset_number}.srt")  # Output filename with +{offset_number} appended
        offset_files.append(output_file)

        with open(input_file, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()

        with open(output_file, 'w', encoding='utf-8') as outfile:
            i = 0
            next_line = ''
            dialogue_next = False
            while i < len(lines):
                line = lines[i].strip()

                if ' --> ' in line:  # Check if the line is a timestamp line
                    dialogue_next = True
                    outfile.write(f"{line}\n")  # Write timestamp line
                    i += 1  # Move to the next line
                elif dialogue_next:
                    dialogue_next = False
                    outfile.write(f"{next_line}\n")
                    next_line = lines[i].strip()
                    i += 1
                else:
                    outfile.write(f"{line}\n")
                    i += 1

        print(f"Offset SRT file created: {output_file}")
        input_file = output_file

    return offset_files

def merge_srt_to_ass(base_filename, offset_files, transcripts_dir):
    # Load the original subtitle file
    original_file = os.path.join(transcripts_dir, base_filename + '.srt')
    subs = pysubs2.load(original_file, encoding=charset_detect(original_file))

    # Merge each offset subtitle file
    for offset_file in offset_files:
        offset_subs = pysubs2.load(offset_file, encoding=charset_detect(offset_file))
        for line in offset_subs:
            subs.append(line)

    # Generate output filename with .ass extension
    output_filename = os.path.join(transcripts_dir, base_filename + '.ass')
    subs.save(output_filename)

    print(f"Merged subtitles saved to: {output_filename}")

def delete_offset_files(offset_files):
    for offset_file in offset_files:
        try:
            os.remove(offset_file)
            print(f"Deleted offset file: {offset_file}")
        except OSError as e:
            print(f"Error deleting file {offset_file}: {e}")

def charset_detect(filename):
    with open(filename, 'rb') as fi:
        rawdata = fi.read()
    encoding = chardet.detect(rawdata)['encoding']
    if encoding.lower() == 'gb2312':  # Decoding may fail using GB2312
        encoding = 'gbk'
    return encoding

def main(input_file, added_lines, transcripts_dir):
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    offset_files = offset_dialogue_lines(input_file, added_lines, transcripts_dir)
    merge_srt_to_ass(base_filename, offset_files, transcripts_dir)
    delete_offset_files(offset_files)  # Delete the offset files after merging

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py input_file.srt added_lines transcripts_dir")
        sys.exit(1)
    
    input_file = sys.argv[1]
    added_lines = int(sys.argv[2])
    transcripts_dir = sys.argv[3]
    
    main(input_file, added_lines, transcripts_dir)
