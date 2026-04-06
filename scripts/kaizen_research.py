"""Weekly kaizen research — Friday afternoon.

Collects external signal (this is the seam you'll adapt most: scraping
the OpenClaw community, subreddits, whatever you follow) and cross-
references it with the week's frictions pulled from daily notes.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from scripts.common import MEMORY_DIR, call_claude, load_prompt, read_file, write_file, ROOT


def recent_frictions(days: int = 7) -> list[str]:
    out: list[str] = []
    for i in range(days):
        day = (date.today() - timedelta(days=i)).isoformat()
        note = read_file(MEMORY_DIR / f"{day}.md")
        if "## Frictions" not in note:
            continue
        section = note.split("## Frictions", 1)[1].split("\n## ", 1)[0]
        for line in section.splitlines():
            line = line.strip()
            if line.startswith("- "):
                out.append(f"{day}: {line[2:]}")
    return out


def system_map() -> list[str]:
    scripts_dir = ROOT / "scripts"
    entries: list[str] = []
    for p in sorted(scripts_dir.glob("*.py")):
        if p.name.startswith("_"):
            continue
        first_line = ""
        text = p.read_text(encoding="utf-8").splitlines()
        if text and text[0].startswith('"""'):
            first_line = text[0].strip('"').strip()
        entries.append(f"{p.name}: {first_line}")
    return entries


def collect_external_signal() -> list[dict]:
    """TODO: point this at whatever you actually follow.

    Suggested seams: the r/ClaudeAI subreddit, the Claude Code discord
    archives, x.com lists, specific Substacks. Each entry should be
    {title, url, summary, source}. Returning empty is fine — the prompt
    degrades gracefully.
    """
    return []


def main() -> None:
    payload = {
        "external": collect_external_signal(),
        "frictions": recent_frictions(),
        "memory_md": read_file(ROOT / "MEMORY.md"),
        "system_map": system_map(),
    }
    report = call_claude(load_prompt("kaizen_research"), payload, max_tokens=4096)
    if not report:
        return
    out_path = MEMORY_DIR / f"kaizen-research-{date.today().isoformat()}.md"
    write_file(out_path, report)
    print(f"[kaizen] wrote {out_path}")


if __name__ == "__main__":
    main()
