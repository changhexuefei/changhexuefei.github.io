import datetime as dt, json, os, pathlib, urllib.request
from zoneinfo import ZoneInfo

USER = "changhexuefei"
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "articles"
OUT.mkdir(exist_ok=True)
today = dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo("Asia/Shanghai")).date()
end = today - dt.timedelta(days=today.weekday())
start = end - dt.timedelta(days=7)
date = end - dt.timedelta(days=1)
filename = f"{date.isoformat()}.md"

def get(url):
    req = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json", "User-Agent":"weekly-article"})
    with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)

events = []
try:
    for page in range(1, 4):
        batch = get(f"https://api.github.com/users/{USER}/events/public?per_page=100&page={page}")
        events += [e for e in batch if start.isoformat() <= e.get("created_at", "")[:10] < end.isoformat()]
        if len(batch) < 100: break
except Exception as exc:
    print(f"GitHub API unavailable: {exc}")

pushes = []
for event in events:
    if event.get("type") == "PushEvent" and event.get("actor", {}).get("login", "").lower() == USER.lower():
        repo = event.get("repo", {}).get("name", "")
        commits = event.get("payload", {}).get("commits", [])
        if repo: pushes.append((repo, commits, event.get("created_at", "")[:10]))

if pushes:
    grouped = {}
    for repo, commits, day in pushes: grouped.setdefault(repo, []).extend(commits)
    title_repo = max(grouped, key=lambda k: len(grouped[k]))
    title = f"这一周，我在 {title_repo.split('/')[-1]} 上推进了什么"
    summary = f"整理 {start} 至 {date} 的公开提交，重点回顾 {len(grouped)} 个仓库中的实际改动。"
    body = [f"# {title}", "", f"> {summary}", "", f"统计周期：{start} 至 {date}（Asia/Shanghai）", "", "## 本周发生了什么", ""]
    body.append(f"这一周在公开活动中检索到 {sum(len(v) for v in grouped.values())} 次本人提交，涉及 {len(grouped)} 个仓库。以下内容只使用 GitHub 公共 PushEvent 中作者为 `{USER}` 的记录。")
    body += ["", "## 项目进展", ""]
    for repo, commits in sorted(grouped.items(), key=lambda kv: -len(kv[1])):
        body.append(f"### [{repo.split('/')[-1]}](https://github.com/{repo})")
        body.append(f"共 {len(commits)} 条公开提交。主要改动记录：")
        for commit in commits[:8]:
            message = commit.get("message", "").splitlines()[0]
            sha = commit.get("sha", "")[:7]
            body.append(f"- [{sha}](https://github.com/{repo}/commit/{commit.get('sha','')})：{message}")
        body.append("")
    body += ["## 这次记录留下的线索", "", "从提交信息可以确认项目在持续迭代；更具体的性能、耗时或使用效果，需要后续补充可验证数据后再下结论。", "", "## 资料范围", "", f"- GitHub 公开事件：{start} 00:00 至 {end} 00:00（UTC API 时间按日期归档）", f"- 作者：[{USER}](https://github.com/{USER})"]
else:
    title = f"这一周的 GitHub 记录：{start} — {date}"
    summary = "本周没有检索到可归属于本人的公开提交活动。"
    body = [f"# {title}", "", f"> {summary}", "", f"统计周期：{start} 至 {date}（Asia/Shanghai）", "", "## 说明", "", "本篇文章没有把 Fork 历史或其他作者的提交当作个人产出。若 GitHub 公开事件接口暂时不完整，下一次运行会重新尝试。", "", "## 资料范围", "", f"- GitHub 公开事件：{start} 00:00 至 {end} 00:00", f"- 作者：[{USER}](https://github.com/{USER})"]

markdown = "\n".join(body) + "\n"
(OUT / filename).write_text(markdown, encoding="utf-8")
import html, re
lines = []
for line in markdown.splitlines():
    safe = html.escape(line)
    if line.startswith("# "): lines.append(f"<h1>{html.escape(line[2:])}</h1>")
    elif line.startswith("## "): lines.append(f"<h2>{html.escape(line[3:])}</h2>")
    elif line.startswith("### "): lines.append(f"<h3>{html.escape(line[4:])}</h3>")
    elif line.startswith("> "): lines.append(f"<blockquote>{html.escape(line[2:])}</blockquote>")
    elif line.startswith("- "): lines.append(f"<li>{html.escape(line[2:])}</li>")
    elif line.strip(): lines.append(f"<p>{safe}</p>")
(OUT / (pathlib.Path(filename).stem + ".html")).write_text("<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width'><link rel='stylesheet' href='../style.css'><main class='article-page'>" + "\n".join(lines) + "</main>", encoding="utf-8")
index = []
for path in sorted(OUT.glob("*.md"), reverse=True):
    text = path.read_text(encoding="utf-8")
    heading = next((line[2:] for line in text.splitlines() if line.startswith("# ")), path.stem)
    quote = next((line[2:] for line in text.splitlines() if line.startswith("> ")), "GitHub 动态文章")
    index.append({"date": path.stem, "period": "WEEKLY", "title": heading, "summary": quote, "tags": ["GitHub", "工程记录"], "url": path.with_suffix('.html').name})
(OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
