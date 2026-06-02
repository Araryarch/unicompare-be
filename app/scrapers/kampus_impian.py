import asyncio
import logging
import re

from scrapling import AsyncFetcher, Selector

from .base import extract_university_name_from_url, parse_programs_table

log = logging.getLogger(__name__)

BASE_URL = "https://kampusimpian.com/snbt/nilai-utbk/"
SOURCE_NAME = "kampusimpian"

detail_cache: dict[str, dict] = {}


async def scrape_page(url: str) -> tuple[list[dict], int | None]:
    resp = await AsyncFetcher.get(url, follow_redirects=True)
    if resp.status != 200:
        return [], None
    sel = Selector(resp.body)
    items = sel.css("li.post-item")
    unis = []
    for item in items:
        link = item.css("h2.post-title a")
        if link:
            href = link[0].attrib.get("href", "")
            name = link[0].text.strip() if link[0].text else ""
            if href and name:
                if href.startswith("/"):
                    href = "https://kampusimpian.com" + href
                unis.append({"name": name, "url": href})
    last_link = sel.css("li.last-page a")
    total = None
    if last_link:
        m = re.search(r"/page/(\d+)/", last_link[0].attrib.get("href", ""))
        if m:
            total = int(m.group(1))
    return unis, total


async def scrape_kampus_impian() -> list[dict]:
    all_unis = []
    first, total_pages = await scrape_page(BASE_URL)
    all_unis.extend(first)
    log.info("Kampus Impian page 1: %d universities", len(first))

    if total_pages and total_pages > 1:
        for p in range(2, total_pages + 1):
            unis, _ = await scrape_page(f"{BASE_URL}page/{p}/")
            all_unis.extend(unis)
            log.info(
                "Kampus Impian page %d/%d: %d universities", p, total_pages, len(unis)
            )

    sem = asyncio.Semaphore(5)

    async def fetch_detail(u: dict) -> dict:
        async with sem:
            url = u["url"]
            if url in detail_cache:
                cached = detail_cache[url]
                programs = cached["programs"]
                detail_name = cached.get("name", "")
            else:
                resp = await AsyncFetcher.get(url, follow_redirects=True)
                programs = []
                detail_name = ""
                if resp.status == 200:
                    sel = Selector(resp.body)
                    for table in sel.css("figure.wp-block-table table"):
                        programs.extend(parse_programs_table(table))
                    h1 = sel.css("h1")
                    if h1:
                        detail_name = h1[0].get_all_text(strip=True)
                        detail_name = re.sub(
                            r"rata[-\s]?rata\s+nilai\s+utbk\s+",
                            "",
                            detail_name,
                            flags=re.IGNORECASE,
                        )
                        detail_name = re.sub(
                            r"prediksi\s+", "", detail_name, flags=re.IGNORECASE
                        )
                        detail_name = re.sub(
                            r"skor\s+utbk\s+", "", detail_name, flags=re.IGNORECASE
                        )
                        detail_name = re.sub(
                            r"\s+untuk\s+masuk\s+",
                            " ",
                            detail_name,
                            flags=re.IGNORECASE,
                        )
                        detail_name = detail_name.strip()
                detail_cache[url] = {"programs": programs, "name": detail_name}

            final_name = (
                detail_name or extract_university_name_from_url(url) or u["name"]
            )
            return {
                "name": final_name,
                "source_url": url,
                "source": SOURCE_NAME,
                "programs": programs,
            }

    tasks = [fetch_detail(u) for u in all_unis]
    results = await asyncio.gather(*tasks)
    return results
