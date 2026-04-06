"""people/<slug>.md read/append helpers."""

from __future__ import annotations

from pathlib import Path

from scripts.common import PEOPLE_DIR, read_file, write_file, CONFIG_DIR, load_yaml


def people_index() -> dict[str, dict]:
    """Flat slug -> entry dict from config/people.yml."""
    cfg = load_yaml(CONFIG_DIR / "people.yml")
    out: dict[str, dict] = {}
    for tier, entries in (cfg.get("tiers") or {}).items():
        for entry in entries or []:
            slug = entry.get("slug")
            if not slug:
                continue
            out[slug] = {**entry, "tier": tier}
    return out


def person_path(slug: str) -> Path:
    return PEOPLE_DIR / f"{slug}.md"


def read_person(slug: str) -> str:
    path = person_path(slug)
    if not path.exists():
        index = people_index()
        entry = index.get(slug, {})
        skeleton = (
            f"# {entry.get('name', slug)}\n\n"
            f"- Slug: {slug}\n"
            f"- Tier: {entry.get('tier', '')}\n"
            f"- Org: {entry.get('org') or entry.get('fund') or entry.get('company', '')}\n\n"
            "## Status\n\n"
            "## History\n\n"
            "## Open commitments (they owe)\n\n"
            "## Open commitments (we owe)\n\n"
            "## What they care about\n\n"
        )
        write_file(path, skeleton)
    return read_file(path)


def append_to_person(slug: str, section: str, line: str) -> None:
    """Append a line to a labeled section of people/<slug>.md.

    If the section doesn't exist, create it at the bottom. Never rewrites
    existing content — human edits are sacred.
    """
    content = read_person(slug)
    header = f"## {section}"
    if header in content:
        lines = content.splitlines()
        for i, existing in enumerate(lines):
            if existing.strip() == header:
                # Insert after the header (and a blank line if present)
                insert_at = i + 1
                if insert_at < len(lines) and lines[insert_at].strip() == "":
                    insert_at += 1
                lines.insert(insert_at, f"- {line}")
                write_file(person_path(slug), "\n".join(lines) + "\n")
                return
    else:
        content += f"\n{header}\n\n- {line}\n"
        write_file(person_path(slug), content)
