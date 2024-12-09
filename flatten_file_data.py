#!/usr/bin/env python3
"""
Directory Parser
This script parses a directory structure, combining the contents of .py and .xml files
into a single output file. It ignores specified folders and provides detailed output.
Usage: python directory_parser.py <root_directory> [output_file]
"""
import os
import sys
from datetime import datetime

INCLUDE_FILES = ('.py', '.xml')
SKIP_FOLDERS = ['tests', 'static', "__pycache__", "i18n"]

def parse_folder(root_dir: str, output_file: str) -> None:
    """
    Recursively parse a folder and write contents of .py and .xml files to the output file.
    Args:
    root_dir (str): The root directory to start parsing from.
    output_file (str): The file to write the parsed contents to.
    """
    with open(output_file, 'a', encoding='utf-8') as outfile:
        outfile.write(f"Root folder: {os.path.abspath(root_dir)}\n\n")
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip folders that are in the SKIP_FOLDERS list
            dirnames[:] = [d for d in dirnames if d not in SKIP_FOLDERS]

            for filename in filenames:
                if filename.endswith(INCLUDE_FILES):
                    file_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(file_path, root_dir)
                    outfile.write(f"[{rel_path}]\n")
                   
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"Error reading file: {str(e)}\n")
                   
                    outfile.write("\n\n")  # Add extra newlines between files

def get_output_filename(root_dir: str) -> str:
    """
    Generate an output filename based on the folder name and current timestamp.
    Args:
    root_dir (str): The root directory being parsed.
    Returns:
    str: The generated output filename.
    """
    folder_name = os.path.basename(os.path.normpath(root_dir))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{folder_name}_parsed_{timestamp}.txt"

def main() -> None:
    """
    Main function to handle argument parsing and initiate the directory parsing process.
    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python directory_parser.py <root_directory> [output_file]")
        sys.exit(1)

    root_directory = sys.argv[1]
    if not os.path.isdir(root_directory):
        print(f"Error: {root_directory} is not a valid directory")
        sys.exit(1)

    output_file = sys.argv[2] if len(sys.argv) == 3 else get_output_filename(root_directory)
    output_file = os.path.join(os.getcwd(), output_file)

    try:
        with open(output_file, 'w', encoding='utf-8'):
            pass
    except IOError as e:
        print(f"Error: Unable to write to output file {output_file}")
        print(f"IOError: {e}")
        sys.exit(1)

    # Parse files and directories starting from the root_directory
    parse_folder(root_directory, output_file)

    print(f"Parsing complete. Output written to {output_file}")

if __name__ == "__main__":
    main()
