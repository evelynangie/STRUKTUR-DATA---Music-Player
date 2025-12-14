from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QColor
from config import IMAGES_DIR, COLOR_ACCENT1, COLOR_ACCENT2
import os

class LoginPage(QWidget):
    """Halaman Login"""
    login_signal = pyqtSignal(str)  # Signal untuk hasil login (username)
    switch_to_signup = pyqtSignal()  # Signal untuk switch ke signup

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()

    def init_ui(self):
        """Inisialisasi UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sisi kiri: Form
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(60, 0, 60, 0)
        left_layout.setSpacing(15)
        left_layout.addStretch(1)

        # Judul
        title_label = QLabel("SPOTIPAI")
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Desktop Music Player")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #b388ff;")
        left_layout.addWidget(subtitle_label)

        left_layout.addSpacing(30)

        # Kolom username
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: {COLOR_ACCENT1}; font-weight: bold;")
        left_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(40)
        left_layout.addWidget(self.username_input)

        # Kolom password
        password_label = QLabel("Password:")
        password_label.setStyleSheet(f"color: {COLOR_ACCENT1}; font-weight: bold;")
        left_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        left_layout.addWidget(self.password_input)

        left_layout.addSpacing(10)

        # Tombol login
        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(45)
        login_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        login_btn.clicked.connect(self.login_action)
        left_layout.addWidget(login_btn)

        # Link sign up
        signup_label = QLabel("Don't have an account? <a href='#' style='color: #b388ff; text-decoration: none;'><b>Sign up</b></a>")
        signup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signup_label.setOpenExternalLinks(False)
        signup_label.linkActivated.connect(self.on_signup_clicked)
        left_layout.addWidget(signup_label)

        left_layout.addStretch(1)

        # Sisi kanan: Gambar
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)

        # Try to load image
        image_label = QLabel()
        image_path = os.path.join(IMAGES_DIR, 'login.jpg')

        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaledToHeight(600, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)

        right_layout.addWidget(image_label)
        right_layout.setAlignment(image_label, Qt.AlignmentFlag.AlignCenter)

        # Tambahkan ke layout utama
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)

    def login_action(self):
        """Menangani klik tombol login"""
        # Ambil input dan bersihkan whitespace di kedua ujung
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Validasi sederhana: input tidak boleh kosong
        if not username or not password:
            QMessageBox.warning(self, "Kesalahan", "Username dan password tidak boleh kosong")
            return

        # Gunakan DataManager untuk memverifikasi kredensial
        user = self.data_manager.login(username, password)
        if user:
            # Emit signal sukses (username)
            self.login_signal.emit(username)
        else:
            QMessageBox.critical(self, "Kesalahan", "Username atau password salah")

    def on_signup_clicked(self):
        """Menangani klik link signup"""
        self.switch_to_signup.emit()

    def reset_form(self):
        """Reset kolom form"""
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()


class SignupPage(QWidget):
    """Halaman Signup"""
    signup_signal = pyqtSignal()  # Signal untuk hasil signup sukses
    switch_to_login = pyqtSignal()  # Signal untuk switch ke login

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()

    def init_ui(self):
        """Inisialisasi UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sisi kiri: Gambar
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 20, 20)

        image_label = QLabel()
        image_path = os.path.join(IMAGES_DIR, 'signup.jpg')

        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaledToHeight(600, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)

        left_layout.addWidget(image_label)
        left_layout.setAlignment(image_label, Qt.AlignmentFlag.AlignCenter)

        # Sisi kanan: Form
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(60, 0, 60, 0)
        right_layout.setSpacing(15)
        right_layout.addStretch(1)

        # Judul
        title_label = QLabel("Create Account")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(title_label)

        right_layout.addSpacing(20)

        # Kolom username
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: {COLOR_ACCENT1}; font-weight: bold;")
        right_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        self.username_input.setMinimumHeight(40)
        right_layout.addWidget(self.username_input)

        # Kolom password
        password_label = QLabel("Password:")
        password_label.setStyleSheet(f"color: {COLOR_ACCENT1}; font-weight: bold;")
        right_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Create a strong password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        right_layout.addWidget(self.password_input)

        right_layout.addSpacing(10)

        # Tombol sign up
        signup_btn = QPushButton("Sign Up")
        signup_btn.setMinimumHeight(45)
        signup_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        signup_btn.clicked.connect(self.signup_action)
        right_layout.addWidget(signup_btn)

        # Link login
        login_label = QLabel("Already have an account? <a href='#' style='color: #b388ff; text-decoration: none;'><b>Login</b></a>")
        login_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_label.setOpenExternalLinks(False)
        login_label.linkActivated.connect(self.on_login_clicked)
        right_layout.addWidget(login_label)

        right_layout.addStretch(1)

        # Tambahkan ke layout utama
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)

    def signup_action(self):
        """Menangani klik tombol signup"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "All fields are required")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return

        if self.data_manager.register(username, password):
            QMessageBox.information(self, "Success", "Account created successfully! Please login.")
            self.reset_form()
            self.switch_to_login.emit()
        else:
            QMessageBox.critical(self, "Error", "Username already exists")

    def on_login_clicked(self):
        """Menangani klik link login"""
        self.switch_to_login.emit()

    def reset_form(self):
        """Reset kolom form"""
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()
