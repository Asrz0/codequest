# audio.py
# Semua suara dibuat lewat sintesis gelombang (square/triangle/noise) dengan numpy.
import numpy as np
import pygame

SR = 22050  # sample rate (lebih ringan untuk HP)


def hz(midi):
    """Konversi nomor nada MIDI ke frekuensi."""
    return 440.0 * (2 ** ((midi - 69) / 12.0))


def gelombang(freq, dur, jenis="persegi", vol=0.5, slide=0.0):
    """Membuat satu nada. slide = perubahan frekuensi (Hz) selama nada."""
    n = max(1, int(SR * dur))
    t = np.arange(n) / SR
    if jenis == "noise":
        data = np.random.uniform(-1, 1, n)
    else:
        fr = freq + slide * (t / dur)
        frac = np.cumsum(fr) / SR % 1.0
        if jenis == "persegi":
            data = np.where(frac < 0.5, 1.0, -1.0)
        elif jenis == "segitiga":
            data = 4 * np.abs(frac - 0.5) - 1
        elif jenis == "sinus":
            data = np.sin(2 * np.pi * frac)
        else:
            data = 2 * frac - 1
    # envelope: naik cepat, turun di akhir (menghindari bunyi "klik")
    env = np.minimum(1.0, t / 0.005) * np.minimum(1.0, (dur - t) / (0.15 * dur + 1e-4))
    return data * env * vol


def tempel(keluar, awal, seg):
    """Menjumlahkan segmen suara ke array keluaran pada posisi awal."""
    akhir = min(len(keluar), awal + len(seg))
    if akhir > awal:
        keluar[awal:akhir] += seg[:akhir - awal]


def render_lagu(lead, bass, bpm, jenis_lead="persegi", jenis_bass="segitiga", drum=""):
    """Merender satu loop lagu dari pola nada lead, bass, dan drum."""
    n = len(lead)
    langkah = 60.0 / bpm / 2
    keluar = np.zeros(int(SR * langkah * n))
    for i in range(n):
        awal = int(i * langkah * SR)
        if lead[i]:
            sambung = lead[(i + 1) % n] != 0
            dur = langkah * (0.95 if sambung else 1.8)
            tempel(keluar, awal, gelombang(hz(lead[i]), dur, jenis_lead, 0.20))
        if bass[i]:
            tempel(keluar, awal, gelombang(hz(bass[i]), langkah * 1.8, jenis_bass, 0.30))
        if drum:
            c = drum[i % len(drum)]
            if c == "k":
                tempel(keluar, awal, gelombang(150, 0.12, "sinus", 0.5, slide=-110))
            elif c == "h":
                tempel(keluar, awal, gelombang(0, 0.04, "noise", 0.10))
            elif c == "s":
                tempel(keluar, awal, gelombang(0, 0.10, "noise", 0.18))
    return keluar


def rangkai(daftar_midi, dur, jenis="persegi", vol=0.4):
    """Menggabungkan beberapa nada berurutan (untuk efek suara)."""
    return np.concatenate([gelombang(hz(m), dur, jenis, vol) for m in daftar_midi])


def pola(daftar, panjang=32):
    return (list(daftar) + [0] * panjang)[:panjang]


# Definisi lagu tiap wilayah: (lead, bass, bpm, jenis lead, jenis bass, drum)
LAGU = {
    "menu": (pola([72, 0, 79, 0, 76, 0, 72, 0, 74, 0, 77, 0, 74, 0, 71, 0,
                   72, 0, 79, 0, 84, 0, 79, 0, 76, 0, 74, 0, 72, 0, 0, 0]),
             pola([48, 0, 48, 0, 55, 0, 55, 0, 53, 0, 53, 0, 55, 0, 55, 0,
                   48, 0, 48, 0, 55, 0, 55, 0, 53, 0, 55, 0, 48, 0, 0, 0]),
             110, "persegi", "segitiga", "k.h.s.h."),
    "hutan": (pola([67, 0, 71, 0, 74, 0, 71, 0, 72, 0, 76, 0, 79, 0, 76, 0,
                    74, 0, 71, 0, 67, 0, 71, 0, 69, 0, 72, 0, 74, 0, 0, 0]),
              pola([43, 0, 50, 0, 43, 0, 50, 0, 48, 0, 55, 0, 48, 0, 55, 0,
                    43, 0, 50, 0, 43, 0, 50, 0, 50, 0, 57, 0, 50, 0, 57, 0]),
              120, "persegi", "segitiga", "k.h.k.h."),
    "gurun": (pola([69, 0, 70, 0, 73, 0, 74, 0, 73, 0, 70, 0, 69, 0, 0, 0,
                    76, 0, 74, 0, 73, 0, 70, 0, 69, 0, 0, 0, 0, 0, 0, 0]),
              pola([45, 0, 0, 0, 45, 0, 52, 0, 46, 0, 0, 0, 46, 0, 53, 0,
                    45, 0, 0, 0, 45, 0, 52, 0, 46, 0, 45, 0, 40, 0, 0, 0]),
              100, "persegi", "segitiga", "k...h...s...h..."),
    "gunung": (pola([74, 0, 0, 0, 77, 0, 0, 0, 76, 0, 0, 0, 72, 0, 0, 0,
                     74, 0, 0, 0, 77, 0, 81, 0, 79, 0, 0, 0, 76, 0, 0, 0]),
               pola([38, 0, 0, 0, 38, 0, 0, 0, 36, 0, 0, 0, 36, 0, 0, 0,
                     34, 0, 0, 0, 34, 0, 0, 0, 33, 0, 0, 0, 33, 0, 0, 0]),
               80, "segitiga", "segitiga", ""),
    "kota": (pola([76, 79, 83, 79, 76, 79, 83, 79, 74, 78, 81, 78, 74, 78, 81, 78,
                   72, 76, 79, 76, 72, 76, 79, 76, 71, 74, 78, 74, 71, 74, 78, 83]),
             pola([40, 0, 40, 0, 40, 0, 40, 0, 38, 0, 38, 0, 38, 0, 38, 0,
                   36, 0, 36, 0, 36, 0, 36, 0, 35, 0, 35, 0, 35, 0, 35, 0]),
             140, "persegi", "persegi", "k.s.k.s."),
}


class AudioManager:
    """Mengelola musik latar (loop) dan efek suara, termasuk volume dan mute."""

    def __init__(self):
        self.aktif = False
        self.vol_musik = 0.6
        self.vol_efek = 0.8
        self.mute = False
        self.lagu = {}
        self.efek = {}
        self.kanal = None
        self.sekarang = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SR, size=-16, channels=1, buffer=1024)
            self.saluran = pygame.mixer.get_init()[2]
            pygame.mixer.set_reserved(1)
            self.kanal = pygame.mixer.Channel(0)
            self._buat_efek()
            for nama, (lead, bass, bpm, jl, jb, drum) in LAGU.items():
                self.lagu[nama] = self._suara(render_lagu(lead, bass, bpm, jl, jb, drum), 0.8)
            self.aktif = True
        except Exception as err:  # tidak ada perangkat audio -> game tetap jalan tanpa suara
            print("Audio dimatikan:", err)

    def _suara(self, arr, puncak=0.9):
        """Mengubah array float menjadi pygame Sound."""
        m = np.max(np.abs(arr)) + 1e-9
        arr = arr / m * puncak
        data = (arr * 32767).astype(np.int16)
        if self.saluran == 2:
            data = np.column_stack((data, data))
        return pygame.sndarray.make_sound(np.ascontiguousarray(data))

    def _buat_efek(self):
        e = self.efek
        e["langkah"] = self._suara(gelombang(0, 0.04, "noise", 1.0) * 0.5, 0.25)
        e["interaksi"] = self._suara(rangkai([76, 83], 0.06), 0.5)
        e["benar"] = self._suara(rangkai([72, 76, 79, 84], 0.09), 0.6)
        e["salah"] = self._suara(np.concatenate([gelombang(200, 0.12, "gigi", 0.5, -80),
                                                 gelombang(150, 0.18, "gigi", 0.5, -60)]), 0.5)
        e["level_up"] = self._suara(rangkai([67, 72, 76, 79, 84, 79, 84], 0.11), 0.7)
        e["menu"] = self._suara(gelombang(880, 0.04, "persegi", 0.5), 0.4)
        e["item"] = self._suara(rangkai([83, 88], 0.08), 0.6)
        e["kristal"] = self._suara(rangkai([72, 76, 79, 84, 88, 91, 96], 0.1, "persegi", 0.4), 0.7)
        e["tulis"] = self._suara(gelombang(600, 0.015, "persegi", 0.4), 0.2)
        e["bug"] = self._suara(gelombang(300, 0.15, "persegi", 0.5, -200), 0.45)

    # ----- kontrol -----
    def mainkan(self, nama):
        if not self.aktif or self.mute:
            return
        s = self.efek.get(nama)
        if s:
            s.set_volume(self.vol_efek)
            s.play()

    def putar_musik(self, nama):
        if not self.aktif or nama == self.sekarang or nama not in self.lagu:
            return
        self.sekarang = nama
        self.kanal.play(self.lagu[nama], loops=-1, fade_ms=600)
        self._volume()

    def henti_musik(self):
        if self.aktif:
            self.kanal.fadeout(400)
            self.sekarang = None

    def _volume(self):
        if self.aktif:
            self.kanal.set_volume(0.0 if self.mute else self.vol_musik * 0.6)

    def atur(self, musik=None, efek=None, mute=None):
        if musik is not None:
            self.vol_musik = max(0.0, min(1.0, musik))
        if efek is not None:
            self.vol_efek = max(0.0, min(1.0, efek))
        if mute is not None:
            self.mute = mute
        self._volume()

    def toggle_mute(self):
        self.atur(mute=not self.mute)
        return self.mute
