#!/usr/bin/env python3
import os
import re
import json
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URLS = {
    "ScienceMissions": {
        "listing_url": "https://science.nasa.gov/science-missions/",
        "link_class":  "hds-content-item-heading",
    },
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

def extract_image_src(soup):
    """
    Extracts the image URL from a page, if available.
    Returns an empty string if not found.
    """
    # Case 1: inside <div class="hds-media-inner"> → <figure> → <img>
    img1 = soup.select_one("div.hds-media-inner figure img")
    if img1 and img1.get("src"):
        return img1["src"]

    # Case 2: inside <figure class="hds-media-inner hds-cover-wrapper hds-media-ratio-cover"> → <a> → <img>
    a = soup.select_one("figure.hds-media-inner.hds-cover-wrapper.hds-media-ratio-cover a")
    if a and a.get("href"):
        return a.get("href")
    
    # Case 3: inside <figure class="hds-media-inner hds-cover-wrapper hds-media-ratio-fit"> → <a>
    a = soup.select_one("figure.hds-media-inner.hds-cover-wrapper.hds-media-ratio-fit a")
    if a and a.get("href"):
        return a.get("href")

    # Case 4: no image
    return ""

def scrape_mission(mission_key, info):
    listing_url = info["listing_url"]
    link_class  = info["link_class"]
    print(f"\nScraping {mission_key} → {listing_url}")

    resp = requests.get(listing_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # matching using css selectors
    links = soup.select(f"a.{link_class}")
    if not links:
        print("  ⚠️  No links found with class", link_class)
        return

    os.makedirs("raw_reports", exist_ok=True)
    results = []
    for a in links:
        title_div = a.find("div", class_="hds-a11y-heading-22")
        title = title_div.text.strip() 
        href = a.get("href")
        if not href:
            continue
        
        # if raw_date:
        #     for fmt in ("%B %d, %Y", "%b %d, %Y"):
        #         try:
        #             dt = datetime.strptime(raw_date, fmt)
        #             iso_date = dt.strftime("%Y-%m-%d")
        #             break
        #         except ValueError:
        #             continue

        page = requests.get(href)
        page.raise_for_status()
        soup2 = BeautifulSoup(page.text, "html.parser")
        
        fields_to_extract = ['type', 'launch', 'target', 'objective', 'launched', 'Decommissioned', 'wavelength']
        result = {}
        # for p in soup2.find_all('p', class_='label margin-0 color-carbon-50-important'):
        #     key = p.get_text(strip=True).lower()
        #     print(key)
        #     # outer_div = p.find_parent().find_next_sibling()
        #     # if outer_div:
        #     #     value = outer_div.get_text(strip=True)
        #     #     data[key] = value

        data = {}
        label_divs = soup2.find_all('p', class_='label margin-0 color-carbon-50-important')
        value_divs =  soup2.find_all('div', class_="p-lg font-weight-bold margin-0 padding-0 line-height-sm")
        name = soup2.find('h1', class_="page-heading-md display-block width-full")
        name_text = name.get_text(strip=True)
        image_link = extract_image_src(soup2)
        
        for i, p in enumerate(label_divs):
            label = p.get_text(strip=True).lower()
            if label in fields_to_extract:
                if value_divs[i]:
                    data[label.lower()] = value_divs[i].get_text(strip=True)
         
        if name_text:
            data["mission_name"] = name_text 
       
        data["graphic"] =  image_link
        data["weblink"] = href          
                    
        results.append(data)
        safe_title= re.sub(r'[\\/*?:"<>|]', "_", title)
        filename = f"{safe_title}.html"
        # path = os.path.join("raw_reports", filename)
        # with open(path, "w", encoding="utf-8") as f:
        #     f.write(page.text)
        # print("  ✔ Saved", filename)
        json_filename = f"missions.json"
        json_path = os.path.join("raw_reports", json_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"  ✔ Saved JSON: {json_path}")
        
    print(results)


if __name__ == "__main__":
    # for key, info in BASE_URLS.items():
    #     scrape_mission(key, info)
    scrape_mission("ScienceMissions", {
        "listing_url": "https://science.nasa.gov/science-missions/",
        "link_class":  "hds-content-item-heading",
    })
