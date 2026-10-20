#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USER = "changhexuefei"

def fetch(url):
    headers = {"User-Agent": "changhexuefei.github.io activity updater", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    since = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
    repos = fetch(f"https://api.github.com/users/{USER}/repos?{urlencode({'sort':'updated','per_page':100})}")
    repos = [repo for repo in repos if not repo.get("archived")][:12]
    commits = []
    for repo in repos[:8]:
        try:
            query = urlencode({"author": USER, "since": since, "per_page": 100})
            commits.extend(fetch(f"https://api.github.com/repos/{USER}/{repo['name']}/commits?{query}"))
        except Exception as error:
            print(f"skip {repo.get('name')}: {error}")
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "repos": repos[:6],
        "commits": commits,
    }
    output = Path("data/recent-activity.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(payload['repos'])} repos and {len(commits)} commits")

if __name__ == "__main__":
    main()
