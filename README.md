# Unicompare API

API perbandingan nilai UTBK untuk membandingkan program studi di berbagai universitas Indonesia.

**Stack:** FastAPI + SQLAlchemy 2.0 (asyncpg) + PostgreSQL + JWT + PBKDF2

## Daftar Isi

- [Setup](#setup)
- [Database](#database)
- [Auth](#auth)
- [Endpoint List](#endpoint-list)
- [Models](#models)
- [DTOs](#dtos)

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # isi DATABASE_URL
python -m scripts.seed_db   # seed data awal
python -m uvicorn app.main:app --reload
```

**Environment Variables:**

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | PostgreSQL connection string |
| `UNICOMPARE_SECRET` | random | Secret key untuk JWT |
| `UNICOMPARE_USERNAME` | `admin` | Username admin default |
| `UNICOMPARE_PASSWORD` | `admin` | Password admin default |

## Database

`app/database.py` — Koneksi async PostgreSQL via asyncpg:

```python
_engine: AsyncEngine | None = None
_AsyncSessionLocal = None
Base = declarative_base()
```

- `init_db()` — create all tables
- `get_db()` — FastAPI dependency untuk session

URL otomatis dikonversi: `postgresql://` → `postgresql+asyncpg://`, `sslmode` → `ssl`.

## Auth

Semua endpoint `/admin/*` pake **Bearer JWT** + role check.

| Dependency | Fungsi |
|---|---|
| `get_current_user` | Decode JWT, return `{username, role}` |
| `require_admin` | Pastikan role = `admin`, return 403 kalo bukan |

Password di-hash dengan **PBKDF2-HMAC-SHA256** (600rb iterasi).

---

## Endpoint List

### Root

#### `GET /`

```python
@app.get("/")
async def root():
    return {"name": "Unicompare API", "version": "1.0.0", "status": "ok"}
```

**Response:**
```json
{"name": "Unicompare API", "version": "1.0.0", "status": "ok"}
```

---

### Auth

#### `POST /api/auth/register`

Mendaftarkan user baru.

```python
@router.post("/auth/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    token = await service.register(db, body.username, body.password)
    if token is None:
        raise HTTPException(status_code=409, detail="Username already exists")
    return TokenResponse(access_token=token)
```

**Request Body:**
```json
{"username": "joko", "password": "rahasia123"}
```

**Response `200`:**
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

**Response `409`:**
```json
{"detail": "Username already exists"}
```

---

#### `POST /api/auth/login`

Login dan dapatkan JWT token.

```python
@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    token = await service.authenticate(db, body.username, body.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=token)
```

**Request Body:**
```json
{"username": "admin", "password": "admin"}
```

**Response `200`:**
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

---

#### `GET /api/auth/me`

Lihat profile user saat ini (perlu Bearer token).

```python
@router.get("/auth/me", response_model=UserResponse)
async def me(user: dict = Depends(service.get_current_user)):
    return UserResponse(username=user["username"], role=user["role"])
```

**Response:**
```json
{"username": "admin", "role": "admin"}
```

---

### Admin — Users

#### `GET /api/admin/users` (Admin only)

Lihat semua user terdaftar.

```python
@router.get("/admin/users", response_model=list[AdminUserResponse])
async def admin_list_users(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    return await service.list_users(db)
```

**Response:**
```json
[
  {"username": "admin", "role": "admin"},
  {"username": "joko", "role": "user"}
]
```

---

#### `DELETE /api/admin/users/{username}` (Admin only)

Hapus user (tidak bisa hapus diri sendiri).

```python
@router.delete("/admin/users/{username}", response_model=DeletedUserResponse)
async def admin_delete_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    if username == user["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    ok = await service.delete_user(db, username)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return DeletedUserResponse(username=username)
```

**Response:**
```json
{"username": "joko"}
```

---

### Admin — Universities

#### `POST /api/admin/universities` (Admin only)

Tambah universitas baru.

```python
@router.post("/admin/universities", response_model=UniversityCreateResponse)
async def admin_create_university(
    body: CreateUniversityRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    uni = await university_service.create_university(db, body)
    return UniversityCreateResponse(id=uni.id, name=uni.name, sources=uni.sources)
```

**Request Body:**
```json
{
  "id": "univ-baru",
  "name": "Universitas Baru",
  "sources": ["internal_mock"]
}
```

**Response:**
```json
{
  "id": "univ-baru",
  "name": "Universitas Baru",
  "sources": ["internal_mock"],
  "program_count": 0
}
```

---

#### `PUT /api/admin/universities/{university_id}` (Admin only)

Update nama dan/atau sources universitas.

```python
@router.put("/admin/universities/{university_id}", response_model=UniversityCreateResponse)
async def admin_update_university(
    university_id: str,
    body: UpdateUniversityRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    uni = await university_service.update_university(db, university_id, body)
    if uni is None:
        raise HTTPException(status_code=404, detail="University not found")
    return UniversityCreateResponse(id=uni.id, name=uni.name, sources=uni.sources)
```

**Request Body** (semua field optional):
```json
{"name": "Nama Baru", "sources": ["internal_mock", "edukasi"]}
```

---

#### `DELETE /api/admin/universities/{university_id}` (Admin only)

Hapus universitas beserta program-programnya (cascade).

```python
@router.delete("/admin/universities/{university_id}")
async def admin_delete_university(
    university_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    ok = await university_service.delete_university(db, university_id)
    if not ok:
        raise HTTPException(status_code=404, detail="University not found")
    return {"message": f"University {university_id} deleted"}
```

---

#### `PUT /api/admin/universities/{university_id}/programs` (Admin only)

Update nilai (score) program studi.

```python
@router.put("/admin/universities/{university_id}/programs", response_model=list[ProgramUpdateResponse])
async def admin_update_program_scores(
    university_id: str,
    body: UpdateProgramScoresRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    result = await university_service.update_program_scores(db, university_id, body)
    if result is None:
        raise HTTPException(status_code=404, detail="University not found")
    return result
```

**Request Body:**
```json
{
  "programs": [
    {"id": 1, "score": 650.5, "score_text": "650.5"},
    {"id": 2, "score": 700.0}
  ]
}
```

**Response:**
```json
[
  {"id": 1, "name": "Kedokteran", "score": 650.5, "score_text": "650.5", "degree": "S1"},
  {"id": 2, "name": "Ilmu Hukum", "score": 700.0, "score_text": "700.0", "degree": "S1"}
]
```

---

### Universities (Public)

#### `GET /api/universities`

Daftar semua universitas.

```python
@router.get("/universities", response_model=UniversityListResponse)
async def get_universities(
    limit: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_universities(db, limit)
```

**Query Params:** `limit` (int, min 0, default 0 = semua)

**Response:**
```json
{
  "total": 12,
  "universities": [
    {"id": "ui", "name": "Universitas Indonesia", "sources": ["internal_mock"], "program_count": 8}
  ]
}
```

---

#### `GET /api/universities/search`

Cari universitas berdasarkan nama atau ID.

```python
@router.get("/universities/search", response_model=UniversityListResponse)
async def search_universities(
    q: str = Query(min_length=1),
    db: AsyncSession = Depends(get_db),
):
    return await service.search_universities(db, q)
```

**Query Params:** `q` (string, min 1 karakter)

---

#### `GET /api/universities/{university_id}/programs`

Lihat program studi suatu universitas.

```python
@router.get("/universities/{university_id}/programs", response_model=ProgramsResponse)
async def get_university_programs(
    university_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await service.list_programs(db, university_id)
    if result is None:
        return JSONResponse({"error": "university not found"}, status_code=404)
    return result
```

**Response:**
```json
{
  "university_id": "ui",
  "university_name": "Universitas Indonesia",
  "programs": [
    {"name": "Kedokteran", "score_text": "750.5", "score": 750.5, "source_count": 1, "degree": "S1"}
  ]
}
```

---

#### `GET /api/universities/{university_name:path}`

Cari detail universitas (bisa pakai nama atau parsial).

```python
@router.get("/universities/{university_name:path}")
async def get_university_detail(
    university_name: str,
    db: AsyncSession = Depends(get_db),
):
    result = await service.get_university_detail(db, university_name)
    if result is None:
        return JSONResponse({"error": "university not found"}, status_code=404)
    return result
```

Contoh: `GET /api/universities/ui` atau `GET /api/universities/indonesia`.

---

### Compare

#### `GET /api/compare`

Cari program studi yang bisa dimasuki dengan skor tertentu.

```python
@router.get("/compare", response_model=CompareResponse)
async def compare(
    score: float = Query(),
    q: str = Query(default=""),
    universities: str = Query(default=""),
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await service.compare_score(
        db=db, score=score, q=q, universities=universities, limit=limit,
    )
```

**Query Params:**

| Param | Type | Default | Description |
|---|---|---|---|
| `score` | float | **required** | Skor UTBK user |
| `q` | string | `""` | Filter nama universitas/prodi |
| `universities` | string | `""` | Filter ID universitas (comma-separated) |
| `limit` | int | `50` | Max hasil (1–500) |

**Response:**
```json
{
  "user_score": 500,
  "total": 5,
  "universities": [
    {
      "id": "univ-baru",
      "name": "Universitas Baru",
      "sources": ["internal_mock"],
      "eligible_count": 3,
      "program_count": 5,
      "eligible_programs": [
        {"name": "Prodi A", "score_text": "480", "score": 480, "source_count": 1, "degree": "S1"}
      ]
    }
  ]
}
```

---

#### `POST /api/compare/choices`

Bandingkan beberapa pilihan program studi.

```python
@router.post("/compare/choices", response_model=CompareChoicesResponse)
async def compare_two_choices(
    body: CompareChoicesRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.compare_choices(db, body.pilihan)
```

**Request Body:**
```json
{
  "pilihan": [
    {"universitas": "ui", "program": "Kedokteran"},
    {"universitas": "itb", "program": "STEI"}
  ]
}
```

**Response:**
```json
{
  "pilihan": [
    {
      "universitas": {"id": "ui", "name": "Universitas Indonesia"},
      "program": {"name": "Kedokteran", "score": 750.5, "score_text": "750.5", "degree": "S1"}
    }
  ],
  "perbandingan": {
    "tertinggi": {"universitas": "Institut Teknologi Bandung", "program": "STEI", "score": 760.0},
    "terendah": {"universitas": "Universitas Indonesia", "program": "Kedokteran", "score": 750.5},
    "selisih": 9.5,
    "urutan": [
      {"universitas": "Institut Teknologi Bandung", "program": "STEI", "score": 760.0},
      {"universitas": "Universitas Indonesia", "program": "Kedokteran", "score": 750.5}
    ]
  }
}
```

---

### Sources

#### `GET /api/sources`

Daftar sumber data.

```python
@router.get("/sources", response_model=SourcesResponse)
async def get_sources(db: AsyncSession = Depends(get_db)):
    return await service.get_sources(db)
```

**Response:**
```json
{
  "sources": [
    {"name": "internal_mock", "label": "Prediksi Internal (Mock)", "count": 45}
  ],
  "total": 1
}
```

---

## Models

```python
class User(Base):
    __tablename__ = "users"
    username: Mapped[str]      # PK
    password: Mapped[str]
    role: Mapped[str]          # "admin" | "user"

class Source(Base):
    __tablename__ = "sources"
    name: Mapped[str]          # PK
    label: Mapped[str]
    count: Mapped[int]

class University(Base):
    __tablename__ = "universities"
    id: Mapped[str]            # PK, slug (e.g. "ui", "itb")
    name: Mapped[str]
    sources: Mapped[list[str]] # JSON column
    programs: list[Program]    # one-to-many

class Program(Base):
    __tablename__ = "programs"
    id: Mapped[int]            # PK, auto increment
    university_id: Mapped[str] # FK → universities.id
    name: Mapped[str]
    score_text: Mapped[str]    # display value
    degree: Mapped[str | None]
    score: Mapped[float | None] # numeric value for filtering
    source_count: Mapped[int]
```

---

## DTOs

### Auth (`app/dto/auth.py`)

| Class | Fields |
|---|---|
| `LoginRequest` | `username: str`, `password: str` |
| `RegisterRequest` | `username: str`, `password: str` |
| `TokenResponse` | `access_token: str`, `token_type: str = "bearer"` |
| `UserResponse` | `username: str`, `role: str = "user"` |
| `AdminUserResponse` | `username: str`, `role: str = "user"` |
| `DeletedUserResponse` | `username: str` |

### University (`app/dto/university.py`)

| Class | Fields |
|---|---|
| `CreateUniversityRequest` | `id: str`, `name: str`, `sources: list[str] = []` |
| `UpdateUniversityRequest` | `name: str \| None`, `sources: list[str] \| None` |
| `UpdateProgramScoreItem` | `id: int`, `score: float \| None`, `score_text: str \| None` |
| `UpdateProgramScoresRequest` | `programs: list[UpdateProgramScoreItem]` |
| `UniversityCreateResponse` | `id: str`, `name: str`, `sources: list[str]`, `program_count: int = 0` |
| `ProgramUpdateResponse` | `id: int`, `name: str`, `score: float \| None`, `score_text: str`, `degree: str \| None` |
| `UniversityListItem` | `id: str`, `name: str`, `sources: list[str]`, `program_count: int` |
| `UniversityListResponse` | `total: int`, `universities: list[UniversityListItem]` |
| `UniversityDetail` | `id: str`, `name: str`, `sources: list[str]`, `program_count: int`, `programs: list[ProgramItem]` |
| `ProgramsResponse` | `university_id: str`, `university_name: str`, `programs: list[ProgramItem]` |
| `ProgramItem` | `name: str`, `score_text: str`, `score: float \| None`, `source_count: int = 1`, `sources: list[str] = []`, `degree: str \| None` |

### Compare (`app/dto/compare.py`)

| Class | Fields |
|---|---|
| `CompareChoicesRequest` | `pilihan: list[CompareChoice]` (min 2) |
| `CompareChoice` | `universitas: str`, `program: str` |
| `CompareChoicesResponse` | `pilihan: list[CompareChoiceResult]`, `perbandingan: Perbandingan` |
| `CompareResponse` | `user_score: float`, `total: int`, `universities: list[CompareUniversity]` |

### Source (`app/dto/source.py`)

| Class | Fields |
|---|---|
| `SourcesResponse` | `sources: list[SourceInfo]`, `total: int` |
| `SourceInfo` | `name: str`, `label: str`, `count: int` |
