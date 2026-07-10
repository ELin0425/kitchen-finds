#!/usr/bin/env python3
"""
One-off Phase K5 fix: for every post, make sure the body's hero image
- points at a real local file (not a broken path or missing entirely)
- carries explicit width/height (via a kramdown IAL block right after the
  image, so kramdown hoists the attributes onto the <img> tag)
- has real descriptive alt text (not a keyword-stuffed title or filename)
- keeps/adds the Unsplash photographer caption where we know it

Run from repo root: python scripts/fix_images.py

This has already been run once (see git history / the images already sitting
in assets/images/posts/). Kept for reference and in case a future post needs
the same treatment - the IMAGES table below is a record of what was done,
not something meant to run again unmodified.
"""
import re
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parent.parent / "_posts"

# path is a site-root-relative web path (starts with /), matching how
# `image:` frontmatter and body hero images are referenced elsewhere.
IMAGES = {
    "2026-06-07-best-air-fryers-under-50.md": dict(
        path="/assets/images/posts/2026-06-07-best-air-fryers-under-50.jpg",
        width=1080, height=720,
        alt="Golden fried chicken bites cooking in an air fryer basket",
        caption=("Fujiphilm", "https://unsplash.com/@fujiphilm"),
    ),
    "2026-06-07-best-immersion-blenders-under-50.md": dict(
        path="/assets/images/posts/2026-06-07-best-immersion-blenders-under-50.jpg",
        width=1080, height=720,
        alt="A hand using an immersion blender to blend ingredients in a cup at the kitchen sink",
        caption=("Louis Hansel", "https://unsplash.com/@louishansel"),
    ),
    "2026-06-09-best-coffee-gadgets-and-accessories-under-50.md": dict(
        path="/assets/images/posts/2026-06-09-best-coffee-gadgets-and-accessories-under.jpg",
        width=1080, height=811,
        alt="A pour-over coffee carafe and cup of coffee next to a compact coffee gadget",
        caption=("Goran Ivos", "https://unsplash.com/@goran_ivos"),
    ),
    "2026-06-10-best-kitchen-tools-for-beginners-under-50.md": dict(
        path="/assets/images/posts/2026-06-19-best-kitchen-tools-for-beginners-under-50.jpg",
        width=1080, height=720,
        alt="A tidy kitchen counter with a cookbook stand, wooden cutting boards, and a crock of utensils",
        caption=None,  # pre-existing asset, no attribution metadata recovered
        insert_missing=True,
    ),
    "2026-06-12-best-meal-prep-gadgets-under-50.md": dict(
        path="/assets/images/posts/2026-06-12-best-meal-prep-gadgets-under-50.jpg",
        width=1080, height=715,
        alt="Hands chopping fresh cilantro with a chef's knife on a cutting board",
        caption=("Alyson McPhee", "https://unsplash.com/@alyson_jane"),
    ),
    "2026-06-15-best-kitchen-gadgets-for-college-students.md": dict(
        path="/assets/images/posts/2026-06-15-best-kitchen-gadgets-for-college-students.jpg",
        width=1080, height=720,
        alt="A small apartment kitchen with an island counter, blender, and gas stove",
        caption=("Franco Debartolo", "https://unsplash.com/@francotheshooter"),
    ),
    "2026-06-17-best-mini-appliances-for-dorm-rooms.md": dict(
        path="/assets/images/posts/2026-06-17-best-mini-appliances-for-dorm-rooms.jpg",
        width=1080, height=720,
        alt="A stainless steel colander on a cutting board with mini kitchen appliances in the background",
        caption=("David Trinks", "https://unsplash.com/@dtrinksrph"),
    ),
    "2026-06-19-best-knife-sharpeners-under-50.md": dict(
        path="/assets/images/posts/2026-06-19-best-knife-sharpeners-under-50.jpg",
        width=1080, height=715,
        alt="Hands chopping fresh herbs with a sharp chef's knife on a cutting board",
        caption=("Alyson McPhee", "https://unsplash.com/@alyson_jane"),
    ),
    "2026-06-22-how-to-sharpen-a-knife-at-home-when-to-do-it-and-what-actual.md": dict(
        path="/assets/images/posts/2026-06-22-how-to-sharpen-a-knife-at-home-when-to-do-it-and-what-actual.jpg",
        width=1080, height=1080,
        alt="Close-up of hands sharpening a knife blade against a whetstone",
        caption=("Sebastian Schuster", "https://unsplash.com/@sschusterphotoart"),
        insert_missing=True,
    ),
    "2026-06-24-best-silicone-spatula-under-50-top-picks-for-every-kitchen-task.md": dict(
        path="/assets/images/posts/2026-06-24-best-silicone-spatula-under-50-top-picks-for-every-kitchen-task.jpg",
        width=1080, height=720,
        alt="A silicone spatula stirring melted dark chocolate in a saucepan",
        caption=("Joanna Stolowicz", "https://unsplash.com/@joanna_stolowicz"),
        insert_missing=True,
    ),
    "2026-06-24-best-vegetable-peelers-under-50-top-picks-for-every-kitchen-style.md": dict(
        path="/assets/images/posts/2026-06-24-best-vegetable-peelers-under-50-top-picks-for-every-kitchen-style.jpg",
        width=1080, height=720,
        alt="A red apple being peeled with a vegetable peeler over a white plate",
        caption=("Sandie Clarke", "https://unsplash.com/@honeypoppet"),
        insert_missing=True,
    ),
    "2026-06-26-15-best-kitchen-organization-tools-under-50-budget-friendly-solutions-for-every-cabinet-and-drawer.md": dict(
        path="/assets/images/posts/2026-06-26-15-best-kitchen-organization-tools-under-50-budget-friendly-solutions-for-every-cabinet-and-drawer.jpg",
        width=1080, height=720,
        alt="An organized kitchen drawer filled with neatly arranged utensils",
        caption=("Daiga Ellaby", "https://unsplash.com/@daiga_ellaby"),
        insert_missing=True,
    ),
    "2026-06-29-how-to-season-a-cast-iron-skillet-and-keep-it-that-way.md": dict(
        path="/assets/images/posts/2026-06-29-how-to-season-a-cast-iron-skillet-and-keep-it-that-way.jpg",
        width=1080, height=1439,
        alt="A red bell pepper resting in a well-seasoned cast iron skillet",
        caption=("Joel Rouse", "https://unsplash.com/@thebumpercrew"),
        insert_missing=True,
    ),
    "2026-07-01-15-best-kitchen-gadgets-under-50-top-tools-that-won-t-break-the-bank.md": dict(
        path="/assets/images/posts/2026-07-01-15-best-kitchen-gadgets-under-50-top-tools-that-wo.jpg",
        width=1080, height=843,
        alt="A kitchen counter with a Dutch oven, mortar and pestle, and a cutting board with a chef's knife",
        caption=("KROK Craft", "https://unsplash.com/@krokcraft"),
    ),
    "2026-07-03-10-best-kitchen-tools-under-20-budget-friendly-gadgets-that-actually-work.md": dict(
        path="/assets/images/posts/2026-07-03-10-best-kitchen-tools-under-20-budget-friendly-gadgets-that-actually-work.jpg",
        width=1080, height=720,
        alt="A kitchen drawer with an assortment of everyday utensils and spoons",
        caption=("Orgalux", "https://unsplash.com/@orgalux"),
        insert_missing=True,
    ),
    "2026-07-06-best-kitchen-gifts-under-50-for-home-cooks.md": dict(
        path="/assets/images/posts/2026-07-06-best-kitchen-gifts-under-50-for-home-cooks.jpg",
        width=1080, height=1620,
        alt="A set of wooden cooking spoons standing in a wooden crock, a classic kitchen gift",
        caption=("Andrew Valdivia", "https://unsplash.com/@donovan_valdivia"),
        insert_missing=True,
    ),
    "2026-07-09-best-chef-knife-under-50-in-2026-top-budget-friendly-options-for-home-cooks.md": dict(
        path="/assets/images/posts/2026-07-09-best-chef-knife-under-50-in-2026-top-budget-friend.jpg",
        width=1080, height=720,
        alt="Two chef's knives laid out on a cutting board next to bread, milk, and sliced fruit",
        caption=("Cooker King", "https://unsplash.com/@cookerking"),
    ),
    "2026-07-10-best-cutting-board-under-50-in-2026-top-picks-for-every-kitchen.md": dict(
        path="/assets/images/posts/2026-07-10-best-cutting-board-under-50-in-2026-top-picks-for-.jpg",
        width=1080, height=608,
        alt="A thick end-grain wood cutting board with a checkerboard pattern",
        caption=("Pawel Wertel", "https://unsplash.com/@szuja"),
    ),
    "2026-07-10-best-nonstick-pan-under-50-in-2026-top-picks-for-every-kitchen-need.md": dict(
        path="/assets/images/posts/2026-07-10-best-nonstick-pan-under-50-in-2026-top-picks-for-e.jpg",
        width=1080, height=720,
        alt="A family cooking breakfast together with a skillet of sausage and eggs on the counter",
        caption=("Jimmy Dean", "https://unsplash.com/@jimmydean"),
    ),
}

IMG_LINE_RE = re.compile(r"^!\[[^\]]*\]\([^)]+\)\s*$", re.M)

# NOTE: kramdown's block IAL (`{:width="..." height="..."}` on the line right
# after a markdown image) does NOT get hoisted onto the <img> tag under
# GitHub Pages' GFM-mode kramdown - it lands on the wrapping <p> instead,
# where width/height are meaningless. Verified live after first deploying
# with that approach. Using a raw HTML <img> tag instead guarantees the
# attributes land on the actual element regardless of parser quirks.


def build_block(info):
    lines = [
        f'<img src="{info["path"]}" alt="{info["alt"]}" '
        f'width="{info["width"]}" height="{info["height"]}">'
    ]
    if info.get("caption"):
        name, profile = info["caption"]
        lines.append(f"*Photo by [{name}]({profile}) on [Unsplash](https://unsplash.com)*")
    return "\n".join(lines)


def fix_frontmatter_image(fm, path):
    if re.search(r"(?m)^image:\s*.+$", fm):
        return re.sub(r"(?m)^image:\s*.+$", f'image: "{path}"', fm)
    # no image: key at all - insert right after category:/categories: if present, else after layout:
    lines = fm.split("\n")
    insert_at = 1  # after layout: line by default
    for i, line in enumerate(lines):
        if line.startswith("category:") or line.startswith("categories:"):
            insert_at = i + 1
    lines.insert(insert_at, f'image: "{path}"')
    return "\n".join(lines)


def process_file(name, info):
    path_on_disk = POSTS_DIR / name
    raw = path_on_disk.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")

    m = re.match(r"^---\r?\n(.*?\r?\n)---\r?\n", text, re.S)
    if not m:
        print(f"SKIP (no frontmatter): {name}")
        return
    fm = m.group(1)
    body = text[m.end():]

    new_fm = fix_frontmatter_image(fm, info["path"])
    block = build_block(info)

    if info.get("insert_missing"):
        # No existing hero image in body - insert the block as the very
        # first thing in the body (matches where every other post's hero
        # image sits). Some posts have mixed CRLF/LF line endings, so strip
        # both characters, not just "\n", or a leading "\r" survives and
        # doubles up the blank line before the image / before the text.
        new_body = "\n" + block + "\n\n" + body.lstrip("\r\n")
    else:
        # Replace the existing ![...](...) line, and drop any pre-existing
        # caption line right after it (we rebuild both from `block`).
        def repl(match):
            return block
        new_body, n = IMG_LINE_RE.subn(repl, body, count=1)
        if n == 0:
            print(f"WARN: no existing image line found to replace in {name}")
            new_body = block + "\n\n" + body.lstrip("\n")
        else:
            # Remove the old caption line (the italic "*Photo by ...*" line)
            # that used to directly follow the old image line, since it's
            # now part of `block`. It will appear directly after our newly
            # inserted block; strip one immediately-following caption line
            # if present and not already the one we just wrote.
            lines = new_body.split("\n")
            block_lines = block.split("\n")
            end_idx = None
            for i in range(len(lines) - len(block_lines) + 1):
                if lines[i:i + len(block_lines)] == block_lines:
                    end_idx = i + len(block_lines)
                    break
            if end_idx is not None and end_idx < len(lines):
                if lines[end_idx].strip().startswith("*Photo by"):
                    del lines[end_idx]
            new_body = "\n".join(lines)

    new_text = f"---\n{new_fm}---\n{new_body}"
    out = new_text.encode("utf-8")
    if bom:
        out = b"\xef\xbb\xbf" + out
    path_on_disk.write_bytes(out)
    print(f"OK: {name}")


def main():
    for name, info in IMAGES.items():
        if not (POSTS_DIR / name).exists():
            print(f"MISSING FILE: {name}")
            continue
        process_file(name, info)


if __name__ == "__main__":
    main()
