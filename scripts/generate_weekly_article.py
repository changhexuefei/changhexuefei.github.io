import datetime as dt
import html
import json
import pathlib
import urllib.request
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
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "weekly-article"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)

events = []
try:
    for page in range(1, 4):
        batch = get(f"https://api.github.com/users/{USER}/events/public?per_page=100&page={page}")
        events += [event for event in batch if start.isoformat() <= event.get("created_at", "")[:10] < end.isoformat()]
        if len(batch) < 100:
            break
except Exception as exc:
    print(f"GitHub API unavailable: {exc}")

pushes = []
for event in events:
    if event.get("type") != "PushEvent" or event.get("actor", {}).get("login", "").lower() != USER.lower():
        continue
    repo = event.get("repo", {}).get("name", "")
    commits = event.get("payload", {}).get("commits", [])
    if repo and commits:
        pushes.append((repo, commits))

grouped = {}
for repo, commits in pushes:
    grouped.setdefault(repo, []).extend(commits)

if grouped:
    main_repo = max(grouped, key=lambda name: len(grouped[name]))
    project_names = ", ".join(name.split("/")[-1] for name in grouped)
    title = f"这一周的技术感想：把 {main_repo.split('/')[-1]} 做得更清楚"
    body = [
        f"# {title}", "",
        "> 提交只是线索，真正值得留下的是做决定时的理由。", "",
        f"感想周期：{start} 至 {date}（Asia/Shanghai）", "",
        "## 这周我在想什么", "",
        f"这周主要围绕 {project_names} 做了一轮迭代。表面上是视觉、数据和内容模块的调整，实际一直在处理同一个问题：怎样让一个会持续变化的个人网站，仍然保持清楚、可靠，而且有自己的表达。", "",
        "我越来越倾向于先把信息结构和失败状态想明白，再去补动画和装饰。这样做的好处是，即使接口暂时不可用，页面也不会失去叙事；即使动画被关闭，内容仍然可以被读懂。", "",
        "## 一个具体的技术判断", "",
        "这次最有价值的判断，是把动态能力拆成互相独立的层。GitHub 数据负责事实，文章负责解释，视觉效果负责建立节奏。它们可以分别失败、分别降级，也可以分别迭代。对个人项目来说，这比一次性追求复杂架构更容易维护。", "",
        "## 我会继续验证什么", "",
        "接下来我会观察两件事：第一，自动生成的文章是否真的提供了提交记录之外的理解；第二，首页的动态效果是否帮助用户找到重点，而不是抢走注意力。如果答案是否定的，就应该继续删减，而不是继续堆功能。", "",
        "## 资料范围", "",
        f"本文根据 GitHub 公开活动整理，涉及 {len(grouped)} 个仓库、{sum(len(items) for items in grouped.values())} 次本人提交。提交内容只用于确认本周的工作主题，不在文章中逐条罗列。"
    ]
else:
    title = f"这一周的技术感想：{start} — {date}"
    body = [
        f"# {title}", "",
        "> 没有新的公开提交，也可以记录一次停下来观察项目的时间。", "",
        f"感想周期：{start} 至 {date}（Asia/Shanghai）", "",
        "## 这周我在想什么", "",
        "本周没有检索到新的公开提交，因此不虚构项目进展。对个人项目来说，暂停开发、整理结构和重新确认方向，同样是技术工作的一部分。", "",
        "## 我会继续验证什么", "",
        "下一周恢复开发后，再用真实的改动补充这篇记录。", "",
        "## 资料范围", "",
        f"本文只使用 {USER} 的 GitHub 公开活动，不把 Fork 历史或其他作者的提交当作个人产出。"
    ]

markdown = "\n".join(body) + "\n"
(OUT / filename).write_text(markdown, encoding="utf-8")
lines = []
for line in markdown.splitlines():
    safe = html.escape(line)
    if line.startswith("# "):
        lines.append(f"<h1>{html.escape(line[2:])}</h1>")
    elif line.startswith("## "):
        lines.append(f"<h2>{html.escape(line[3:])}</h2>")
    elif line.startswith("> "):
        lines.append(f"<blockquote>{html.escape(line[2:])}</blockquote>")
    elif line.strip():
        lines.append(f"<p>{safe}</p>")
(OUT / (pathlib.Path(filename).stem + ".html")).write_text(
    "<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width'><link rel='stylesheet' href='../style.css'><main class='article-page'>"
    + "\n".join(lines) + "</main>", encoding="utf-8"
)
index = []
for path in sorted(OUT.glob("*.md"), reverse=True):
    text = path.read_text(encoding="utf-8")
    heading = next((line[2:] for line in text.splitlines() if line.startswith("# ")), path.stem)
    quote = next((line[2:] for line in text.splitlines() if line.startswith("> ")), "GitHub 技术感想")
    index.append({"date": path.stem, "period": "TECH REFLECTION", "title": heading, "summary": quote, "tags": ["技术感想", "GitHub"], "url": path.with_suffix(".html").name})
(OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
