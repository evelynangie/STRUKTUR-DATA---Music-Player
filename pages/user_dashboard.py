from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QTabWidget, QListWidget, QListWidgetItem, QSlider,
                           QGroupBox, QLineEdit, QDialog, QDialogButtonBox, QFormLayout, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QPen, QColor, QBrush
from config import COLOR_ACCENT1, COLOR_ACCENT2, MUSIC_DIR
import pygame
import os
import time
import shutil
import random

class UserDashboard(QWidget):
    """Dashboard User"""
    logout_signal = pyqtSignal()

    def __init__(self, data_manager, username):
        super().__init__()
        self.data_manager = data_manager
        self.username = username
        self.current_playing_song = None
        self.is_paused = False
        self.is_looping = False
        self.song_length = 0
        self.is_seeking = False
        
        # Track posisi manual
        self.play_start_time = 0  # Waktu saat mulai play
        self.last_position = 0    # Posisi terakhir saat pause (dalam detik)
        self.seek_position = 0    # Posisi yang diinginkan saat seek (dalam detik)
        
        # Track playlist dan random mode
        self.playlist_finished = False
        self.played_songs = set()  # Track lagu yang sudah diputar untuk hindari repeat
        
        # Timer untuk progress dan auto-play detection
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        
        # Timer khusus untuk deteksi lagu selesai
        self.end_check_timer = QTimer()
        self.end_check_timer.timeout.connect(self.check_song_end)
        
        # Inisialisasi pygame mixer
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        self.init_ui()
        self.load_library()
        self.load_playlist()
        self.update_sidebar_profile()
        self.load_profile_image()

    def logout_action(self):
        """Menangani aksi logout"""
        self.logout_signal.emit()

    def init_ui(self):
        """Inisialisasi UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setStyleSheet(f"background-color: #000000;")
        sidebar.setMaximumWidth(250)
        self.sidebar_layout = QVBoxLayout(sidebar)
        self.sidebar_layout.setContentsMargins(20, 30, 20, 30)
        self.sidebar_layout.setSpacing(15)

        # Logo
        logo_label = QLabel("SPOTIPAI")
        logo_font = QFont()
        logo_font.setPointSize(20)
        logo_font.setBold(True)
        logo_label.setFont(logo_font)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(logo_label)

        self.sidebar_layout.addSpacing(30)

        # Item menu
        menu_label = QLabel("User Menu")
        menu_label.setStyleSheet(f"color: {COLOR_ACCENT2}; font-weight: bold; font-size: 10px;")
        self.sidebar_layout.addWidget(menu_label)

        home_btn = self.create_sidebar_button("🏠 Home")
        home_btn.setMaximumHeight(45)
        home_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT1};
                border-radius: 8px;
                color: white;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        home_btn.clicked.connect(lambda: self.switch_to_tab(0))  # Library tab
        self.sidebar_layout.addWidget(home_btn)

        playlist_btn = self.create_sidebar_button("📋 My Playlist")
        playlist_btn.setMaximumHeight(45)
        playlist_btn.clicked.connect(lambda: self.switch_to_tab(1))  # Playlist tab
        self.sidebar_layout.addWidget(playlist_btn)

        account_btn = self.create_sidebar_button("👤 Account")
        account_btn.setMaximumHeight(45)
        account_btn.clicked.connect(lambda: self.switch_to_tab(2))  # Account tab
        self.sidebar_layout.addWidget(account_btn)

        self.sidebar_layout.addSpacing(20)

        # Bagian bawah
        self.sidebar_layout.addStretch()

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
        logout_btn.clicked.connect(self.logout_action)
        self.sidebar_layout.addWidget(logout_btn)

        # Area konten
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(15)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabBar::tab {{
                background-color: {COLOR_ACCENT1};
                color: white;
                padding: 8px 20px;
                margin-right: 2px;
                border-radius: 8px 8px 0 0;
            }}
            QTabBar::tab:selected {{
                background-color: {COLOR_ACCENT2};
            }}
            QTabWidget::pane {{
                border: none;
            }}
        """)

        # Tab 1: Library
        library_tab = QWidget()
        library_layout = QVBoxLayout(library_tab)
        library_layout.setSpacing(15)

        lib_title = QLabel("Available Songs")
        lib_font = QFont()
        lib_font.setPointSize(14)
        lib_font.setBold(True)
        lib_title.setFont(lib_font)
        library_layout.addWidget(lib_title)

        self.library_table = QTableWidget()
        self.library_table.setColumnCount(4)
        self.library_table.setHorizontalHeaderLabels(["Title", "Artist", "Genre", "Action"])
        self.library_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.library_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.library_table.setMinimumHeight(300)
        library_layout.addWidget(self.library_table)

        self.tabs.addTab(library_tab, "🎵 Library")

        # Tab 2: Playlist
        playlist_tab = QWidget()
        playlist_layout = QVBoxLayout(playlist_tab)
        playlist_layout.setSpacing(15)

        pl_title = QLabel("My Playlist")
        pl_font = QFont()
        pl_font.setPointSize(14)
        pl_font.setBold(True)
        pl_title.setFont(pl_font)
        playlist_layout.addWidget(pl_title)

        self.playlist_table = QTableWidget()
        self.playlist_table.setColumnCount(4)
        self.playlist_table.setHorizontalHeaderLabels(["Title", "Artist", "Genre", "Action"])
        self.playlist_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.playlist_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.playlist_table.setMinimumHeight(300)
        playlist_layout.addWidget(self.playlist_table)

        self.tabs.addTab(playlist_tab, "📋 Playlist")

        # Tab 3: Account 
        account_tab = QWidget()
        account_layout = QVBoxLayout(account_tab)
        account_layout.setContentsMargins(20, 20, 20, 20)
        account_layout.setSpacing(20)

        # Profile Picture Section
        profile_pic_group = QGroupBox("Profile Picture")
        # group box background transparent and remove box border
        profile_pic_group.setStyleSheet(f"""
            QGroupBox {{
                color: white;
                font-weight: bold;
                background: transparent;
                border: none;
                padding-top: 6px;
            }}
        """)
        profile_pic_layout = QVBoxLayout(profile_pic_group)
        
        # Profile image display
        self.profile_image_label = QLabel()
        self.profile_image_label.setFixedSize(120, 120)
        self.profile_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_image_label.setStyleSheet("""
            background-color: transparent;
        """)
        profile_pic_layout.addWidget(self.profile_image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Username (store as attribute so we can update it immediately)
        self.account_username_label = QLabel(self.username)
        self.account_username_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        profile_pic_layout.addWidget(self.account_username_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Button layout
        button_layout = QHBoxLayout()
        
        upload_btn = QPushButton("Upload Photo")
        upload_btn.setMinimumHeight(40)
        upload_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT2};
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #6a1b9a;
            }}
        """)
        upload_btn.clicked.connect(self.upload_profile_image)
        button_layout.addWidget(upload_btn)

        self.remove_profile_btn = QPushButton("Remove")
        self.remove_profile_btn.setMinimumHeight(40)
        self.remove_profile_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #ff6b6b;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #ff5252;
            }}
        """)
        self.remove_profile_btn.clicked.connect(self.remove_profile_image)
        button_layout.addWidget(self.remove_profile_btn)

        profile_pic_layout.addLayout(button_layout)
        account_layout.addWidget(profile_pic_group)

        # small spacing before settings
        account_layout.addSpacing(20)

        # Account Settings Section
        settings_group = QGroupBox("Account Settings")
        settings_group.setStyleSheet(f"""
            QGroupBox {{
                color: white;
                font-weight: bold;
                border: none;
                padding-top: 10px;
            }}
        """)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(15)

        # Change Username button
        change_user_btn = QPushButton("Change Username")
        change_user_btn.setMinimumHeight(40)
        change_user_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #4a4a4a;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                text-align: left;
                padding-left: 15px;
            }}
            QPushButton:hover {{
                background-color: #5a5a5a;
            }}
        """)
        change_user_btn.clicked.connect(self.change_username_simple)
        settings_layout.addWidget(change_user_btn)

        # Change Password button
        change_pass_btn = QPushButton("Change Password")
        change_pass_btn.setMinimumHeight(40)
        change_pass_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #4a4a4a;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                text-align: left;
                padding-left: 15px;
            }}
            QPushButton:hover {{
                background-color: #5a5a5a;
            }}
        """)
        change_pass_btn.clicked.connect(self.change_password_simple)
        settings_layout.addWidget(change_pass_btn)

        account_layout.addWidget(settings_group)
        account_layout.addStretch()

        self.tabs.addTab(account_tab, "👤 Account")

        # Hide tab bar since navigation is through sidebar
        self.tabs.tabBar().setVisible(False)

        content_layout.addWidget(self.tabs)

        # Kontrol pemutaran
        playback_widget = QWidget()
        playback_widget.setStyleSheet(f"background-color: {COLOR_ACCENT1}; border-radius: 12px;")
        playback_layout = QVBoxLayout(playback_widget)
        playback_layout.setContentsMargins(20, 15, 20, 15)

        # Now playing
        now_playing_label = QLabel("Now Playing:")
        now_playing_label.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
        playback_layout.addWidget(now_playing_label)

        self.now_playing = QLabel("No song selected")
        self.now_playing.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        playback_layout.addWidget(self.now_playing)

        # Progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)  # Gunakan range lebih besar untuk presisi
        self.progress_slider.setValue(0)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #333;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #333;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #555;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        self.progress_slider.sliderPressed.connect(self.on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self.on_slider_released)
        self.progress_slider.sliderMoved.connect(self.on_slider_moved)  # Ganti dengan handler khusus
        # TAMBAHKAN: Custom property untuk track posisi drag
        self.drag_position = 0
        playback_layout.addWidget(self.progress_slider)

        # Label waktu
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setStyleSheet("color: white; font-size: 12px;")
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        self.total_time_label = QLabel("0:00")
        self.total_time_label.setStyleSheet("color: white; font-size: 12px;")
        time_layout.addWidget(self.total_time_label)
        playback_layout.addLayout(time_layout)

        # Kontrol
        control_layout = QHBoxLayout()

        self.play_btn = QPushButton("▶ Play")
        self.play_btn.setMinimumWidth(100)
        self.play_btn.setMinimumHeight(40)
        self.play_btn.clicked.connect(self.play_current)
        control_layout.addWidget(self.play_btn)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setMinimumWidth(100)
        self.pause_btn.setMinimumHeight(40)
        self.pause_btn.clicked.connect(self.pause_song)
        self.pause_btn.setEnabled(False)
        control_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setMinimumWidth(100)
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.clicked.connect(self.stop_song)
        control_layout.addWidget(self.stop_btn)

        prev_btn = QPushButton("⏮ Prev")
        prev_btn.setMinimumWidth(100)
        prev_btn.setMinimumHeight(40)
        prev_btn.clicked.connect(self.prev_song)
        control_layout.addWidget(prev_btn)

        next_btn = QPushButton("⏭ Next")
        next_btn.setMinimumWidth(100)
        next_btn.setMinimumHeight(40)
        next_btn.clicked.connect(self.next_song)
        control_layout.addWidget(next_btn)

        self.loop_btn = QPushButton("🔁 Loop")
        self.loop_btn.setMinimumWidth(100)
        self.loop_btn.setMinimumHeight(40)
        self.loop_btn.clicked.connect(self.toggle_loop)
        control_layout.addWidget(self.loop_btn)

        playlist_play_btn = QPushButton("▶ Playlist")
        playlist_play_btn.setMinimumWidth(100)
        playlist_play_btn.setMinimumHeight(40)
        playlist_play_btn.clicked.connect(self.play_playlist)
        control_layout.addWidget(playlist_play_btn)

        playback_layout.addLayout(control_layout)

        content_layout.addWidget(playback_widget)

        # Tambahkan ke layout utama
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

    def make_circular_pixmap(self, pixmap, size):
        """Membuat pixmap bulat dari gambar persegi"""
        # Resize to square
        square_pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                     Qt.TransformationMode.SmoothTransformation)
        
        # Create circular pixmap
        circular = QPixmap(size, size)
        circular.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(circular)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create circular clipping path
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        
        # Draw image
        painter.drawPixmap(0, 0, square_pixmap)

        painter.end()
        
        return circular

    def create_default_avatar(self, size=35):
        """Membuat avatar bulat default"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw circle
        painter.setBrush(QBrush(QColor("#333")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)
        
        # Draw avatar icon
        painter.setPen(QColor("white"))
        font = painter.font()
        font.setPointSize(size // 2)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "👤")
        
        painter.end()
        return pixmap

    def load_profile_image(self):
        """Memuat dan menampilkan gambar profil"""
        profile_image = self.data_manager.get_user_profile_image(self.username)
        
        if profile_image and os.path.exists(profile_image):
            # Load image and make it circular
            pixmap = QPixmap(profile_image)
            circular_pixmap = self.make_circular_pixmap(pixmap, 120)
            self.profile_image_label.setPixmap(circular_pixmap)
            self.remove_profile_btn.setVisible(True)
        else:
            # Create default avatar
            default_pixmap = self.create_default_avatar(120)
            self.profile_image_label.setPixmap(default_pixmap)
            self.remove_profile_btn.setVisible(False)

    def load_library(self):
        """Memuat lagu-lagu perpustakaan"""
        self.library_table.setRowCount(0)
        songs = self.data_manager.get_all_songs()

        for song in songs:
            row = self.library_table.rowCount()
            self.library_table.insertRow(row)

            self.library_table.setItem(row, 0, QTableWidgetItem(song.title))
            self.library_table.setItem(row, 1, QTableWidgetItem(song.artist))
            self.library_table.setItem(row, 2, QTableWidgetItem(song.genre))

            # Tombol aksi
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            play_btn = QPushButton("Play")
            play_btn.setMaximumWidth(70)
            play_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT1};
                    color: white;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: bold;
                }}
            """)
            play_btn.clicked.connect(lambda checked, s=song: self.play_song(s))
            action_layout.addWidget(play_btn)

            add_btn = QPushButton("+ Add")
            add_btn.setMaximumWidth(70)
            add_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT2};
                    color: white;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: bold;
                }}
            """)
            add_btn.clicked.connect(lambda checked, s=song: self.add_to_playlist(s))
            action_layout.addWidget(add_btn)

            self.library_table.setCellWidget(row, 3, action_widget)

    def load_playlist(self):
        """Memuat playlist pengguna"""
        self.playlist_table.setRowCount(0)
        songs = self.data_manager.get_user_playlist(self.username)

        for song in songs:
            row = self.playlist_table.rowCount()
            self.playlist_table.insertRow(row)

            self.playlist_table.setItem(row, 0, QTableWidgetItem(song.title))
            self.playlist_table.setItem(row, 1, QTableWidgetItem(song.artist))
            self.playlist_table.setItem(row, 2, QTableWidgetItem(song.genre))

            # Tombol aksi
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            play_btn = QPushButton("Play")
            play_btn.setMaximumWidth(70)
            play_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT1};
                    color: white;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: bold;
                }}
            """)
            play_btn.clicked.connect(lambda checked, s=song: self.play_song(s))
            action_layout.addWidget(play_btn)

            remove_btn = QPushButton("Remove")
            remove_btn.setMaximumWidth(70)
            remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ff6b6b;
                    color: white;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: bold;
                }}
            """)
            remove_btn.clicked.connect(lambda checked, s=song: self.remove_from_playlist(s))
            action_layout.addWidget(remove_btn)

            self.playlist_table.setCellWidget(row, 3, action_widget)

    def add_to_playlist(self, song):
        """Menambah lagu ke playlist"""
        if self.data_manager.add_to_playlist(self.username, song.song_id):
            self.load_playlist()
            QMessageBox.information(self, "Success", f"'{song.title}' added to playlist")
        else:
            QMessageBox.warning(self, "Info", f"'{song.title}' already in playlist")

    def remove_from_playlist(self, song):
        """Menghapus lagu dari playlist"""
        if self.data_manager.remove_from_playlist(self.username, song.song_id):
            self.load_playlist()
            QMessageBox.information(self, "Success", f"'{song.title}' removed from playlist")

    def play_song(self, song):
        """Memainkan lagu menggunakan pygame"""
        self.stop_song()  # Hentikan lagu saat ini

        self.current_playing_song = song
        self.played_songs.add(song.song_id)  # Track lagu yang sudah diputar
        self.now_playing.setText(f"♫ {song.title} — {song.artist}")
        self.is_paused = False
        self.progress_slider.setValue(0)  # Reset slider
        self.last_position = 0
        self.seek_position = 0

        # Coba muat dan mainkan file
        if song.file_path and os.path.exists(song.file_path):
            try:
                pygame.mixer.music.load(song.file_path)
                sound = pygame.mixer.Sound(song.file_path)
                self.song_length = sound.get_length()
                self.total_time_label.setText(self.format_time(self.song_length))
                
                # Mulai play
                pygame.mixer.music.play(-1 if self.is_looping else 1)
                
                # Set waktu mulai untuk tracking manual
                self.play_start_time = time.time()
                
                # Mulai timer
                self.progress_timer.start(100)  # Update lebih cepat (100ms)
                self.end_check_timer.start(500)  # Cek lagu selesai setiap 500ms
                self.play_btn.setEnabled(False)
                self.pause_btn.setEnabled(True)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to play song: {str(e)}")
                self.song_length = 0
        else:
            self.song_length = 0
            self.total_time_label.setText("0:00")
            self.play_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)

    def play_current(self):
        """Memainkan lagu saat ini"""
        if self.current_playing_song:
            if self.is_paused:
                # Lanjutkan dari posisi saat ini
                pygame.mixer.music.unpause()
                self.progress_timer.start(100)
                self.is_paused = False
                self.pause_btn.setText("⏸ Pause")
            else:
                self.play_song(self.current_playing_song)
        else:
            QMessageBox.warning(self, "Info", "No song selected")

    def pause_song(self):
        """Menjeda lagu"""
        if pygame.mixer.music.get_busy() and not self.is_paused:
            pygame.mixer.music.pause()
            self.progress_timer.stop()
            self.end_check_timer.stop()  # Stop end check saat pause
            self.is_paused = True
            
            # Simpan posisi saat ini sebelum pause
            if self.song_length > 0:
                current_time = time.time()
                elapsed = current_time - self.play_start_time
                self.last_position = elapsed % self.song_length if self.is_looping else min(elapsed, self.song_length)
                
            self.pause_btn.setText("▶ Resume")
        elif self.is_paused:
            # Resume dari posisi terakhir
            try:
                # Stop dan load ulang dari posisi terakhir
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.current_playing_song.file_path)
                pygame.mixer.music.play(-1 if self.is_looping else 1)
                
                # Coba set posisi
                try:
                    pygame.mixer.music.set_pos(self.last_position)
                except:
                    # Fallback: atur waktu mulai berdasarkan posisi
                    pass
                
                # Update waktu mulai untuk tracking
                self.play_start_time = time.time() - self.last_position
                
                self.progress_timer.start(100)
                self.end_check_timer.start(500)  # Start kembali end check
                self.is_paused = False
                self.pause_btn.setText("⏸ Pause")
            except Exception as e:
                print(f"Resume error: {e}")
                QMessageBox.warning(self, "Error", f"Failed to resume: {str(e)}")

    def stop_song(self):
        """Menghentikan lagu"""
        pygame.mixer.music.stop()
        self.progress_timer.stop()
        self.end_check_timer.stop()  # Jangan lupa stop timer ini juga
        self.progress_slider.setValue(0)
        self.song_length = 0
        self.current_playing_song = None
        self.now_playing.setText("No song selected")
        self.is_paused = False
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ Pause")
        self.current_time_label.setText("0:00")
        self.total_time_label.setText("0:00")
        
        # Reset tracking variables
        self.last_position = 0
        self.seek_position = 0
        self.play_start_time = 0

    def check_song_end(self):
        """Memeriksa apakah lagu telah berakhir dan memainkan berikutnya secara otomatis"""
        if self.is_looping or self.is_paused or not self.current_playing_song:
            return
            
        if not pygame.mixer.music.get_busy():
            # Musik sudah tidak aktif (berarti sudah selesai)
            print("Song ended, playing next...")
            self.end_check_timer.stop()
            self.next_song()

    def next_song(self):
        """Memainkan lagu berikutnya dengan prioritas: playlist > artis sama > acak, tanpa pengulangan hingga semua dimainkan"""
        # Jika sudah dalam mode random (playlist habis), langsung random
        if self.playlist_finished:
            self.play_random_from_library(silent=True)
            return
        
        # Cek dulu playlist user
        playlist_songs = self.data_manager.get_user_playlist(self.username)
        
        if playlist_songs and len(playlist_songs) > 0:
            # Ada playlist, cari next song dalam playlist
            if not self.current_playing_song:
                # Jika belum ada lagu yang dimainkan, mulai dari pertama di playlist
                self.play_song(playlist_songs[0])
                return
                
            # Cari index lagu saat ini di playlist
            current_index = -1
            for i, song in enumerate(playlist_songs):
                if song.song_id == self.current_playing_song.song_id:
                    current_index = i
                    break
            
            if current_index >= 0:
                # Ada di playlist, cek apakah ada next song
                if current_index < len(playlist_songs) - 1:
                    # Ada next song di playlist
                    next_song_obj = playlist_songs[current_index + 1]
                    self.play_song(next_song_obj)
                    return
                else:
                    # Sudah di akhir playlist, set flag dan lanjut ke random dari library
                    self.playlist_finished = True
                    self.play_random_from_library(silent=True)
                    return
            else:
                # Lagu saat ini tidak ada di playlist, mulai dari awal playlist
                self.play_song(playlist_songs[0])
                return
        else:
            # Playlist kosong, langsung random dari library
            self.playlist_finished = True
            self.play_random_from_library(silent=True)

    def play_random_from_library(self, silent=False):
        """Memainkan lagu acak dari perpustakaan dengan prioritas artis sama, menghindari lagu yang sudah dimainkan"""
        all_songs = self.data_manager.get_all_songs()
        if not all_songs:
            if not silent:
                QMessageBox.information(self, "No Songs", "No songs available in library")
            return
        
        if not self.current_playing_song:
            # Jika belum ada lagu, pilih random dari semua
            available_songs = [song for song in all_songs if song.song_id not in self.played_songs]
            if available_songs:
                random_song = random.choice(available_songs)
                self.play_song(random_song)
            else:
                if not silent:
                    QMessageBox.information(self, "All Songs Played", "All songs have been played. Playback stopped.")
                self.stop_song()
            return
        
        # Cari lagu dengan artis yang sama yang belum diputar
        current_artist = self.current_playing_song.artist
        same_artist_songs = [song for song in all_songs if song.song_id != self.current_playing_song.song_id and song.artist == current_artist and song.song_id not in self.played_songs]
        
        if same_artist_songs:
            random_song = random.choice(same_artist_songs)
            self.play_song(random_song)
            if not silent:
                self.now_playing.setText(f"♫ {random_song.title} — {random_song.artist} (Same Artist)")
        else:
            # Tidak ada artis sama yang belum diputar, pilih random dari semua yang belum diputar
            available_songs = [song for song in all_songs if song.song_id not in self.played_songs]
            
            if available_songs:
                random_song = random.choice(available_songs)
                self.play_song(random_song)
                if not silent:
                    self.now_playing.setText(f"♫ {random_song.title} — {random_song.artist} (Random)")
            else:
                # Semua lagu sudah diputar
                QMessageBox.information(self, "All Songs Played", "All songs have been played. Playback stopped.")
                self.stop_song()

    def prev_song(self):
        """Memainkan lagu sebelumnya dengan prioritas playlist"""
        # Cek dulu playlist user
        playlist_songs = self.data_manager.get_user_playlist(self.username)
        
        if playlist_songs and len(playlist_songs) > 0:
            # Ada playlist, cari prev song dalam playlist
            if not self.current_playing_song:
                # Jika belum ada lagu yang dimainkan, mulai dari terakhir di playlist
                self.play_song(playlist_songs[-1])
                return
                
            # Cari index lagu saat ini di playlist
            current_index = -1
            for i, song in enumerate(playlist_songs):
                if song.song_id == self.current_playing_song.song_id:
                    current_index = i
                    break
            
            if current_index >= 0:
                # Ada di playlist, cek apakah ada prev song
                if current_index > 0:
                    # Ada prev song di playlist
                    prev_song_obj = playlist_songs[current_index - 1]
                    self.play_song(prev_song_obj)
                    return
                else:
                    # Sudah di awal playlist, kembali ke akhir
                    prev_song_obj = playlist_songs[-1]
                    self.play_song(prev_song_obj)
                    return
            else:
                # Lagu saat ini tidak ada di playlist, mulai dari awal playlist
                self.play_song(playlist_songs[0])
                return
        else:
            # Playlist kosong, cari prev song dari history atau random
            self.play_random_from_library(silent=True)

    def update_progress(self):
        """Update progress slider secara realtime dengan tracking manual"""
        if not self.is_seeking and self.song_length > 0:
            if pygame.mixer.music.get_busy() and not self.is_paused:
                # Hitung posisi berdasarkan waktu
                current_time = time.time()
                elapsed = current_time - self.play_start_time
                
                # Handle looping
                if self.is_looping:
                    elapsed = elapsed % self.song_length
                elif elapsed > self.song_length:
                    # Song sudah selesai
                    elapsed = self.song_length
                    self.song_finished()
                
                # Hitung persentase (0-1000 untuk lebih smooth)
                value = int((elapsed / self.song_length) * 1000)
                value = min(1000, max(0, value))  # Clamp value
                
                # Update slider TANPA trigger event
                self.progress_slider.blockSignals(True)  # Blok sinyal sementara
                self.progress_slider.setValue(value)
                self.progress_slider.blockSignals(False)  # Buka blokir
                
                # Update time label
                self.current_time_label.setText(self.format_time(elapsed))

    def song_finished(self):
        """Dipanggil ketika lagu selesai (terdeteksi oleh tracking progress)"""
        if not self.is_looping and not self.is_paused:
            print("Song finished detected in update_progress")
            self.progress_timer.stop()
            self.end_check_timer.stop()
            
            # Auto-play next song dengan delay kecil
            QTimer.singleShot(200, self.next_song)  # Delay 200ms

    def seek_song(self, position):
        """Melompat ke posisi dalam lagu"""
        if self.current_playing_song and self.song_length > 0:
            # Konversi posisi 0-100, konversi ke detik
            self.seek_position = (position / 100) * self.song_length
            
            try:
                # Simpan state
                was_playing = pygame.mixer.music.get_busy() and not self.is_paused
                current_volume = pygame.mixer.music.get_volume() if pygame.mixer.music.get_busy() else 1.0
                
                # Stop musik
                pygame.mixer.music.stop()
                self.progress_timer.stop()
                
                # Load ulang musik
                pygame.mixer.music.load(self.current_playing_song.file_path)
                
                # Play dari posisi yang diinginkan
                pygame.mixer.music.play(-1 if self.is_looping else 1)
                
                # Coba set posisi
                try:
                    pygame.mixer.music.set_pos(self.seek_position)
                except:
                    # Jika set_pos tidak didukung, kita atur waktu mulai manual
                    pass
                
                # Update waktu mulai untuk tracking
                self.play_start_time = time.time() - self.seek_position
                self.last_position = self.seek_position
                
                # Set volume kembali
                pygame.mixer.music.set_volume(current_volume)
                
                # Update UI
                self.progress_slider.setValue(int((position / 100) * 1000))
                self.current_time_label.setText(self.format_time(self.seek_position))
                
                # Jika sebelumnya paused, tetap paused
                if not was_playing:
                    pygame.mixer.music.pause()
                    self.is_paused = True
                    self.pause_btn.setText("▶ Resume")
                else:
                    # Lanjutkan timer
                    self.progress_timer.start(100)
                    
            except Exception as e:
                print(f"Seek error: {e}")
                QMessageBox.warning(self, "Seek Error", f"Cannot seek: {str(e)}")
                
                # Reset ke posisi sebelumnya
                if pygame.mixer.music.get_busy():
                    self.progress_timer.start(100)

    def toggle_loop(self):
        """Mengaktifkan/nonaktifkan mode loop"""
        self.is_looping = not self.is_looping
        self.loop_btn.setText("🔁 Loop (ON)" if self.is_looping else "🔁 Loop")
        
        if self.current_playing_song and pygame.mixer.music.get_busy():
            # Restart dengan pengaturan loop baru
            try:
                # Simpan posisi saat ini
                if self.song_length > 0:
                    current_time = time.time()
                    current_pos = current_time - self.play_start_time
                    if self.is_looping:
                        current_pos = current_pos % self.song_length
                    else:
                        current_pos = min(current_pos, self.song_length)
                
                # Stop dan restart
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.current_playing_song.file_path)
                pygame.mixer.music.play(-1 if self.is_looping else 1)
                
                # Coba set posisi kembali
                try:
                    pygame.mixer.music.set_pos(current_pos)
                except:
                    pass
                
                # Update waktu mulai
                self.play_start_time = time.time() - current_pos
                
            except Exception as e:
                print(f"Toggle loop error: {e}")

    def on_slider_pressed(self):
        """Dipanggil saat user mulai drag slider"""
        self.is_seeking = True
        self.progress_timer.stop()
        
        # Simpan posisi awal drag
        self.drag_start_value = self.progress_slider.value()

    def on_slider_released(self):
        """Dipanggil saat user selesai drag slider"""
        if self.is_seeking:
            self.is_seeking = False
            
            # Dapatkan nilai akhir slider
            final_value = self.progress_slider.value()
            
            # Konversi ke persentase (0-100)
            position_percent = (final_value / 1000) * 100
            
            # Lakukan seek ke posisi akhir
            self.seek_song(position_percent)

    def on_slider_moved(self, position):
        """Handler khusus untuk sliderMoved signal"""
        if self.is_seeking and self.song_length > 0:
            # Update time label saja (tidak update slider value)
            seek_time = (position / 1000) * self.song_length
            self.current_time_label.setText(self.format_time(seek_time))
            
            # Simpan posisi drag untuk referensi
            self.drag_position = position

    def format_time(self, seconds):
        """Memformat detik ke MM:SS"""
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def switch_to_tab(self, index):
        """Beralih ke tab tertentu"""
        self.tabs.setCurrentIndex(index)

    def update_sidebar_profile(self):
        """Memperbarui sidebar dengan gambar profil"""
        # Remove existing profile
        for i in reversed(range(self.sidebar_layout.count())):
            widget = self.sidebar_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'objectName') and widget.objectName() == 'profile_widget':
                widget.setParent(None)

        # Create new profile widget
        profile_widget = QWidget()
        profile_widget.setObjectName('profile_widget')
        profile_layout = QHBoxLayout(profile_widget)
        profile_layout.setContentsMargins(0, 0, 0, 0)
        profile_layout.setSpacing(10)

        # Profile image or default
        profile_image = self.data_manager.get_user_profile_image(self.username)
        image_label = QLabel()
        image_label.setFixedSize(35, 35)
        
        if profile_image and os.path.exists(profile_image):
            pixmap = QPixmap(profile_image)
            circular = self.make_circular_pixmap(pixmap, 35)
            image_label.setPixmap(circular)
        else:
            default_pixmap = self.create_default_avatar(35)
            image_label.setPixmap(default_pixmap)
        
        profile_layout.addWidget(image_label)
        
        # Username
        username_label = QLabel(self.username)
        username_label.setStyleSheet("color: #b388ff; font-size: 12px; font-weight: bold;")
        profile_layout.addWidget(username_label)
        profile_layout.addStretch()

        # Add to sidebar before logout button
        self.sidebar_layout.insertWidget(self.sidebar_layout.count() - 1, profile_widget)

    def upload_profile_image(self):
        """Unggah gambar"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                image_path = selected_files[0]
                
                # Check if image
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    QMessageBox.warning(self, "Error", "Invalid image file")
                    return
                
                # Create profiles directory
                profiles_dir = os.path.join("assets", "images", "profiles")
                os.makedirs(profiles_dir, exist_ok=True)
                
                # Save as PNG
                new_path = os.path.join(profiles_dir, f"{self.username}_profile.png")
                
                try:
                    # Copy and make circular
                    pixmap.save(new_path, "PNG")
                    
                    # Update database
                    if self.data_manager.update_user_profile_image(self.username, new_path):
                        self.load_profile_image()
                        self.update_sidebar_profile()
                        QMessageBox.information(self, "Success", "Profile picture updated!")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to update profile")
                        
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to save image: {str(e)}")

    def remove_profile_image(self):
        """Menghapus gambar profil"""
        reply = QMessageBox.question(self, "Remove Photo", 
                                   "Remove profile picture?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Get current image
            current_image = self.data_manager.get_user_profile_image(self.username)
            
            # Remove file if exists
            if current_image and os.path.exists(current_image):
                try:
                    os.remove(current_image)
                except:
                    pass
            
            # Update database
            if self.data_manager.update_user_profile_image(self.username, ""):
                self.load_profile_image()
                self.update_sidebar_profile()
                QMessageBox.information(self, "Success", "Photo removed!")
            else:
                QMessageBox.warning(self, "Error", "Failed to remove photo")

    def change_username_simple(self):
        """Dialog perubahan username"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Change Username")
        dialog.setFixedSize(300, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Form
        form_layout = QFormLayout()
        
        new_username = QLineEdit()
        new_username.setPlaceholderText("New username")
        form_layout.addRow("New Username:", new_username)
        
        password = QLineEdit()
        password.setPlaceholderText("Your password")
        password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", password)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            if not new_username.text() or not password.text():
                QMessageBox.warning(self, "Error", "Please fill all fields")
                return
            
            # Verify password
            if not self.data_manager.verify_password(self.username, password.text()):
                QMessageBox.warning(self, "Error", "Wrong password")
                return
            
            # Update username
            if self.data_manager.update_username(self.username, new_username.text()):
                self.username = new_username.text()
                self.update_sidebar_profile()
                # Update account tab display and username label immediately
                self.update_account_tab()
                if hasattr(self, 'account_username_label'):
                    self.account_username_label.setText(self.username)
                    self.account_username_label.repaint()
                QMessageBox.information(self, "Success", "Username changed!")
            else:
                QMessageBox.warning(self, "Error", "Username already exists")

    def change_password_simple(self):
        """Dialog perubahan password"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Change Password")
        dialog.setFixedSize(300, 250)
        
        layout = QVBoxLayout(dialog)
        
        # Form
        form_layout = QFormLayout()
        
        old_pass = QLineEdit()
        old_pass.setPlaceholderText("Current password")
        old_pass.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Current:", old_pass)
        
        new_pass = QLineEdit()
        new_pass.setPlaceholderText("New password")
        new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("New:", new_pass)
        
        confirm_pass = QLineEdit()
        confirm_pass.setPlaceholderText("Confirm new")
        confirm_pass.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirm:", confirm_pass)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            if not all([old_pass.text(), new_pass.text(), confirm_pass.text()]):
                QMessageBox.warning(self, "Error", "Please fill all fields")
                return
            
            if new_pass.text() != confirm_pass.text():
                QMessageBox.warning(self, "Error", "New passwords don't match")
                return
            
            if len(new_pass.text()) < 6:
                QMessageBox.warning(self, "Error", "Password too short (min 6)")
                return
            
            # Verify old password
            if not self.data_manager.verify_password(self.username, old_pass.text()):
                QMessageBox.warning(self, "Error", "Current password is wrong")
                return
            
            # Update password
            if self.data_manager.update_password(self.username, new_pass.text()):
                QMessageBox.information(self, "Success", "Password changed!")
            else:
                QMessageBox.warning(self, "Error", "Failed to change password")

    def update_account_tab(self):
        """Memperbarui tampilan tab akun"""
        profile_image = self.data_manager.get_user_profile_image(self.username)
        
        if profile_image and os.path.exists(profile_image):
            pixmap = QPixmap(profile_image)
            circ = self.make_circular_pixmap(pixmap, 120)
            self.profile_image_label.setPixmap(circ)
            self.remove_profile_btn.setVisible(True)
        else:
            # Default avatar
            default = self.create_default_avatar(120)
            self.profile_image_label.setPixmap(default)
            self.remove_profile_btn.setVisible(False)
        # Update username label in account tab immediately
        if hasattr(self, 'account_username_label'):
            self.account_username_label.setText(self.username)
            self.account_username_label.repaint()

    def play_playlist(self):
        """Memainkan seluruh playlist dari awal"""
        playlist_songs = self.data_manager.get_user_playlist(self.username)
        
        if not playlist_songs:
            QMessageBox.information(self, "Empty Playlist", "Your playlist is empty")
            return
        
        # Reset state untuk mulai playlist baru
        self.playlist_finished = False
        self.played_songs.clear()  # Reset track lagu yang sudah diputar
        
        # Stop current song
        self.stop_song()
        
        # Mainkan lagu pertama
        self.play_song(playlist_songs[0])
        QMessageBox.information(self, "Playlist Started", 
                              f"Playing playlist with {len(playlist_songs)} songs")
