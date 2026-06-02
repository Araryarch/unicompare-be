import asyncio
import logging

from .base import extract_university_name_from_url, fetch_page_tables

log = logging.getLogger(__name__)

BASE_URL = "https://www.smkitsi.sch.id/category/utbk/"
SOURCE_NAME = "smkitsi"

detail_cache: dict[str, list[dict]] = {}


async def scrape_smkitsi() -> list[dict]:
    from scrapling import AsyncFetcher, Selector

    all_links = set()
    for page in range(1, 6):
        url = f"{BASE_URL}page/{page}/" if page > 1 else BASE_URL
        try:
            resp = await AsyncFetcher.get(url, follow_redirects=True)
            sel = Selector(resp.body)
            for a in sel.css('a[href*="skor-utbk"]'):
                href = a.attrib.get("href", "")
                if href:
                    all_links.add(href)
        except Exception as e:
            log.warning("Smkitsi page %d error: %s", page, e)

    log.info("Smkitsi: %d UTBK pages found", len(all_links))
    sem = asyncio.Semaphore(5)

    async def scrape_one(url: str) -> dict:
        async with sem:
            programs = await fetch_page_tables(url, detail_cache)
            name = extract_university_name_from_url(url)
            return {
                "name": name,
                "source_url": url,
                "source": SOURCE_NAME,
                "programs": programs,
            }

    tasks = [scrape_one(url) for url in all_links]
    results = await asyncio.gather(*tasks)
    return results
