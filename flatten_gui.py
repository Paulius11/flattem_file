import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                            QFileDialog, QLineEdit, QMessageBox, QToolBar,
                            QAction, QDialog, QGroupBox, QShortcut)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QIcon, QKeySequence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_FILE_EXTENSIONS = {'.py', '.xml'}
DEFAULT_SKIP_FOLDERS = {'tests', 'static', '__pycache__', 'i18n'}
WINDOW_TITLE = "Directory Content Generator"
WINDOW_MIN_SIZE = (800, 600)
SETTINGS_FILE = 'config.json'

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass

@dataclass
class Configuration:
    """Data class to hold application configuration."""
    include_files: Set[str]
    skip_folders: Set[str]

    @classmethod
    def get_defaults(cls) -> 'Configuration':
        return cls(
            include_files=DEFAULT_FILE_EXTENSIONS.copy(),
            skip_folders=DEFAULT_SKIP_FOLDERS.copy()
        )

    def save(self, filepath: Path = Path(SETTINGS_FILE)) -> None:
        """Save configuration to JSON file."""
        try:
            config_data = {
                'include_files': list(self.include_files),
                'skip_folders': list(self.skip_folders)
            }
            with filepath.open('w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise ConfigurationError(f"Could not save configuration: {e}")

    @classmethod
    def load(cls, filepath: Path = Path(SETTINGS_FILE)) -> 'Configuration':
        """Load configuration from JSON file."""
        try:
            if not filepath.exists():
                return cls.get_defaults()
            
            with filepath.open('r') as f:
                config_data = json.load(f)
            
            return cls(
                include_files=set(config_data.get('include_files', DEFAULT_FILE_EXTENSIONS)),
                skip_folders=set(config_data.get('skip_folders', DEFAULT_SKIP_FOLDERS))
            )
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return cls.get_defaults()

class ConfigDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None, config: Optional[Configuration] = None):
        super().__init__(parent)
        self.config = config or Configuration.get_defaults()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the dialog UI components."""
        self.setWindowTitle("Configuration")
        self.setModal(True)
        layout = QVBoxLayout(self)

        # File extensions configuration
        files_group = QGroupBox("Include File Extensions")
        files_layout = QVBoxLayout()
        
        self.files_input = QLineEdit()
        self.files_input.setText(', '.join(self.config.include_files))
        self.files_input.setPlaceholderText("Enter file extensions (e.g., .py, .xml)")
        
        files_layout.addWidget(QLabel("Enter file extensions separated by commas:"))
        files_layout.addWidget(self.files_input)
        files_group.setLayout(files_layout)
        
        # Skip folders configuration
        folders_group = QGroupBox("Skip Folders")
        folders_layout = QVBoxLayout()
        
        self.folders_input = QLineEdit()
        self.folders_input.setText(', '.join(self.config.skip_folders))
        self.folders_input.setPlaceholderText("Enter folder names to skip")
        
        folders_layout.addWidget(QLabel("Enter folder names to skip separated by commas:"))
        folders_layout.addWidget(self.folders_input)
        folders_group.setLayout(folders_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        
        # Add all to main layout
        layout.addWidget(files_group)
        layout.addWidget(folders_group)
        layout.addLayout(buttons_layout)

    def get_config(self) -> Configuration:
        """Get the configuration from dialog inputs."""
        return Configuration(
            include_files={ext.strip() for ext in self.files_input.text().split(',') if ext.strip()},
            skip_folders={folder.strip() for folder in self.folders_input.text().split(',') if folder.strip()}
        )

class DirectoryScanner:
    """Handles directory scanning and content generation."""
    
    def __init__(self, config: Configuration):
        self.config = config

    def scan_directory(self, root_dir: Path) -> str:
        """Scan directory and generate content."""
        if not root_dir.is_dir():
            raise ValueError(f"Invalid directory: {root_dir}")

        content = []
        content.append(f"Root folder: {root_dir.absolute()}\n")

        for file_path in self._iterate_files(root_dir):
            rel_path = file_path.relative_to(root_dir)
            content.append(f"[{rel_path}]")
            
            try:
                content.append(file_path.read_text(encoding='utf-8'))
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                content.append(f"Error reading file: {str(e)}")
            
            content.append("\n")

        return "\n".join(content)

    def _iterate_files(self, root_dir: Path):
        """Iterator for matching files in directory."""
        for path in root_dir.rglob('*'):
            if path.is_file() and any(str(path).endswith(ext) for ext in self.config.include_files):
                if not any(skip in path.parts for skip in self.config.skip_folders):
                    yield path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Configuration.load()
        self.scanner = DirectoryScanner(self.config)
        self.previous_path = None
        self.previous_line_count = 0
        self._setup_ui()
        self._setup_shortcuts()

    def _setup_ui(self) -> None:
        """Setup the main window UI components."""
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        
        # Create toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Add folder selection to toolbar
        self.folder_input = QLineEdit()
        self.folder_input.setMinimumWidth(300)
        self.folder_input.setPlaceholderText("Enter folder path...")
        self.toolbar.addWidget(self.folder_input)
        
        # Add actions
        self._create_action("Browse", self.browse_folder, QKeySequence.Open)
        self.toolbar.addSeparator()
        self._create_action("Settings", self.show_config_dialog, QKeySequence.Preferences)
        self._create_action("Generate", self.generate_content, QKeySequence("Ctrl+G"))
        self.toolbar.addSeparator()
        self._create_action("Copy", self.copy_to_clipboard, QKeySequence.Copy)
        self._create_action("Save", self.save_to_file, QKeySequence.Save)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont('Courier', 10))
        self.text_display.textChanged.connect(self._update_line_count)
        layout.addWidget(self.text_display)
        
        # Create status bar
        self.statusBar = self.statusBar()
        self._update_line_count()

    def _create_action(self, text: str, slot, shortcut: Optional[QKeySequence] = None) -> None:
        """Helper method to create toolbar actions."""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        shortcut_text = shortcut.toString() if isinstance(shortcut, QKeySequence) else str(shortcut) if shortcut else 'No shortcut'
        action.setToolTip(f"{text} ({shortcut_text})")

        action.triggered.connect(slot)
        self.toolbar.addAction(action)

    def _update_line_count(self) -> None:
        """Update the line count in the status bar."""
        text = self.text_display.toPlainText()
        current_path = Path(self.folder_input.text()) if self.folder_input.text() else None
        
        if text:
            current_line_count = text.count('\n') + 1
            status_message = f"Total lines: {current_line_count:,}"
            
            if (current_path and self.previous_path 
                and current_path == self.previous_path 
                and self.previous_line_count > 0):
                difference = current_line_count - self.previous_line_count
                if difference != 0:
                    status_message += f" ({'+'if difference > 0 else ''}{difference:,} lines)"
            
            self.statusBar.showMessage(status_message)
            self.previous_line_count = current_line_count
            self.previous_path = current_path
        else:
            self.statusBar.showMessage("Total lines: 0")
            self.previous_line_count = 0

    def _setup_shortcuts(self) -> None:
        """Setup additional keyboard shortcuts."""
        QShortcut(QKeySequence.Quit, self, self.close)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close)

    def show_config_dialog(self) -> None:
        """Show the configuration dialog."""
        dialog = ConfigDialog(self, self.config)
        if dialog.exec_() == QDialog.Accepted:
            self.config = dialog.get_config()
            self.scanner.config = self.config
            self.config.save()

    def browse_folder(self) -> None:
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_input.setText(folder)

    def generate_content(self) -> None:
        """Generate content from selected directory."""
        try:
            root_dir = Path(self.folder_input.text())
            if not root_dir.is_dir():
                raise ValueError("Invalid directory")

            if not self.config.include_files:
                raise ConfigurationError("No file extensions configured")

            content = self.scanner.scan_directory(root_dir)
            self.text_display.setText(content)
            logger.info("Content generated successfully")
            QMessageBox.information(self, "Success", "Content generated successfully!")
            
        except (ValueError, ConfigurationError) as e:
            logger.error(f"Error generating content: {e}")
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def copy_to_clipboard(self) -> None:
        """Copy content to clipboard."""
        content = self.text_display.toPlainText()
        if not content:
            QMessageBox.warning(self, "Error", "No content to copy!")
            return
            
        QApplication.clipboard().setText(content)
        logger.info("Content copied to clipboard")
        QMessageBox.information(self, "Success", "Content copied to clipboard!")

    def save_to_file(self) -> None:
        """Save content to file."""
        content = self.text_display.toPlainText()
        if not content:
            QMessageBox.warning(self, "Error", "No content to save!")
            return
            
        filename = f"directory_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            Path(filename).write_text(content, encoding='utf-8')
            logger.info(f"Content saved to {filename}")
            QMessageBox.information(self, "Success", f"Saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
