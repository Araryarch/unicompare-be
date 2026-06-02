from app.scrapers import (
    scrape_haipintar,
    scrape_kampus_impian,
    scrape_smkitsi,
    scrape_smkn5,
    scrape_sonora,
)

ALL_SOURCES = [
    ("kampusimpian", "Kampus Impian", scrape_kampus_impian),
    ("smkitsi", "SMK IT SI", scrape_smkitsi),
    ("sonora", "Sonora ID", scrape_sonora),
    ("haipintar", "Hai Pintar", scrape_haipintar),
    ("smkn5", "SMKN 5 Bekasi", scrape_smkn5),
]
