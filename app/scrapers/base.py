import logging
import re

from app.utils.url_utils import extract_last_path_segment

log = logging.getLogger(__name__)


async def fetch_page_tables(
    url: str,
    cache: dict[str, list[dict]] | None = None,
    table_selector: str = "table",
    timeout: int | None = None,
) -> list[dict]:
    from scrapling import AsyncFetcher, Selector

    if cache is not None and url in cache:
        return cache[url]
    try:
        resp = await AsyncFetcher.get(url, follow_redirects=True, timeout=timeout)
        programs = []
        if resp.status == 200:
            sel = Selector(resp.body)
            for table in sel.css(table_selector):
                programs.extend(parse_programs_table(table))
    except Exception:
        programs = []
    if cache is not None:
        cache[url] = programs
    return programs


def extract_university_name_from_url(url: str) -> str:
    if "kampusimpian.com" in url or "/snbt/nilai-utbk/" in url:
        raw = extract_last_path_segment(url)
        if raw:
            return raw
    if "smkitsi.sch.id" in url:
        m = re.search(r"/skor-utbk[-/]?(.+)", url)
        if m:
            raw = m.group(1).rstrip("/").replace("-", " ").replace("/", " ").title()
            raw = re.sub(r"\s+\d{4}\s*$", "", raw)
            if raw.endswith(" Kedokteran"):
                raw = raw[: -len(" Kedokteran")]
            raw = raw.strip()
            if raw.upper() in {
                "IPB",
                "ITB",
                "ITH",
                "ITK",
                "ITS",
                "UGM",
                "UB",
                "UBT",
                "UHO",
                "ULM",
                "UM",
                "UNAIR",
                "UNCEN",
                "UNDANA",
                "UNDIKSHA",
                "UNDIP",
                "UNEJ",
                "UNESA",
                "UNG",
                "UNHAS",
                "UNIMA",
                "UNIMOR",
                "UNIPA",
                "UNKHAIR",
                "UNM",
                "UNMUL",
                "UNMUS",
                "UNNES",
                "UNPAD",
                "UNPATTI",
                "UNRAM",
                "UNS",
                "UNSIKA",
                "UNSIL",
                "UNSOED",
                "UNSRAT",
                "UNSULBAR",
                "UNTAD",
                "UNTAN",
                "UNTIDAR",
                "UNUD",
                "UNY",
                "UPI",
                "UPR",
                "UTM",
            }:
                raw = raw.upper()
            return raw if raw else url
    if "sonora.id" in url:
        m = re.search(r"/skor-utbk[-/]?(.+)", url)
        if m:
            raw = m.group(1).rstrip("/")
            raw = re.sub(r"[-/]snbt", "", raw)
            raw = re.sub(r"\s*\d{4}.*$", "", raw)
            raw = raw.replace("-", " ").replace("/", " ").title().strip()
            return raw if raw else url
    return url


def parse_programs_table(table) -> list[dict]:
    rows = table.css("tr")
    if not rows:
        return []

    header_cells = rows[0].css("td, th")
    header_texts = [h.get_all_text(strip=True).upper() for h in header_cells]

    prodi_idx = None
    nilai_idx = None
    jenjang_idx = None

    for i, h in enumerate(header_texts):
        if any(x in h for x in ("PRODI", "JURUSAN", "PROGRAM STUDI")):
            prodi_idx = i
        elif any(x in h for x in ("NILAI UTBK", "SKOR UTBK", "NILAI")):
            nilai_idx = i
        elif "JENJANG" in h:
            jenjang_idx = i

    if prodi_idx is None or nilai_idx is None:
        return []

    programs = []
    for row in rows[1:]:
        cells = row.css("td, th")
        if len(cells) <= max(prodi_idx, nilai_idx):
            continue
        prodi = cells[prodi_idx].get_all_text(strip=True)
        nilai = cells[nilai_idx].get_all_text(strip=True)
        jenjang = ""
        if jenjang_idx is not None and len(cells) > jenjang_idx:
            jenjang = cells[jenjang_idx].get_all_text(strip=True)
        if prodi and nilai:
            entry = {"name": str(prodi), "score_text": str(nilai)}
            if jenjang:
                entry["degree"] = str(jenjang)
            programs.append(entry)
    return programs
