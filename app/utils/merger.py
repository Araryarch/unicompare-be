import logging
import re

from app.utils.normalize_name import (
    long_normalize_name,
    short_normalize_name,
)
from app.utils.normalize_name import (
    normalize_name as base_normalize,
)
from app.utils.score_utils import enrich_programs

log = logging.getLogger(__name__)


def _merge_program(programs: dict[str, dict], new_prog: dict, source: str) -> None:
    key = new_prog["name"]
    if key in programs:
        existing = programs[key]
        if source not in existing.get("sources", []):
            existing.setdefault("sources", []).append(source)
            existing["source_count"] = existing.get("source_count", 1) + 1
        if new_prog.get("score") is not None:
            existing["_sum"] = (
                existing.get(
                    "_sum", existing.get("score", 0) * (existing["source_count"] - 1)
                )
                + new_prog["score"]
            )
            existing["score"] = existing["_sum"] / existing["source_count"]
            existing["score_text"] = new_prog["score_text"]
    else:
        new_p = dict(new_prog)
        new_p.setdefault("sources", []).append(source)
        new_p["source_count"] = 1
        if new_p.get("score") is not None:
            new_p["_sum"] = new_p["score"]
        programs[key] = new_p


def merge_universities(*source_lists: list[dict]) -> list[dict]:
    def _normalize_name(name: str) -> str:
        n = base_normalize(name)
        return re.sub(r"(ipb|itb|its|ugm|ub|ui)$", "", n).strip()

    def _make_uni_id(name: str) -> str:
        return re.sub(r"[^a-z0-9]", "-", _normalize_name(name).replace(" ", "-")).strip(
            "-"
        )

    def _name_score(name: str) -> int:
        n = name.lower()
        if any(
            x in n for x in ("universitas", "institut", "sekolah tinggi", "politeknik")
        ):
            return 3
        if any(
            x in n
            for x in ("itb", "its", "ui", "ugm", "ipb", "unair", "undip", "unpad", "ub")
        ):
            return 2
        return 1

    merged: dict[str, dict] = {}
    for source_list in source_lists:
        for entry in source_list:
            raw_name = entry["name"]
            name_norm = _normalize_name(raw_name)
            programs = enrich_programs(entry["programs"])
            group_found = False
            for key, group in merged.items():
                group_norm = _normalize_name(group["names"][0])
                short_a = short_normalize_name(name_norm)
                long_a = long_normalize_name(name_norm)
                short_b = short_normalize_name(group_norm)
                long_b = long_normalize_name(group_norm)
                if short_a and short_b and (short_a in long_b or short_b in long_a):
                    if raw_name not in group["names"]:
                        group["names"].append(raw_name)
                    group["sources"].add(entry.get("source", ""))
                    for p in programs:
                        _merge_program(group["programs"], p, entry.get("source", ""))
                    group_found = True
                    break

            if not group_found:
                merged[name_norm] = {
                    "names": [raw_name],
                    "sources": {entry.get("source", "")},
                    "programs": {p["name"]: p for p in programs},
                }

    groups = []
    for name_norm, group in merged.items():
        all_names = group["names"]
        best_name = max(all_names, key=_name_score)
        programs_list = list(group["programs"].values())
        for p in programs_list:
            if "source_count" in p:
                p["score"] = p.get("_sum", 0) / p["source_count"]
                del p["_sum"]
        programs_list.sort(key=lambda x: x.get("score") or 0, reverse=True)
        groups.append(
            {
                "id": _make_uni_id(best_name),
                "name": best_name,
                "sources": sorted(group["sources"]),
                "programs": programs_list,
            }
        )

    groups.sort(key=lambda x: x["name"].lower())
    return groups
