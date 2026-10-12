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

window_start = dt.datetime.combine(start, dt.time.min, tzinfo=ZoneInfo("Asia/Shanghai")).astimezone(dt.timezone.utc).isoformat()
window_end = dt.datetime.combine(end, dt.time.min, tzinfo=ZoneInfo("Asia/Shanghai")).astimezone(dt.timezone.utc).isoformat()

# The public events feed is incomplete and can omit older PushEvents. Read each
# owned repository's commit endpoint instead, matching the same source as the site chart.
pushes = []
try:
    repositories = get(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")
    for repository in repositories:
        repo = repository.get("full_name", "")
        if not repo or repository.get("fork"):
            continue
        commits = get(
            f"https://api.github.com/repos/{repo}/commits"
            f"?author={USER}&since={window_start}&until={window_end}&per_page=100"
        )
        if commits:
            pushes.append((repo, commits))
except Exception as exc:
    print(f"GitHub repository commits unavailable: {exc}")

grouped = {}
for repo, commits in pushes:
    grouped.setdefault(repo, []).extend(commits)

if grouped:
    main_repo = max(grouped, key=lambda name: len(grouped[name]))
    project_names = ", ".join(name.split("/")[-1] for name in grouped)
    all_messages = " ".join(commit.get("commit", {}).get("message", "") for items in grouped.values() for commit in items).lower()
    themes = []
    theme_rules = [
        (("fail-closed", "safety", "stop"), "安全状态与 fail-closed 设计"),
        (("recovery", "timeout", "reconnect", "retry"), "故障恢复、超时和重连"),
        (("gcs", "tcp", "physical", "controller"), "真实设备连接与 GCS 通信"),
        (("virtual", "sim", "evidence", "acceptance", "ci"), "虚拟设备验证与 CI 证据"),
        (("ui", "compose", "stateflow", "state"), "界面状态建模与状态流转"),
    ]
    for keywords, label in theme_rules:
        if any(keyword in all_messages for keyword in keywords):
            themes.append(label)
    theme_text = "、".join(themes[:4]) or "工程结构和持续验证"
    title = f"这一周的技术感想：把 {main_repo.split('/')[-1]} 做得更可靠"
    body = [
        f"# {title}", "",
        "> 提交只是线索，真正值得留下的是做决定时的理由。", "",
        f"感想周期：{start} 至 {date}（Asia/Shanghai）", "",
        "## 这周真正推进的事情", "",
        f"这周主要围绕 {project_names} 展开，记录到 {sum(len(items) for items in grouped.values())} 次本人提交。改动集中在 {theme_text}。这些提交并不是彼此孤立的功能堆叠，而是在把同一个目标逐步落地：让设备控制、模拟验证和界面状态在异常发生时仍然可解释、可恢复。", "",
        "## 我得到的技术判断", "",
        "涉及真实设备的程序，最危险的不是一次明确的失败，而是旧状态继续被当成新状态使用。因此这周的重点不是让路径“尽量成功”，而是让每一次超时、断开、取消和并发操作都能明确地失效，并留下可验证的证据。", "",
        "虚拟设备和 CI 证据也不只是测试替身。它们把难以稳定复现的硬件问题变成可以重复运行的场景，让恢复流程、资源释放和状态边界都能在提交阶段被检查。这样，真实硬件验证就可以聚焦兼容性，而不是承担所有基础正确性的证明责任。", "",
        "## 还需要继续打磨的地方", "",
        "当前文章能说明本周的技术方向，但还不能替代完整的变更说明。下一步应该把关键决策与具体验证结果关联起来，明确哪些结论来自自动化测试，哪些仍需要真实设备确认。", "",
        "## 资料范围", "",
        f"本文根据 {len(grouped)} 个仓库的提交记录整理，共 {sum(len(items) for items in grouped.values())} 次本人提交。提交信息用于归纳技术主题，不在文章中逐条复制。"
    ]
else:
    title = f"这一周的技术感想：{start} — {date}"
    body = [
        f"# {title}", "",
        "> 没有新的公开提交，也可以记录一次停下来观察项目的时间。", "",
        f"感想周期：{start} 至 {date}（Asia/Shanghai）", "",
        "## 这周我在想什么", "",
        "本周没有检索到新的公开提交，因此不虚构项目进展。暂停开发、整理结构和重新确认方向，同样是技术工作的一部分。", "",
        "## 我会继续验证什么", "",
        "下一周恢复开发后，再用真实的改动补充这篇记录。", "",
        "## 资料范围", "",
        f"本文只使用 {USER} 的 GitHub 仓库提交记录，不把 Fork 历史或其他作者的提交当作个人产出。"
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
