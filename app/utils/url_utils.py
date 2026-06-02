def extract_last_path_segment(url: str) -> str | None:
    parts = url.rstrip("/").split("/")
    if parts:
        raw = parts[-1].replace("-", " ").title()
        return raw if raw else None
    return None
