import os
import json

# Path dasar dan aset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
MUSIC_DIR = os.path.join(ASSETS_DIR, 'music')
# Direktori tempat menyimpan file data aplikasi (JSON)
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Nama file data utama
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
SONGS_FILE = os.path.join(DATA_DIR, 'songs.json')

# Colors
COLOR_PRIMARY = "#0d0d0d"       # Black
COLOR_ACCENT1 = "#b388ff"       # Soft purple
COLOR_ACCENT2 = "#ffb3d9"       # Soft pink
COLOR_TEXT = "#ffffff"          # White
COLOR_CARD = "#1a1a1a"          # Dark grey
COLOR_HOVER = "#b388ff"         # Soft purple 

# Window
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
WINDOW_TITLE = "SPOTIPAI Desktop"

# Admin USN & PASS
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Border radius
BORDER_RADIUS = 12
