"""Weekly research digest — Sunday 8am.

Reads sources from config/research_sources.yml. Fetching logic is a
seam — the scaffolding here just loads config and calls Claude so you
can wire up your preferred fetcher (X API, RSS, Readwise, etc.).
"""

from __future__ import annotations

from datetime import date

from scripts.common import (
    CONFIG_DIR,
    MEMORY_DIR,
    ROOT,
    call_claude,
    load_prompt,
    load_yaml,
    read_file,
    write_file,
)


def fetch_items(sources: dict) -> list[dict]:
    """TODO: implement for the sources you actually track.

    Should return a list of dicts:
      {source, tier, title, url, text, engagement}
    """
    return []


def focus_areas_from_memory() -> list[str]:
    memory = read_file(ROOT / "MEMORY.md")
    out: list[str] = []
    if "Current focus" not in memory:
        return out
    block = memory.split("Current focus", 1)[1].splitlines()
    for line in block:
        line = line.strip()
        if line.startswith(("1.", "2.", "3.", "-")) and len(line) > 3:
            out.append(line.lstrip("0123456789.- ").strip())
        if line.startswith("## "):
            break
    return out[:3]


def main() -> None:
    sources = load_yaml(CONFIG_DIR / "research_sources.yml")
    payload = {
        "items": fetch_items(sources),
        "focus": focus_areas_from_memory(),
        "boost_keywords": sources.get("boost_keywords", []),
        "demote_keywords": sources.get("demote_keywords", []),
    }
    digest = call_claude(load_prompt("research_digest"), payload, max_tokens=4096)
    if not digest:
        return
    out = MEMORY_DIR / f"digest-{date.today().isoformat()}.md"
    write_file(out, digest)
    print(f"[digest] wrote {out}")


if __name__ == "__main__":
    main()
