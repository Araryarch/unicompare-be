import re


def normalize_name(name: str) -> str:
    n = name.strip().lower()
    n = re.sub(r"rata[-\s]?rata\s+nilai\s+utbk\s+", "", n)
    n = re.sub(r"skor\s+utbk\s+", "", n)
    n = re.sub(r"nilai\s+utbk\s+", "", n)
    n = re.sub(r"prediksi\s+", "", n)
    n = re.sub(r"[^a-z0-9\s]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    known_shortcuts = {
        "ui": "universitas indonesia",
        "itb": "institut teknologi bandung",
        "its": "institut teknologi sepuluh nopember",
        "ugm": "universitas gadjah mada",
        "ipb": "institut pertanian bogor",
        "ub": "universitas brawijaya",
        "unair": "universitas airlangga",
        "undip": "universitas diponegoro",
        "unpad": "universitas padjadjaran",
        "uns": "universitas sebelas maret",
        "uny": "universitas negeri yogyakarta",
        "unesa": "universitas negeri surabaya",
        "unnes": "universitas negeri semarang",
        "upi": "universitas pendidikan indonesia",
        "um": "universitas negeri malang",
        "unsoed": "universitas jenderal soedirman",
        "uho": "universitas halu oleo",
        "ulm": "universitas lambung mangkurat",
        "unhas": "universitas hasanuddin",
        "unud": "universitas udayana",
        "unram": "universitas mataram",
        "untan": "universitas tanjungpura",
        "unmul": "universitas mulawarman",
        "unsrat": "universitas sam ratulangi",
        "uncen": "universitas cenderawasih",
        "unpatti": "universitas pattimura",
        "undana": "universitas nusa cendana",
        "ung": "universitas negeri gorontalo",
        "unima": "universitas negeri manado",
        "unm": "universitas negeri makassar",
        "untad": "universitas tadulako",
        "ut": "universitas terbuka",
    }
    if n in known_shortcuts:
        return known_shortcuts[n]
    n = re.sub(r"^universitas\s+", "", n)
    n = re.sub(r"^institut\s+", "", n)
    n = re.sub(r"\bnegeri\b", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def short_normalize_name(name: str) -> str:
    s = normalize_name(name)
    return "".join([c for c in s if c.isalpha()])[:20]


def long_normalize_name(name: str) -> str:
    s = normalize_name(name)
    s = re.sub(r"negeri", "", s)
    return s


def make_uni_id(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "-", normalize_name(name).replace(" ", "-")).strip("-")
