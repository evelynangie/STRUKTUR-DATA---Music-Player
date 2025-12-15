# SPOTIPAI Desktop - Music Player Application 

## Project Overview

SPOTIPAI Desktop adalah aplikasi media player desktop yang dibangun dengan PyQt6. Aplikasi ini memiliki fitur manajemen lagu untuk admin dan fitur pemutaran musik untuk user biasa.

## Fitur Utama

### Admin Features
- 🎵 Kelola Library Lagu (Tambah, Edit, Hapus)
- 📊 Dashboard dengan tampilan daftar lagu lengkap
- 🔐 Login dengan akun admin

### User Features
- 🎵 Browse dan putar musik dari library
- 📋 Buat dan kelola playlist pribadi
- ▶️ Kontrol playback (Play, Pause, Stop, Next, Prev, Loop)
- 🔐 Akun user dengan password

## Li

- **Python 3.10**
- **PyQt6** - GUI Framework
- **Pygame** - Audio playback
- **JSON** - Data storage

## Struktur Project

```
SPOTIPAI_Desktop/
├── main.py                # Entry point aplikasi
├── config.py              # Configuration & constants
├── models.py              # Data models & JSON manager
│
├── ui/
│   ├── __init__.py
│   └── stylesheet.py      # Global stylesheet PyQt
│
├── pages/
│   ├── __init__.py
│   ├── auth_pages.py      # Login & Signup pages
│   ├── admin_dashboard.py # Admin dashboard
│   └── user_dashboard.py  # User dashboard
│
├── assets/
│   ├── images/           # Image assets
│   │   ├── login.png
│   │   └── signup.png
│   └── music/            # Audio files
│
├── data/                 # Data files (JSON)
│   ├── users.json
│   ├── songs.json
│   └── playlists.json
│
└── README.md            # Dokumentasi
```

## Prerequisites

- **Python 3.10** atau versi lebih baru
- **pip** untuk menginstall dependencies

## Instalasi & Setup

### 1. Clone Repository

```bash
git clone <URL_REPOSITORY_ANDA>
cd SPOTIPAI_Desktop
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi

```bash
python main.py
```

## Penggunaan

### Login Default Admin
- **Username:** admin
- **Password:** admin123

### Membuat User Baru
1. Klik "Sign up" di halaman login
2. Isi username dan password
3. Klik "Sign Up"
4. Kembali ke login dan masuk dengan akun baru

### Sebagai Admin
1. Login dengan akun admin
2. Dashboard akan menampilkan "Manage Songs"
3. Dapat menambah, edit, dan menghapus lagu

### Sebagai User
1. Login dengan akun user
2. Di tab "Library" dapat melihat semua lagu
3. Klik "Play" untuk memutar atau "+ Add" untuk menambah ke playlist
4. Di tab "Playlist" dapat melihat lagu-lagu di playlist pribadi
5. Gunakan kontrol playback untuk mengontrol musik

## Penjelasan Arsitektur

### Models (models.py)
- **SongNode**: Merepresentasikan satu lagu
- **UserNode**: Merepresentasikan satu user
- **DataManager**: Manager untuk mengelola semua data
  - Menyimpan dan load data dari JSON files
  - Implementasi linked list untuk songs dan users

### Pages (pages/)
- **LoginPage**: Halaman login user
- **SignupPage**: Halaman registrasi user baru
- **AdminDashboard**: Dashboard untuk admin (manage songs)
- **UserDashboard**: Dashboard untuk user biasa (play music)

### UI (ui/)
- **stylesheet.py**: Stylesheet global dengan tema custom (dark, purple, dan pink )

### Config (config.py)
- Berisi definisi path global, warna, dan nilai konstanta

## Tema Warna

- **Primary (Background):** #0d0d0d (Black)
- **Accent 1 (Buttons):** #b388ff (Soft purple)
- **Accent 2 (Hover):** #ffb3d9 (Soft pink)
- **Text:** #ffffff (White)
- **Card Background:** #1a1a1a (Dark grey)

## Audio Playback

Menggunakan **Pygame Mixer**:
- `pygame.mixer.music.load(file_path)` - Load audio file
- `pygame.mixer.music.play()` - Play audio
- `pygame.mixer.music.pause()` - Pause audio
- `pygame.mixer.music.unpause()` - Resume audio
- `pygame.mixer.music.stop()` - Stop audio

Pastikan file MP3 ada di folder yang ditunjuk atau di `assets/music/`

## Data Storage

Data disimpan dalam format JSON di folder `data/`:
- **users.json** - Data user (username, password, playlist)
- **songs.json** - Data lagu (title, artist, genre, file_path)
  
## Troubleshooting

### Error: "No module named 'PyQt6'"
```bash
pip install PyQt6
```

### Error: "No module named 'pygame'"
```bash
pip install pygame
```

### Musik tidak bisa diputar
- Pastikan file MP3 ada di path yang benar
- Atau upload file MP3 ke folder `assets/music/`

### Data tidak tersimpan
- Pastikan folder `data/` ada dan dapat ditulis
- Check permission folder

## Development Notes

- Data otomatis tersimpan ke JSON setiap kali ada perubahan
- Admin user (admin/admin123) terinisialisasi saat first run
- Sample songs sudah ditambahkan saat first run
- QStackedWidget digunakan untuk navigasi antar halaman
- Implementasi Linked List

## Lisensi & Author

Dikembangkan untuk tugas Struktur Data Semester 3

### Anggota Kelompok (Developer)
- Evelyna Angie 
- Cindy Natasa
- Ivana Gabby Lauretta

### Repository GitHub
- https://github.com/evelynangie/STRUKTUR-DATA---Music-Player

Enjoy our program ^-^ 🎵
