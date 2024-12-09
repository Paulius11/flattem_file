import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                            QFileDialog, QLineEdit, QMessageBox, QToolBar,
                            QAction, QDialog, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class ConfigDialog(QDialog):
    def __init__(self, parent=None, initial_files=('.py', '.xml'), initial_folders=None):
        super().__init__(parent)
        if initial_folders is None:
            initial_folders = ['tests', 'static', "__pycache__", "i18n"]
            
        self.setWindowTitle("Configuration")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        # File extensions configuration
        files_group = QGroupBox("Include File Extensions")
        files_layout = QVBoxLayout()
        
        self.files_input = QLineEdit()
        self.files_input.setText(', '.join(initial_files))
        self.files_input.setPlaceholderText("Enter file extensions (e.g., .py, .xml)")
        
        files_layout.addWidget(QLabel("Enter file extensions separated by commas:"))
        files_layout.addWidget(self.files_input)
        files_group.setLayout(files_layout)
        
        # Skip folders configuration
        folders_group = QGroupBox("Skip Folders")
        folders_layout = QVBoxLayout()
        
        self.folders_input = QLineEdit()
        self.folders_input.setText(', '.join(initial_folders))
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
    
    def get_config(self):
        files = [ext.strip() for ext in self.files_input.text().split(',') if ext.strip()]
        folders = [folder.strip() for folder in self.folders_input.text().split(',') if folder.strip()]
        return files, folders

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Directory Content Generator")
        self.setMinimumSize(800, 600)
        
        # Initialize configuration
        self.include_files = ['.py', '.xml']
        self.skip_folders = ['tests', 'static', "__pycache__", "i18n"]
        
        self.setup_ui()

    def setup_ui(self):
        # Create toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Add folder selection to toolbar
        self.folder_input = QLineEdit()
        self.folder_input.setMinimumWidth(300)
        self.folder_input.setPlaceholderText("Enter folder path...")
        self.toolbar.addWidget(self.folder_input)
        
        browse_action = QAction("Browse", self)
        browse_action.triggered.connect(self.browse_folder)
        self.toolbar.addAction(browse_action)
        
        self.toolbar.addSeparator()
        
        # Add configuration action to toolbar
        config_action = QAction("Settings", self)
        config_action.triggered.connect(self.show_config_dialog)
        self.toolbar.addAction(config_action)
        
        generate_action = QAction("Generate", self)
        generate_action.triggered.connect(self.generate_content)
        self.toolbar.addAction(generate_action)
        
        self.toolbar.addSeparator()
        
        # Add copy and save actions to toolbar
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        self.toolbar.addAction(copy_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_to_file)
        self.toolbar.addAction(save_action)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont('Courier', 10))
        layout.addWidget(self.text_display)

    def show_config_dialog(self):
        dialog = ConfigDialog(self, self.include_files, self.skip_folders)
        if dialog.exec_() == QDialog.Accepted:
            self.include_files, self.skip_folders = dialog.get_config()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_input.setText(folder)

    def generate_content(self):
        root_dir = self.folder_input.text()
        if not root_dir or not os.path.isdir(root_dir):
            QMessageBox.warning(self, "Error", "Please select a valid directory.")
            return

        if not self.include_files:
            QMessageBox.warning(self, "Error", "Please configure at least one file extension.")
            return

        content = []
        content.append(f"Root folder: {os.path.abspath(root_dir)}\n")
        content.append(f"Including files: {', '.join(self.include_files)}")
        content.append(f"Skipping folders: {', '.join(self.skip_folders)}\n")

        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in self.skip_folders]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in self.include_files):
                    file_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(file_path, root_dir)
                    content.append(f"[{rel_path}]")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content.append(infile.read())
                    except Exception as e:
                        content.append(f"Error reading file: {str(e)}")
                    
                    content.append("\n")

        self.text_display.setText("\n".join(content))
        QMessageBox.information(self, "Success", "Content generated successfully!")

    def copy_to_clipboard(self):
        if not self.text_display.toPlainText():
            QMessageBox.warning(self, "Error", "No content to copy!")
            return
            
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_display.toPlainText())
        QMessageBox.information(self, "Success", "Content copied to clipboard!")

    def save_to_file(self):
        if not self.text_display.toPlainText():
            QMessageBox.warning(self, "Error", "No content to save!")
            return
            
        filename = f"directory_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.text_display.toPlainText())
            QMessageBox.information(self, "Success", f"Saved to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
