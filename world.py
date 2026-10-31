# world.py
# Dunia tile-based 64x64 (tile 16x16): 4 wilayah, NPC, objek, musuh ringan,
# air beranimasi, rumput bergoyang, awan, siklus siang-malam, dan partikel.
import math
import random
import pygame
import ui
from customization import gambar_karakter, config_acak

UBIN = 16
LP, TP = 64, 64  # lebar dan tinggi peta (dalam tile)

(RUMPUT, POHON, SEMAK, AIR, PASIR, KAKTUS, RERUNTUHAN, OASIS, SALJU, BATU, JEMBATAN,
 JALAN, GEDUNG, GEDUNG_NEON, BUNGA, LANTAI, TROTOAR, POHON_SALJU, AIR_ES) = range(19)

# Tile yang tidak bisa dilewati
PADAT = {POHON, SEMAK, AIR, KAKTUS, RERUNTUHAN, OASIS, BATU, GEDUNG, GEDUNG_NEON, POHON_SALJU, AIR_ES}
DASAR = {"hutan": RUMPUT, "gurun": PASIR, "gunung": SALJU, "kota": TROTOAR}
JUMLAH_FRAME = {AIR: 4, AIR_ES: 4, OASIS: 4, RUMPUT: 3, BUNGA: 2}
WARNA_MINI = {RUMPUT: (56, 140, 60), POHON: (30, 100, 45), SEMAK: (36, 110, 48), AIR: (50, 100, 210),
              PASIR: (222, 190, 120), KAKTUS: (50, 140, 70), RERUNTUHAN: (150, 130, 110),
              OASIS: (40, 185, 190), SALJU: (235, 240, 250), BATU: (120, 125, 140),
              JEMBATAN: (165, 115, 65), JALAN: (36, 36, 52), GEDUNG: (90, 60, 150),
              GEDUNG_NEON: (255, 60, 200), BUNGA: (240, 80, 120), LANTAI: (152, 152, 168),
              TROTOAR: (72, 72, 98), POHON_SALJU: (30, 90, 70), AIR_ES: (140, 195, 235)}

WILAYAH = {
    "hutan": {"nama": "Hutan Algoritma", "topik": "Logika & Algoritma", "warna": (90, 220, 110),
              "item": ["Daun Logika", "Ranting Loop", "Buah If-Else"]},
    "gurun": {"nama": "Gurun Basis Data", "topik": "Basis Data & SQL", "warna": (255, 220, 70),
              "item": ["Kepingan Tabel", "Kunci Primer", "Gulungan SQL"]},
    "gunung": {"nama": "Pegunungan Jaringan", "topik": "Jaringan Komputer", "warna": (90, 170, 255),
               "item": ["Kristal IP", "Kabel Fiber", "Peta DNS"]},
    "kota": {"nama": "Kota Cyber", "topik": "Keamanan & Biner", "warna": (255, 80, 220),
             "item": ["Chip Neon", "Token Sandi", "Biner Emas"]},
}
URUTAN_WILAYAH = ["hutan", "gurun", "gunung", "kota"]
TARGET_TANTANGAN = 3  # jumlah tantangan NPC agar gerbang kristal terbuka

# (id, nama, wilayah, jenis, tx, ty, sapaan, kalimat setelah selesai)
DAFTAR_NPC = [
    ("pemandu", "Prof. Pixel", "hutan", "pemandu", 33, 34,
     ["Halo! Aku Prof. Pixel. Kristal Data dunia ini pecah menjadi 4 pecahan.",
      "Pergilah ke Hutan, Gurun, Pegunungan, dan Kota Cyber. Bantu penduduk dengan tantangan mereka.",
      "Selesaikan 3 tantangan di tiap wilayah, lalu masuki Gerbang Kristal-nya. Gerakkan dengan WASD, bicara dengan E."],
     ["Kembalikan 4 pecahan ke Kristal Pusat di plaza ini. Semangat!"]),
    ("hutan_loop", "Pak Loop", "hutan", "pilgan", 20, 20,
     ["Selamat datang di Hutan Algoritma! Pohon di sini tumbuh berurutan seperti langkah algoritma.",
      "Jawab 3 pertanyaanku, minimal 2 yang benar ya!"],
     ["Hebat! Kamu paham logika dengan baik."]),
    ("hutan_cabang", "Bu Cabang", "hutan", "urutan", 8, 6,
     ["Algoritma itu soal urutan. Kalau urutannya salah, hasilnya kacau.",
      "Susun langkah-langkah ini dengan benar."],
     ["Urutanmu rapi sekali!"]),
    ("hutan_bit", "Kak Bit", "hutan", "biner", 24, 8,
     ["Komputer hanya mengenal 0 dan 1. Bisakah kamu menyalakan bit yang tepat?"],
     ["Kamu jago berhitung biner!"]),
    ("hutan_kancil", "Si Kancil", "hutan", "cocok", 6, 24,
     ["Aku suka istilah pemrograman. Bantu aku mencocokkan istilah dengan artinya."],
     ["Terima kasih, sekarang aku tidak bingung lagi."]),
    ("gurun_tabel", "Tuan Tabel", "gurun", "pilgan", 44, 20,
     ["Di Gurun Basis Data, semua data tersimpan rapi dalam tabel.",
      "Jawab pertanyaanku tentang basis data!"],
     ["Datamu aman bersamamu."]),
    ("gurun_kunci", "Nona Kunci", "gurun", "urutan", 58, 6,
     ["Query SQL harus ditulis dengan urutan yang benar.", "Susunlah dengan tepat."],
     ["Query yang sempurna!"]),
    ("gurun_bit", "Pak Unta", "gurun", "biner", 38, 8,
     ["Unta pun bisa berhitung biner. Coba ubah angka ini ke biner."],
     ["Kamu secepat unta!"]),
    ("gurun_istilah", "Bu Kaktus", "gurun", "cocok", 56, 26,
     ["Cocokkan istilah basis data berikut dengan artinya."],
     ["Pengetahuanmu menyegarkan seperti oasis."]),
    ("gunung_ip", "Kak Router", "gunung", "pilgan", 20, 42,
     ["Brrr... selamat datang di Pegunungan Jaringan!",
      "Jawab pertanyaan tentang jaringan agar aku bisa menghangatkan sinyal."],
     ["Sinyalnya kuat sekali sekarang!"]),
    ("gunung_dns", "Nenek DNS", "gunung", "urutan", 8, 58,
     ["Aku yang menerjemahkan nama menjadi alamat. Susun alurnya dengan benar."],
     ["Kamu mengerti cara kerja internet."]),
    ("gunung_oktet", "Beruang Oktet", "gunung", "biner", 26, 58,
     ["Alamat IP tersusun dari oktet 8 bit. Ubah angka ini ke biner."],
     ["Hebat! Oktetmu tepat."]),
    ("gunung_topo", "Yeti Topologi", "gunung", "cocok", 6, 40,
     ["Cocokkan istilah jaringan berikut."],
     ["Jaringan kita terhubung sempurna."]),
    ("kota_siber", "Agen Siber", "kota", "pilgan", 40, 44,
     ["Selamat datang di Kota Cyber. Hati-hati, banyak penipu digital di sini.",
      "Tunjukkan bahwa kamu paham keamanan siber!"],
     ["Kamu siap menjaga kota ini."]),
    ("kota_phish", "Detektif Phish", "kota", "urutan", 56, 36,
     ["Ada kasus mencurigakan! Susun langkah penanganannya dengan benar."],
     ["Kasus terpecahkan!"]),
    ("kota_hex", "Robot Biner", "kota", "biner", 48, 58,
     ["BEEP BOOP. Ubah bilangan ini ke biner, manusia."],
     ["BEEP! Perhitungan benar."]),
    ("kota_istilah", "Hacker Putih", "kota", "cocok", 56, 52,
     ["Aku hacker yang baik. Cocokkan istilah keamanan ini."],
     ["Kamu calon pakar keamanan!"]),
]

# (jenis, id, tx, ty, wilayah, teks)
DAFTAR_OBJEK = [
    ("portal_pusat", "pusat", 32, 31, "hutan", []),
    ("portal", "hutan", 22, 14, "hutan", []),
    ("portal", "gurun", 44, 12, "gurun", []),
    ("portal", "gunung", 14, 53, "gunung", []),
    ("portal", "kota", 48, 44, "kota", []),
    ("papan", "p1", 29, 34, "hutan", ["Selamat datang di Plaza Kristal! Barat laut: Hutan, timur laut: Gurun, barat daya: Pegunungan, tenggara: Kota Cyber."]),
    ("papan", "p2", 26, 26, "hutan", ["Hutan Algoritma: belajar logika, percabangan, dan perulangan."]),
    ("papan", "p3", 38, 26, "gurun", ["Gurun Basis Data: belajar tabel, primary key, dan SQL."]),
    ("papan", "p4", 16, 45, "gunung", ["Pegunungan Jaringan: seberangi jembatan di sebelah timur untuk ke selatan."]),
    ("papan", "p5", 36, 33, "kota", ["Kota Cyber: keamanan siber, password, dan bilangan biner."]),
    ("peti", "c1", 4, 4, "hutan", []), ("peti", "c2", 16, 27, "hutan", []),
    ("peti", "c3", 60, 20, "gurun", []), ("peti", "c4", 36, 24, "gurun", []),
    ("peti", "c5", 4, 36, "gunung", []), ("peti", "c6", 30, 60, "gunung", []),
    ("peti", "c7", 33, 41, "kota", []), ("peti", "c8", 57, 60, "kota", []),
]

_gudang_ubin = None


def wilayah_tile(tx, ty):
    if ty < 32:
        return "hutan" if tx < 32 else "gurun"
    return "gunung" if tx < 32 else "kota"


class GudangUbin:
    """Menggambar tile secara prosedural (pixel art) lalu menyimpannya di cache."""

    def __init__(self):
        self.cache = {}

    def ambil(self, id_, v, f):
        kunci = (id_, v, f)
        img = self.cache.get(kunci)
        if img is None:
            img = self._buat(id_, v, f)
            self.cache[kunci] = img
        return img

    def _bintik(self, s, rng, warna_list, jumlah=7):
        for _ in range(jumlah):
            s.set_at((rng.randrange(16), rng.randrange(16)), rng.choice(warna_list))

    def _buat(self, id_, v, f):
        s = pygame.Surface((UBIN, UBIN))
        rng = random.Random(id_ * 31 + v)
        draw = pygame.draw
        if id_ in (RUMPUT, POHON, SEMAK, BUNGA):
            s.fill((56, 140, 60))
            self._bintik(s, rng, [(70, 160, 70), (44, 112, 50)])
            if id_ == RUMPUT and v >= 2:  # rumput tinggi bergoyang
                for bx in (3, 8, 12):
                    g = (f + bx) % 3 - 1
                    for k in range(5):
                        s.set_at((bx + (g if k >= 3 else 0), 14 - k), (100, 195, 95))
            elif id_ == POHON:
                draw.rect(s, (110, 70, 40), (7, 9, 2, 7))
                draw.circle(s, (30, 100, 45), (8, 6), 6)
                draw.circle(s, (48, 135, 60), (6, 4), 3)
            elif id_ == SEMAK:
                draw.circle(s, (36, 110, 48), (8, 10), 5)
                draw.circle(s, (52, 140, 62), (6, 9), 3)
                for p in ((5, 8), (10, 11), (8, 13)):
                    s.set_at(p, (220, 70, 70))
            elif id_ == BUNGA:
                warna = [(240, 80, 120), (250, 220, 60), (245, 245, 245), (170, 110, 240)][v % 4]
                for i, bx in enumerate((3, 9, 13)):
                    by = 5 + i * 3 + (f if i % 2 == 0 else 0)
                    s.set_at((bx, by), warna)
                    s.set_at((bx, by + 1), (40, 120, 50))
                    s.set_at((bx, by + 2), (40, 120, 50))
        elif id_ in (AIR, AIR_ES, OASIS):
            dasar, garis = {AIR: ((50, 100, 210), (130, 180, 255)),
                            AIR_ES: ((140, 195, 235), (225, 245, 255)),
                            OASIS: ((40, 185, 190), (180, 255, 245))}[id_]
            s.fill(dasar)
            for baris in (2, 7, 12):
                yy = (baris + f) % 16
                for x in range(16):
                    if (x + baris * 2 + f * 4) % 8 < 3:
                        s.set_at((x, yy), garis)
        elif id_ == JEMBATAN:
            s.fill((50, 100, 210) if v == 0 else (140, 195, 235))
            kayu, gelap = (165, 115, 65), (110, 72, 40)
            if v == 0:  # menyeberang timur-barat
                for x in range(0, 16, 4):
                    draw.rect(s, kayu, (x, 2, 3, 12))
                    draw.rect(s, gelap, (x + 3, 2, 1, 12))
                draw.rect(s, gelap, (0, 1, 16, 2))
                draw.rect(s, gelap, (0, 13, 16, 2))
            else:  # menyeberang utara-selatan
                for y in range(0, 16, 4):
                    draw.rect(s, kayu, (2, y, 12, 3))
                    draw.rect(s, gelap, (2, y + 3, 12, 1))
                draw.rect(s, gelap, (1, 0, 2, 16))
                draw.rect(s, gelap, (13, 0, 2, 16))
        elif id_ in (PASIR, KAKTUS, RERUNTUHAN):
            s.fill((222, 190, 120))
            self._bintik(s, rng, [(196, 160, 96), (240, 215, 150)], 8)
            if id_ == KAKTUS:
                hijau, terang = (50, 140, 70), (80, 175, 95)
                draw.rect(s, hijau, (6, 3, 4, 13))
                draw.rect(s, hijau, (2, 7, 4, 2))
                draw.rect(s, hijau, (2, 5, 2, 4))
                draw.rect(s, hijau, (10, 9, 4, 2))
                draw.rect(s, hijau, (12, 6, 2, 5))
                draw.rect(s, terang, (7, 4, 1, 11))
                s.set_at((7, 2), (240, 100, 160))
            elif id_ == RERUNTUHAN:
                batu, gelap = (150, 130, 110), (105, 90, 75)
                if v % 2 == 0:
                    draw.rect(s, batu, (5, 6, 6, 10))
                    draw.rect(s, batu, (4, 4, 8, 3))
                    draw.rect(s, gelap, (10, 6, 1, 10))
                    draw.line(s, gelap, (6, 8), (8, 11))
                else:
                    draw.rect(s, batu, (1, 8, 5, 8))
                    draw.rect(s, batu, (7, 6, 4, 10))
                    draw.rect(s, batu, (12, 9, 3, 7))
                    draw.rect(s, gelap, (5, 8, 1, 8))
                    draw.rect(s, gelap, (10, 6, 1, 10))
        elif id_ in (SALJU, BATU, POHON_SALJU):
            s.fill((235, 240, 250))
            self._bintik(s, rng, [(205, 220, 240), (255, 255, 255)], 7)
            if id_ == BATU:
                draw.polygon(s, (120, 125, 140), [(2, 15), (4, 6), (9, 3), (14, 8), (14, 15)])
                draw.polygon(s, (160, 165, 180), [(4, 6), (9, 3), (9, 9), (5, 12)])
                draw.polygon(s, (250, 252, 255), [(4, 6), (9, 3), (11, 5), (8, 6)])
            elif id_ == POHON_SALJU:
                draw.rect(s, (90, 60, 40), (7, 12, 2, 4))
                draw.polygon(s, (30, 90, 70), [(8, 1), (3, 7), (13, 7)])
                draw.polygon(s, (36, 105, 80), [(8, 4), (2, 11), (14, 11)])
                draw.line(s, (255, 255, 255), (5, 7), (11, 7))
                draw.line(s, (255, 255, 255), (4, 11), (12, 11))
        elif id_ == JALAN:
            s.fill((36, 36, 52))
            self._bintik(s, rng, [(46, 46, 64), (28, 28, 42)], 6)
            if v == 0:
                draw.rect(s, (240, 200, 60), (2, 7, 5, 2))
                draw.rect(s, (240, 200, 60), (10, 7, 5, 2))
            elif v == 1:
                draw.rect(s, (240, 200, 60), (7, 2, 2, 5))
                draw.rect(s, (240, 200, 60), (7, 10, 2, 5))
        elif id_ == TROTOAR:
            s.fill((72, 72, 98))
            draw.rect(s, (56, 56, 80), (0, 0, 16, 1))
            draw.rect(s, (56, 56, 80), (0, 8, 16, 1))
            draw.rect(s, (56, 56, 80), (8, 0, 1, 8))
            draw.rect(s, (56, 56, 80), (0, 8, 1, 8))
        elif id_ == LANTAI:
            s.fill((152, 152, 168))
            draw.rect(s, (120, 120, 138), (0, 0, 8, 8), 1)
            draw.rect(s, (120, 120, 138), (8, 8, 8, 8), 1)
            self._bintik(s, rng, [(190, 190, 205)], 3)
        elif id_ == GEDUNG:
            s.fill((38, 38, 66))
            for wx in (2, 7, 12):
                for wy in (2, 8):
                    lit = rng.random() < 0.55
                    warna = rng.choice([(255, 230, 120), (90, 240, 255), (255, 110, 210)]) if lit else (22, 22, 40)
                    draw.rect(s, warna, (wx, wy, 3, 4))
        elif id_ == GEDUNG_NEON:
            s.fill((52, 46, 92))
            neon = [(255, 60, 200), (60, 255, 230), (255, 230, 60), (140, 255, 90)][v % 4]
            draw.rect(s, neon, (0, 0, 16, 3))
            draw.rect(s, (30, 26, 60), (0, 3, 16, 2))
            for wx in (2, 7, 12):
                warna = rng.choice([(255, 230, 120), (90, 240, 255), (22, 22, 40)])
                draw.rect(s, warna, (wx, 9, 3, 4))
        return s


def gudang():
    global _gudang_ubin
    if _gudang_ubin is None:
        _gudang_ubin = GudangUbin()
    return _gudang_ubin


# ---------- Entitas ----------
class NPC:
    def __init__(self, data):
        self.id, self.nama, self.wilayah, self.jenis, tx, ty, self.sapa, self.selesai = data
        self.x = tx * UBIN + 8.0
        self.y = ty * UBIN + 14.0
        self.rumah = (self.x, self.y)
        self.cfg = config_acak(random.Random(self.nama))
        self.arah = "bawah"
        self.gerak = False
        self.timer = random.uniform(0.5, 2.5)
        self.t = random.uniform(0, 5)

    def rect(self):
        return pygame.Rect(int(self.x - 5), int(self.y - 6), 10, 6)

    def update(self, dt, world):
        self.t += dt
        self.timer -= dt
        if self.timer <= 0:  # pilih: diam atau jalan ke arah acak
            self.timer = random.uniform(1.0, 3.0)
            self.gerak = random.random() < 0.5
            self.arah = random.choice(["bawah", "atas", "kiri", "kanan"])
        if self.gerak:
            dx = {"kiri": -1, "kanan": 1}.get(self.arah, 0)
            dy = {"atas": -1, "bawah": 1}.get(self.arah, 0)
            nx, ny = self.x + dx * 14 * dt, self.y + dy * 14 * dt
            r = pygame.Rect(int(nx - 5), int(ny - 6), 10, 6)
            jauh = abs(nx - self.rumah[0]) > 24 or abs(ny - self.rumah[1]) > 24
            if jauh or world.tabrak(r, abaikan=self):
                self.gerak = False
            else:
                self.x, self.y = nx, ny

    def gambar(self, view, kx, ky, t):
        frame = int(self.t * 6) % 4 if self.gerak else 4 + int(self.t * 2) % 2
        img = gambar_karakter(self.cfg, self.arah, frame)
        sx, sy = int(self.x) - kx, int(self.y) - ky
        pygame.draw.ellipse(view, (20, 40, 20), (sx - 5, sy - 2, 10, 4))
        view.blit(img, (sx - 8, sy - 19))
        if self.jenis != "pemandu" and not self.selesai_flag:
            by = sy - 26 + int(math.sin(t * 5) * 1.5)
            view.fill((255, 220, 70), (sx - 1, by, 2, 5))
            view.fill((255, 220, 70), (sx - 1, by + 6, 2, 2))

    selesai_flag = False


class Bug:
    """Musuh ringan: makhluk bug hijau yang berkeliaran. Tekan E untuk men-debug."""

    def __init__(self, x, y, wilayah):
        self.x, self.y = x, y
        self.rumah = (x, y)
        self.wilayah = wilayah
        self.hidup = True
        self.respawn = 0.0
        self.timer = random.uniform(0.5, 2)
        self.vx = self.vy = 0.0
        self.t = random.uniform(0, 5)

    def update(self, dt, world):
        if not self.hidup:
            self.respawn -= dt
            if self.respawn <= 0:
                self.hidup = True
            return
        self.t += dt
        self.timer -= dt
        if self.timer <= 0:
            self.timer = random.uniform(0.8, 2.2)
            if random.random() < 0.3:
                self.vx = self.vy = 0
            else:
                self.vx, self.vy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                self.vx *= 16
                self.vy *= 16
        nx, ny = self.x + self.vx * dt, self.y + self.vy * dt
        jauh = abs(nx - self.rumah[0]) > 40 or abs(ny - self.rumah[1]) > 40
        if jauh or world.solid_px(nx, ny):
            self.vx, self.vy = -self.vx, -self.vy
        else:
            self.x, self.y = nx, ny

    def gambar(self, view, kx, ky, t):
        if not self.hidup:
            return
        sx, sy = int(self.x) - kx, int(self.y) - ky
        tekan = int(self.t * 4) % 2
        pygame.draw.ellipse(view, (20, 40, 20), (sx - 6, sy - 2, 12, 4))
        tinggi = 8 - tekan
        pygame.draw.ellipse(view, (60, 190, 90), (sx - 6, sy - tinggi, 12, tinggi))
        pygame.draw.ellipse(view, (110, 235, 130), (sx - 4, sy - tinggi + 1, 5, 3))
        view.fill((20, 20, 40), (sx - 3, sy - tinggi + 3, 2, 2))
        view.fill((20, 20, 40), (sx + 1, sy - tinggi + 3, 2, 2))
        # antena kecil
        view.fill((200, 60, 60), (sx - 1, sy - tinggi - 2, 2, 2))


class Objek:
    """Papan petunjuk, peti, portal wilayah, dan portal pusat."""

    def __init__(self, data, dunia):
        self.jenis, self.id, tx, ty, self.wilayah, self.teks = data
        self.x = tx * UBIN + 8.0
        self.y = ty * UBIN + 14.0
        self.dunia = dunia

    def rect(self):
        if self.jenis in ("portal", "portal_pusat"):
            return pygame.Rect(int(self.x - 7), int(self.y - 6), 14, 6)
        return pygame.Rect(int(self.x - 5), int(self.y - 5), 10, 5)

    def gambar(self, view, kx, ky, t):
        sx, sy = int(self.x) - kx, int(self.y) - ky
        pr = self.dunia.progres
        draw = pygame.draw
        if self.jenis == "papan":
            view.fill((110, 70, 40), (sx - 1, sy - 8, 2, 8))
            view.fill((170, 120, 70), (sx - 6, sy - 15, 12, 8))
            view.fill((110, 70, 40), (sx - 6, sy - 15, 12, 1))
            view.fill((60, 40, 20), (sx - 4, sy - 12, 8, 1))
            view.fill((60, 40, 20), (sx - 4, sy - 10, 6, 1))
        elif self.jenis == "peti":
            buka = self.id in pr.peti
            view.fill((130, 80, 40), (sx - 6, sy - 8, 12, 8))
            view.fill((90, 55, 25), (sx - 6, sy - 8, 12, 2))
            view.fill((240, 200, 60), (sx - 1, sy - 5, 2, 3))
            if buka:
                view.fill((30, 20, 10), (sx - 5, sy - 10, 10, 3))
            else:
                view.fill((160, 100, 50), (sx - 6, sy - 10, 12, 3))
        elif self.jenis == "portal":
            kunci = self.id
            selesai = kunci in pr.kristal
            n = self.dunia.hitung_selesai(kunci)
            if selesai:
                warna = WILAYAH[kunci]["warna"]
            elif n >= TARGET_TANTANGAN:
                warna = (90, 255, 255)
            else:
                warna = (110, 110, 130)
            view.fill((90, 90, 110), (sx - 7, sy - 3, 14, 3))
            cy = sy - 13
            draw.circle(view, warna, (sx, cy), 8, 2)
            for i in range(6):
                a = t * (3 if n >= TARGET_TANTANGAN else 0.5) + i * math.pi / 3
                view.fill(warna, (sx + int(math.cos(a) * 8) - 1, cy + int(math.sin(a) * 8) - 1, 2, 2))
            if selesai or n >= TARGET_TANTANGAN:
                draw.polygon(view, warna, [(sx, cy - 4), (sx + 3, cy), (sx, cy + 4), (sx - 3, cy)])
        elif self.jenis == "portal_pusat":
            view.fill((120, 120, 140), (sx - 9, sy - 4, 18, 4))
            cy = sy - 18
            draw.circle(view, (200, 200, 230), (sx, cy), 11, 2)
            for i, kunci in enumerate(URUTAN_WILAYAH):
                a = t * 1.5 + i * math.pi / 2
                ada = kunci in pr.kristal
                warna = WILAYAH[kunci]["warna"] if ada else (70, 70, 90)
                ox, oy = int(math.cos(a) * 11), int(math.sin(a) * 11)
                view.fill(warna, (sx + ox - 2, cy + oy - 2, 4, 4))
            if len(pr.kristal) >= 4:
                draw.polygon(view, (255, 255, 255), [(sx, cy - 7), (sx + 5, cy), (sx, cy + 7), (sx - 5, cy)])
            else:
                draw.polygon(view, (110, 110, 140), [(sx, cy - 5), (sx + 3, cy), (sx, cy + 5), (sx - 3, cy)])


class Partikel:
    """Partikel suasana per wilayah: kunang-kunang, debu, salju, percikan neon."""
    JUMLAH = {"hutan": 18, "gurun": 25, "gunung": 45, "kota": 30}

    def __init__(self, wilayah):
        self.wilayah = wilayah
        self.p = []
        for _ in range(self.JUMLAH.get(wilayah, 0)):
            self.p.append([random.uniform(0, ui.VIEW_W), random.uniform(0, ui.VIEW_H),
                           random.uniform(0, 6.28), random.uniform(0.6, 1.4)])
        self.glow = pygame.Surface((5, 5), pygame.SRCALPHA)
        pygame.draw.circle(self.glow, (255, 255, 120, 70), (2, 2), 2)

    def update(self, dt):
        W, H = ui.VIEW_W, ui.VIEW_H
        for q in self.p:
            q[2] += dt * 1.5
            if self.wilayah == "hutan":
                q[0] += math.cos(q[2]) * 8 * dt
                q[1] += math.sin(q[2] * 0.7) * 8 * dt
            elif self.wilayah == "gurun":
                q[0] += (20 + 10 * q[3]) * dt
                q[1] += math.sin(q[2]) * 6 * dt
            elif self.wilayah == "gunung":
                q[1] += (12 + 8 * q[3]) * dt
                q[0] += math.sin(q[2]) * 10 * dt
            else:
                q[1] += (60 + 40 * q[3]) * dt
            q[0] %= W
            q[1] %= H

    def gambar(self, view):
        for q in self.p:
            x, y = int(q[0]), int(q[1])
            if self.wilayah == "hutan":
                b = 0.5 + 0.5 * math.sin(q[2] * 3)
                if b > 0.3:
                    view.fill((255, 255, 120), (x, y, 1, 1))
                if b > 0.7:
                    view.blit(self.glow, (x - 2, y - 2))
            elif self.wilayah == "gurun":
                view.fill((235, 205, 150), (x, y, 2, 1))
            elif self.wilayah == "gunung":
                view.fill((255, 255, 255), (x, y, 2 if q[3] > 1.1 else 1, 2 if q[3] > 1.1 else 1))
            else:
                warna = (255, 60, 200) if q[3] > 1.0 else (60, 255, 230)
                view.fill(warna, (x, y, 1, 3))


# ---------- Dunia ----------
class World:
    def __init__(self, progres):
        self.progres = progres
        self.rng = random.Random(2026)
        self.peta = [[RUMPUT] * LP for _ in range(TP)]
        self.varian = [[self.rng.randrange(4) for _ in range(LP)] for _ in range(TP)]
        self._bangun_peta()
        self.npc = [NPC(d) for d in DAFTAR_NPC]
        self.objek = [Objek(d, self) for d in DAFTAR_OBJEK]
        for n in self.npc:
            self.bersihkan(int(n.x // UBIN), int(n.y // UBIN))
        for o in self.objek:
            self.bersihkan(int(o.x // UBIN), int(o.y // UBIN))
        self.bug = []
        self._buat_bug()
        self.spawn = (31 * UBIN + 8, 34 * UBIN + 14)
        self.waktu = 0.0
        self.waktu_hari = 0.2
        self.kx = self.ky = 0.0
        self.partikel = Partikel("hutan")
        self.awan = [[self.rng.uniform(0, LP * UBIN), self.rng.uniform(0, TP * UBIN), self.rng.choice([30, 44, 58])]
                     for _ in range(14)]
        self.teks = []
        self.cd_bug = 0.0
        self.malam = pygame.Surface((ui.VIEW_W, ui.VIEW_H))
        self.minimap = self._buat_minimap()
        self.sinkron_npc()

    # ----- pembuatan peta -----
    def _bangun_peta(self):
        r = self.rng
        P = self.peta
        for ty in range(TP):
            for tx in range(LP):
                w = wilayah_tile(tx, ty)
                p = r.random()
                if w == "hutan":
                    t = POHON if p < 0.10 else SEMAK if p < 0.14 else BUNGA if p < 0.21 else RUMPUT
                elif w == "gurun":
                    t = KAKTUS if p < 0.05 else RERUNTUHAN if p < 0.07 else PASIR
                elif w == "gunung":
                    t = POHON_SALJU if p < 0.07 else BATU if p < 0.12 else SALJU
                else:
                    t = TROTOAR
                P[ty][tx] = t
        # Hutan: sungai berkelok dari utara ke selatan dengan 2 jembatan
        for ty in range(32):
            cx = 11 + int(round(2 * math.sin(ty * 0.35)))
            for tx in (cx, cx + 1):
                if ty in (13, 14, 26, 27):
                    P[ty][tx] = JEMBATAN
                    self.varian[ty][tx] = 0
                else:
                    P[ty][tx] = AIR
            if ty in (13, 14, 26, 27):
                for tx in (cx - 1, cx + 2):
                    P[ty][tx] = RUMPUT
        # Gurun: oasis
        for ty in range(0, 20):
            for tx in range(40, 62):
                d = math.hypot(tx - 50, ty - 8)
                if d <= 3.2:
                    P[ty][tx] = OASIS
                elif d <= 4.6:
                    P[ty][tx] = SEMAK if r.random() < 0.4 else PASIR
        # Pegunungan: jurang air es dengan jembatan
        for tx in range(2, 30):
            for ty in (47, 48):
                P[ty][tx] = JEMBATAN if tx in (13, 14) else AIR_ES
                if tx in (13, 14):
                    self.varian[ty][tx] = 1
        for tx in (12, 13, 14, 15):
            for ty in (46, 49):
                P[ty][tx] = SALJU
        # Kota Cyber: jalan, trotoar, gedung neon
        blok = {}
        for ty in range(32, TP):
            for tx in range(32, LP):
                mx, my = tx % 8, ty % 8
                if mx == 0 or my == 0:
                    P[ty][tx] = JALAN
                    self.varian[ty][tx] = 2 if (mx == 0 and my == 0) else (1 if mx == 0 else 0)
                elif mx in (1, 7) or my in (1, 7):
                    P[ty][tx] = TROTOAR
                else:
                    k = (tx // 8, ty // 8)
                    if k not in blok:
                        blok[k] = r.random() < 0.72
                    if blok[k]:
                        P[ty][tx] = GEDUNG_NEON if my == 2 else GEDUNG
                    else:
                        P[ty][tx] = LANTAI
        # Plaza pusat dan area bersih di sekelilingnya
        for ty in range(25, 39):
            for tx in range(25, 39):
                if 28 <= tx <= 35 and 28 <= ty <= 35:
                    P[ty][tx] = LANTAI
                elif P[ty][tx] in PADAT:
                    P[ty][tx] = DASAR[wilayah_tile(tx, ty)]
        # Tepi peta padat
        tepi = {"hutan": POHON, "gurun": KAKTUS, "gunung": POHON_SALJU, "kota": GEDUNG}
        for i in range(LP):
            for (tx, ty) in ((i, 0), (i, TP - 1), (0, i), (LP - 1, i)):
                P[ty][tx] = tepi[wilayah_tile(tx, ty)]

    def bersihkan(self, tx, ty):
        """Pastikan area 3x3 di sekitar entitas bisa dilewati."""
        for yy in range(ty - 1, ty + 2):
            for xx in range(tx - 1, tx + 2):
                if 1 <= xx < LP - 1 and 1 <= yy < TP - 1 and self.peta[yy][xx] in PADAT:
                    self.peta[yy][xx] = DASAR[wilayah_tile(xx, yy)]

    def _buat_bug(self):
        for w in URUTAN_WILAYAH:
            x0 = 0 if w in ("hutan", "gunung") else 32
            y0 = 0 if w in ("hutan", "gurun") else 32
            n = 0
            while n < 3:
                tx = self.rng.randrange(x0 + 2, x0 + 30)
                ty = self.rng.randrange(y0 + 2, y0 + 30)
                if self.peta[ty][tx] in PADAT or self.peta[ty][tx] in (JEMBATAN, JALAN):
                    continue
                if math.hypot(tx - 32, ty - 32) < 8:
                    continue
                self.bug.append(Bug(tx * UBIN + 8.0, ty * UBIN + 12.0, w))
                n += 1

    def _buat_minimap(self):
        s = pygame.Surface((LP, TP))
        for y in range(TP):
            for x in range(LP):
                s.set_at((x, y), WARNA_MINI.get(self.peta[y][x], (0, 0, 0)))
        return pygame.transform.scale(s, (LP * 2, TP * 2))

    # ----- query -----
    def hitung_selesai(self, kunci):
        return len([i for i in self.progres.tantangan if i.startswith(kunci + "_")])

    def sinkron_npc(self):
        """Menandai NPC yang tantangannya sudah selesai (menghilangkan tanda seru)."""
        for n in self.npc:
            n.selesai_flag = n.id in self.progres.tantangan

    def solid_tile(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= LP or ty >= TP:
            return True
        return self.peta[ty][tx] in PADAT

    def solid_px(self, x, y):
        return self.solid_tile(int(x // UBIN), int(y // UBIN))

    def tabrak(self, rect, abaikan=None):
        for ty in range(rect.top // UBIN, (rect.bottom - 1) // UBIN + 1):
            for tx in range(rect.left // UBIN, (rect.right - 1) // UBIN + 1):
                if self.solid_tile(tx, ty):
                    return True
        for n in self.npc:
            if n is not abaikan and rect.colliderect(n.rect()):
                return True
        for o in self.objek:
            if rect.colliderect(o.rect()):
                return True
        return False

    def wilayah_px(self, x, y):
        return wilayah_tile(int(x // UBIN), int(y // UBIN))

    def cari_interaksi(self, player):
        """Mencari entitas terdekat (dalam jarak 22 px) yang bisa diajak berinteraksi."""
        px, py = player.pusat()
        terbaik, jarak = None, 22.0
        for n in self.npc:
            d = math.hypot(n.x - px, n.y - 4 - py)
            if d < jarak:
                terbaik, jarak = ("npc", n), d
        for o in self.objek:
            d = math.hypot(o.x - px, o.y - 4 - py)
            if d < jarak:
                terbaik, jarak = ("objek", o), d
        for b in self.bug:
            if b.hidup:
                d = math.hypot(b.x - px, b.y - 4 - py)
                if d < jarak:
                    terbaik, jarak = ("bug", b), d
        return terbaik

    def hancurkan_bug(self, b):
        b.hidup = False
        b.respawn = 15.0
        self.tambah_teks("+3 XP", b.x, b.y - 12, (120, 255, 140))

    def tambah_teks(self, isi, x, y, warna=(255, 255, 255)):
        self.teks.append({"teks": isi, "x": x, "y": y, "t": 0.0, "warna": warna})

    def nama_waktu(self):
        w = self.waktu_hari
        if w < 0.1 or w >= 0.95:
            return "Pagi"
        if w < 0.4:
            return "Siang"
        if w < 0.55:
            return "Sore"
        return "Malam"

    # ----- update -----
    def pusatkan(self, player, langsung=False):
        tx = player.x - ui.VIEW_W / 2
        ty = player.y - 10 - ui.VIEW_H / 2
        tx = max(0, min(LP * UBIN - ui.VIEW_W, tx))
        ty = max(0, min(TP * UBIN - ui.VIEW_H, ty))
        if langsung:
            self.kx, self.ky = tx, ty
        else:
            self.kx += (tx - self.kx) * 0.12
            self.ky += (ty - self.ky) * 0.12

    def atur_partikel(self, wilayah):
        if self.partikel.wilayah != wilayah:
            self.partikel = Partikel(wilayah)

    def update(self, dt, player, audio):
        self.waktu += dt
        self.waktu_hari = (self.waktu_hari + dt / 180.0) % 1.0  # 1 hari = 3 menit
        for n in self.npc:
            n.update(dt, self)
        for b in self.bug:
            b.update(dt, self)
        self.partikel.update(dt)
        for a in self.awan:
            a[0] = (a[0] + 5 * dt) % (LP * UBIN + 80)
        for tk in self.teks:
            tk["t"] += dt
        self.teks = [tk for tk in self.teks if tk["t"] < 1.2]
        # tabrakan dengan bug: hanya terdorong, tidak ada hukuman
        self.cd_bug -= dt
        if self.cd_bug <= 0:
            for b in self.bug:
                if b.hidup and abs(b.x - player.x) < 8 and abs(b.y - player.y) < 7:
                    self.cd_bug = 1.0
                    dx, dy = player.x - b.x, player.y - b.y
                    p = math.hypot(dx, dy) or 1
                    nx, ny = player.x + dx / p * 8, player.y + dy / p * 8
                    if not self.tabrak(player.rect_kaki(nx, ny)):
                        player.x, player.y = nx, ny
                    audio.mainkan("bug")
                    self.tambah_teks("Bug!", player.x, player.y - 22, (255, 120, 120))
                    break
        self.pusatkan(player)

    # ----- gambar -----
    def gambar(self, view, player):
        kx, ky = int(self.kx), int(self.ky)
        t = self.waktu
        g = gudang()
        tx0, ty0 = max(0, kx // UBIN), max(0, ky // UBIN)
        tx1 = min(LP, (kx + ui.VIEW_W) // UBIN + 2)
        ty1 = min(TP, (ky + ui.VIEW_H) // UBIN + 2)
        for ty in range(ty0, ty1):
            baris, var = self.peta[ty], self.varian[ty]
            for tx in range(tx0, tx1):
                id_, v, f = baris[tx], var[tx], 0
                if id_ in (AIR, AIR_ES, OASIS):
                    f = (int(t * 4) + ty) % 4
                elif id_ == RUMPUT and v >= 2:
                    f = (int(t * 3) + tx) % 3
                elif id_ == BUNGA:
                    f = (int(t * 2) + tx) % 2
                view.blit(g.ambil(id_, v, f), (tx * UBIN - kx, ty * UBIN - ky))
        # entitas diurutkan berdasarkan y agar tumpang-tindih terlihat benar
        daftar = list(self.objek) + list(self.npc) + [b for b in self.bug if b.hidup] + [player]
        daftar.sort(key=lambda e: e.y)
        for e in daftar:
            e.gambar(view, kx, ky, t)
        # awan
        for ax, ay, aw in self.awan:
            sx, sy = int(ax - 40 - kx), int(ay - ky)
            if -80 < sx < ui.VIEW_W and -30 < sy < ui.VIEW_H:
                self._awan(view, sx, sy, aw)
        # siklus siang-malam
        gelap = max(0.0, -math.sin(2 * math.pi * self.waktu_hari)) ** 0.7
        if gelap > 0.02:
            self.malam.fill((12, 14, 60))
            self.malam.set_alpha(int(135 * gelap))
            view.blit(self.malam, (0, 0))
        elif 0.4 < self.waktu_hari < 0.55:  # semburat sore
            self.malam.fill((255, 150, 60))
            self.malam.set_alpha(28)
            view.blit(self.malam, (0, 0))
        self.partikel.gambar(view)

    def _awan(self, view, x, y, w):
        lapis = pygame.Surface((w, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(lapis, (255, 255, 255, 70), (0, 4, w, 10))
        pygame.draw.ellipse(lapis, (255, 255, 255, 70), (w // 4, 0, w // 2, 10))
        view.blit(lapis, (x, y))

    def gambar_teks(self, surface):
        """Teks melayang (XP, Bug!) digambar di resolusi layar penuh."""
        for tk in self.teks:
            sx = int((tk["x"] - self.kx) * ui.SKALA)
            sy = int((tk["y"] - self.ky) * ui.SKALA - tk["t"] * 30)
            ui.teks(surface, tk["teks"], sx, sy, 28, tk["warna"], tengah=True)

    def gambar_minimap(self, surface, x, y, player, t):
        ui.panel(surface, (x - 6, y - 6, LP * 2 + 12, TP * 2 + 12), (10, 10, 30), ui.PUTIH, 255)
        surface.blit(self.minimap, (x, y))
        for n in self.npc:
            if n.jenis != "pemandu" and not n.selesai_flag:
                surface.fill((255, 220, 70), (x + int(n.x / UBIN * 2) - 1, y + int(n.y / UBIN * 2) - 1, 3, 3))
        for o in self.objek:
            if o.jenis == "portal":
                ok = o.id in self.progres.kristal
                siap = self.hitung_selesai(o.id) >= TARGET_TANTANGAN
                warna = WILAYAH[o.id]["warna"] if ok else ((90, 255, 255) if siap else (130, 130, 150))
                surface.fill(warna, (x + int(o.x / UBIN * 2) - 2, y + int(o.y / UBIN * 2) - 2, 5, 5))
        if int(t * 3) % 2 == 0:
            surface.fill((255, 255, 255), (x + int(player.x / UBIN * 2) - 2, y + int(player.y / UBIN * 2) - 2, 5, 5))
        surface.fill((255, 60, 60), (x + int(player.x / UBIN * 2) - 1, y + int(player.y / UBIN * 2) - 1, 3, 3))
