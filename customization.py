# customization.py
# Sprite karakter digambar dari beberapa LAYER (kaki, badan, kepala, rambut, aksesori)
# sehingga kustomisasi tampil konsisten di semua arah dan frame animasi.
import pygame
import ui

KULIT = [(255, 224, 189), (241, 194, 125), (224, 172, 105), (198, 134, 66), (141, 85, 36), (92, 56, 28)]
RAMBUT = [(40, 30, 25), (110, 70, 30), (200, 150, 60), (235, 215, 130),
          (200, 60, 60), (60, 90, 200), (150, 70, 200), (235, 235, 235)]
BAJU = [(220, 60, 60), (60, 120, 220), (60, 180, 90), (240, 200, 50),
        (150, 80, 200), (240, 140, 50), (235, 235, 235), (50, 50, 60)]
NAMA_BADAN = ["Standar", "Bulat", "Jangkung"]
NAMA_RAMBUT = ["Pendek", "Panjang", "Jabrik", "Kuncir", "Botak", "Mohawk"]

# kaki = tinggi kaki, x0/x1 = lebar badan, lk = lebar satu kaki
TIPE = [{"kaki": 4, "x0": 5, "x1": 10, "lk": 2},
        {"kaki": 3, "x0": 4, "x1": 11, "lk": 3},
        {"kaki": 6, "x0": 6, "x1": 9, "lk": 2}]

PANJANG, TINGGI_SPRITE = 16, 20
_cache = {}


def gelapkan(c, f=0.7):
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f))


def config_default():
    return {"badan": 0, "kulit": 1, "rambut_gaya": 0, "rambut_warna": 0, "baju": 1,
            "topi": False, "kacamata": False, "headphone": False, "tas": False, "aks_warna": 0}


def config_acak(rng):
    return {"badan": rng.randrange(3), "kulit": rng.randrange(6), "rambut_gaya": rng.randrange(6),
            "rambut_warna": rng.randrange(8), "baju": rng.randrange(8),
            "topi": rng.random() < 0.3, "kacamata": rng.random() < 0.3,
            "headphone": rng.random() < 0.2, "tas": rng.random() < 0.3,
            "aks_warna": rng.randrange(8)}


def rapikan_config(cfg):
    """Memastikan config dari file simpanan valid (kunci lengkap, nilai dalam batas)."""
    hasil = config_default()
    batas = {"badan": 3, "kulit": 6, "rambut_gaya": 6, "rambut_warna": 8, "baju": 8, "aks_warna": 8}
    if isinstance(cfg, dict):
        for k, v in cfg.items():
            if k in batas and isinstance(v, int):
                hasil[k] = v % batas[k]
            elif k in ("topi", "kacamata", "headphone", "tas"):
                hasil[k] = bool(v)
    return hasil


def gambar_karakter(cfg, arah, frame):
    """Menggambar sprite 16x20. arah: bawah/atas/kiri/kanan. frame: 0-3 jalan, 4-5 diam."""
    kunci = (tuple(sorted(cfg.items())), arah, frame)
    if kunci in _cache:
        return _cache[kunci]
    s = pygame.Surface((PANJANG, TINGGI_SPRITE), pygame.SRCALPHA)
    t = TIPE[cfg["badan"]]
    kulit = KULIT[cfg["kulit"]]
    rambut = RAMBUT[cfg["rambut_warna"]]
    baju = BAJU[cfg["baju"]]
    aks = BAJU[cfg["aks_warna"]]
    celana = (40, 40, 90)
    sepatu = (30, 30, 30)
    naik = -1 if frame in (1, 3, 5) else 0  # badan naik-turun saat jalan / bernapas
    kanan = (arah == "kanan")
    samping = arah in ("kiri", "kanan")
    d = 1 if kanan else -1

    # posisi vertikal dihitung dari kaki (y=19) ke atas
    ly1 = 19
    ly0 = 19 - t["kaki"] + 1
    ty1 = ly0 - 1
    ty0 = ty1 - 3
    hy1 = ty0 - 1
    hy0 = hy1 - 6
    tx0, tx1 = t["x0"], t["x1"]
    hx0, hx1 = 4, 11

    def R(x0, y0, x1, y1, warna, geser=True):
        if geser:
            y0 += naik
            y1 += naik
        s.fill(warna, (x0, y0, x1 - x0 + 1, y1 - y0 + 1))

    # --- Layer 1: tas (di belakang badan untuk tampak samping) ---
    if cfg["tas"] and samping:
        bx0 = tx0 - 3 if kanan else tx1 + 1
        R(bx0 + 1 if kanan else bx0, ty0, bx0 + 2 if kanan else bx0 + 2, ty1, aks)

    # --- Layer 2: kaki ---
    lk = t["lk"]
    off = 1 if frame in (1, 3) else 0
    if not samping:
        kiri = (8 - lk, 7)
        knan = (8, 7 + lk)
        y_kiri = ly0 + (1 if frame == 1 else 0)
        y_kanan = ly0 + (1 if frame == 3 else 0)
        R(kiri[0], y_kiri, kiri[1], ly1 - 1, celana, False)
        R(kiri[0], ly1, kiri[1], ly1, sepatu, False)
        R(knan[0], y_kanan, knan[1], ly1 - 1, celana, False)
        R(knan[0], ly1, knan[1], ly1, sepatu, False)
    else:
        arah_k = -1 if frame == 3 else 1
        xb = 6 + (-d * off * arah_k)
        xf = 6 + (d * off * arah_k)
        R(xb, ly0, xb + 2, ly1 - 1, gelapkan(celana), False)
        R(xb, ly1, xb + 2, ly1, sepatu, False)
        R(xf, ly0, xf + 2, ly1 - 1, celana, False)
        R(xf, ly1, xf + 2, ly1, sepatu, False)

    # --- Layer 3: badan ---
    R(tx0, ty0, tx1, ty1, baju)
    R(tx0, ty1, tx1, ty1, gelapkan(baju))
    if not samping:
        ayun = 1 if frame == 1 else (-1 if frame == 3 else 0)
        R(tx0 - 1, ty0 + max(0, ayun), tx0 - 1, ty0 + 2 + max(0, ayun), kulit)
        R(tx1 + 1, ty0 + max(0, -ayun), tx1 + 1, ty0 + 2 + max(0, -ayun), kulit)
        if cfg["tas"]:
            if arah == "atas":
                R(tx0, ty0, tx1, ty1 - 1, aks)
                R(tx0 + 1, ty0 + 1, tx1 - 1, ty0 + 1, gelapkan(aks))
            else:
                R(tx0 + 1, ty0, tx0 + 1, ty1, gelapkan(aks))
                R(tx1 - 1, ty0, tx1 - 1, ty1, gelapkan(aks))
    else:
        ayun = (1 if frame == 1 else (-1 if frame == 3 else 0)) * d
        R(7 + ayun, ty0, 8 + ayun, ty0 + 2, kulit)

    # --- Layer 4: kepala ---
    R(hx0, hy0 + 1, hx1, hy1 - 1, kulit)
    R(hx0 + 1, hy0, hx1 - 1, hy0, kulit)
    R(hx0 + 1, hy1, hx1 - 1, hy1, kulit)
    eye_y = hy0 + 3

    # --- Layer 5: rambut ---
    g = cfg["rambut_gaya"]

    def duri(xs):
        for x in xs:
            R(x, hy0 - 2, x, hy0 - 1, rambut)

    if g != 4:
        if g == 5:  # mohawk
            if arah in ("bawah", "atas"):
                R(7, hy0 - 2, 8, hy0 + 1, rambut)
            else:
                R(6, hy0 - 1, 9, hy0 + 1, rambut)
        elif arah == "atas":
            R(hx0, hy0, hx1, hy1 - 1 + (4 if g == 1 else 0), rambut)
            if g == 3:
                R(7, hy1, 8, hy1 + 3, rambut)
            if g == 2:
                duri((5, 7, 9))
        elif arah == "bawah":
            R(hx0, hy0, hx1, hy0 + 1, rambut)
            R(hx0, hy0 + 2, hx0, hy0 + 3, rambut)
            R(hx1, hy0 + 2, hx1, hy0 + 3, rambut)
            if g == 1:
                R(hx0 - 0, hy0 + 4, hx0, hy1 + 3, rambut)
                R(hx1, hy0 + 4, hx1, hy1 + 3, rambut)
            if g == 3:
                R(hx1 + 1, hy0 + 3, hx1 + 1, hy0 + 5, rambut)
            if g == 2:
                duri((5, 7, 9))
        else:  # samping
            R(hx0, hy0, hx1, hy0 + 1, rambut)
            bx0, bx1 = (hx0, hx0 + 3) if kanan else (hx1 - 3, hx1)
            R(bx0, hy0 + 2, bx1, hy0 + 4, rambut)
            if g == 1:
                R(bx0, hy0 + 5, bx1, hy1 + 3, rambut)
            if g == 3:
                xk = hx0 - 1 if kanan else hx1 + 1
                R(xk, hy0 + 3, xk, hy0 + 6, rambut)
            if g == 2:
                duri((6, 8, 10))
            if g == 0:
                R(hx1 if kanan else hx0, hy0 + 2, hx1 if kanan else hx0, hy0 + 2, rambut)

    # --- Layer 6: aksesori kepala ---
    if cfg["topi"]:
        R(hx0, hy0 - 1, hx1, hy0 + 1, aks)
        if arah == "bawah":
            R(hx0 + 1, hy0 + 2, hx1 - 1, hy0 + 2, gelapkan(aks))
        elif samping:
            if kanan:
                R(hx1, hy0 + 2, hx1 + 2, hy0 + 2, gelapkan(aks))
            else:
                R(hx0 - 2, hy0 + 2, hx0, hy0 + 2, gelapkan(aks))
    if cfg["headphone"]:
        band = (60, 60, 70)
        R(hx0, hy0 - 1, hx1, hy0 - 1, band)
        if samping:
            R(6, hy0 + 2, 8, hy0 + 4, aks)
        else:
            R(hx0 - 1, hy0 + 2, hx0, hy0 + 4, aks)
            R(hx1, hy0 + 2, hx1 + 1, hy0 + 4, aks)
    # --- Layer 7: wajah (mata dan kacamata) ---
    mata = (20, 20, 40)
    if arah == "bawah":
        if cfg["kacamata"]:
            R(5, eye_y - 1, 10, eye_y - 1, (20, 20, 20))
            R(5, eye_y, 7, eye_y, (130, 200, 255))
            R(8, eye_y, 10, eye_y, (130, 200, 255))
        R(6, eye_y, 6, eye_y, mata)
        R(9, eye_y, 9, eye_y, mata)
        R(7, hy0 + 5, 8, hy0 + 5, (200, 110, 110))
    elif samping:
        ex = hx1 - 2 if kanan else hx0 + 2
        if cfg["kacamata"]:
            if kanan:
                R(hx1 - 2, eye_y, hx1, eye_y, (130, 200, 255))
                R(hx0 + 1, eye_y, hx1 - 3, eye_y, (20, 20, 20))
            else:
                R(hx0, eye_y, hx0 + 2, eye_y, (130, 200, 255))
                R(hx0 + 3, eye_y, hx1 - 1, eye_y, (20, 20, 20))
        R(ex, eye_y, ex, eye_y, mata)

    s2 = s
    _cache[kunci] = s2
    return s2


# ---------- Layar kustomisasi ----------
class LayarKustomisasi:
    """Layar untuk mengubah tampilan karakter dengan pratinjau beranimasi."""

    BARIS = [("Tipe Badan", "badan", "nama", NAMA_BADAN),
             ("Warna Kulit", "kulit", "warna", KULIT),
             ("Gaya Rambut", "rambut_gaya", "nama", NAMA_RAMBUT),
             ("Warna Rambut", "rambut_warna", "warna", RAMBUT),
             ("Warna Baju", "baju", "warna", BAJU),
             ("Topi", "topi", "ya", None),
             ("Kacamata", "kacamata", "ya", None),
             ("Headphone", "headphone", "ya", None),
             ("Tas", "tas", "ya", None),
             ("Warna Aksesori", "aks_warna", "warna", BAJU)]

    def __init__(self, cfg, audio, saat_selesai, saat_batal):
        self.cfg = dict(cfg)
        self.audio = audio
        self.saat_selesai = saat_selesai
        self.saat_batal = saat_batal
        self.idx = 0
        self.t = 0.0
        self.rects = []
        self.rect_batal = pygame.Rect(410, 496, 130, 36)

    def _ubah(self, baris, arah):
        _, kunci, jenis, daftar = baris
        if jenis == "ya":
            self.cfg[kunci] = not self.cfg[kunci]
        else:
            self.cfg[kunci] = (self.cfg[kunci] + arah) % len(daftar)
        self.audio.mainkan("menu")

    def _acak(self):
        import random
        self.cfg = config_acak(random.Random())
        self.audio.mainkan("item")

    def tangani(self, e):
        total = len(self.BARIS) + 2  # + tombol Acak dan Selesai
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.idx = (self.idx - 1) % total
                self.audio.mainkan("menu")
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.idx = (self.idx + 1) % total
                self.audio.mainkan("menu")
            elif e.key in (pygame.K_LEFT, pygame.K_a) and self.idx < len(self.BARIS):
                self._ubah(self.BARIS[self.idx], -1)
            elif e.key in (pygame.K_RIGHT, pygame.K_d) and self.idx < len(self.BARIS):
                self._ubah(self.BARIS[self.idx], 1)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                if self.idx < len(self.BARIS):
                    self._ubah(self.BARIS[self.idx], 1)
                elif self.idx == len(self.BARIS):
                    self._acak()
                else:
                    self.saat_selesai(self.cfg)
            elif e.key == pygame.K_ESCAPE:
                self.saat_batal()
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect_batal.collidepoint(e.pos):
                self.saat_batal()
                return
            for i, r in enumerate(self.rects):
                if r.collidepoint(e.pos):
                    self.idx = i
                    if i < len(self.BARIS):
                        # klik sisi kiri = mundur, sisi kanan = maju
                        self._ubah(self.BARIS[i], -1 if e.pos[0] < r.centerx else 1)
                    elif i == len(self.BARIS):
                        self._acak()
                    else:
                        self.saat_selesai(self.cfg)

    def update(self, dt):
        self.t += dt

    def gambar(self, surface):
        ui.latar_judul(surface, self.t)
        ui.teks(surface, "KUSTOMISASI KARAKTER", ui.LEBAR // 2, 18, 48, ui.KUNING, tengah=True)
        # pratinjau beranimasi: berputar arah dan berjalan
        ui.panel(surface, (50, 80, 330, 430), (30, 34, 70))
        arahs = ["bawah", "kanan", "atas", "kiri"]
        arah = arahs[int(self.t / 1.6) % 4]
        frame = int(self.t * 8) % 4
        img = gambar_karakter(self.cfg, arah, frame)
        besar = pygame.transform.scale(img, (PANJANG * 12, TINGGI_SPRITE * 12))
        surface.blit(besar, (215 - PANJANG * 6, 150))
        ui.teks(surface, "Pratinjau: " + arah, 215, 420, 26, ui.ABU, tengah=True)
        ui.teks(surface, "Atas/Bawah: pilih  Kiri/Kanan: ubah", 215, 460, 22, ui.ABU, tengah=True)
        # daftar opsi
        self.rects = []
        y = 80
        for i, (nama, kunci, jenis, daftar) in enumerate(self.BARIS):
            r = pygame.Rect(410, y, 500, 32)
            self.rects.append(r)
            if i == self.idx:
                ui.panel(surface, r, (60, 60, 120), ui.KUNING, 220)
            ui.teks(surface, nama, 425, y + 5, 28, ui.KUNING if i == self.idx else ui.PUTIH)
            if jenis == "ya":
                ui.teks(surface, "Ya" if self.cfg[kunci] else "Tidak", 760, y + 5, 28,
                        ui.HIJAU if self.cfg[kunci] else ui.ABU, tengah=True)
            elif jenis == "nama":
                ui.teks(surface, "< " + daftar[self.cfg[kunci]] + " >", 760, y + 5, 28, tengah=True)
            else:
                ui.teks(surface, "<", 665, y + 5, 28)
                pygame.draw.rect(surface, daftar[self.cfg[kunci]], (700, y + 4, 120, 24))
                pygame.draw.rect(surface, ui.PUTIH, (700, y + 4, 120, 24), 2)
                ui.teks(surface, ">", 840, y + 5, 28)
            y += 36
        for j, nama in enumerate(["Acak", "Selesai"]):
            i = len(self.BARIS) + j
            r = pygame.Rect(410 + j * 255, y + 8, 245, 42)
            self.rects.append(r)
            ui.panel(surface, r, (60, 60, 120) if i == self.idx else (36, 36, 80),
                     ui.KUNING if i == self.idx else ui.PUTIH, 230)
            ui.teks(surface, nama, r.centerx, r.y + 9, 32,
                    ui.KUNING if i == self.idx else ui.PUTIH, tengah=True)
        ui.panel(surface, self.rect_batal, (60, 40, 40), ui.MERAH, 240)
        ui.teks(surface, "Batal", self.rect_batal.centerx, self.rect_batal.y + 8, 26, tengah=True)
