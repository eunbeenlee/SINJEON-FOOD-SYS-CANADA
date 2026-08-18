import json
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path
import re

RSS_URL = "https://rss.app/feeds/QiquOv60dsl7EOm8.xml"
OUTPUT_FILE = Path("instagram-feed.json")

NS = {
    "media": "http://search.yahoo.com/mrss/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/"
}


def clean_html(text):
    if not text:
        return ""

    text = unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def get_text(parent, tag):
    element = parent.find(tag)
    if element is not None and element.text:
        return element.text.strip()
    return ""


def get_media_url(item):
    media_content = item.find("media:content", NS)

    if media_content is not None:
        url = media_content.attrib.get("url")
        if url:
            return url

    media_thumbnail = item.find("media:thumbnail", NS)

    if media_thumbnail is not None:
        url = media_thumbnail.attrib.get("url")
        if url:
            return url

    description = get_text(item, "description")

    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', description or "")

    if match:
        return match.group(1)

    return ""


def main():
    print("Fetching Instagram RSS...")

    request = urllib.request.Request(
        RSS_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)

    posts = []

    for item in root.findall("./channel/item"):
        title = clean_html(get_text(item, "title"))
        permalink = get_text(item, "link")
        pub_date = get_text(item, "pubDate")
        image_url = get_media_url(item)

        if not permalink:
            continue

        posts.append({
            "media_type": "IMAGE",
            "media_url": image_url,
            "thumbnail_url": image_url,
            "permalink": permalink,
            "caption": title,
            "timestamp": pub_date
        })

    posts = posts[:6]

    output = {
        "data": posts
    }

    OUTPUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Updated {OUTPUT_FILE}")
    print(f"Posts: {len(posts)}")


if __name__ == "__main__":
    main()
