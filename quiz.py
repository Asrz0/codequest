# quiz.py
# QuizManager memuat bank soal dari data/soal.json dan membuat 4 jenis tantangan:
# pilihan ganda, susun urutan, teka-teki biner, dan pencocokan istilah.
import json
import random
import pygame
import ui


class TantanganDasar:
    """Kelas dasar semua tantangan: menyimpan hasil (lulus, xp, benar, total)."""

    def __init__(self, audio, judul, nama_wilayah):
        self.audio = audio
        self.judul = judul
        self.nama_wilayah = nama_wilayah
        self.selesai = False   # True saat pemain menutup layar hasil
        self.lulus = False
        self.xp = 0
        self.benar = 0
        self.total = 0
        self.fase = "main"     # "main" atau "hasil"
        self.t = 0.0
        self.rect_batal = pygame.Rect(866, 34, 46, 40)  # tombol X (keluar tanpa hadiah)

    def update(self, dt):
        self.t += dt

    def tombol_lanjut(self, e):
        return e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e)

    def klik(self, e):
        return e.type == pygame.MOUSEBUTTONDOWN and e.button == 1

    def kerangka(self, surface, sub=""):
        """Latar gelap + panel + judul."""
        lapis = pygame.Surface((ui.LEBAR, ui.TINGGI), pygame.SRCALPHA)
        lapis.fill((0, 0, 0, 170))
        surface.blit(lapis, (0, 0))
        ui.panel(surface, (40, 30, 880, 480))
        ui.teks(surface, self.judul + " - " + self.nama_wilayah, 65, 45, 36, ui.KUNING)
        if sub:
            ui.teks(surface, sub, 850 - ui.font(30).size(sub)[0], 50, 30, ui.ABU)
        if self.fase != "hasil":
            ui.panel(surface, self.rect_batal, (110, 30, 30), ui.MERAH, 240)
            ui.teks(surface, "X", self.rect_batal.centerx, self.rect_batal.y + 9, 30, tengah=True)

    def layar_hasil(self, surface, ringkas):
        """Layar hasil umum."""
        warna = ui.HIJAU if self.lulus else ui.MERAH
        ui.teks(surface, "BERHASIL!" if self.lulus else "BELUM BERHASIL", 480, 150, 64, warna, tengah=True)
        y = 240
        for baris in ringkas:
            ui.teks(surface, baris, 480, y, 34, tengah=True)
            y += 44
        ui.teks(surface, "+%d XP" % self.xp, 480, y + 10, 44, ui.KUNING, tengah=True)
        if int(self.t * 2) % 2 == 0:
            ui.teks(surface, "Tekan Enter untuk lanjut", 480, 460, 28, ui.ABU, tengah=True)


class TantanganPilihanGanda(TantanganDasar):
    def __init__(self, daftar, audio, nama_wilayah, judul="Kuis Pilihan Ganda", min_benar=2):
        TantanganDasar.__init__(self, audio, judul, nama_wilayah)
        self.soal = daftar
        self.total = len(daftar)
        self.min_benar = min_benar
        self.i = 0
        self.rect_opsi = []
        self._siapkan()

    def _siapkan(self):
        s = self.soal[self.i]
        pil = list(enumerate(s["pilihan"]))
        random.shuffle(pil)  # acak urutan pilihan
        self.opsi = [(teks, idx == s["jawab"]) for idx, teks in pil]
        self.kursor = 0
        self.terjawab = False
        self.pilih = None

    def _jawab(self, k):
        if self.terjawab or k >= len(self.opsi):
            return
        self.terjawab = True
        self.pilih = k
        if self.opsi[k][1]:
            self.benar += 1
            self.xp += 10
            self.audio.mainkan("benar")
        else:
            self.audio.mainkan("salah")

    def _lanjut(self):
        self.i += 1
        if self.i >= len(self.soal):
            self.fase = "hasil"
            self.lulus = self.benar >= self.min_benar
            if self.lulus:
                self.xp += 5
        else:
            self._siapkan()

    def tangani(self, e):
        if self.fase == "hasil":
            if self.tombol_lanjut(e) or self.klik(e):
                self.selesai = True
            return
        if e.type == pygame.KEYDOWN:
            if not self.terjawab:
                if e.key in (pygame.K_UP, pygame.K_w):
                    self.kursor = (self.kursor - 1) % len(self.opsi)
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    self.kursor = (self.kursor + 1) % len(self.opsi)
                elif pygame.K_1 <= e.key <= pygame.K_4:
                    self._jawab(e.key - pygame.K_1)
                elif self.tombol_lanjut(e):
                    self._jawab(self.kursor)
            elif self.tombol_lanjut(e):
                self._lanjut()
        elif self.klik(e):
            if not self.terjawab:
                for k, r in enumerate(self.rect_opsi):
                    if r.collidepoint(e.pos):
                        self._jawab(k)
            else:
                self._lanjut()

    def gambar(self, surface):
        if self.fase == "hasil":
            self.kerangka(surface)
            self.layar_hasil(surface, ["Benar %d dari %d soal" % (self.benar, self.total),
                                       "Minimal %d benar untuk lulus" % self.min_benar])
            return
        self.kerangka(surface, "Soal %d/%d" % (self.i + 1, self.total))
        s = self.soal[self.i]
        y = 100
        for baris in ui.bungkus(s["tanya"], 32, 800):
            ui.teks(surface, baris, 70, y, 32)
            y += 36
        self.rect_opsi = []
        y = 205
        for k, (teks, benar) in enumerate(self.opsi):
            r = pygame.Rect(70, y, 820, 46)
            self.rect_opsi.append(r)
            isi, tepi = (40, 44, 90), ui.PUTIH
            if self.terjawab:
                if benar:
                    isi, tepi = (30, 100, 50), ui.HIJAU
                elif k == self.pilih:
                    isi, tepi = (110, 30, 30), ui.MERAH
            elif k == self.kursor:
                isi, tepi = (60, 60, 130), ui.KUNING
            ui.panel(surface, r, isi, tepi, 240)
            ui.teks(surface, "%d. %s" % (k + 1, teks), 90, y + 12, 28)
            y += 54
        if self.terjawab:
            benar = self.opsi[self.pilih][1]
            ui.teks(surface, "Benar!" if benar else "Kurang tepat.", 70, 425, 30,
                    ui.HIJAU if benar else ui.MERAH)
            yy = 455
            for baris in ui.bungkus(s["penjelasan"], 24, 780)[:2]:
                ui.teks(surface, baris, 70, yy, 24, ui.PUTIH)
                yy += 24
            ui.teks(surface, "[Enter]", 860, 480, 22, ui.KUNING)


class TantanganUrutan(TantanganDasar):
    def __init__(self, soal, audio, nama_wilayah):
        TantanganDasar.__init__(self, audio, "Susun Urutan", nama_wilayah)
        self.soal = soal
        self.benar_urut = list(soal["langkah"])
        self.item = list(soal["langkah"])
        for _ in range(20):  # acak sampai urutannya berbeda dari aslinya
            random.shuffle(self.item)
            if self.item != self.benar_urut:
                break
        self.dipakai = [False] * len(self.item)
        self.urutan = []
        self.kursor = 0
        self.total = 1
        self.rect_item = []
        self.rect_undo = pygame.Rect(500, 435, 200, 42)

    def _pilih(self, i):
        if i < 0 or i >= len(self.item) or self.dipakai[i]:
            return
        self.dipakai[i] = True
        self.urutan.append(i)
        self.audio.mainkan("interaksi")
        self._geser(1)
        if len(self.urutan) == len(self.item):
            self._periksa()

    def _geser(self, arah):
        """Memindahkan kursor ke item berikutnya yang belum dipakai."""
        if all(self.dipakai):
            return
        for _ in range(len(self.item)):
            self.kursor = (self.kursor + arah) % len(self.item)
            if not self.dipakai[self.kursor]:
                return

    def _batal(self):
        if self.urutan:
            i = self.urutan.pop()
            self.dipakai[i] = False
            self.kursor = i
            self.audio.mainkan("menu")

    def _periksa(self):
        jawab = [self.item[i] for i in self.urutan]
        self.fase = "hasil"
        if jawab == self.benar_urut:
            self.lulus = True
            self.benar = 1
            self.xp = 25
            self.audio.mainkan("benar")
        else:
            self.audio.mainkan("salah")

    def tangani(self, e):
        if self.fase == "hasil":
            if self.tombol_lanjut(e) or self.klik(e):
                self.selesai = True
            return
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                if self.dipakai[self.kursor]:
                    self._geser(1)
                self._geser(-1)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self._geser(1)
            elif self.tombol_lanjut(e):
                self._pilih(self.kursor)
            elif e.key in (pygame.K_BACKSPACE, pygame.K_x):
                self._batal()
        elif self.klik(e):
            if self.rect_undo.collidepoint(e.pos):
                self._batal()
            for i, r in enumerate(self.rect_item):
                if r.collidepoint(e.pos):
                    self._pilih(i)

    def gambar(self, surface):
        self.kerangka(surface)
        if self.fase == "hasil":
            if self.lulus:
                self.layar_hasil(surface, ["Urutan langkahmu sudah benar!"])
            else:
                ui.teks(surface, "Urutan belum tepat. Urutan yang benar:", 70, 100, 32, ui.MERAH)
                y = 145
                for n, b in enumerate(self.benar_urut):
                    ui.teks(surface, "%d. %s" % (n + 1, b), 90, y, 26, ui.HIJAU)
                    y += 32
                yy = y + 10
                for baris in ui.bungkus(self.soal["penjelasan"], 24, 800):
                    ui.teks(surface, baris, 70, yy, 24)
                    yy += 26
                ui.teks(surface, "Tekan Enter, lalu coba lagi nanti.", 70, 470, 24, ui.ABU)
            return
        ui.teks(surface, self.soal["judul"], 70, 95, 32)
        ui.teks(surface, "Pilih langkah (Enter/klik). Backspace: batalkan.", 70, 128, 24, ui.ABU)
        ui.teks(surface, "Langkah tersedia", 70, 165, 28, ui.KUNING)
        ui.teks(surface, "Urutanmu", 500, 165, 28, ui.KUNING)
        self.rect_item = []
        y = 200
        for i, teks in enumerate(self.item):
            r = pygame.Rect(70, y, 410, 44)
            self.rect_item.append(r)
            if self.dipakai[i]:
                ui.panel(surface, r, (30, 30, 50), (80, 80, 100), 200)
                ui.teks(surface, teks[:34], 80, y + 12, 22, (90, 90, 110))
            else:
                sel = (i == self.kursor)
                ui.panel(surface, r, (60, 60, 130) if sel else (40, 44, 90), ui.KUNING if sel else ui.PUTIH, 240)
                ui.teks(surface, teks[:34], 80, y + 12, 22)
            y += 50
        ui.panel(surface, self.rect_undo, (60, 40, 40), ui.MERAH, 240)
        ui.teks(surface, "Batalkan", self.rect_undo.centerx, self.rect_undo.y + 11, 26, tengah=True)
        y = 200
        for n, i in enumerate(self.urutan):
            ui.teks(surface, "%d. %s" % (n + 1, self.item[i][:34]), 500, y, 24, ui.HIJAU)
            y += 38


class TantanganBiner(TantanganDasar):
    def __init__(self, soal, audio, nama_wilayah):
        TantanganDasar.__init__(self, audio, "Teka-teki Biner", nama_wilayah)
        self.soal = soal
        self.n = soal["bit"]
        self.bits = [0] * self.n
        self.kursor = 0
        self.percobaan = 0
        self.rect_bit = []
        self.rect_periksa = pygame.Rect(390, 402, 180, 46)

    def _nilai(self):
        v = 0
        for b in self.bits:
            v = v * 2 + b
        return v

    def _toggle(self, i):
        self.bits[i] = 1 - self.bits[i]
        self.audio.mainkan("menu")

    def _periksa(self):
        self.percobaan += 1
        if self._nilai() == self.soal["nilai"]:
            self.fase = "hasil"
            self.lulus = True
            self.benar = 1
            self.total = self.percobaan
            self.xp = 20 if self.percobaan == 1 else 12
            self.audio.mainkan("benar")
        else:
            self.audio.mainkan("salah")

    def tangani(self, e):
        if self.fase == "hasil":
            if self.tombol_lanjut(e) or self.klik(e):
                self.selesai = True
            return
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_LEFT, pygame.K_a):
                self.kursor = (self.kursor - 1) % self.n
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self.kursor = (self.kursor + 1) % self.n
            elif e.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s):
                self._toggle(self.kursor)
            elif e.key == pygame.K_RETURN:
                self._periksa()
        elif self.klik(e):
            if self.rect_periksa.collidepoint(e.pos):
                self._periksa()
                return
            for i, r in enumerate(self.rect_bit):
                if r.collidepoint(e.pos):
                    self.kursor = i
                    self._toggle(i)

    def gambar(self, surface):
        self.kerangka(surface, "Percobaan: %d" % self.percobaan)
        if self.fase == "hasil":
            self.layar_hasil(surface, [self.soal["penjelasan"]])
            return
        y = 110
        for baris in ui.bungkus(self.soal["tanya"], 32, 800):
            ui.teks(surface, baris, 70, y, 32)
            y += 36
        lebar = 80 if self.n <= 4 else 90
        total = self.n * (lebar + 10)
        x0 = 480 - total // 2
        self.rect_bit = []
        for i in range(self.n):
            nilai = 2 ** (self.n - 1 - i)
            r = pygame.Rect(x0 + i * (lebar + 10), 240, lebar if self.n <= 4 else 64, 110)
            if self.n > 4:
                r.x = 480 - (self.n * 74) // 2 + i * 74
            self.rect_bit.append(r)
            ui.teks(surface, str(nilai), r.centerx, 205, 30, ui.ABU, tengah=True)
            nyala = self.bits[i] == 1
            ui.panel(surface, r, (30, 120, 60) if nyala else (40, 40, 80),
                     ui.KUNING if i == self.kursor else ui.PUTIH, 245)
            ui.teks(surface, str(self.bits[i]), r.centerx, r.y + 30, 56, ui.HIJAU if nyala else ui.ABU, tengah=True)
        ui.teks(surface, "Sentuh/klik kotak untuk ubah 0/1 (keyboard: Kiri/Kanan, Spasi, Enter)", 480, 368, 22, ui.ABU, tengah=True)
        ui.panel(surface, self.rect_periksa, (30, 100, 60), ui.HIJAU, 245)
        ui.teks(surface, "PERIKSA", self.rect_periksa.centerx, self.rect_periksa.y + 12, 30, tengah=True)
        if self.percobaan > 0:
            ui.teks(surface, "Belum tepat, coba lagi!", 480, 458, 28, ui.MERAH, tengah=True)
        if self.percobaan >= 2:
            ui.teks(surface, "Petunjuk: " + self.soal["penjelasan"], 480, 488, 22, ui.KUNING, tengah=True)


class TantanganPencocokan(TantanganDasar):
    def __init__(self, soal, audio, nama_wilayah):
        TantanganDasar.__init__(self, audio, "Cocokkan Istilah", nama_wilayah)
        self.soal = soal
        n = len(soal["pasangan"])
        self.kiri = list(range(n))
        self.kanan = list(range(n))
        random.shuffle(self.kiri)
        random.shuffle(self.kanan)
        self.cocok = set()
        self.kolom = 0
        self.kur_k = 0
        self.kur_r = 0
        self.pilih_kiri = None
        self.salah = 0
        self.flash = 0.0
        self.rect_k = []
        self.rect_r = []

    def _geser(self, kolom, arah):
        daftar = self.kiri if kolom == 0 else self.kanan
        kur = self.kur_k if kolom == 0 else self.kur_r
        for _ in range(len(daftar)):
            kur = (kur + arah) % len(daftar)
            if daftar[kur] not in self.cocok:
                break
        if kolom == 0:
            self.kur_k = kur
        else:
            self.kur_r = kur

    def _awal(self):
        """Pindahkan kursor ke item pertama yang belum cocok pada kedua kolom."""
        for i, p in enumerate(self.kiri):
            if p not in self.cocok:
                self.kur_k = i
                break
        for i, p in enumerate(self.kanan):
            if p not in self.cocok:
                self.kur_r = i
                break

    def _ambil_kiri(self, i):
        if self.kiri[i] in self.cocok:
            return
        self.pilih_kiri = self.kiri[i]
        self.kur_k = i
        self.kolom = 1
        self.audio.mainkan("interaksi")

    def _ambil_kanan(self, i):
        if self.pilih_kiri is None or self.kanan[i] in self.cocok:
            return
        if self.kanan[i] == self.pilih_kiri:
            self.cocok.add(self.pilih_kiri)
            self.audio.mainkan("benar")
        else:
            self.salah += 1
            self.flash = 0.4
            self.audio.mainkan("salah")
        self.pilih_kiri = None
        self.kolom = 0
        self._awal()
        if len(self.cocok) == len(self.kiri):
            self.fase = "hasil"
            self.lulus = True
            n = len(self.kiri)
            self.benar = n
            self.total = n + self.salah
            self.xp = max(10, 30 - 5 * self.salah)

    def update(self, dt):
        self.t += dt
        if self.flash > 0:
            self.flash -= dt

    def tangani(self, e):
        if self.fase == "hasil":
            if self.tombol_lanjut(e) or self.klik(e):
                self.selesai = True
            return
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self._geser(self.kolom, -1)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self._geser(self.kolom, 1)
            elif e.key in (pygame.K_LEFT, pygame.K_a) and self.kolom == 1:
                self.kolom = 0
                self.pilih_kiri = None
            elif self.tombol_lanjut(e):
                if self.kolom == 0:
                    self._ambil_kiri(self.kur_k)
                else:
                    self._ambil_kanan(self.kur_r)
        elif self.klik(e):
            for i, r in enumerate(self.rect_k):
                if r.collidepoint(e.pos):
                    self._ambil_kiri(i)
            for i, r in enumerate(self.rect_r):
                if r.collidepoint(e.pos):
                    self._ambil_kanan(i)

    def gambar(self, surface):
        self.kerangka(surface, "Salah: %d" % self.salah)
        p = self.soal["pasangan"]
        if self.fase == "hasil":
            self.layar_hasil(surface, ["Semua pasangan cocok! (salah %d kali)" % self.salah,
                                       self.soal["penjelasan"][:70]])
            return
        ui.teks(surface, self.soal["judul"], 70, 95, 32)
        ui.teks(surface, "Pilih istilah di kiri, lalu pasangannya di kanan.", 70, 130, 24, ui.ABU)
        self.rect_k, self.rect_r = [], []
        for kol, daftar, rects in ((0, self.kiri, self.rect_k), (1, self.kanan, self.rect_r)):
            y = 180
            for i, idx in enumerate(daftar):
                x = 70 if kol == 0 else 400
                r = pygame.Rect(x, y, 320 if kol == 0 else 490, 54)
                rects.append(r)
                isi, tepi = (40, 44, 90), ui.PUTIH
                if idx in self.cocok:
                    isi, tepi = (30, 100, 50), ui.HIJAU
                elif kol == 0 and self.pilih_kiri == idx:
                    isi, tepi = (110, 90, 20), ui.KUNING
                elif kol == self.kolom and i == (self.kur_k if kol == 0 else self.kur_r):
                    isi, tepi = (60, 60, 130), ui.KUNING
                if self.flash > 0 and kol == 1 and i == self.kur_r:
                    isi, tepi = (110, 30, 30), ui.MERAH
                ui.panel(surface, r, isi, tepi, 240)
                teks = p[idx][0] if kol == 0 else p[idx][1]
                ui.teks(surface, teks, r.x + 14, r.y + 16, 26 if kol == 0 else 24)
                y += 62


class QuizManager:
    """Memuat soal dan membuat tantangan. Soal tidak berulang sampai semua terpakai."""

    def __init__(self, jalur, audio):
        with open(jalur, encoding="utf-8") as f:
            self.data = json.load(f)
        self.audio = audio
        self.antrean = {}
        self.aktif = None

    def _ambil(self, wilayah, jenis, n):
        kunci = (wilayah, jenis)
        daftar = self.data[wilayah][jenis]
        antre = self.antrean.get(kunci, [])
        hasil = []
        while len(hasil) < n:
            if not antre:
                antre = list(range(len(daftar)))
                random.shuffle(antre)
            hasil.append(daftar[antre.pop()])
        self.antrean[kunci] = antre
        return hasil

    def buat(self, jenis, wilayah, gerbang=False):
        nama = self.data[wilayah]["nama"]
        if jenis == "pilgan":
            judul = "Gerbang Kristal" if gerbang else "Kuis Pilihan Ganda"
            c = TantanganPilihanGanda(self._ambil(wilayah, "pilihan_ganda", 3), self.audio, nama, judul, 2)
        elif jenis == "urutan":
            c = TantanganUrutan(self._ambil(wilayah, "urutan", 1)[0], self.audio, nama)
        elif jenis == "biner":
            c = TantanganBiner(self._ambil(wilayah, "biner", 1)[0], self.audio, nama)
        else:
            c = TantanganPencocokan(self._ambil(wilayah, "pencocokan", 1)[0], self.audio, nama)
        self.aktif = c
        return c

    def jumlah_soal(self, wilayah):
        return len(self.data[wilayah]["pilihan_ganda"])
