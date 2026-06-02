import importlib

_SCRAPER_MODULES: dict[str, str] = {
    "kampus_impian": ".kampus_impian",
    "smkitsi": ".smkitsi",
    "sonora": ".sonora",
    "haipintar": ".haipintar",
    "smkn5": ".smkn5",
}


def _load(name: str):
    mod = importlib.import_module(_SCRAPER_MODULES[name], __package__)
    return getattr(mod, f"scrape_{name}")


def scrape_kampus_impian():
    return _load("kampus_impian")()


def scrape_smkitsi():
    return _load("smkitsi")()


def scrape_sonora():
    return _load("sonora")()


def scrape_haipintar():
    return _load("haipintar")()


def scrape_smkn5():
    return _load("smkn5")()


__all__ = [
    "scrape_kampus_impian",
    "scrape_smkitsi",
    "scrape_sonora",
    "scrape_haipintar",
    "scrape_smkn5",
]
