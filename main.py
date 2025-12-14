import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, COLOR_PRIMARY
from ui.stylesheet import get_stylesheet
from models import DataManager
from pages.auth_pages import LoginPage, SignupPage
from pages.admin_dashboard import AdminDashboard
from pages.user_dashboard import UserDashboard

import pygame

class MainApplication(QMainWindow):
    """Jendela utama aplikasi"""
    
    def __init__(self):
        super().__init__()
        
        # Inisialisasi audio mixer (pygame) untuk pemutaran musik
        pygame.mixer.init()
        
        # Inisialisasi pengelola data dan muat data awal
        self.data_manager = DataManager()
        self.data_manager.init_default_data()
        
        # Pengaturan jendela utama
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(800, 600)
        
        # Terapkan stylesheet global
        self.setStyleSheet(get_stylesheet())
        
        # Buat stacked widget untuk mengelola halaman UI
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Buat halaman autentikasi
        self.login_page = LoginPage(self.data_manager)
        self.signup_page = SignupPage(self.data_manager)
        
        # Tambah halaman ke stacked widget
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.signup_page)
        
        # Sambungkan sinyal-sinyal antar halaman
        self.login_page.login_signal.connect(self.on_login_success)
        self.login_page.switch_to_signup.connect(self.show_signup_page)
        
        self.signup_page.signup_signal.connect(self.show_login_page)
        self.signup_page.switch_to_login.connect(self.show_login_page)
        
        # Tampilkan halaman login terlebih dahulu
        self.show_login_page()
        
        # Referensi ke dashboard (dibuat saat login)
        self.admin_dashboard = None
        self.user_dashboard = None

    def show_login_page(self):
        """Tampilkan halaman login dan reset form"""
        self.login_page.reset_form()
        self.stacked_widget.setCurrentWidget(self.login_page)

    def show_signup_page(self):
        """Tampilkan halaman pendaftaran (signup)"""
        self.signup_page.reset_form()
        self.stacked_widget.setCurrentWidget(self.signup_page)

    def on_login_success(self, username):
        """Tindakan yang dijalankan setelah login sukses.
        Menentukan apakah user adalah admin atau user biasa, lalu menampilkan
        dashboard yang sesuai.
        """
        user = self.data_manager.get_user_by_username(username)
        
        if user and user.is_admin:
            # Tampilkan dashboard admin
            self.admin_dashboard = AdminDashboard(self.data_manager, username)
            self.admin_dashboard.logout_signal.connect(self.show_login_page)
            
            # Hapus instance admin dashboard lama jika ada
            for i in range(self.stacked_widget.count()):
                widget = self.stacked_widget.widget(i)
                if isinstance(widget, AdminDashboard) and widget != self.admin_dashboard:
                    self.stacked_widget.removeWidget(widget)
            
            # Tambah dan tampilkan dashboard admin baru
            self.stacked_widget.addWidget(self.admin_dashboard)
            self.stacked_widget.setCurrentWidget(self.admin_dashboard)
        else:
            # Tampilkan dashboard user biasa
            self.user_dashboard = UserDashboard(self.data_manager, username)
            self.user_dashboard.logout_signal.connect(self.show_login_page)
            
            # Hapus instance user dashboard lama jika ada
            for i in range(self.stacked_widget.count()):
                widget = self.stacked_widget.widget(i)
                if isinstance(widget, UserDashboard) and widget != self.user_dashboard:
                    self.stacked_widget.removeWidget(widget)
            
            # Tambah dan tampilkan dashboard user baru
            self.stacked_widget.addWidget(self.user_dashboard)
            self.stacked_widget.setCurrentWidget(self.user_dashboard)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create main window
    window = MainApplication()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
