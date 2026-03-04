# 📸 PhotoBooth

Mesin photobooth digital berbasis Streamlit dengan pembayaran Midtrans, penyimpanan Supabase, dan panel admin.

## Alur Pengguna
1. **Landing** → klik Mulai Sesi
2. **Bayar** → scan QR Midtrans (Rp 10.000)
3. **Pilih Frame** → 6 pilihan frame + opsi mirror
4. **Foto** → 4 slot, timer 5 menit, retake bebas
5. **Filter** → pilih filter, preview strip
6. **Cetak** → download via QR code

## Stack
- **Frontend**: Streamlit
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Payment**: Midtrans SNAP
- **Deploy**: Streamlit Cloud

---

## Setup

### 1. Supabase
Buat project di [supabase.com](https://supabase.com), lalu jalankan SQL ini di **SQL Editor**:

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    paid_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending',
    midtrans_order_id TEXT,
    frame_choice TEXT,
    mirror BOOLEAN DEFAULT FALSE,
    filter_choice TEXT DEFAULT 'Original',
    photo_urls TEXT[],
    strip_url TEXT
);
```

Lalu buat **Storage Bucket**:
- Nama: `fotobox-photos`
- Public: ✅ Ya

### 2. Midtrans
- Daftar di [midtrans.com](https://midtrans.com)
- Ambil **Server Key** dari Dashboard → Settings → Access Keys
- Untuk testing gunakan Sandbox

### 3. Secrets
Buat file `.streamlit/secrets.toml` (lihat `secrets.toml.example`):

```toml
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "your-service-role-key"
MIDTRANS_SERVER_KEY = "SB-Mid-server-xxxx"
MIDTRANS_PROD = false
ADMIN_PASSWORD = "password-kamu"
```

### 4. Install & Run Lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 5. Deploy ke Streamlit Cloud
1. Push semua file ke GitHub
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Connect repo, set `app.py` sebagai main file
4. Di **Settings → Secrets**, masukkan isi `secrets.toml`
5. Deploy!

> ⚠️ Jangan push `secrets.toml` ke GitHub. Sudah ada di `.gitignore`.

---

## Struktur File
```
photobooth/
├── app.py                  # Landing page
├── pages/
│   ├── 1_payment.py        # Pembayaran Midtrans
│   ├── 2_frame.py          # Pilih frame & mirror
│   ├── 3_shoot.py          # Sesi foto (timer 5 menit)
│   ├── 4_filter.py         # Filter & cetak
│   └── 5_admin.py          # Panel admin
├── db.py                   # Supabase helper
├── payment.py              # Midtrans helper
├── utils.py                # Filter, frame, strip builder
├── requirements.txt
└── .streamlit/
    └── secrets.toml        # (jangan di-push ke GitHub!)
```

## Panel Admin
Buka `/5_admin` dari sidebar atau langsung ke URL `/5_admin`.
Login dengan password yang kamu set di `ADMIN_PASSWORD`.

Fitur admin:
- Statistik harian (total sesi, revenue, dll)
- Filter by tanggal & status
- Lihat foto & strip tiap sesi
