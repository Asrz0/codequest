# player.py
# Class Player (gerak, animasi, tabrakan) dan Progres (XP, level, kristal, item).
import pygame
from customization import gambar_karakter

KECEPATAN = 62  # piksel per detik (dalam kanvas dunia 320x180)


class Progres:
    """Data kemajuan pemain yang disimpan ke file."""

    def __init__(self):
        self.xp = 0
        self.level = 1
        self.xp_total = 0
        self.kristal = []      # kunci wilayah yang kristalnya sudah pulih
        self.tantangan = []    # id NPC yang tantangannya sudah selesai
        self.peti = []         # id peti yang sudah dibuka
        self.item = {}         # nama item -> jumlah
        self.benar = 0
        self.total = 0
        self.bug = 0
        self.waktu_main = 0.0
        self.tamat = False

    def xp_perlu(self):
        return 40 + 20 * (self.level - 1)

    def tambah_xp(self, jumlah):
        """Menambah XP. Mengembalikan berapa kali naik level."""
        self.xp += jumlah
        self.xp_total += jumlah
        naik = 0
        while self.xp >= self.xp_perlu():
            self.xp -= self.xp_perlu()
            self.level += 1
            naik += 1
        return naik

    def tambah_item(self, nama):
        self.item[nama] = self.item.get(nama, 0) + 1

    def akurasi(self):
        if self.total == 0:
            return 0
        return int(100 * self.benar / self.total)

    def ke_dict(self):
        return dict(self.__dict__)

    @staticmethod
    def dari_dict(d):
        p = Progres()
        for k, v in d.items():
            if hasattr(p, k):
                setattr(p, k, v)
        return p


class Player:
    def __init__(self, cfg, x, y, progres):
        self.cfg = cfg
        self.x = float(x)   # posisi KAKI (tengah bawah) dalam piksel dunia
        self.y = float(y)
        self.arah = "bawah"
        self.bergerak = False
        self.frame_t = 0.0
        self.idle_t = 0.0
        self.langkah_t = 0.0
        self.efek = 0.0
        self.progres = progres
        self.bayangan = pygame.Surface((10, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(self.bayangan, (0, 0, 0, 90), (0, 0, 10, 4))

    def rect_kaki(self, x=None, y=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        return pygame.Rect(int(x - 5), int(y - 6), 10, 6)

    def mulai_efek(self):
        self.efek = 0.4

    def update(self, dt, tombol, world, audio, sentuh=(0.0, 0.0)):
        dx = (1 if (tombol[pygame.K_RIGHT] or tombol[pygame.K_d]) else 0) - \
             (1 if (tombol[pygame.K_LEFT] or tombol[pygame.K_a]) else 0)
        dy = (1 if (tombol[pygame.K_DOWN] or tombol[pygame.K_s]) else 0) - \
             (1 if (tombol[pygame.K_UP] or tombol[pygame.K_w]) else 0)
        if sentuh != (0.0, 0.0):  # joystick virtual menggantikan keyboard
            dx, dy = sentuh
        self.bergerak = (dx != 0 or dy != 0)
        if self.bergerak:
            panjang = (dx * dx + dy * dy) ** 0.5
            if panjang > 1 or sentuh == (0.0, 0.0):
                dx /= panjang
                dy /= panjang
            # gerak sumbu X dan Y terpisah agar bisa "menyusur" dinding
            nx = self.x + dx * KECEPATAN * dt
            if not world.tabrak(self.rect_kaki(nx, self.y)):
                self.x = nx
            ny = self.y + dy * KECEPATAN * dt
            if not world.tabrak(self.rect_kaki(self.x, ny)):
                self.y = ny
            if abs(dx) >= abs(dy):
                self.arah = "kanan" if dx > 0 else "kiri"
            else:
                self.arah = "bawah" if dy > 0 else "atas"
            self.frame_t += dt * 8
            self.idle_t = 0
            self.langkah_t += dt
            if self.langkah_t > 0.28:
                self.langkah_t = 0
                audio.mainkan("langkah")
        else:
            self.idle_t += dt
            self.frame_t = 0
        if self.efek > 0:
            self.efek -= dt

    def pusat(self):
        return (self.x, self.y - 4)

    def gambar(self, view, kx, ky, t):
        if self.bergerak:
            frame = int(self.frame_t) % 4
        else:
            frame = 4 + int(self.idle_t * 2) % 2
        img = gambar_karakter(self.cfg, self.arah, frame)
        sx = int(self.x) - kx
        sy = int(self.y) - ky
        view.blit(self.bayangan, (sx - 5, sy - 2))
        view.blit(img, (sx - 8, sy - 19))
        if self.efek > 0:  # efek interaksi: cincin yang melebar
            r = int((0.4 - self.efek) / 0.4 * 12) + 2
            pygame.draw.circle(view, (255, 240, 120), (sx, sy - 8), r, 1)
            for ox, oy in ((r, 0), (-r, 0), (0, r), (0, -r)):
                view.fill((255, 255, 255), (sx + ox, sy - 8 + oy, 2, 2))
