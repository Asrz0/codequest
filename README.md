# Code Quest: Petualangan Informatika

Game 2D top-down adventure edukasi informatika (Python + Pygame, aplikasi desktop).

## Instalasi dan menjalankan
    pip install -r requirements.txt
    python main.py
Butuh Python 3.10+. Semua gambar dan suara dibuat lewat kode (tanpa file aset).

## Kontrol
HP/layar sentuh: joystick kiri = gerak, tombol E = interaksi, tombol || = jeda, ketuk layar = lanjut dialog.
Keyboard: WASD/Panah = gerak | E/Enter = interaksi, lanjut dialog | Esc = jeda | M = mute | F11 = layar penuh

## Membuat .exe (PyInstaller)
    pip install pyinstaller
    pyinstaller --onefile --windowed --name CodeQuest --add-data "data;data" main.py
(Windows memakai `;`. Di Linux/macOS: `--add-data "data:data"`.) Hasil: dist/CodeQuest.exe.
File save.json dibuat di sebelah .exe.

## Menambah soal (data/soal.json)
Tiap wilayah (hutan, gurun, gunung, kota) punya 4 daftar:
- pilihan_ganda: {"tanya", "pilihan":[4 teks], "jawab": indeks benar (0-3), "penjelasan"}
- urutan: {"judul", "langkah":[urutan BENAR, akan diacak game], "penjelasan"}
- biner: {"tanya", "nilai": angka, "bit": 4 atau 8, "penjelasan"}
- pencocokan: {"judul", "pasangan":[["istilah","arti"], ...4 pasang], "penjelasan"}
Cukup tambah objek baru di daftar; tidak perlu mengubah kode.

## Menambah NPC / objek
Di world.py tambah baris pada DAFTAR_NPC atau DAFTAR_OBJEK (koordinat dalam tile).
Jenis NPC: pilgan, urutan, biner, cocok. Id NPC harus diawali kunci wilayah (mis. "hutan_baru").

## Menambah wilayah baru
1. Tambah entri di WILAYAH dan URUTAN_WILAYAH (world.py), dan bagian baru di soal.json.
2. Tambah aturan tile di World._bangun_peta dan fungsi wilayah_tile.
3. Tambah lagu di LAGU (audio.py) dan jenis partikel di Partikel (world.py).

## Menambah item kustomisasi
customization.py: tambah warna ke KULIT/RAMBUT/BAJU, nama ke NAMA_RAMBUT/NAMA_BADAN,
lalu gambar layer barunya di gambar_karakter() dan tambahkan baris di LayarKustomisasi.BARIS.

## Android (APK)
APK hanya bisa dibuat di Linux. Cara termudah dari Windows: GitHub Actions (gratis, build di cloud).
1. Buat akun GitHub, buat repository baru, unggah seluruh isi folder codequest (termasuk folder .github dan buildozer.spec).
2. Buka tab Actions > "Build APK" > Run workflow. Tunggu 15-40 menit.
3. Unduh artifact "CodeQuest-APK" (file .apk), kirim ke HP, pasang (izinkan "install dari sumber tidak dikenal").
Uji tampilan sentuh di PC: set CQ_SENTUH=1 sebelum menjalankan python main.py.
