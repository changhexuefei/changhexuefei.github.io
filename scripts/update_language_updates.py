#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

SOURCES = [
    {"key": "kotlin", "name": "Kotlin", "repo": "JetBrains/kotlin", "kind": "release", "home": "https://kotlinlang.org/", "url": "https://github.com/JetBrains/kotlin/releases"},
    {"key": "java", "name": "Java", "repo": "openjdk/jdk", "kind": "tag", "home": "https://openjdk.org/", "url": "https://github.com/openjdk/jdk/tags"},
    {"key": "python", "name": "Python", "repo": "python/cpython", "kind": "tag", "home": "https://www.python.org/", "url": "https://github.com/python/cpython/tags"},
]

def fetch(url):
    headers = {"User-Agent": "changhexuefei.github.io language updater", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    items = []
    for source in SOURCES:
        try:
            endpoint = f"https://api.github.com/repos/{source['repo']}/releases?per_page=8" if source["kind"] == "release" else f"https://api.github.com/repos/{source['repo']}/tags?per_page=8"
            payload = fetch(endpoint)
            if source["kind"] == "release":
                item = next((entry for entry in payload if not entry.get("draft")), payload[0] if payload else None)
                if not item:
                    raise RuntimeError("no release")
                version = item.get("tag_name") or item.get("name") or "latest"
                title = item.get("name") or version
                summary = (item.get("body") or f"{source['name']} 官方发布已更新。").replace("\n", " ").strip()[:220]
                date = item.get("published_at") or item.get("created_at")
                link = item.get("html_url") or source["url"]
            else:
                item = payload[0] if payload else None
                if not item:
                    raise RuntimeError("no tag")
                version = item.get("name") or "latest"
                title = ("OpenJDK " if source["key"] == "java" else "CPython ") + version
                summary = "官方版本标签已更新，点击查看最新代码与版本信息。"
                date = None
                link = source["url"]
            items.append({"key": source["key"], "name": source["name"], "version": version, "title": title, "summary": summary, "date": date, "url": link, "home": source["home"]})
        except Exception as error:
            print(f"skip {source['name']}: {error}")
    output = Path("data/language-updates.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"updated_at": datetime.now(timezone.utc).isoformat(), "items": items}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(items)} language updates")

if __name__ == "__main__":
    main()
