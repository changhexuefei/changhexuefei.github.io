#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

FEEDS = [
    ("Google DeepMind", "https://deepmind.google/blog/rss.xml", "https://deepmind.google/blog/"),
    ("NVIDIA AI", "https://developer.nvidia.com/blog/feed/", "https://developer.nvidia.com/blog/"),
    ("OpenAI", "https://openai.com/news/rss.xml", "https://openai.com/news/"),
]
TOPIC = re.compile(r"world model|world models|physical ai|robotics|agent|foundation model|multimodal|reasoning|generative", re.I)
CHINA = re.compile(r"\b(qwen|deepseek|kimi|doubao|zhipu|moonshot|baidu|alibaba)\b", re.I)
TAG = re.compile(r"<[^>]+>")
SPACE = re.compile(r"\s+")

def text(node, names):
    for name in names:
        child = node.find(name)
        if child is not None and child.text:
            return child.text.strip()
    return ""

def parse_feed(xml, source, home):
    root = ET.fromstring(xml)
    entries = list(root.findall(".//item")) + list(root.findall(".//{*}entry"))
    result = []
    for entry in entries:
        title = text(entry, ["title", "{*}title"])
        summary = text(entry, ["description", "summary", "content", "{*}description", "{*}summary", "{*}content"])
        link = text(entry, ["link", "{*}link"])
        link_node = entry.find("{*}link")
        if link_node is not None:
            link = link_node.attrib.get("href") or link
        date = text(entry, ["pubDate", "published", "updated", "{*}pubDate", "{*}published", "{*}updated"])
        body = SPACE.sub(" ", TAG.sub(" ", f"{title} {summary}")).strip()
        if title and TOPIC.search(body) and not CHINA.search(body):
            result.append({
                "title": title,
                "summary": SPACE.sub(" ", TAG.sub(" ", summary)).strip()[:220],
                "url": link or home,
                "date": date,
                "source": source,
                "home": home,
            })
    return result

def date_key(value):
    try:
        return parsedate_to_datetime(value).timestamp()
    except Exception:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0

def main():
    items = []
    for source, url, home in FEEDS:
        try:
            request = Request(url, headers={"User-Agent": "changhexuefei.github.io AI frontier updater"})
            with urlopen(request, timeout=25) as response:
                items.extend(parse_feed(response.read(), source, home))
        except Exception as error:
            print(f"skip {source}: {error}")
    unique = {}
    for item in sorted(items, key=lambda row: date_key(row["date"]), reverse=True):
        unique.setdefault(item["title"], item)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": list(unique.values())[:6],
        "sources": [{"name": source, "url": url, "home": home} for source, url, home in FEEDS],
    }
    output = Path("data/ai-frontier.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(payload['items'])} AI updates")

if __name__ == "__main__":
    main()
