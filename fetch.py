#!/usr/bin/env python3
"""Generate RSS feeds for 哥飞 SEO sources that have no native feed.

Sources:
  web.cafe /all      -> feeds/webcafe-all.xml   (tutorials + topics, latest)
  web.cafe /topics   -> feeds/webcafe-topics.xml (community posts)
  web.cafe /tutorials-> feeds/webcafe-tutorials.xml (column index, newest articles)

Runs on pure HTTP (no browser): the pages carry SSR HTML.
State (seen ids) is kept in state.json so each run only appends new items.
"""
from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
FEEDS = ROOT / "feeds"
STATE = ROOT / "state.json"
BASE = "https://new.web.cafe"
UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
}
MAX_ITEMS = 120


def get(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def parse_items(page: str, prefix: str, exclude: str = "") -> list[dict]:
    """Parse one listing page. prefix: /tutorial/detail | /topic | /tutorial."""
    ex = f"(?!{re.escape(exclude)}/)" if exclude else ""
    pat = re.compile(
        rf'<a href="({re.escape(prefix)}/{ex}[a-z0-9]{{6,}})"[^>]*>(.*?)</a>', re.S
    )
    items = []
    for m in pat.finditer(page):
        path, inner = m.group(1), m.group(2)
        title = clean(inner)
        title = re.sub(r"^#\s*", "", title)
        title = re.sub(r"\s*\d+\s*篇$", "", title)
        if len(title) < 4:
            continue
        tail = page[m.end(): m.end() + 1400]
        am = re.search(rf'<a href="{re.escape(prefix).rsplit("/",1)[0]}/u/[a-z0-9]+"[^>]*>([^<]+)</a>', tail)
        if not am:
            am = re.search(r'<a href="/u/[a-z0-9]+"[^>]*>([^<]+)</a>', tail)
        author = html.unescape(am.group(1)).strip() if am else ""
        tm = re.search(r'<time[^>]*dateTime="([^"]+)"', tail)
        if tm:
            date = tm.group(1)
        else:
            dm = re.search(r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2})", tail)
            date = dm.group(1) if dm else ""
        items.append(
            {
                "id": path,
                "link": BASE + path,
                "title": title,
                "author": author,
                "date": date,
            }
        )
    # de-dup by id, keep page order (newest first)
    seen, out = set(), []
    for it in items:
        if it["id"] in seen:
            continue
        seen.add(it["id"])
        out.append(it)
    return out


def to_date(raw: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def build_rss(name: str, title: str, link: str, desc: str, items: list[dict]) -> str:
    now = format_datetime(datetime.now(timezone.utc))
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        f"<title>{escape(title)}</title>",
        f"<link>{escape(link)}</link>",
        f"<description>{escape(desc)}</description>",
        "<language>zh-CN</language>",
        f"<lastBuildDate>{now}</lastBuildDate>",
        f'<atom:link href="{escape(link)}" rel="self" type="application/rss+xml"/>',
    ]
    for it in items[:MAX_ITEMS]:
        pub = format_datetime(to_date(it.get("date", "")) if it.get("date") else datetime.now(timezone.utc))
        author = it.get("author") or ""
        parts += [
            "<item>",
            f"<title>{escape(it['title'])}</title>",
            f"<link>{escape(it['link'])}</link>",
            f"<guid isPermaLink=\"true\">{escape(it['link'])}</guid>",
            f"<pubDate>{pub}</pubDate>",
            f"<description>{escape((author + '：' if author else '') + it['title'])}</description>" if author else f"<description>{escape(it['title'])}</description>",
        ]
        if author:
            parts.append(f"<dc:creator xmlns:dc=\"http://purl.org/dc/elements/1.1/\">{escape(author)}</dc:creator>")
        parts.append("</item>")
    parts += ["</channel>", "</rss>"]
    return "\n".join(parts)


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def main() -> int:
    FEEDS.mkdir(parents=True, exist_ok=True)
    state = load_state()
    jobs = [
        ("webcafe-all", "/all", "/tutorial/detail", "Web.Cafe 最新教程", "哥飞社群最新教程（教程流）"),
        ("webcafe-topics", "/topics", "/topic", "Web.Cafe 社群帖子", "哥飞朋友们社群最新讨论与复盘"),
        ("webcafe-columns", "/tutorials", "/tutorial", "Web.Cafe 教程专栏", "哥飞社群教程专栏最新文章"),
    ]
    ok = 0
    for slug, path, kind, title, desc in jobs:
        try:
            page = get(BASE + path)
            fresh = parse_items(page, kind, exclude="detail" if kind == "/tutorial" else "")
            kept = state.get(slug, [])
            by_id = {i["id"]: i for i in kept}
            added = 0
            for it in fresh:
                if it["id"] not in by_id:
                    added += 1
                by_id[it["id"]] = it
            merged = list(by_id.values())[:MAX_ITEMS]
            state[slug] = merged
            xml = build_rss(slug, title, f"https://hello532.github.io/seo-rss/feeds/{slug}.xml", desc, merged)
            (FEEDS / f"{slug}.xml").write_text(xml, encoding="utf-8")
            print(f"{slug}: {len(fresh)} on page, +{added} new, {len(merged)} total")
            ok += 1
        except Exception as e:  # noqa: BLE001
            print(f"{slug}: FAILED {type(e).__name__}: {e}", file=sys.stderr)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
