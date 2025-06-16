#!/usr/bin/env python3
import os
import re
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URLS = {
    "Mars2020": {
        "listing_url": "https://mars.nasa.gov/mars2020/mission/status/",
        "link_class":  "hds-content-item-heading",
    },
    "InSight": {
        "listing_url": "https://mars.nasa.gov/insight/mission/status/",
        "link_class":  "hds-content-item-heading",
    },
    "MAVEN": {
        "listing_url": "https://mars.nasa.gov/maven/mission/status/",
        "link_class":  "hds-content-item-heading",
    },
}

# regex to match "Jun 06, 2025" or "June 6, 2025" (case‐insensitive)
DATE_REGEX = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
    r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b",
    re.IGNORECASE,
)


def extract_date_from_listing(a_tag):
    """Try to pull 'Month DD, YYYY' out of the link text or title."""
    text = a_tag.get_text(" ", strip=True)
    m = DATE_REGEX.search(text)
    if m:
        return m.group(0)

    title = a_tag.get("title", "")
    m = DATE_REGEX.search(title)
    if m:
        return m.group(0)

    return None


def extract_date_from_article(url):
    """Fetch the article page and extract its date (ISO YYYY-MM-DD)."""
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # 1) <time datetime="2025-06-06T12:00:00Z">
    t = soup.find("time", datetime=True)
    if t and t.has_attr("datetime"):
        return t["datetime"][:10]

    # 2) <meta property="article:published_time" content="2025-06-06T...">
    m = soup.find("meta", {"property": "article:published_time"})
    if m and m.has_attr("content"):
        return m["content"][:10]

    # 3) The DIV→SPAN pattern: <div class="article-meta-item">…<span class="heading-12 text-uppercase">Jun 06, 2025</span>
    span = soup.select_one("div.article-meta-item span.heading-12")
    if span:
        txt = span.get_text(strip=True)
        for fmt in ("%b %d, %Y", "%B %d, %Y"):
            try:
                dt = datetime.strptime(txt, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

    # # 4) Last resort: regex‐scan the full text
    # full_text = soup.get_text(" ", strip=True)
    # m2 = DATE_REGEX.search(full_text)
    # if m2:
    #     raw = m2.group(0)
    #     for fmt in ("%b %d, %Y", "%B %d, %Y"):
    #         try:
    #             dt = datetime.strptime(raw, fmt)
    #             return dt.strftime("%Y-%m-%d")
    #         except ValueError:
    #             pass

    return None


def scrape_mission(mission_key, info):
    listing_url = info["listing_url"]
    link_class  = info["link_class"]
    print(f"\nScraping {mission_key} → {listing_url}")

    resp = requests.get(listing_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # find all <a class="hds-content-item-heading">…
    links = soup.select(f"a.{link_class}")
    if not links:
        print("  ⚠️  No links found with class", link_class)
        return

    os.makedirs("raw_reports", exist_ok=True)

    for a in links:
        href = a.get("href")
        if not href:
            continue

        # 1) try extracting date from the listing element
        raw_date = extract_date_from_listing(a)
        iso_date = None
        if raw_date:
            for fmt in ("%B %d, %Y", "%b %d, %Y"):
                try:
                    dt = datetime.strptime(raw_date, fmt)
                    iso_date = dt.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue

        # 2) if that failed, fetch the article itself
        if not iso_date:
            iso_date = extract_date_from_article(href)

        if not iso_date:
            print("  ⚠️  Skipping (no date found):", href)
            continue

        # 3) fetch & save
        page = requests.get(href)
        page.raise_for_status()
        filename = f"{mission_key}_{iso_date}.html"
        path = os.path.join("raw_reports", filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(page.text)
        print("  ✔ Saved", filename)


if __name__ == "__main__":
    for key, info in BASE_URLS.items():
        scrape_mission(key, info)
