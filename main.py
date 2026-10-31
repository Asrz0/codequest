# main.py
# Code Quest: Petualangan Informatika
# Class Game: mengatur menu, scene, input, HUD, simpan/muat, dan loop utama 60 FPS.
import json
import random
import pygame

import ui
from audio import AudioManager, SR
from customization import LayarKustomisasi, config_default, rapikan_config
from player import Player, Progres
from quiz import QuizManager
from world import World, WILAYAH, URUTAN_WILAYAH, TARGET_TANTANGAN

JUDUL = "Code Quest: Petualangan Informatika"


class Game:
    def __init__(self):
        pygame.mixer.pre_init(SR, -16, 1, 1024)
        pygame.init()
        pygame.display.set_caption(JUDUL)
        try:
            if ui.ANDROID:
                self.layar = pygame.display.set_mode((ui.LEBAR, ui.TINGGI), pygame.FULLSCREEN | pygame.SCALED)
            else:
                self.layar = pygame.display.set_mode((ui.LEBAR, ui.TINGGI), pygame.SCALED | pygame.RESIZABLE)
        except pygame.error:
            self.layar = pygame.display.set_mode((ui.LEBAR, ui.TINGGI))
        self.view = pygame.Surface((ui.VIEW_W, ui.VIEW_H))
        self.jam = pygame.time.Clock()
        self.jalan = True
        self.t = 0.0

        self.audio = AudioManager()
        self.kuis = QuizManager(ui.jalur_sumber("data/soal.json"), self.audio)
        self.dialog = ui.KotakDialog(self.audio)
        self.transisi = ui.Transisi()
        self.sentuh = ui.KontrolSentuh()
        self.blok_klik = 0.0   # mengabaikan klik tiruan sesaat setelah menyentuh tombol layar
        self.set_rect = []

        self.pengaturan = {"musik": 0.6, "efek": 0.8, "mute": False}
        self.cfg = config_default()
        self.data_save = {}
        self.jalur_save = ui.jalur_simpan("save.json")
        self.muat_file()

        self.progres = None
        self.player = None
        self.world = None
        self.chal = None          # tantangan yang sedang berjalan
        self.chal_info = None     # (jenis, npc atau kunci wilayah)
        self.layar_kustom = None
        self.wilayah = None
        self.spanduk = ["", 0.0]
        self.state = "menu"
        self.kembali = "menu"     # state tujuan saat keluar dari pengaturan
        self.menu_idx = 0
        self.menu_rect = []
        self.pause_idx = 0
        self.pause_rect = []
        self.set_idx = 0
        self.ending = False
        self.audio.putar_musik("menu")

    # ---------- Simpan / muat ----------
    def muat_file(self):
        try:
            with open(self.jalur_save, encoding="utf-8") as f:
                self.data_save = json.load(f)
            self.pengaturan.update(self.data_save.get("pengaturan", {}))
            self.cfg = rapikan_config(self.data_save.get("karakter"))
        except (OSError, ValueError):
            self.data_save = {}
        # AudioManager dibuat sebelum muat_file, jadi terapkan volume setelahnya
        if hasattr(self, "audio"):
            self.terapkan_audio()

    def terapkan_audio(self):
        self.audio.atur(self.pengaturan["musik"], self.pengaturan["efek"], self.pengaturan["mute"])

    def ada_save(self):
        return "progres" in self.data_save

    def simpan_semua(self):
        data = dict(self.data_save)
        data["pengaturan"] = self.pengaturan
        data["karakter"] = self.cfg
        if self.progres and self.player and self.world:
            data["progres"] = self.progres.ke_dict()
            data["posisi"] = [self.player.x, self.player.y]
            data["waktu_hari"] = self.world.waktu_hari
        try:
            with open(self.jalur_save, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.data_save = data
        except OSError:
            pass

    # ---------- Memulai game ----------
    def buat_dunia(self, progres, x=None, y=None):
        self.progres = progres
        self.world = World(progres)
        px, py = self.world.spawn if x is None else (x, y)
        self.player = Player(self.cfg, px, py, progres)
        self.world.pusatkan(self.player, True)
        self.wilayah = None
        self.state = "dunia"
        self.ending = False

    def mulai_baru(self):
        self.buat_dunia(Progres())
        self.dialog.buka("Narator", [
            "Kamu sedang belajar di depan komputer, tiba-tiba layar bersinar dan menarikmu masuk ke dunia digital!",
            "Kristal Data, sumber pengetahuan dunia ini, telah pecah menjadi 4 pecahan.",
            "Selesaikan tantangan di tiap wilayah untuk memulihkannya. Bicaralah dengan Prof. Pixel di plaza."])
        self.simpan_semua()

    def lanjutkan(self):
        d = self.data_save
        pos = d.get("posisi", [None, None])
        self.buat_dunia(Progres.dari_dict(d["progres"]), pos[0], pos[1])
        self.world.waktu_hari = d.get("waktu_hari", 0.2)

    def pindah(self, aksi, mode="piksel"):
        self.transisi.mulai(aksi, mode, 0.9)

    # ---------- Event ----------
    def event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
            return
        if e.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            boleh = self.state == "dunia" and not self.dialog.aktif and not self.transisi.aktif
            aksi = self.sentuh.tangani(e, boleh)
            if self.sentuh.diklaim:
                self.blok_klik = 0.3
                self.sentuh.diklaim = False
            if aksi == "aksi":
                self.interaksi()
            elif aksi == "jeda":
                self.pause_idx = 0
                self.state = "pause"
            return
        if self.blok_klik > 0 and e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            return
        if self.transisi.aktif:
            return
        f = getattr(self, "event_" + self.state)
        f(e)

    def event_menu(self, e):
        n = 5
        nonaktif = [] if self.ada_save() else [1]
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.menu_idx = (self.menu_idx - 1) % n
                while self.menu_idx in nonaktif:
                    self.menu_idx = (self.menu_idx - 1) % n
                self.audio.mainkan("menu")
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_idx = (self.menu_idx + 1) % n
                while self.menu_idx in nonaktif:
                    self.menu_idx = (self.menu_idx + 1) % n
                self.audio.mainkan("menu")
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self.pilih_menu(self.menu_idx)
            elif e.key == pygame.K_m:
                self.pengaturan["mute"] = self.audio.toggle_mute()
        elif e.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.menu_rect):
                if r.collidepoint(e.pos) and i not in nonaktif:
                    self.menu_idx = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self.menu_rect):
                if r.collidepoint(e.pos) and i not in nonaktif:
                    self.menu_idx = i
                    self.pilih_menu(i)

    def pilih_menu(self, i):
        self.audio.mainkan("interaksi")
        if i == 0:      # Main Baru -> kustomisasi dulu
            self.buka_kustom(lambda cfg: self.selesai_kustom_baru(cfg), "menu")
        elif i == 1:    # Lanjutkan
            self.pindah(self.lanjutkan)
        elif i == 2:    # Kustomisasi dari menu
            self.buka_kustom(lambda cfg: self.selesai_kustom(cfg, "menu"), "menu")
        elif i == 3:
            self.kembali = "menu"
            self.state = "setting"
        elif i == 4:
            self.jalan = False

    # ----- kustomisasi -----
    def buka_kustom(self, saat_selesai, kembali):
        self.layar_kustom = LayarKustomisasi(self.cfg, self.audio, saat_selesai,
                                             lambda: self.batal_kustom(kembali))
        self.state = "kustom"

    def batal_kustom(self, kembali):
        self.state = kembali

    def selesai_kustom(self, cfg, kembali):
        self.cfg = rapikan_config(cfg)
        if self.player:
            self.player.cfg = self.cfg
        self.simpan_semua()
        self.audio.mainkan("level_up")
        self.state = kembali

    def selesai_kustom_baru(self, cfg):
        self.cfg = rapikan_config(cfg)
        self.audio.mainkan("level_up")
        self.pindah(self.mulai_baru)

    def event_kustom(self, e):
        self.layar_kustom.tangani(e)

    # ----- pengaturan -----
    def event_setting(self, e):
        butir = ["musik", "efek", "mute", None]
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self.set_rect):
                if r.collidepoint(e.pos):
                    self.set_idx = i
                    k = butir[i]
                    if k in ("musik", "efek"):
                        if e.pos[0] >= 470:  # ketuk pada bar = atur volume
                            self.pengaturan[k] = round(max(0.0, min(1.0, (e.pos[0] - 480) / 210.0)), 1)
                            self.terapkan_audio()
                            self.audio.mainkan("menu")
                    elif k == "mute":
                        self.pengaturan["mute"] = not self.pengaturan["mute"]
                        self.terapkan_audio()
                    else:
                        self.keluar_setting()
            return
        if e.type != pygame.KEYDOWN:
            return
        if e.key in (pygame.K_UP, pygame.K_w):
            self.set_idx = (self.set_idx - 1) % 4
            self.audio.mainkan("menu")
        elif e.key in (pygame.K_DOWN, pygame.K_s):
            self.set_idx = (self.set_idx + 1) % 4
            self.audio.mainkan("menu")
        elif e.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
            arah = -1 if e.key in (pygame.K_LEFT, pygame.K_a) else 1
            k = butir[self.set_idx]
            if k in ("musik", "efek"):
                self.pengaturan[k] = round(max(0.0, min(1.0, self.pengaturan[k] + 0.1 * arah)), 1)
                self.terapkan_audio()
                self.audio.mainkan("menu")
            elif k == "mute":
                self.pengaturan["mute"] = not self.pengaturan["mute"]
                self.terapkan_audio()
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            if self.set_idx == 2:
                self.pengaturan["mute"] = not self.pengaturan["mute"]
                self.terapkan_audio()
            elif self.set_idx == 3:
                self.keluar_setting()
        elif e.key == pygame.K_ESCAPE:
            self.keluar_setting()

    def keluar_setting(self):
        self.simpan_semua()
        self.state = self.kembali

    # ----- dunia -----
    def event_dunia(self, e):
        if self.dialog.aktif:  # tombol E/Enter/Spasi atau ketuk layar melanjutkan dialog
            if (e.type == pygame.KEYDOWN and e.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE)) or \
                    (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
                self.dialog.tekan()
            return
        if e.type != pygame.KEYDOWN:
            return
        if e.key == pygame.K_ESCAPE:
            self.pause_idx = 0
            self.state = "pause"
            self.audio.mainkan("menu")
        elif e.key in (pygame.K_e, pygame.K_RETURN):
            self.interaksi()
        elif e.key == pygame.K_m:
            self.pengaturan["mute"] = self.audio.toggle_mute()

    def interaksi(self):
        hasil = self.world.cari_interaksi(self.player)
        if not hasil:
            return
        jenis, ent = hasil
        self.audio.mainkan("interaksi")
        self.player.mulai_efek()
        if jenis == "npc":
            self.bicara_npc(ent)
        elif jenis == "objek":
            self.pakai_objek(ent)
        else:
            self.world.hancurkan_bug(ent)
            self.progres.bug += 1
            self.beri_xp(3)
            self.audio.mainkan("item")

    def beri_xp(self, jumlah):
        naik = self.progres.tambah_xp(jumlah)
        if naik > 0:
            self.audio.mainkan("level_up")
            self.spanduk = ["LEVEL %d!" % self.progres.level, 2.5]

    def bicara_npc(self, npc):
        if npc.jenis == "pemandu":
            teks = npc.sapa if len(self.progres.kristal) == 0 else npc.selesai
            self.dialog.buka(npc.nama, teks)
        elif npc.id in self.progres.tantangan:
            self.dialog.buka(npc.nama, npc.selesai)
        else:
            self.dialog.buka(npc.nama, npc.sapa, lambda: self.mulai_tantangan(npc.jenis, npc.wilayah, npc))

    def mulai_tantangan(self, jenis, wilayah, sumber, gerbang=False):
        self.chal = self.kuis.buat(jenis, wilayah, gerbang)
        self.chal_info = (jenis, wilayah, sumber, gerbang)
        self.state = "kuis"

    def pakai_objek(self, o):
        pr = self.progres
        if o.jenis == "papan":
            self.dialog.buka("Papan Petunjuk", o.teks)
        elif o.jenis == "peti":
            if o.id in pr.peti:
                self.dialog.buka("Peti", ["Peti ini sudah kosong."])
            else:
                pr.peti.append(o.id)
                item = random.choice(WILAYAH[self.world.wilayah_px(o.x, o.y)]["item"])
                pr.tambah_item(item)
                self.beri_xp(5)
                self.audio.mainkan("item")
                self.dialog.buka("Peti", ["Kamu menemukan %s! (+5 XP)" % item])
        elif o.jenis == "portal":
            n = self.world.hitung_selesai(o.id)
            if o.id in pr.kristal:
                self.dialog.buka("Gerbang Kristal", ["Pecahan Kristal Data wilayah ini sudah dipulihkan."])
            elif n < TARGET_TANTANGAN:
                self.dialog.buka("Gerbang Kristal", [
                    "Gerbang terkunci! Selesaikan %d tantangan penduduk wilayah ini (baru %d)." % (TARGET_TANTANGAN, n),
                    "Cari tanda seru kuning pada karakter. Cek minimap untuk lokasinya."])
            else:
                self.dialog.buka("Gerbang Kristal", [
                    "Gerbang terbuka! Jawab 3 soal terakhir (minimal 2 benar) untuk mengambil pecahan kristal."],
                    lambda: self.mulai_tantangan("pilgan", o.id, o, True))
        elif o.jenis == "portal_pusat":
            if len(pr.kristal) >= 4:
                self.dialog.buka("Kristal Pusat", [
                    "Keempat pecahan bersatu... Kristal Data bersinar terang!",
                    "Dunia digital pulih berkat pengetahuanmu. Terima kasih, Penjelajah!"], self.mulai_ending)
            else:
                self.dialog.buka("Kristal Pusat", [
                    "Kristal ini masih retak. Pecahan terkumpul: %d dari 4." % len(pr.kristal)])

    def mulai_ending(self):
        self.progres.tamat = True
        self.simpan_semua()
        self.audio.mainkan("kristal")
        self.pindah(self.buka_ringkasan_ending)

    def buka_ringkasan_ending(self):
        self.ending = True
        self.state = "ringkasan"

    # ----- kuis -----
    def event_kuis(self, e):
        c = self.chal
        batal = (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE) or \
                (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and c.rect_batal.collidepoint(e.pos))
        if batal and c.fase != "hasil":
            self.state = "dunia"  # batal tanpa hadiah
            self.chal = None
            return
        c.tangani(e)

    def selesai_kuis(self):
        c = self.chal
        jenis, wilayah, sumber, gerbang = self.chal_info
        pr = self.progres
        pr.benar += c.benar
        pr.total += c.total
        self.state = "dunia"
        self.chal = None
        self.beri_xp(c.xp)
        if c.lulus:
            item = random.choice(WILAYAH[wilayah]["item"])
            pr.tambah_item(item)
            if gerbang:
                if wilayah not in pr.kristal:
                    pr.kristal.append(wilayah)
                self.audio.mainkan("kristal")
                self.spanduk = ["PECAHAN KRISTAL %s!" % WILAYAH[wilayah]["nama"].upper(), 3.5]
                self.dialog.buka("Gerbang Kristal", [
                    "Pecahan Kristal Data %s kembali bersinar! Kamu mendapat %s." % (WILAYAH[wilayah]["nama"], item),
                    "Kristal terkumpul: %d dari 4." % len(pr.kristal)])
            else:
                if sumber.id not in pr.tantangan:
                    pr.tantangan.append(sumber.id)
                self.world.sinkron_npc()
                self.audio.mainkan("item")
                n = self.world.hitung_selesai(wilayah)
                baris = ["Bagus! Kamu mendapat %s dan %d XP." % (item, c.xp)]
                if n == TARGET_TANTANGAN:
                    baris.append("Gerbang Kristal %s sekarang terbuka!" % WILAYAH[wilayah]["nama"])
                self.dialog.buka(sumber.nama, baris)
            self.simpan_semua()
        else:
            self.dialog.buka("Tantangan", ["Belum berhasil, tapi tidak apa-apa. Pelajari penjelasannya dan coba lagi!"])

    # ----- pause -----
    def event_pause(self, e):
        butir = ["Lanjutkan", "Kustomisasi", "Pengaturan", "Ringkasan Skor", "Simpan Game", "Ke Menu Utama"]
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.state = "dunia"
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.pause_idx = (self.pause_idx - 1) % len(butir)
                self.audio.mainkan("menu")
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.pause_idx = (self.pause_idx + 1) % len(butir)
                self.audio.mainkan("menu")
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self.pilih_pause(self.pause_idx)
            elif e.key == pygame.K_m:
                self.pengaturan["mute"] = self.audio.toggle_mute()
        elif e.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.pause_rect):
                if r.collidepoint(e.pos):
                    self.pause_idx = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self.pause_rect):
                if r.collidepoint(e.pos):
                    self.pilih_pause(i)

    def pilih_pause(self, i):
        self.audio.mainkan("interaksi")
        if i == 0:
            self.state = "dunia"
        elif i == 1:
            self.buka_kustom(lambda cfg: self.selesai_kustom(cfg, "pause"), "pause")
        elif i == 2:
            self.kembali = "pause"
            self.state = "setting"
        elif i == 3:
            self.ending = False
            self.state = "ringkasan"
        elif i == 4:
            self.simpan_semua()
            self.spanduk = ["GAME TERSIMPAN", 2.0]
            self.state = "dunia"
        elif i == 5:
            self.simpan_semua()
            self.pindah(self.ke_menu)

    def ke_menu(self):
        self.progres = self.player = self.world = None
        self.state = "menu"
        self.menu_idx = 0
        self.audio.putar_musik("menu")

    # ----- ringkasan -----
    def event_ringkasan(self, e):
        if (e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e, pygame.K_ESCAPE)) or \
                (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
            self.state = "dunia"
            self.audio.mainkan("menu")

    # ---------- Update ----------
    def update(self, dt):
        self.t += dt
        self.transisi.update(dt)
        if self.blok_klik > 0:
            self.blok_klik -= dt
        if self.state != "dunia" or self.dialog.aktif:
            self.sentuh.reset()
        if self.state == "kustom":
            self.layar_kustom.update(dt)
        if self.spanduk[1] > 0:
            self.spanduk[1] -= dt
        if self.state in ("dunia", "kuis", "pause") and self.world:
            self.dialog.update(dt)
        if self.state == "dunia" and not self.transisi.aktif:
            self.progres.waktu_main += dt
            if not self.dialog.aktif:
                self.player.update(dt, pygame.key.get_pressed(), self.world, self.audio,
                                   self.sentuh.knob if self.sentuh.aktif else (0.0, 0.0))
            self.world.update(dt, self.player, self.audio)
            w = self.world.wilayah_px(self.player.x, self.player.y)
            if w != self.wilayah:
                self.wilayah = w
                self.audio.putar_musik(w)
                self.world.atur_partikel(w)
                self.spanduk = [WILAYAH[w]["nama"], 3.0]
        elif self.state == "kuis":
            self.chal.update(dt)
            if self.chal.selesai:
                self.selesai_kuis()
        elif self.state in ("menu", "kustom", "setting") and not self.world:
            self.audio.putar_musik("menu")
        elif self.state == "ringkasan":
            self.audio.putar_musik("menu")

    # ---------- Gambar ----------
    def gambar(self):
        s = self.state
        if s == "menu":
            self.gambar_menu()
        elif s == "kustom":
            self.layar_kustom.gambar(self.layar)
        elif s == "setting":
            if self.kembali == "menu":
                ui.latar_judul(self.layar, self.t)
            else:
                self.gambar_dunia()
            self.gambar_setting()
        elif s == "ringkasan":
            self.gambar_dunia()
            self.gambar_ringkasan()
        elif s in ("dunia", "kuis", "pause"):
            self.gambar_dunia()
            if s == "kuis":
                self.chal.gambar(self.layar)
            elif s == "pause":
                self.gambar_pause()
        self.transisi.gambar(self.layar)

    def gambar_dunia(self):
        if not self.world:
            self.layar.fill((0, 0, 0))
            return
        self.world.gambar(self.view, self.player)
        pygame.transform.scale(self.view, (ui.LEBAR, ui.TINGGI), self.layar)
        self.world.gambar_teks(self.layar)
        self.gambar_hud()
        self.dialog.gambar(self.layar, self.t)
        if self.state == "dunia" and not self.dialog.aktif:
            self.sentuh.gambar(self.layar)

    def gambar_menu(self):
        ui.latar_judul(self.layar, self.t)
        ui.teks(self.layar, "CODE QUEST", ui.LEBAR // 2, 50, 110, ui.KUNING, tengah=True)
        ui.teks(self.layar, "Petualangan Informatika", ui.LEBAR // 2, 140, 52, ui.PUTIH, tengah=True)
        nonaktif = [] if self.ada_save() else [1]
        self.menu_rect = ui.gambar_menu(self.layar, ["Main Baru", "Lanjutkan", "Kustomisasi", "Pengaturan", "Keluar"],
                                        self.menu_idx, ui.LEBAR // 2, 230, 58, 38, nonaktif)
        ui.teks(self.layar, "Atas/Bawah + Enter, atau klik mouse. F11: layar penuh", ui.LEBAR // 2, 515, 22,
                ui.ABU, tengah=True)

    def gambar_setting(self):
        ui.panel(self.layar, (230, 110, 500, 330))
        ui.teks(self.layar, "PENGATURAN", ui.LEBAR // 2, 130, 52, ui.KUNING, tengah=True)
        butir = [("Volume Musik", "musik"), ("Volume Efek", "efek"), ("Mute", "mute"), ("Kembali", None)]
        y = 210
        self.set_rect = []
        for i, (nama, k) in enumerate(butir):
            self.set_rect.append(pygame.Rect(250, y - 6, 460, 44))
            warna = ui.KUNING if i == self.set_idx else ui.PUTIH
            ui.teks(self.layar, nama, 260, y, 32, warna)
            if k in ("musik", "efek"):
                ui.bar(self.layar, 480, y + 4, 210, 22, self.pengaturan[k], ui.HIJAU)
            elif k == "mute":
                ui.teks(self.layar, "AKTIF" if self.pengaturan["mute"] else "mati", 480, y, 32,
                        ui.MERAH if self.pengaturan["mute"] else ui.ABU)
            y += 55
        ui.teks(self.layar, "Kiri/Kanan atau ketuk bar: ubah   Esc: kembali", ui.LEBAR // 2, 405, 22, ui.ABU, tengah=True)

    def gambar_pause(self):
        lapis = pygame.Surface((ui.LEBAR, ui.TINGGI), pygame.SRCALPHA)
        lapis.fill((0, 0, 0, 150))
        self.layar.blit(lapis, (0, 0))
        ui.teks(self.layar, "JEDA", ui.LEBAR // 2, 70, 72, ui.KUNING, tengah=True)
        self.pause_rect = ui.gambar_menu(
            self.layar, ["Lanjutkan", "Kustomisasi", "Pengaturan", "Ringkasan Skor", "Simpan Game", "Ke Menu Utama"],
            self.pause_idx, ui.LEBAR // 2, 160, 56, 36)

    def gambar_ringkasan(self):
        pr = self.progres
        lapis = pygame.Surface((ui.LEBAR, ui.TINGGI), pygame.SRCALPHA)
        lapis.fill((0, 0, 0, 190))
        self.layar.blit(lapis, (0, 0))
        ui.panel(self.layar, (180, 40, 600, 470))
        judul = "SELAMAT! KRISTAL DATA PULIH" if self.ending else "RINGKASAN SKOR"
        ui.teks(self.layar, judul, ui.LEBAR // 2, 60, 46, ui.KUNING, tengah=True)
        menit = int(pr.waktu_main // 60)
        detik = int(pr.waktu_main % 60)
        selesai = len(pr.tantangan)
        baris = [("Level", str(pr.level)), ("Total XP", str(pr.xp_total)),
                 ("Kristal terkumpul", "%d / 4" % len(pr.kristal)),
                 ("Tantangan selesai", "%d / 12" % selesai),
                 ("Jawaban benar", "%d dari %d" % (pr.benar, pr.total)),
                 ("Akurasi", "%d%%" % pr.akurasi()),
                 ("Bug di-debug", str(pr.bug)),
                 ("Item dikoleksi", str(sum(pr.item.values()))),
                 ("Waktu bermain", "%02d:%02d" % (menit, detik))]
        y = 125
        for nama, nilai in baris:
            ui.teks(self.layar, nama, 220, y, 30)
            ui.teks(self.layar, nilai, 740 - ui.font(30).size(nilai)[0], y, 30, ui.KUNING)
            y += 38
        if self.ending:
            ui.teks(self.layar, "Kamu boleh terus menjelajah dunia!", ui.LEBAR // 2, 475, 26, ui.HIJAU, tengah=True)
        else:
            ui.teks(self.layar, "Tekan Enter untuk kembali", ui.LEBAR // 2, 475, 26, ui.ABU, tengah=True)

    def gambar_hud(self):
        pr = self.progres
        L = self.layar
        # panel level + XP + kristal
        ui.panel(L, (10, 10, 270, 74), (16, 18, 40), ui.PUTIH, 215)
        ui.teks(L, "LV %d" % pr.level, 22, 18, 30, ui.KUNING)
        ui.bar(L, 92, 22, 176, 16, pr.xp / float(pr.xp_perlu()), ui.BIRU)
        ui.teks(L, "%d/%d XP" % (pr.xp, pr.xp_perlu()), 92, 40, 20, ui.ABU)
        for i, k in enumerate(URUTAN_WILAYAH):
            x = 30 + i * 34
            ada = k in pr.kristal
            warna = WILAYAH[k]["warna"] if ada else (70, 70, 90)
            pygame.draw.polygon(L, warna, [(x, 56), (x + 9, 66), (x, 78), (x - 9, 66)])
            pygame.draw.polygon(L, ui.PUTIH, [(x, 56), (x + 9, 66), (x, 78), (x - 9, 66)], 2)
        ui.teks(L, "Kristal %d/4" % len(pr.kristal), 160, 62, 24)
        # minimap
        self.world.gambar_minimap(L, ui.LEBAR - 140, 16, self.player, self.t)
        ui.teks(L, self.world.nama_waktu(), ui.LEBAR - 76, 160, 22, ui.ABU, tengah=True)
        if self.pengaturan["mute"]:
            ui.teks(L, "MUTE", ui.LEBAR - 76, 182, 22, ui.MERAH, tengah=True)
        # indikator misi aktif
        w = self.wilayah or "hutan"
        if w in pr.kristal:
            for k in URUTAN_WILAYAH:
                if k not in pr.kristal:
                    w = k
                    break
        if len(pr.kristal) >= 4:
            misi = ["MISI: Kembali ke Kristal Pusat di plaza!"]
        else:
            n = self.world.hitung_selesai(w)
            status = "SELESAI" if w in pr.kristal else ("TERBUKA" if n >= TARGET_TANTANGAN else "terkunci")
            misi = ["MISI: " + WILAYAH[w]["nama"] + " (" + WILAYAH[w]["topik"] + ")",
                    "Tantangan %d/%d   Gerbang: %s" % (min(n, TARGET_TANTANGAN), TARGET_TANTANGAN, status)]
        if not self.dialog.aktif:
            ui.panel(L, (10, ui.TINGGI - 62, 440, 52), (16, 18, 40), ui.PUTIH, 215)
            for j, b in enumerate(misi):
                ui.teks(L, b, 20, ui.TINGGI - 56 + j * 22, 22, ui.PUTIH if j == 0 else ui.KUNING)
            hasil = self.world.cari_interaksi(self.player)
            if hasil and self.state == "dunia":
                jenis, ent = hasil
                nama = getattr(ent, "nama", None) or {"papan": "papan", "peti": "peti", "portal": "gerbang",
                                                       "portal_pusat": "Kristal Pusat"}.get(getattr(ent, "jenis", ""), "bug")
                aksi = "Debug" if jenis == "bug" else ("Bicara" if jenis == "npc" else "Periksa")
                ui.panel(L, (ui.LEBAR // 2 - 150, ui.TINGGI - 62, 300, 40), (16, 18, 40), ui.KUNING, 230)
                ui.teks(L, "[E] %s %s" % (aksi, nama if jenis != "bug" else "Bug"), ui.LEBAR // 2, ui.TINGGI - 52,
                        26, ui.KUNING, tengah=True)
        # spanduk (nama wilayah, level up, dll.)
        if self.spanduk[1] > 0:
            lebar = ui.font(46).size(self.spanduk[0])[0] + 60
            ui.panel(L, (ui.LEBAR // 2 - lebar // 2, 100, lebar, 60), (30, 20, 70), ui.KUNING, 225)
            ui.teks(L, self.spanduk[0], ui.LEBAR // 2, 112, 46, ui.KUNING, tengah=True)

    # ---------- Loop utama ----------
    def jalankan(self):
        while self.jalan:
            dt = min(self.jam.tick(60) / 1000.0, 0.05)  # delta time (detik), dibatasi agar stabil
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.jalan = False
                elif e.type == getattr(pygame, "APP_WILLENTERBACKGROUND", -1):
                    self.simpan_semua()  # Android: simpan saat aplikasi ke latar belakang
                else:
                    self.event(e)
            self.update(dt)
            self.gambar()
            pygame.display.flip()
        self.simpan_semua()  # simpan otomatis saat keluar
        pygame.quit()


if __name__ == "__main__":
    Game().jalankan()
