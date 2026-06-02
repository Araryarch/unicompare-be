import asyncio
import logging

from scrapling import AsyncFetcher, Selector

from app.utils.url_utils import extract_last_path_segment

from .base import fetch_page_tables

log = logging.getLogger(__name__)

CATEGORY_URL = "https://www.smkn5kotabekasi.sch.id/category/utbk/"
SOURCE_NAME = "smkn5"

detail_cache: dict[str, list[dict]] = {}


async def discover_pages() -> set[str]:
    pages = set()
    for page_num in range(1, 8):
        url = f"{CATEGORY_URL}page/{page_num}/" if page_num > 1 else CATEGORY_URL
        try:
            resp = await AsyncFetcher.get(url, follow_redirects=True, timeout=10)
            sel = Selector(resp.body)
            for a in sel.css(
                'a[href*="utbk"], a[href*="nilai-utbk"], a[href*="skor-utbk"]'
            ):
                href = a.attrib.get("href", "")
                if (
                    href
                    and "smkn5kotabekasi.sch.id" in href
                    and "/category/" not in href
                ):
                    pages.add(href)
        except Exception as e:
            log.warning("Smkn5 page %d error: %s", page_num, e)
    return pages


async def scrape_smkn5() -> list[dict]:
    pages = await discover_pages()
    log.info("Smkn5: %d UTBK pages found", len(pages))
    sem = asyncio.Semaphore(5)

    async def scrape_one(url: str) -> dict:
        async with sem:
            programs = await fetch_page_tables(url, detail_cache)
            raw_name = extract_last_path_segment(url) or url
            for prefix in ["Rata Rata Nilai Utbk ", "Nilai Utbk ", "Skor Utbk "]:
                if raw_name.startswith(prefix):
                    raw_name = raw_name[len(prefix) :]
            raw_name = (
                raw_name.replace("Jalur Snbt", "").replace("Kedokteran", "").strip()
            )
            return {
                "name": raw_name,
                "source_url": url,
                "source": SOURCE_NAME,
                "programs": programs,
            }

    tasks = [scrape_one(url) for url in pages]
    results = await asyncio.gather(*tasks)
    return results
