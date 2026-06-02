# Unicompare API

Scrapes universitas beserta jurusan dan nilai UTBK dari berbagai sumber menggunakan **Scrapling** + **FastAPI**.

## Struktur Folder

```
app/
├── main.py              # Inisialisasi FastAPI + register router
├── config.py            # Konfigurasi terpusat (daftar sumber)
│
├── source/              # Fitur: info sumber data
│   ├── api.py           #   endpoint /api/sources
│   ├── service.py       #   business logic
│   └── models.py        #   Pydantic schemas
│
├── university/          # Fitur: universitas (list, search, detail)
│   ├── api.py           #   endpoint /api/universities/*
│   ├── service.py       #   business logic + cache
│   └── models.py        #   Pydantic schemas
│
├── compare/             # Fitur: perbandingan skor UTBK
│   ├── api.py           #   endpoint /api/compare
│   ├── service.py       #   business logic
│   └── models.py        #   Pydantic schemas
│
├── scrapers/            # Pengambilan data dari website
│   ├── base.py          #   helper parsing & normalisasi
│   ├── kampus_impian.py
│   ├── smkitsi.py
│   ├── sonora.py
│   ├── haipintar.py
│   └── smkn5.py
│
└── utils/               # Utility functions
    └── merger.py        #   penggabungan data universitas
```

## Cara Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan server

```bash
python run.py
```

Server akan berjalan di `http://localhost:8000`.

### 3. Akses API

Buka `http://localhost:8000/docs` untuk Swagger UI, atau gunakan Bruno (lihat `docs/bruno/`).

## API Endpoints

| Method | Path | Deskripsi |
|--------|------|-----------|
| GET | `/api/sources` | List semua sumber data |
| GET | `/api/universities` | List semua universitas |
| GET | `/api/universities/search?q=uin` | Cari universitas by nama |
| GET | `/api/universities/{path}` | Detail jurusan & nilai UTBK satu universitas |
| GET | `/api/compare?score=500` | Cari jurusan yang lolos berdasarkan skor kamu |

### Query Parameters

**`/api/universities`**
- `limit` (int, optional) — batasi jumlah hasil

**`/api/universities/search`**
- `q` (string, required) — kata kunci nama universitas

**`/api/compare`**
- `score` (float, required) — nilai UTBK kamu
- `universities` (string, optional) — filter kampus, pisah dengan koma
- `q` (string, optional) — filter nama kampus/jurusan
- `limit` (int, default `50`) — batasi hasil

## Tech Stack

- **FastAPI** — web framework
- **Scrapling** — HTTP client & HTML parser
- **uvicorn** — ASGI server
