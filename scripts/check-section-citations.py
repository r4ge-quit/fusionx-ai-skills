#!/usr/bin/env python3
"""Flag reference-file citations that name one section without indicating
full/multi-section coverage.

This cannot determine whether a flagged citation is actually incomplete —
that requires reading the target file and judging whether sibling sections
govern the same task. It only narrows where a human (or a future session)
needs to look, per README.md's "Conventions" section. A citation is flagged
if it names a specific section of a `references/*.md` (or similar) file
without any nearby language ("in full", "read the whole file", "all N
sections", "every section", "both sections") indicating the reader was told
to go beyond that one named section.
"""

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST_PATH = ROOT / "scripts" / "section-citation-allowlist.json"

SECTION_CITE = re.compile(
    r"[`\"']?[\w./-]+\.md[`\"']?'?s?\s+(?:own\s+)?(?:\"[^\"]+\"\s+)?[Ss]ection\s+[\w\d]+",
)
FULL_COVERAGE_HINTS = re.compile(
    r"in full|whole file|read.{0,15}fully|every section|all (?:three|four|five|\d+) sections|"
    r"both sections|read.{0,10}whole|self-contained|entirety",
    re.IGNORECASE,
)


def scan(path: Path) -> list[tuple[int, str]]:
    hits = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, line in enumerate(lines, start=1):
        if not SECTION_CITE.search(line):
            continue
        window = " ".join(lines[max(0, i - 3) : i + 2])
        if FULL_COVERAGE_HINTS.search(window):
            continue
        hits.append((i, line.strip()))
    return hits


def load_allowlist() -> list[dict]:
    if not ALLOWLIST_PATH.exists():
        return []
    return json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))


def is_allowlisted(rel_path: str, line_text: str, allowlist: list[dict]) -> bool:
    for entry in allowlist:
        if entry["file"] == rel_path and entry["line_contains"] in line_text:
            return True
    return False


def main() -> int:
    show_allowlisted = "--show-allowlisted" in sys.argv
    allowlist = load_allowlist()
    targets = sorted(ROOT.glob("skills/*/SKILL.md"))
    any_new_hits = False
    for target in targets:
        rel = str(target.relative_to(ROOT)).replace("\\", "/")
        hits = scan(target)
        new_hits = [
            (n, t) for n, t in hits if not is_allowlisted(rel, t, allowlist)
        ]
        allowlisted_hits = [
            (n, t) for n, t in hits if is_allowlisted(rel, t, allowlist)
        ]
        if new_hits:
            any_new_hits = True
            print(f"\n{rel}:")
            for lineno, text in new_hits:
                print(f"  L{lineno}: {text}")
        if show_allowlisted and allowlisted_hits:
            print(f"\n{rel} (allowlisted, already reviewed):")
            for lineno, text in allowlisted_hits:
                print(f"  L{lineno}: {text}")

    if any_new_hits:
        print(
            "\nEach line above names a specific section without nearby "
            "full/multi-section coverage language, and is NOT in "
            "scripts/section-citation-allowlist.json. Read the target file "
            "and confirm no sibling section governs the same task. If it's "
            "genuinely fine (full coverage established elsewhere, or "
            "correctly scoped to one task with no orphaned sibling), add it "
            "to the allowlist with a reason instead of ignoring this "
            "output — see README.md's Conventions section for the two real "
            "incidents this check exists to catch."
        )
        return 1

    print("No new (non-allowlisted) section citations flagged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
