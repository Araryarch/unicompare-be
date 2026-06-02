import asyncio
import logging

from app.utils.url_utils import extract_last_path_segment

from .base import fetch_page_tables

log = logging.getLogger(__name__)

MASTER_URL = "https://haipintar.com/daftar-prediksi-skor-utbk-ptn/"
SOURCE_NAME = "haipintar"

detail_cache: dict[str, list[dict]] = {}


async def discover_pages() -> set[str]:
    from scrapling import AsyncFetcher, Selector

    pages = set()
    try:
        resp = await AsyncFetcher.get(MASTER_URL, follow_redirects=True)
        if resp.status == 200:
            sel = Selector(resp.body)
            for a in sel.css('a[href*="skor-utbk-"], a[href*="rata-rata-skor-utbk"]'):
                href = a.attrib.get("href", "")
                if href and "haipintar.com" in href and href != MASTER_URL:
                    pages.add(href)
    except Exception as e:
        log.warning("Haipintar master list error: %s", e)
    return pages


async def scrape_haipintar() -> list[dict]:
    pages = await discover_pages()
    log.info("Haipintar: %d UTBK pages found", len(pages))
    sem = asyncio.Semaphore(5)

    async def scrape_one(url: str) -> dict:
        async with sem:
            programs = await fetch_page_tables(url, detail_cache)
            raw_name = extract_last_path_segment(url) or url
            name = (
                raw_name.replace("Skor Utbk ", "")
                .replace("Rata Rata Skor Utbk ", "")
                .strip()
            )
            return {
                "name": name,
                "source_url": url,
                "source": SOURCE_NAME,
                "programs": programs,
            }

    tasks = [scrape_one(url) for url in pages]
    results = await asyncio.gather(*tasks)
    return results
