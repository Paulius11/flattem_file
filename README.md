# Directory Content Parser

A Python utility for parsing and combining the contents of specific file types from a directory structure into a single output file. Available in both GUI and command-line versions.

## Features

- Recursively parse directory structures
- Combine contents of specified file types (default: .py and .xml)
- Exclude specified folders from parsing
- Generate timestamped output files
- Choose between GUI and command-line interfaces
- Copy generated content to clipboard (GUI version)
- Configurable file extensions and skip folders

## Installation

1. Ensure you have Python 3.x installed
2. Install required dependencies:
```bash
pip install PyQt5
```

## Usage

### GUI Version (flatten_gui.py)

1. Run the GUI application:
```bash
python flatten_gui.py
```

2. Use the interface to:
   - Browse or enter the directory path
   - Configure included file extensions and folders to skip
   - Generate combined content
   - Copy content to clipboard
   - Save content to file

#### GUI Features
- Intuitive toolbar interface
- File extension configuration
- Folder exclusion settings
- Real-time content preview
- Copy to clipboard functionality
- Automatic file saving with timestamps

### Command-Line Version (flatten_file_data.py)

1. Run the script with required arguments:
```bash
python flatten_file_data.py <root_directory> [output_file]
```

Example:
```bash
python flatten_file_data.py ./my_project output.txt
```

If no output file is specified, one will be generated automatically using the format: `{folder_name}_parsed_{timestamp}.txt`

## Configuration

Default settings (can be modified in both versions):

- Included file extensions:
  - `.py`
  - `.xml`

- Skipped folders:
  - `tests`
  - `static`
  - `__pycache__`
  - `i18n`

### Modifying Settings

#### GUI Version
Use the Settings button in the toolbar to modify:
- Included file extensions
- Folders to skip

#### Command-Line Version
Edit the constants at the top of `flatten_file_data.py`:
```python
INCLUDE_FILES = ('.py', '.xml')
SKIP_FOLDERS = ['tests', 'static', "__pycache__", "i18n"]
```

## Output Format

The generated output file includes:
- Absolute path of the root directory
- Relative path of each included file
- Complete content of each file
- Clear separation between files

Example output:
```
Root folder: /absolute/path/to/directory

[relative/path/to/file1.py]
<content of file1.py>

[relative/path/to/file2.xml]
<content of file2.xml>
```

## Error Handling

Both versions include robust error handling for:
- Invalid directories
- Inaccessible files
- File reading/writing issues
- Invalid configurations

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
