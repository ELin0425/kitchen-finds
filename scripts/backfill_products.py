#!/usr/bin/env python3
"""
One-off backfill: adds a `products:` frontmatter list (name + amazon URL) to
existing roundup posts in _posts/, so head-custom.html's ItemList JSON-LD
(see Phase K1) has something to render on posts written before the content
generators started emitting `products:` themselves.

How it works:
  1. Split each post into frontmatter + body.
  2. Split the body into sections at every H2 (##) or H3 (###) heading.
  3. Skip sections that are clearly not a single-product pick: FAQ questions
     (heading ends in "?"), and headings matching a denylist of generic
     "why/how we/key features/etc" section titles.
  4. Within a surviving section, find the first Amazon link (markdown
     `[text](url)` or inline `<a href="url">text</a>`).
  5. Product name = the link's anchor text, unless that text is a generic
     CTA phrase ("Check price on Amazon" etc) in which case fall back to
     the section heading text (numbering stripped).
  6. Skip posts that end up with zero product sections (how-to posts).
  7. Insert the resulting `products:` list into the frontmatter block
     in-place (no reformatting of the rest of the frontmatter).

Run from repo root: python scripts/backfill_products.py [--dry-run]
"""
import re
import sys
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parent.parent / "_posts"

# H2 heading text (lowercased) containing any of these substrings is not a
# product-roundup section (it's intro/criteria/FAQ/meta) and is excluded
# both from "is this the roundup H2" matching and from per-H2 fallback mode.
H2_DENYLIST = [
    "faq", "related articles", "why ", "what to look for", "what to skip",
    "how we", "our testing", "key features", "should you buy",
    "comparison table", "quick picks", "bottom line", "testing methodology",
    "how to use this guide", "different types of", "outperform",
    "makes a difference", "what makes", "mistakes that", "types explained",
]

# H2 heading regex that indicates "this is the ranked product roundup section".
ROUNDUP_H2 = re.compile(r"^(top|best|our top|the best)\b", re.I)

# Anchor text that's a generic call-to-action, not a real product name.
GENERIC_CTA = ["check price", "amazon", "buy now", "view price", "see price"]

MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]*amazon\.com[^)]*)\)")
HTML_LINK = re.compile(
    r'<a\s+href="(https?://[^"]*amazon\.com[^"]*)"[^>]*>([^<]+)</a>'
)


def clean_heading(text):
    """Strip leading numbering like '1. ', '#1: ', 'Product #3: '."""
    text = re.sub(r"^(product\s*)?#?\d+[.:)]\s*", "", text, flags=re.I)
    return text.strip().strip(":").strip()


def first_amazon_link(section_body):
    """Return (anchor_text, url) for the first Amazon link in this section, or None."""
    md = MD_LINK.search(section_body)
    html = HTML_LINK.search(section_body)
    # Pick whichever match comes first in the text.
    candidates = []
    if md:
        candidates.append((md.start(), md.group(1), md.group(2)))
    if html:
        candidates.append((html.start(), html.group(2), html.group(1)))
    if not candidates:
        return None
    candidates.sort(key=lambda c: c[0])
    _, text, url = candidates[0]
    return text.strip(), url.strip()


def is_denied_h2(heading_text):
    h = heading_text.lower().rstrip()
    if h.endswith("?"):
        return True
    return any(term in h for term in H2_DENYLIST)


def name_from_section(heading_text, anchor_text):
    if any(cta in anchor_text.lower() for cta in GENERIC_CTA):
        return clean_heading(heading_text)
    return anchor_text


def split_headings(text, levels):
    """Split text on H2/H3 (## or ###) headings. Returns list of
    (level, heading_text, section_body) in reading order. `levels` is a
    regex char class, e.g. '2' for H2-only or '2,3' for H2 and H3."""
    parts = re.split(rf"(?m)^(#{{{levels}}} .+)$", text)
    sections = []
    for i in range(1, len(parts), 2):
        heading_line = parts[i]
        section_body = parts[i + 1] if i + 1 < len(parts) else ""
        level = len(heading_line) - len(heading_line.lstrip("#"))
        heading_text = heading_line.lstrip("#").strip()
        sections.append((level, heading_text, section_body))
    return sections


def items_from_h2_body(h2_body):
    """Extract [(name, url), ...] from a single H2 section's body. If it has
    child H3s, one item per H3 (the common case: each H3 is one product
    pick). Otherwise, walk the H2 body directly and pull out every distinct
    Amazon link in order (covers posts that skip H3 headings entirely and
    put one product per H2 paragraph)."""
    items = []
    h3_sections = split_headings(h2_body, "3")
    if h3_sections:
        for _, heading_text, section_body in h3_sections:
            link = first_amazon_link(section_body)
            if not link:
                continue
            anchor_text, url = link
            items.append((name_from_section(heading_text, anchor_text), url))
        return items

    remaining = h2_body
    while True:
        link = first_amazon_link(remaining)
        if not link:
            break
        anchor_text, url = link
        items.append((anchor_text, url))
        idx = remaining.find(url)
        remaining = remaining[idx + len(url):]
    return items


def extract_products(body):
    """Find the product picks in a post body, return [(name, url), ...] in
    reading order. Strategy:
      1. Split on H2 sections. Find the one that looks like the ranked
         product roundup (heading starts with Top/Best/Our Top, isn't a
         denylisted meta section).
      2. Pull products out of that H2 (per-child-H3, or per-link if no H3s).
      3. If no H2 matches the roundup pattern, fall back to pulling products
         out of every non-denylisted top-level H2 the same way (covers posts
         that never use a single dedicated "Top X" section but instead one
         product per topical H2 category, each with its own H3 sub-picks or
         none at all).
    """
    seen_urls = set()
    products = []

    def add(name, url):
        if url in seen_urls or not name:
            return
        products.append((name, url))
        seen_urls.add(url)

    h2_sections = split_headings(body, "2")

    roundup_body = None
    for _, heading_text, section_body in h2_sections:
        if is_denied_h2(heading_text):
            continue
        if ROUNDUP_H2.match(heading_text.strip()):
            roundup_body = section_body
            break

    if roundup_body is not None:
        for name, url in items_from_h2_body(roundup_body):
            add(name, url)
        return products

    # Fallback: pull products from every non-denylisted top-level H2.
    for _, heading_text, section_body in h2_sections:
        if is_denied_h2(heading_text):
            continue
        for name, url in items_from_h2_body(section_body):
            add(name, url)

    return products


def split_frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None, None, text
    fm = m.group(1)
    body = text[m.end():]
    return fm, body, None


def yaml_escape(s):
    """Double-quoted YAML scalar escaping, good enough for these plain-text names/urls."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_products_block(products):
    lines = ["products:"]
    for name, url in products:
        lines.append(f"  - name: {yaml_escape(name)}")
        lines.append(f"    url: {yaml_escape(url)}")
    return "\n".join(lines) + "\n"


def process_file(path, dry_run):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    fm, body, _ = split_frontmatter(text)
    if fm is None:
        print(f"SKIP (no frontmatter): {path.name}")
        return

    if re.search(r"(?m)^products:", fm):
        print(f"SKIP (already has products:): {path.name}")
        return

    products = extract_products(body)
    if not products:
        print(f"SKIP (no product sections found): {path.name}")
        return

    print(f"{path.name}: {len(products)} products")
    for name, url in products:
        print(f"    - {name}  ->  {url}")

    if dry_run:
        return

    new_fm = fm.rstrip("\n") + "\n" + build_products_block(products)
    new_text = f"---\n{new_fm}---\n" + body
    out = new_text.encode("utf-8")
    if bom:
        out = b"\xef\xbb\xbf" + out
    path.write_bytes(out)


def main():
    dry_run = "--dry-run" in sys.argv
    for path in sorted(POSTS_DIR.glob("*.md")):
        process_file(path, dry_run)


if __name__ == "__main__":
    main()
