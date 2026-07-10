#!/usr/bin/env python3
"""
One-off backfill: adds a `category:` frontmatter key (distinct from Jekyll's
built-in `categories:`) to every post, based on what the post is actually
about. Used to power the /guides/ and /small-spaces/ hub pages (Phase K3),
plus gives the rest of the catalog a real topic taxonomy for future use.

Run from repo root: python scripts/backfill_category.py
"""
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parent.parent / "_posts"

# filename -> category slug, assigned by hand after reading each post.
CATEGORY = {
    "2026-06-07-best-air-fryers-under-50.md": "appliances",
    "2026-06-07-best-immersion-blenders-under-50.md": "appliances",
    "2026-06-09-best-coffee-gadgets-and-accessories-under-50.md": "appliances",
    "2026-06-10-best-kitchen-tools-for-beginners-under-50.md": "prep-tools",
    "2026-06-12-best-meal-prep-gadgets-under-50.md": "prep-tools",
    "2026-06-15-best-kitchen-gadgets-for-college-students.md": "small-spaces",
    "2026-06-17-best-mini-appliances-for-dorm-rooms.md": "small-spaces",
    "2026-06-19-best-knife-sharpeners-under-50.md": "knives",
    "2026-06-22-how-to-sharpen-a-knife-at-home-when-to-do-it-and-what-actual.md": "guides",
    "2026-06-24-best-silicone-spatula-under-50-top-picks-for-every-kitchen-task.md": "prep-tools",
    "2026-06-24-best-vegetable-peelers-under-50-top-picks-for-every-kitchen-style.md": "prep-tools",
    "2026-06-26-15-best-kitchen-organization-tools-under-50-budget-friendly-solutions-for-every-cabinet-and-drawer.md": "organization",
    "2026-06-29-how-to-season-a-cast-iron-skillet-and-keep-it-that-way.md": "guides",
    "2026-07-01-15-best-kitchen-gadgets-under-50-top-tools-that-won-t-break-the-bank.md": "gadgets",
    "2026-07-03-10-best-kitchen-tools-under-20-budget-friendly-gadgets-that-actually-work.md": "gadgets",
    "2026-07-06-best-kitchen-gifts-under-50-for-home-cooks.md": "small-spaces",
    "2026-07-09-best-chef-knife-under-50-in-2026-top-budget-friendly-options-for-home-cooks.md": "knives",
    "2026-07-10-best-cutting-board-under-50-in-2026-top-picks-for-every-kitchen.md": "prep-tools",
    "2026-07-10-best-nonstick-pan-under-50-in-2026-top-picks-for-every-kitchen-need.md": "cookware",
}


def process_file(path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")

    if "\ncategory:" in text.split("\n---", 1)[0] + "\n":
        print(f"SKIP (already has category:): {path.name}")
        return

    slug = CATEGORY.get(path.name)
    if not slug:
        print(f"SKIP (no mapping): {path.name}")
        return

    # Insert right after the `categories:` line if present, else right after
    # the opening `---`.
    lines = text.split("\n")
    insert_at = None
    for i, line in enumerate(lines):
        if line.startswith("categories:"):
            insert_at = i + 1
            break
    if insert_at is None:
        for i, line in enumerate(lines):
            if line.strip() == "---" and i > 0:
                insert_at = i + 1
                break

    lines.insert(insert_at, f"category: {slug}")
    new_text = "\n".join(lines)
    out = new_text.encode("utf-8")
    if bom:
        out = b"\xef\xbb\xbf" + out
    path.write_bytes(out)
    print(f"{path.name}: category: {slug}")


def main():
    for path in sorted(POSTS_DIR.glob("*.md")):
        process_file(path)


if __name__ == "__main__":
    main()
