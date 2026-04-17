#!/usr/bin/env python3
import os
import re
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path

# ─────────────────────────────────────────
#  Load .env manual (tanpa library tambahan)
# ─────────────────────────────────────────
def load_env(filepath=".env"):
    if not Path(filepath).exists():
        return
    current_key = None
    current_vals = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip("\n")
            bare = stripped.strip()
            if not bare or bare.startswith("#"):
                continue
            if "=" in bare and not stripped[0] in (" ", "\t"):
                if current_key:
                    os.environ[current_key] = "\n".join(current_vals).strip()
                    current_vals = []
                key, _, val = bare.partition("=")
                current_key = key.strip()
                if val.strip():
                    current_vals = [val.strip()]
            else:
                current_vals.append(bare)
    if current_key:
        os.environ[current_key] = "\n".join(current_vals).strip()

load_env()

# ─────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
#  Parse GMAIL_ACCOUNTS dari .env
#  Format tiap baris:  email|apppassword
# ─────────────────────────────────────────
def parse_gmail_accounts() -> list:
    raw = os.environ.get("GMAIL_ACCOUNTS", "")
    accounts = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        gmail, _, pwd = line.partition("|")
        gmail = gmail.strip()
        pwd = pwd.strip()
        if "@" in gmail and pwd:
            accounts.append({"gmail": gmail, "app_password": pwd})
    return accounts

# ─────────────────────────────────────────
#  File untuk menyimpan state rotasi (last_index)
# ─────────────────────────────────────────
ROTATION_STATE_FILE = "rotation_state.json"

def load_last_index() -> int:
    """Membaca last_index terakhir dari file, jika ada."""
    if os.path.exists(ROTATION_STATE_FILE):
        try:
            with open(ROTATION_STATE_FILE, "r") as f:
                data = json.load(f)
                return data.get("last_index", -1)
        except (json.JSONDecodeError, KeyError, TypeError):
            return -1
    return -1

def save_last_index(index: int):
    """Menyimpan last_index ke file."""
    with open(ROTATION_STATE_FILE, "w") as f:
        json.dump({"last_index": index}, f)

# ─────────────────────────────────────────
#  Email template
# ─────────────────────────────────────────
RECIPIENTS = ["android@support.whatsapp.com", "support@support.whatsapp.com"]
SUBJECT = "Problem Login WhatsApp"

def build_body(phone: str) -> str:
    return (
        "السلام عليكم ورحمة الله وبركاته\n"
        "اسمي [Violina] أود أن أستعرض المشاكل التي أواجهها\n"
        "لقد حاولت التحقق من الرقم ولكن هناك نص \"Login not available now\" "
        "عندما أكون مالك الرقم، يرجى مراجعته على الفور. هذا هو رقمي\n"
        f"{phone}\n"
        "السلام عليكم ورحمة الله وبركاته، شكرا لكم."
    )

# ─────────────────────────────────────────
#  Helper: normalise nomor (pastikan ada +)
# ─────────────────────────────────────────
def normalise_phone(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"[^\d+]", "", raw)
    if not raw.startswith("+"):
        raw = "+" + raw
    return raw

# ─────────────────────────────────────────
#  Kirim email via SMTP (Gmail)
# ─────────────────────────────────────────
def send_email_smtp(account: dict, phone: str) -> bool:
    gmail = account["gmail"]
    app_pass = account["app_password"]
    body = build_body(phone)

    msg = MIMEMultipart()
    msg["From"] = gmail
    msg["To"] = ", ".join(RECIPIENTS)
    msg["Subject"] = SUBJECT
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            server.login(gmail, app_pass)
            server.sendmail(gmail, RECIPIENTS, msg.as_string())
        logger.info(f"Email sent from {gmail} for {phone}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(f"SMTP Auth failed for {gmail}")
        return False
    except Exception as e:
        logger.error(f"SMTP error: {e}")
        return False

# ─────────────────────────────────────────
#  Fungsi utama interaktif dengan rotasi dan penyimpanan state
# ─────────────────────────────────────────
def main():
    accounts = parse_gmail_accounts()
    if not accounts:
        print("❌ ERROR: Tidak ada akun Gmail di file .env!")
        print("   Format contoh:\n   GMAIL_ACCOUNTS=\"email1|app_password1\\nemail2|app_password2\"")
        return

    print(f"✅ {len(accounts)} akun Gmail terdaftar:")
    for i, acc in enumerate(accounts, 1):
        print(f"   {i}. {acc['gmail']}")
    print("\n📧 Bot pengirim email ke WhatsApp Support.")
    print("   (Rotasi round-robin, state disimpan, waktu WIB)\n")

    # Load state rotasi terakhir
    last_index = load_last_index()
    print(f"[STATE] Indeks terakhir yang tersimpan: {last_index}")

    print("┌─────────────────────────────────────────────────┐")
    print("│  Ketik nomor telepon (dengan atau tanpa +)      │")
    print("│  atau ketik 'exit' / 'quit' untuk keluar.       │")
    print("└─────────────────────────────────────────────────┘")

    while True:
        raw_input = input("\n📱 Nomor > ").strip()
        if raw_input.lower() in ("exit", "quit", "keluar"):
            print("👋 Keluar...")
            break

        if not raw_input:
            print("❌ Nomor tidak boleh kosong.")
            continue

        phone = normalise_phone(raw_input)
        if len(phone) < 8:
            print("❌ Nomor terlalu pendek (minimal 8 digit setelah +).")
            continue

        # Rotasi: pilih akun berikutnya secara berurutan
        last_index = (last_index + 1) % len(accounts)
        save_last_index(last_index)  # simpan state setelah indeks berubah
        account = accounts[last_index]

        # Debug print
        print(f"[DEBUG] Menggunakan akun ke-{last_index+1} dari {len(accounts)}: {account['gmail']}")

        print(f"📤 Mengirim email untuk {phone} menggunakan {account['gmail']} ...")
        ok = send_email_smtp(account, phone)

        if ok:
            # Waktu WIB (UTC+7)
            now_wib = (datetime.utcnow() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M WIB")
            print(f"✅ Email berhasil dikirim!")
            print(f"   Nomor : {phone}")
            print(f"   Dari  : {account['gmail']}")
            print(f"   Waktu : {now_wib}")
        else:
            print(f"❌ Gagal kirim dari {account['gmail']}!")
            print("   Periksa App Password di file .env")

if __name__ == "__main__":
    main()
