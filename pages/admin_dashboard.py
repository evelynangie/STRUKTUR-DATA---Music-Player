from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QTableWidget, QTableWidgetItem, QLineEdit, QSpinBox, 
                           QComboBox, QFileDialog, QMessageBox, QDialog, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from config import COLOR_ACCENT1, COLOR_ACCENT2, COLOR_CARD, MUSIC_DIR
import os

class AddSongDialog(QDialog):
    """Dialog untuk tambah/edit lagu"""
    def __init__(self, parent=None, song=None):
        super().__init__(parent)
        self.song = song
        self.setWindowTitle("Add Song" if not song else "Edit Song")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        """Inisialisasi UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title
        title_label = QLabel("Title:")
        title_label.setStyleSheet(f"color: {COLOR_ACCENT1}; font-weight: bold;")
        layout.addWidget(title_label)

        self.title_input = QLineEdit()
        self.title_input.setMinimumHeight(35)
        if self.song:
            self.title_input.setText(self.song.title)
        layout.addWidget(self.title_input)

        # Artist
        artist_label = QLabel("Artist:")
        artist_label.setStyleSheet(f"color: {COLOR_ACCENT1}; font-weight: bold;")
        layout.addWidget(artist_label)

        self.artist_input = QLineEdit()
        self.artist_input.setMinimumHeight(35)
        if self.song:
            self.artist_input.setText(self.song.artist)
        layout.addWidget(self.artist_input)

        # Genre
        genre_label = QLabel("Genre:")
        genre_label.setStyleSheet(f"color: {COLOR_ACCENT1}; font-weight: bold;")
        layout.addWidget(genre_label)

        self.genre_input = QLineEdit()
        self.genre_input.setMinimumHeight(35)
        if self.song:
            self.genre_input.setText(self.song.genre)
        layout.addWidget(self.genre_input)

        # File path
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected" if not self.song else self.song.file_path)
        self.file_label.setStyleSheet("color: #888888;")
        file_layout.addWidget(self.file_label)

        browse_btn = QPushButton("Browse")
        browse_btn.setMaximumWidth(100)
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        layout.addSpacing(10)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def browse_file(self):
        """Browse file MP3"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Music File", MUSIC_DIR, "MP3 Files (*.mp3);;All Files (*)"
        )
        if file_path:
            self.file_label.setText(file_path)

    def get_data(self):
        """Get data dari form"""
        return {
            "title": self.title_input.text(),
            "artist": self.artist_input.text(),
            "genre": self.genre_input.text(),
            "file_path": self.file_label.text()
        }


class AdminDashboard(QWidget):
    """Dashboard Admin"""
    logout_signal = pyqtSignal()

    def __init__(self, data_manager, username):
        super().__init__()
        self.data_manager = data_manager
        self.username = username
        self.init_ui()
        self.load_songs()

    def init_ui(self):
        """Inisialisasi UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setStyleSheet(f"background-color: #000000;")
        sidebar.setMaximumWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(15)

        # Logo
        logo_label = QLabel("SPOTIPAI")
        logo_font = QFont()
        logo_font.setPointSize(20)
        logo_font.setBold(True)
        logo_label.setFont(logo_font)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        sidebar_layout.addSpacing(30)

        # Menu items
        menu_label = QLabel("Admin Menu")
        menu_label.setStyleSheet(f"color: {COLOR_ACCENT2}; font-weight: bold; font-size: 10px;")
        sidebar_layout.addWidget(menu_label)

        dashboard_btn = self.create_sidebar_button("📊 Dashboard")
        dashboard_btn.setMaximumHeight(45)
        sidebar_layout.addWidget(dashboard_btn)

        songs_btn = self.create_sidebar_button("🎵 Manage Songs")
        songs_btn.setMaximumHeight(45)
        songs_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT1};
                border-radius: 8px;
                color: white;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        sidebar_layout.addWidget(songs_btn)

        sidebar_layout.addSpacing(20)

        # Bottom section
        sidebar_layout.addStretch()

        user_label = QLabel(f"👤 {self.username}")
        user_label.setStyleSheet("color: #b388ff; font-size: 11px;")
        sidebar_layout.addWidget(user_label)

        logout_btn = QPushButton("Logout")
        logout_btn.setMinimumHeight(40)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #ff6b6b;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: #ff5252;
            }}
        """)
        logout_btn.clicked.connect(self.logout_signal.emit)
        sidebar_layout.addWidget(logout_btn)

        # Content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Song Library")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()

        add_btn = QPushButton("+ Add Song")
        add_btn.setMinimumWidth(150)
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self.add_song)
        header_layout.addWidget(add_btn)

        content_layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Title", "Artist", "Genre", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setMinimumHeight(400)
        content_layout.addWidget(self.table)

        # Add to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content, 1)

    def create_sidebar_button(self, text):
        """Membuat tombol sidebar"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                text-align: left;
                padding: 10px;
                font-weight: bold;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ACCENT1};
            }}
        """)
        return btn

    def load_songs(self):
        """Load songs ke table"""
        self.table.setRowCount(0)
        songs = self.data_manager.get_all_songs()

        for song in songs:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(song.title))
            self.table.setItem(row, 1, QTableWidgetItem(song.artist))
            self.table.setItem(row, 2, QTableWidgetItem(song.genre))

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            edit_btn = QPushButton("Edit")
            edit_btn.setMaximumWidth(80)
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT1};
                    color: white;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: bold;
                }}
            """)
            edit_btn.clicked.connect(lambda checked, s=song: self.edit_song(s))
            action_layout.addWidget(edit_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setMaximumWidth(80)
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ff6b6b;
                    color: white;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: bold;
                }}
            """)
            delete_btn.clicked.connect(lambda checked, s=song: self.delete_song(s))
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 3, action_widget)

    def add_song(self):
        """Add lagu baru"""
        dialog = AddSongDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.data_manager.add_song(
                data["title"], data["artist"], data["genre"],
                data["file_path"]
            )
            self.load_songs()
            QMessageBox.information(self, "Success", "Song added successfully")

    def edit_song(self, song):
        """Edit lagu"""
        dialog = AddSongDialog(self, song)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.data_manager.update_song(
                song.song_id,
                data["title"], data["artist"], data["genre"],
                data["file_path"]
            )
            self.load_songs()
            QMessageBox.information(self, "Success", "Song updated successfully")

    def delete_song(self, song):
        """Delete lagu"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{song.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_song(song.song_id)
            self.load_songs()
            QMessageBox.information(self, "Success", "Song deleted successfully")
