# ui.py
# Fungsi bantu tampilan: font, teks, panel, kotak dialog mesin ketik, dan transisi layar.
import os
import sys
import math
import random
import pygame

# Ukuran jendela dan kanvas dunia (dunia digambar kecil lalu diperbesar 3x agar terlihat retro)
ANDROID = "ANDROID_ARGUMENT" in os.environ  # True saat berjalan sebagai aplikasi Android

LEBAR, TINGGI = 960, 540
VIEW_W, VIEW_H = 320, 180
SKALA = 3

# Warna umum
PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
KUNING = (255, 220, 70)
HIJAU = (90, 220, 110)
MERAH = (240, 80, 80)
BIRU = (90, 170, 255)
ABU = (150, 150, 170)
UNGU = (170, 110, 255)
PANEL = (26, 30, 60)


def jalur_sumber(rel):
    """Lokasi file bawaan game (aman untuk mode .exe PyInstaller)."""
    if getattr(sys, "frozen", False):
        dasar = sys._MEIPASS
    else:
        dasar = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dasar, rel)


def jalur_simpan(nama):
    """Lokasi file simpanan (di sebelah game / .exe)."""
    if ANDROID:  # di Android hanya folder privat aplikasi yang boleh ditulis
        dasar = os.environ.get("ANDROID_PRIVATE", os.path.dirname(os.path.abspath(__file__)))
    elif getattr(sys, "frozen", False):
        dasar = os.path.dirname(sys.executable)
    else:
        dasar = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dasar, nama)


# ---------- Font dan teks ----------
_font_cache = {}


def font(ukuran):
    """Font bawaan pygame (di-cache supaya hemat)."""
    if ukuran not in _font_cache:
        _font_cache[ukuran] = pygame.font.Font(None, ukuran)
    return _font_cache[ukuran]


def teks(surface, isi, x, y, ukuran=24, warna=PUTIH, tengah=False, bayangan=True):
    """Menggambar teks (tanpa antialias agar terlihat blok/pixel)."""
    f = font(ukuran)
    img = f.render(str(isi), False, warna)
    if tengah:
        x = x - img.get_width() // 2
    if bayangan:
        surface.blit(f.render(str(isi), False, HITAM), (x + 2, y + 2))
    surface.blit(img, (x, y))
    return img.get_width()


def bungkus(isi, ukuran, lebar):
    """Memecah teks menjadi beberapa baris sesuai lebar."""
    f = font(ukuran)
    hasil = []
    for paragraf in str(isi).split("\n"):
        kata = paragraf.split(" ")
        baris = ""
        for k in kata:
            coba = k if baris == "" else baris + " " + k
            if f.size(coba)[0] <= lebar:
                baris = coba
            else:
                hasil.append(baris)
                baris = k
        hasil.append(baris)
    return hasil


def panel(surface, rect, isi=PANEL, tepi=PUTIH, alpha=235):
    """Kotak panel bergaya retro dengan tepi ganda."""
    r = pygame.Rect(rect)
    lapis = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    lapis.fill((isi[0], isi[1], isi[2], alpha))
    surface.blit(lapis, (r.x, r.y))
    pygame.draw.rect(surface, tepi, r, 3)
    pygame.draw.rect(surface, HITAM, r.inflate(-6, -6), 2)


def bar(surface, x, y, w, h, rasio, warna, latar=(40, 40, 70)):
    """Bar progres (misal XP)."""
    rasio = max(0.0, min(1.0, rasio))
    pygame.draw.rect(surface, latar, (x, y, w, h))
    pygame.draw.rect(surface, warna, (x, y, int(w * rasio), h))
    pygame.draw.rect(surface, PUTIH, (x, y, w, h), 2)


def gambar_menu(surface, daftar, indeks, cx, y0, jarak=58, ukuran=40, nonaktif=()):
    """Menggambar daftar menu vertikal, mengembalikan daftar rect untuk mouse."""
    rects = []
    for i, nama in enumerate(daftar):
        y = y0 + i * jarak
        if i in nonaktif:
            warna = (90, 90, 110)
        elif i == indeks:
            warna = KUNING
        else:
            warna = PUTIH
        lebar = font(ukuran).size(nama)[0]
        rect = pygame.Rect(cx - 180, y - 6, 360, ukuran + 8)
        rects.append(rect)
        if i == indeks:
            panel(surface, rect, (50, 50, 110), KUNING, 200)
            teks(surface, ">", cx - lebar // 2 - 30, y, ukuran, KUNING)
        teks(surface, nama, cx, y, ukuran, warna, tengah=True)
    return rects


def latar_judul(surface, t):
    """Latar animasi retro untuk menu utama: langit, bintang, gunung, awan."""
    for y in range(0, TINGGI, 6):
        r = y / TINGGI
        surface.fill((int(20 + 70 * r), int(24 + 30 * r), int(70 + 90 * r)), (0, y, LEBAR, 6))
    rng = random.Random(5)
    for i in range(70):
        x = rng.randrange(LEBAR)
        y = rng.randrange(0, 300)
        kedip = 0.5 + 0.5 * math.sin(t * 2 + i)
        c = int(120 + 135 * kedip)
        surface.fill((c, c, c), (x, y, 3, 3))
    for lapis, warna, tinggi, geser in ((0, (40, 40, 90), 150, 0.3), (1, (28, 28, 70), 100, 0.6)):
        titik = [(0, TINGGI)]
        for x in range(0, LEBAR + 20, 20):
            y = TINGGI - tinggi - 50 * abs(math.sin(x * 0.012 + lapis * 2)) - 20 * math.sin(x * 0.04 + t * geser * 0)
            titik.append((x, int(y)))
        titik.append((LEBAR, TINGGI))
        pygame.draw.polygon(surface, warna, titik)
    for i in range(4):
        x = (t * (15 + i * 6) + i * 260) % (LEBAR + 200) - 100
        y = 60 + i * 55
        for dx, dy, w in ((0, 0, 90), (20, -12, 60), (-15, 8, 50)):
            surface.fill((200, 210, 240), (int(x + dx), y + dy, w, 14))


# ---------- Kotak dialog mesin ketik ----------
class KotakDialog:
    """Dialog dengan efek teks mesin ketik. Tekan E/Enter untuk lanjut."""

    def __init__(self, audio):
        self.audio = audio
        self.aktif = False
        self.nama = ""
        self.baris = []
        self.i = 0
        self.t = 0.0
        self.huruf = 0
        self.selesai = None

    def buka(self, nama, baris, selesai=None):
        self.nama = nama
        self.baris = list(baris)
        self.i = 0
        self.t = 0.0
        self.huruf = 0
        self.selesai = selesai
        self.aktif = True

    def update(self, dt):
        if not self.aktif:
            return
        self.t += dt
        baru = min(int(self.t * 45), len(self.baris[self.i]))
        if baru > self.huruf and baru % 3 == 0:
            self.audio.mainkan("tulis")
        self.huruf = baru

    def tekan(self):
        """Dipanggil saat pemain menekan tombol lanjut."""
        if not self.aktif:
            return
        if self.huruf < len(self.baris[self.i]):
            self.huruf = len(self.baris[self.i])  # tampilkan semua huruf
            self.t = 999
            return
        self.i += 1
        if self.i >= len(self.baris):
            self.aktif = False
            cb = self.selesai
            self.selesai = None
            if cb:
                cb()
        else:
            self.t = 0.0
            self.huruf = 0

    def gambar(self, surface, t):
        if not self.aktif:
            return
        panel(surface, (40, 365, 880, 150))
        lebar_nama = font(30).size(self.nama)[0] + 40
        panel(surface, (60, 330, lebar_nama, 42), (60, 40, 110), KUNING)
        teks(surface, self.nama, 80, 340, 30, KUNING)
        sisa = self.huruf
        y = 385
        for baris in bungkus(self.baris[self.i], 30, 840):
            potong = baris[:max(0, sisa)]
            teks(surface, potong, 65, y, 30)
            sisa -= len(baris) + 1
            y += 34
        if self.huruf >= len(self.baris[self.i]) and int(t * 2) % 2 == 0:
            teks(surface, "[E]", 860, 480, 24, KUNING)


# ---------- Transisi layar ----------
class Transisi:
    """Transisi retro: 'piksel' (dissolve kotak-kotak) atau 'fade'."""
    UKURAN = 40

    def __init__(self):
        self.aktif = False
        self.sel = []
        for r in range(14):
            for c in range(24):
                self.sel.append((c * self.UKURAN, r * self.UKURAN))
        random.Random(3).shuffle(self.sel)
        self.t = 0.0
        self.durasi = 1.0
        self.aksi = None
        self.mode = "piksel"
        self.sudah = False
        self.gelap = pygame.Surface((LEBAR, TINGGI))
        self.gelap.fill(HITAM)

    def mulai(self, aksi, mode="piksel", durasi=1.0):
        self.aktif = True
        self.t = 0.0
        self.durasi = durasi
        self.aksi = aksi
        self.mode = mode
        self.sudah = False

    def update(self, dt):
        if not self.aktif:
            return
        self.t += dt
        if not self.sudah and self.t >= self.durasi / 2:
            self.sudah = True
            if self.aksi:
                self.aksi()  # ganti scene saat layar tertutup penuh
        if self.t >= self.durasi:
            self.aktif = False

    def gambar(self, surface):
        if not self.aktif:
            return
        setengah = self.durasi / 2
        if self.t < setengah:
            p = self.t / setengah
        else:
            p = 1 - (self.t - setengah) / setengah
        p = max(0.0, min(1.0, p))
        if self.mode == "fade":
            self.gelap.set_alpha(int(255 * p))
            surface.blit(self.gelap, (0, 0))
        else:
            n = int(p * len(self.sel))
            for (x, y) in self.sel[:n]:
                surface.fill(HITAM, (x, y, self.UKURAN, self.UKURAN))


# ---------- Kontrol sentuh (Android / layar sentuh) ----------
class KontrolSentuh:
    """Joystick virtual (kiri), tombol AKSI (kanan), dan tombol JEDA. Mendukung multi-touch."""

    def __init__(self):
        self.aktif = ANDROID or os.environ.get("CQ_SENTUH") == "1"
        self.joy = (120, 390)      # pusat joystick
        self.r = 80
        self.aksi_c = (840, 400)   # pusat tombol aksi
        self.jeda_c = (318, 34)    # pusat tombol jeda
        self.jari_joy = None
        self.knob = (0.0, 0.0)     # arah joystick -1..1
        self.diklaim = False       # True jika sentuhan baru mengenai kontrol
        self.s_joy = pygame.Surface((self.r * 2 + 4, self.r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(self.s_joy, (255, 255, 255, 50), (self.r + 2, self.r + 2), self.r)
        pygame.draw.circle(self.s_joy, (255, 255, 255, 120), (self.r + 2, self.r + 2), self.r, 3)
        self.s_knob = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(self.s_knob, (255, 255, 255, 140), (32, 32), 30)
        self.s_aksi = pygame.Surface((124, 124), pygame.SRCALPHA)
        pygame.draw.circle(self.s_aksi, (255, 220, 70, 110), (62, 62), 58)
        pygame.draw.circle(self.s_aksi, (255, 255, 255, 170), (62, 62), 58, 3)

    def reset(self):
        self.jari_joy = None
        self.knob = (0.0, 0.0)

    def _joy(self, x, y):
        dx, dy = (x - self.joy[0]) / self.r, (y - self.joy[1]) / self.r
        p = math.hypot(dx, dy)
        if p > 1:
            dx, dy = dx / p, dy / p
            p = 1
        self.knob = (0.0, 0.0) if p < 0.2 else (dx, dy)
        self.knob_gambar = (dx, dy)

    def tangani(self, e, boleh):
        """Memproses event jari. Mengembalikan 'aksi', 'jeda', atau None."""
        self.aktif = True
        x, y = e.x * LEBAR, e.y * TINGGI
        fid = e.finger_id
        if e.type == pygame.FINGERDOWN and boleh:
            if math.hypot(x - self.joy[0], y - self.joy[1]) < self.r * 1.4 and self.jari_joy is None:
                self.jari_joy = fid
                self._joy(x, y)
                self.diklaim = True
            elif math.hypot(x - self.aksi_c[0], y - self.aksi_c[1]) < 62:
                self.diklaim = True
                return "aksi"
            elif math.hypot(x - self.jeda_c[0], y - self.jeda_c[1]) < 32:
                self.diklaim = True
                return "jeda"
        elif e.type == pygame.FINGERMOTION and fid == self.jari_joy:
            self._joy(x, y)
        elif e.type == pygame.FINGERUP and fid == self.jari_joy:
            self.reset()
        return None

    def gambar(self, surface):
        if not self.aktif:
            return
        surface.blit(self.s_joy, (self.joy[0] - self.r - 2, self.joy[1] - self.r - 2))
        kx, ky = getattr(self, "knob_gambar", (0, 0)) if self.jari_joy is not None else (0, 0)
        surface.blit(self.s_knob, (self.joy[0] + kx * self.r * 0.6 - 32, self.joy[1] + ky * self.r * 0.6 - 32))
        surface.blit(self.s_aksi, (self.aksi_c[0] - 62, self.aksi_c[1] - 62))
        teks(surface, "E", self.aksi_c[0], self.aksi_c[1] - 18, 56, PUTIH, tengah=True)
        pygame.draw.circle(surface, (16, 18, 40), self.jeda_c, 26)
        pygame.draw.circle(surface, PUTIH, self.jeda_c, 26, 3)
        surface.fill(PUTIH, (self.jeda_c[0] - 8, self.jeda_c[1] - 9, 5, 18))
        surface.fill(PUTIH, (self.jeda_c[0] + 3, self.jeda_c[1] - 9, 5, 18))
