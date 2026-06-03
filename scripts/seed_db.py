import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine, Base, AsyncSessionLocal
from app.models import University, Program, Source

MOCK_UNIVERSITIES = [
    {
        "id": "ui",
        "name": "Universitas Indonesia",
        "programs": [
            {"name": "Kedokteran", "score": 750.5},
            {"name": "Ilmu Hukum", "score": 710.2},
            {"name": "Ilmu Komputer", "score": 735.8},
            {"name": "Manajemen", "score": 720.0},
            {"name": "Akuntansi", "score": 715.4},
            {"name": "Teknik Industri", "score": 700.1},
            {"name": "Psikologi", "score": 690.5},
            {"name": "Ilmu Komunikasi", "score": 685.3}
        ]
    },
    {
        "id": "itb",
        "name": "Institut Teknologi Bandung",
        "programs": [
            {"name": "Sekolah Teknik Elektro dan Informatika (STEI)", "score": 760.0},
            {"name": "Fakultas Teknik Pertambangan dan Perminyakan (FTTM)", "score": 745.2},
            {"name": "Sekolah Bisnis dan Manajemen (SBM)", "score": 730.5},
            {"name": "Fakultas Teknologi Industri (FTI)", "score": 710.4},
            {"name": "Fakultas Teknik Sipil dan Lingkungan (FTSL)", "score": 705.8},
            {"name": "Sekolah Arsitektur, Perencanaan dan Pengembangan Kebijakan (SAPPK)", "score": 695.1}
        ]
    },
    {
        "id": "ugm",
        "name": "Universitas Gadjah Mada",
        "programs": [
            {"name": "Kedokteran", "score": 740.0},
            {"name": "Teknologi Informasi", "score": 725.5},
            {"name": "Ilmu Hukum", "score": 705.3},
            {"name": "Manajemen", "score": 712.1},
            {"name": "Psikologi", "score": 695.0},
            {"name": "Hubungan Internasional", "score": 690.4},
            {"name": "Arsitektur", "score": 680.7},
            {"name": "Ilmu Komunikasi", "score": 675.2}
        ]
    },
    {
        "id": "its",
        "name": "Institut Teknologi Sepuluh Nopember",
        "programs": [
            {"name": "Teknik Informatika", "score": 720.5},
            {"name": "Sistem Informasi", "score": 700.2},
            {"name": "Teknik Industri", "score": 690.8},
            {"name": "Teknik Elektro", "score": 685.1},
            {"name": "Teknik Sipil", "score": 675.4},
            {"name": "Arsitektur", "score": 665.0}
        ]
    },
    {
        "id": "unair",
        "name": "Universitas Airlangga",
        "programs": [
            {"name": "Kedokteran", "score": 735.0},
            {"name": "Kedokteran Gigi", "score": 710.5},
            {"name": "Ilmu Hukum", "score": 695.2},
            {"name": "Psikologi", "score": 680.1},
            {"name": "Kesehatan Masyarakat", "score": 660.8},
            {"name": "Manajemen", "score": 670.3}
        ]
    }
]

async def seed():
    print("Membuat ulang tabel database (drop & create)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("Menyimpan data sources...")
    async with AsyncSessionLocal() as session:
        session.add(Source(name="internal_mock", label="Prediksi Internal (Mock)", count=34))
        await session.commit()

    print("Menyimpan data universities...")
    async with AsyncSessionLocal() as session:
        for u in MOCK_UNIVERSITIES:
            uni = University(
                id=u["id"],
                name=u["name"],
                sources=["internal_mock"]
            )
            session.add(uni)
            for p in u["programs"]:
                prog = Program(
                    university_id=uni.id,
                    name=p["name"],
                    score_text=str(p["score"]),
                    degree="S1",
                    score=p["score"],
                    source_count=1
                )
                session.add(prog)
        await session.commit()
    
    print("Seeding database fiktif berhasil!")

if __name__ == "__main__":
    asyncio.run(seed())
