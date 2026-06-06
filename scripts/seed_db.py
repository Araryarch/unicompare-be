import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import _engine as engine, Base, _AsyncSessionLocal as AsyncSessionLocal
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
    },
    {
        "id": "undip",
        "name": "Universitas Diponegoro",
        "programs": [
            {"name": "Kedokteran", "score": 715.4},
            {"name": "Kesehatan Masyarakat", "score": 645.2},
            {"name": "Teknik Sipil", "score": 630.0},
            {"name": "Teknik Mesin", "score": 625.8},
            {"name": "Ilmu Hukum", "score": 650.5},
            {"name": "Ilmu Komunikasi", "score": 640.1},
            {"name": "Informatika", "score": 680.2},
            {"name": "Akuntansi", "score": 655.7}
        ]
    },
    {
        "id": "unpad",
        "name": "Universitas Padjadjaran",
        "programs": [
            {"name": "Pendidikan Dokter", "score": 720.1},
            {"name": "Psikologi", "score": 670.5},
            {"name": "Ilmu Komunikasi", "score": 665.8},
            {"name": "Ilmu Hukum", "score": 660.4},
            {"name": "Manajemen", "score": 655.0},
            {"name": "Akuntansi", "score": 645.3},
            {"name": "Teknik Informatika", "score": 675.2},
            {"name": "Hubungan Internasional", "score": 650.0}
        ]
    },
    {
        "id": "ub",
        "name": "Universitas Brawijaya",
        "programs": [
            {"name": "Kedokteran", "score": 718.5},
            {"name": "Teknik Informatika", "score": 685.0},
            {"name": "Ilmu Hukum", "score": 640.2},
            {"name": "Manajemen", "score": 635.8},
            {"name": "Teknik Industri", "score": 645.5},
            {"name": "Kesehatan Masyarakat", "score": 620.4},
            {"name": "Ilmu Komunikasi", "score": 630.1},
            {"name": "Administrasi Bisnis", "score": 625.6}
        ]
    },
    {
        "id": "uns",
        "name": "Universitas Sebelas Maret",
        "programs": [
            {"name": "Kedokteran", "score": 710.2},
            {"name": "Informatika", "score": 670.8},
            {"name": "Teknik Sipil", "score": 625.5},
            {"name": "Ilmu Hukum", "score": 635.4},
            {"name": "Manajemen", "score": 630.1},
            {"name": "Psikologi", "score": 645.0},
            {"name": "Ilmu Komunikasi", "score": 620.8}
        ]
    },
    {
        "id": "unnes",
        "name": "Universitas Negeri Semarang",
        "programs": [
            {"name": "Pendidikan Guru Sekolah Dasar", "score": 580.5},
            {"name": "Manajemen", "score": 595.2},
            {"name": "Akuntansi", "score": 590.1},
            {"name": "Ilmu Hukum", "score": 605.8},
            {"name": "Teknik Informatika", "score": 620.4},
            {"name": "Kesehatan Masyarakat", "score": 585.5},
            {"name": "Pendidikan Bahasa Inggris", "score": 570.6}
        ]
    },
    {
        "id": "upi",
        "name": "Universitas Pendidikan Indonesia",
        "programs": [
            {"name": "Pendidikan Guru Sekolah Dasar", "score": 590.2},
            {"name": "Psikologi", "score": 620.5},
            {"name": "Manajemen", "score": 610.8},
            {"name": "Ilmu Komunikasi", "score": 605.4},
            {"name": "Pendidikan Bahasa Inggris", "score": 585.1},
            {"name": "Ilmu Komputer", "score": 635.7}
        ]
    },
    {
        "id": "unhas",
        "name": "Universitas Hasanuddin",
        "programs": [
            {"name": "Pendidikan Dokter", "score": 705.4},
            {"name": "Kesehatan Masyarakat", "score": 615.2},
            {"name": "Teknik Informatika", "score": 655.8},
            {"name": "Ilmu Hukum", "score": 625.1},
            {"name": "Manajemen", "score": 620.5},
            {"name": "Teknik Sipil", "score": 610.4},
            {"name": "Kehutanan", "score": 580.6}
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
        session.add(Source(name="internal_mock", label="Prediksi Internal (Mock)", count=45))
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
