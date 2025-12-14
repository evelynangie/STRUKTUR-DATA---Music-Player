# Commit Log - SPOTIPAI Desktop

## Riwayat Perkembangan Program

### Initial Setup (29-11-2025)
- Membuat struktur proyek dasar
- Menambahkan file config.py, models.py, main.py
- Implementasi struktur data: singly linked list untuk songs/users, doubly linked list untuk playlist
- Fitur dasar: add/view/edit/delete songs (Admin), login/signup (User)

### UI Development (01-12-2025)
- Menambahkan PyQt6 GUI dengan pages: auth_pages.py, admin_dashboard.py, user_dashboard.py
- Stylesheet dan layout responsive
- Integrasi pygame untuk pemutaran musik

### Fitur Utama (07-12-2025)
- Implementasi pemutaran musik dengan kontrol play/pause/stop/next/prev
- Playlist management: add/remove songs, play playlist
- Logika next/prev: prioritas playlist > artis sama > random tanpa repeat

### Bug Fixes & Finalisasi (12-12-2025)
- Perbaikan song_id unik menggunakan counter per huruf pertama
- Optimasi UI dan error handling

### Final Version
- Aplikasi lengkap dengan semua fitur
- Dokumentasi lengkap di README.md

## Struktur Data Digunakan
- Singly Linked List: Penyimpanan songs dan users
- Doubly Linked List: Playlist per user untuk navigasi maju/mundur
- Dictionary: Counter untuk song_id dan serialisasi data