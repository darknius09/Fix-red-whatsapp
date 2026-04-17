# Fix-red-whatsapp

Berikut adalah panduan lengkap dari awal hingga script berjalan di Termux, cocok untuk pemula dan siap kamu tulis di GitHub.

---

📱 WhatsApp Fix Bot – Panduan Termux (Tanpa Telegram)

Bot ini mengirim email banding ke WhatsApp Support menggunakan akun Gmail secara bergantian (round-robin) dan menyimpan state rotasi. Waktu menggunakan WIB.
Tidak perlu bot Telegram, semua berjalan di terminal.

---

🧰 1. Instal Termux

1. Unduh Termux dari F-Droid (disarankan) atau Google Play (versi lama).
2. Buka Termux, tunggu instalasi selesai.
3. Update paket:
   ```bash
   pkg update && pkg upgrade -y
   ```

---

📦 2. Install Python

```bash
pkg install python -y
```

Cek versi:

```bash
python --version
```

Harus Python 3.8 atau lebih baru.

---

📁 3. Buat Folder dan Masuk ke Dalamnya

```bash
git clone https://github.com/darknius09/Fix-red-whatsapp fixwa
cd fixwa
```

---

🔑 4. Edit File .env untuk Menyimpan Akun Gmail

Isi dengan format berikut (ganti dengan akun dan App Password kamu):

```env
BOT_TOKEN=tidak_dipakai_tapi_biarkan_ada
GMAIL_ACCOUNTS=email1@gmail.com|app_password1
email2@gmail.com|app_password2
email3@gmail.com|app_password3
```

Cara dapat App Password Gmail:

· Buka myaccount.google.com/apppasswords (harus aktifkan 2FA dulu).
· Pilih “Mail” dan “Other” → beri nama → Generate.
· Salin 16 huruf (tanpa spasi) dan tempel setelah tanda |.

Simpan file .env dengan Ctrl + X, Y, Enter.

---

🚀 5. Jalankan Bot

```bash
python wa.py
```

Jika sukses, akan tampil daftar akun dan prompt:

```
📱 Nomor >
```

Ketik nomor telepon (contoh: 628123456789 atau +628123456789) lalu Enter.
Bot akan mengirim email secara bergantian sesuai urutan akun di .env.
Setiap kali kirim, akan muncul debug seperti:

```
[DEBUG] Menggunakan akun ke-1 dari 3: email1@gmail.com
✅ Email berhasil dikirim!
   Nomor : +628123456789
   Dari  : email1@gmail.com
   Waktu : 2025-04-17 14:30 WIB
```

Untuk keluar, ketik exit.

---

💾 7. File State Rotasi

Bot menyimpan indeks terakhir di rotation_state.json.
Jika bot dihentikan dan dijalankan lagi, ia akan melanjutkan dari akun berikutnya (tidak mulai dari awaal)
--
🎉 Selesai

Sekarang kamu bisa mengirim email banding ke WhatsApp Support langsung dari Termux dengan rotasi akun otomatis.
Jika ada pertanyaan, buka issue di repo GitHub-mu. Selamat mencoba!


