import json
import os
from config import USERS_FILE, SONGS_FILE, DATA_DIR, ADMIN_USERNAME, ADMIN_PASSWORD

class SongNode:
    """Node untuk song dalam linked list"""
    def __init__(self, song_id, title, artist, genre, file_path=""):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.genre = genre
        self.file_path = file_path
        self.next = None

    def to_dict(self):
        return {
            "song_id": self.song_id,
            "title": self.title,
            "artist": self.artist,
            "genre": self.genre,
            "file_path": self.file_path
        }

    @staticmethod
    def from_dict(data):
        return SongNode(
            data["song_id"], data["title"], data["artist"],
            data["genre"], data.get("file_path", "")
        )


class PlaylistNode:
    """Node untuk doubly linked list playlist"""
    def __init__(self, song_id):
        self.song_id = song_id
        self.prev = None
        self.next = None

    def to_dict(self):
        return {"song_id": self.song_id}

    @staticmethod
    def from_dict(data):
        return PlaylistNode(data["song_id"])


class DoublyLinkedList:
    """Doubly linked list untuk playlist"""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self):
        return self.head is None

    def append(self, song_id):
        """Tambah song ke akhir playlist"""
        new_node = PlaylistNode(song_id)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def remove(self, song_id):
        """Hapus song dari playlist"""
        current = self.head
        while current:
            if current.song_id == song_id:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                
                self.size -= 1
                return True
            current = current.next
        return False

    def contains(self, song_id):
        """Cek apakah song ada di playlist"""
        current = self.head
        while current:
            if current.song_id == song_id:
                return True
            current = current.next
        return False

    def to_list(self):
        """Konversi ke daftar dict untuk penyimpanan ke JSON"""
        result = []
        current = self.head
        while current:
            result.append(current.to_dict())
            current = current.next
        return result

    def from_list(self, data_list):
        """Muat playlist dari daftar JSON. Input: daftar string (song_id) atau daftar dict dengan kunci 'song_id'."""
        self.head = None
        self.tail = None
        self.size = 0
        for item in data_list:
            if isinstance(item, str):
                song_id = item
            elif isinstance(item, dict):
                song_id = item.get("song_id")
            else:
                continue

            if song_id:
                self.append(song_id)

    def get_all_song_ids(self):
        """Dapatkan semua song_id dalam list"""
        result = []
        current = self.head
        while current:
            result.append(current.song_id)
            current = current.next
        return result

    def get_next(self, song_id):
        """Dapatkan `song_id` berikutnya setelah `song_id` yang diberikan"""
        current = self.head
        while current:
            if current.song_id == song_id:
                return current.next.song_id if current.next else None
            current = current.next
        return None

    def get_prev(self, song_id):
        """Dapatkan `song_id` sebelumnya sebelum `song_id` yang diberikan"""
        current = self.head
        while current:
            if current.song_id == song_id:
                return current.prev.song_id if current.prev else None
            current = current.next
        return None

    def get_first(self):
        """Dapatkan `song_id` pertama dalam playlist"""
        return self.head.song_id if self.head else None

    def get_last(self):
        """Dapatkan `song_id` terakhir dalam playlist"""
        return self.tail.song_id if self.tail else None


class UserNode:
    """Node untuk user dalam linked list"""
    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.playlist = DoublyLinkedList()  # Menggunakan doubly linked list
        self.profile_image = ""  # Path ke foto profil
        self.next = None

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "is_admin": self.is_admin,
            "playlist": self.playlist.to_list(),
            "profile_image": self.profile_image
        }

    @staticmethod
    def from_dict(data):
        user = UserNode(
            data["username"],
            data["password"],
            data.get("is_admin", False)
        )
        user.playlist.from_list(data.get("playlist", []))
        user.profile_image = data.get("profile_image", "")
        return user


class DataManager:
    """Manager untuk mengelola data JSON"""

    def __init__(self):
        self._ensure_data_files_exist()
        self.library_head = None
        self.users_head = None
        self.letter_counters = {}  # Counter per huruf pertama genre untuk song_id unik
        self._load_all_data()

    def _ensure_data_files_exist(self):
        """Buat file JSON jika belum ada"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        if not os.path.exists(USERS_FILE):
            self._save_json(USERS_FILE, [])

        if not os.path.exists(SONGS_FILE):
            self._save_json(SONGS_FILE, [])

    def _load_all_data(self):
        """Load semua data dari JSON ke memory"""
        self._load_songs()
        self._load_users()

    def _load_songs(self):
        """Load lagu dari JSON"""
        data = self._load_json(SONGS_FILE)
        self.library_head = None
        self.letter_counters = {}

        for song_data in data:
            node = SongNode.from_dict(song_data)
            node.next = self.library_head
            self.library_head = node

            # Update letter counters untuk song_id unik
            genre = song_data.get("genre", "")
            if genre and node.song_id:
                first_letter = genre[0].upper()
                count = int(node.song_id[1:]) if len(node.song_id) > 1 and node.song_id[1:].isdigit() else 0
                if first_letter not in self.letter_counters:
                    self.letter_counters[first_letter] = 0
                self.letter_counters[first_letter] = max(self.letter_counters[first_letter], count)

    def _load_users(self):
        """Load user dari JSON"""
        data = self._load_json(USERS_FILE)
        self.users_head = None

        for user_data in data:
            user = UserNode.from_dict(user_data)
            user.next = self.users_head
            self.users_head = user

    def _load_json(self, file_path):
        """Baca file JSON. Kembalikan list kosong jika file tidak ada atau JSON tidak valid."""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            # Bila file corrupt atau berformat salah, kembalikan default
            return []

    def _save_json(self, file_path, data):
        """Save JSON file"""
        # Pastikan direktori tujuan ada sebelum menulis
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Gunakan 'utf-8-sig' saat menyimpan agar file dapat dibukadengan benar pada berbagai editor di Windows.
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # SONG MANAGEMENT 
    def add_song(self, title, artist, genre, file_path=""):
        """Tambah lagu"""
        first_letter = genre[0].upper() if genre else "S"
        if first_letter not in self.letter_counters:
            self.letter_counters[first_letter] = 0
        count = self.letter_counters[first_letter] + 1
        self.letter_counters[first_letter] = count
        song_id = f"{first_letter}{count}"

        node = SongNode(song_id, title, artist, genre, file_path)
        node.next = self.library_head
        self.library_head = node

        self._save_songs()
        return song_id

    def delete_song(self, song_id):
        """Hapus lagu dari library berdasarkan `song_id`"""
        prev = None
        ptr = self.library_head

        while ptr:
            if ptr.song_id == song_id:
                if prev:
                    prev.next = ptr.next
                else:
                    self.library_head = ptr.next
                self._save_songs()
                return True
            prev = ptr
            ptr = ptr.next

        return False

    def update_song(self, song_id, title=None, artist=None, genre=None, file_path=None):
        """Perbarui informasi lagu berdasarkan `song_id`"""
        ptr = self.library_head

        while ptr:
            if ptr.song_id == song_id:
                if title:
                    ptr.title = title
                if artist:
                    ptr.artist = artist
                if genre:
                    ptr.genre = genre
                if file_path:
                    ptr.file_path = file_path
                self._save_songs()
                return True
            ptr = ptr.next

        return False

    def get_all_songs(self):
        """Dapatkan semua lagu sebagai daftar objek `SongNode`"""
        songs = []
        ptr = self.library_head
        while ptr:
            songs.append(ptr)
            ptr = ptr.next
        return songs

    def get_song_by_id(self, song_id):
        """Dapatkan lagu berdasarkan `song_id`"""
        ptr = self.library_head
        while ptr:
            if ptr.song_id == song_id:
                return ptr
            ptr = ptr.next
        return None

    def get_song_by_index(self, index):
        """Dapatkan lagu berdasarkan indeks (0-based)"""
        ptr = self.library_head
        i = 0
        while ptr:
            if i == index:
                return ptr
            ptr = ptr.next
            i += 1
        return None

    def _save_songs(self):
        """Simpan daftar lagu ke file JSON"""
        songs_data = []
        ptr = self.library_head
        while ptr:
            songs_data.append(ptr.to_dict())
            ptr = ptr.next
        self._save_json(SONGS_FILE, songs_data)

    # USER MANAGEMENT 
    def register(self, username, password, is_admin=False):
        """Daftarkan user baru ke dalam sistem"""
        ptr = self.users_head
        while ptr:
            if ptr.username == username:
                return False
            ptr = ptr.next

        user = UserNode(username, password, is_admin)
        user.next = self.users_head
        self.users_head = user

        self._save_users()
        return True

    def login(self, username, password):
        """Autentikasi user berdasarkan username dan password"""
        ptr = self.users_head
        while ptr:
            if ptr.username == username and ptr.password == password:
                return ptr
            ptr = ptr.next
        return None

    def get_user_by_username(self, username):
        """Dapatkan objek user berdasarkan `username`"""
        ptr = self.users_head
        while ptr:
            if ptr.username == username:
                return ptr
            ptr = ptr.next
        return None

    def _save_users(self):
        """Simpan data user ke file JSON"""
        users_data = []
        ptr = self.users_head
        while ptr:
            users_data.append(ptr.to_dict())
            ptr = ptr.next
        self._save_json(USERS_FILE, users_data)

    # PLAYLIST MANAGEMENT 
    def add_to_playlist(self, username, song_id):
        """Tambah lagu ke playlist user"""
        user = self.get_user_by_username(username)
        if user and not user.playlist.contains(song_id):
            user.playlist.append(song_id)
            self._save_users()
            return True
        return False

    def remove_from_playlist(self, username, song_id):
        """Hapus lagu dari playlist user"""
        user = self.get_user_by_username(username)
        if user and user.playlist.remove(song_id):
            self._save_users()
            return True
        return False

    def get_user_playlist(self, username):
        """Dapatkan playlist user sebagai daftar objek `SongNode`"""
        user = self.get_user_by_username(username)
        if user:
            songs = []
            for song_id in user.playlist.get_all_song_ids():
                song = self.get_song_by_id(song_id)
                if song:
                    songs.append(song)
            return songs
        return []

    def get_next_song_in_playlist(self, username, current_song_id):
        """Dapatkan lagu berikutnya dalam playlist user setelah `current_song_id`"""
        user = self.get_user_by_username(username)
        if user:
            next_song_id = user.playlist.get_next(current_song_id)
            if next_song_id:
                return self.get_song_by_id(next_song_id)
        return None

    def get_prev_song_in_playlist(self, username, current_song_id):
        """Dapatkan lagu sebelumnya dalam playlist user sebelum `current_song_id`"""
        user = self.get_user_by_username(username)
        if user:
            prev_song_id = user.playlist.get_prev(current_song_id)
            if prev_song_id:
                return self.get_song_by_id(prev_song_id)
        return None

    def clear_playlist(self, username):
        """Bersihkan playlist user (hapus semua lagu)"""
        user = self.get_user_by_username(username)
        if user:
            user.playlist = DoublyLinkedList()
            self._save_users()
            return True
        return False

    def update_user_profile_image(self, username, image_path):
        """Perbarui path foto profil user"""
        user = self.get_user_by_username(username)
        if user:
            user.profile_image = image_path
            self._save_users()
            return True
        return False

    def get_user_profile_image(self, username):
        """Dapatkan path foto profil user"""
        user = self.get_user_by_username(username)
        return user.profile_image if user else ""

    def init_default_data(self):
        """Inisialisasi data dengan contoh lagu dan akun admin default jika belum ada"""
        # Cek apakah data sudah ada
        songs = self.get_all_songs()
        if len(songs) > 0:
            return

        # Add sample songs
        self.add_song("Mr. Loverman", "Ricky Montgomery", "Fave")

        # Add admin user jika belum ada
        if not self.get_user_by_username(ADMIN_USERNAME):
            self.register(ADMIN_USERNAME, ADMIN_PASSWORD, is_admin=True)

    def verify_password(self, username, password):
        """Verifikasi kecocokan password untuk sebuah user"""
        user = self.get_user_by_username(username)
        return user and user.password == password

    def update_username(self, old_username, new_username):
        """Perbarui username pengguna jika nama baru belum dipakai"""
        # Periksa apakah username baru sudah ada
        if self.get_user_by_username(new_username):
            return False
        
        user = self.get_user_by_username(old_username)
        if user:
            user.username = new_username
            self._save_users()
            return True
        return False

    def update_password(self, username, new_password):
        """Perbarui password user"""
        user = self.get_user_by_username(username)
        if user:
            user.password = new_password
            self._save_users()
            return True
        return False
