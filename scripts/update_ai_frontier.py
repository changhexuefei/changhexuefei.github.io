#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

FEEDS = [
    ("Google DeepMind", "https://deepmind.google/blog/rss.xml", "https://deepmind.google/blog/"),
    ("NVIDIA AI", "https://developer.nvidia.com/blog/feed/", "https://developer.nvidia.com/blog/"),
    ("OpenAI", "https://openai.com/news/rss.xml", "https://openai.com/news/"),
    ("Stanford HAI · Fei-Fei Li", "https://hai.stanford.edu/news/rss.xml", "https://hai.stanford.edu/news/"),
]
WORLD_LABS = ("World Labs · Fei-Fei Li", "https://www.worldlabs.ai/blog", "https://www.worldlabs.ai/blog")
TOPIC = re.compile(r"world model|world models|spatial intelligence|physical ai|robotics|agent|foundation model|multimodal|reasoning|generative|3d world|computer vision|fei[- ]fei li", re.I)
CHINA = re.compile(r"\b(qwen|deepseek|kimi|doubao|zhipu|moonshot|baidu|alibaba)\b", re.I)
TAG = re.compile(r"<[^>]+>")
SPACE = re.compile(r"\s+")

def clean(value):
    return SPACE.sub(" ", TAG.sub(" ", value or "")).strip()

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
        body = clean(f"{title} {summary}")
        if title and TOPIC.search(body) and not CHINA.search(body):
            result.append({"title": title, "summary": clean(summary)[:220], "url": link or home, "date": date, "source": source, "home": home})
    return result

class WorldLabsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items, self.href, self.parts = [], "", []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            self.href = attrs.get("href", "")
            self.parts = []
    def handle_data(self, data):
        if self.href:
            self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.href:
            title = clean(" ".join(self.parts))
            title = re.sub(r"\\s*Read More.*$", "", title, flags=re.I).strip()
            title = re.sub(r"^(January|February|March|April|May|June|July|August|September|October|November|December) \\d{1,2}, \\d{4}\\s+", "", title)
            body = title
            if title and len(title) > 12 and TOPIC.search(body):
                url = self.href if self.href.startswith("http") else "https://www.worldlabs.ai" + self.href
                self.items.append({"title": title, "summary": "World Labs 官方研究与产品动态，聚焦空间智能和可交互世界模型。", "url": url, "date": "", "source": WORLD_LABS[0], "home": WORLD_LABS[2]})
            self.href, self.parts = "", []

def fetch(url):
    request = Request(url, headers={"User-Agent": "changhexuefei.github.io AI frontier updater"})
    with urlopen(request, timeout=25) as response:
        return response.read()

def date_key(value):
    try:
        return parsedate_to_datetime(value).timestamp()
    except Exception:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0

def main():
    items, featured = [], None
    for source, url, home in FEEDS:
        try:
            items.extend(parse_feed(fetch(url), source, home))
        except Exception as error:
            print(f"skip {source}: {error}")
    try:
        parser = WorldLabsParser()
        parser.feed(fetch(WORLD_LABS[1]).decode("utf-8", "ignore"))
        featured = parser.items[0] if parser.items else None
        items.extend(parser.items)
    except Exception as error:
        print(f"skip {WORLD_LABS[0]}: {error}")
    unique = {}
    for item in sorted(items, key=lambda row: date_key(row["date"]), reverse=True):
        unique.setdefault(item["title"], item)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "featured": featured,
        "items": list(unique.values())[:8],
        "sources": [{"name": source, "url": url, "home": home} for source, url, home in FEEDS] + [{"name": WORLD_LABS[0], "url": WORLD_LABS[1], "home": WORLD_LABS[2]}],
    }
    output = Path("data/ai-frontier.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(payload['items'])} AI updates; featured={bool(featured)}")

if __name__ == "__main__":
    main()
