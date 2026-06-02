def parse_nilai(nilai_str: str) -> float | None:
    cleaned = nilai_str.strip().replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def enrich_programs(programs: list[dict]) -> list[dict]:
    enriched = []
    for p in programs:
        val = parse_nilai(p["score_text"])
        enriched.append({**p, "score": val})
    return enriched
