document.querySelector("#year").textContent = new Date().getFullYear();
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const orbitArt = document.querySelector(".orbit-art");
if (orbitArt) {
  orbitArt.insertAdjacentHTML("beforeend", '<div class="orbit-stat stat-cold"><span>COLD START</span><strong>~0.2<small>s</small></strong><i></i></div><div class="orbit-stat stat-ram"><span>RAM</span><strong>35<small> MB</small></strong><i></i></div><div class="orbit-stat stat-modules"><span>MODULES</span><strong>40<small>+</small></strong><i></i></div><div class="orbit-stat stat-formats"><span>FORMATS</span><strong>18</strong><i></i></div>');
  const svg = orbitArt.querySelector("svg");
  svg?.insertAdjacentHTML("beforeend", '<g class="orbit-movers"><circle r="9" fill="#6f9fff"><animateMotion dur="12s" repeatCount="indefinite" path="M 60,260 a 220,78 0 1 0 440,0 a 220,78 0 1 0 -440,0"/></circle><circle r="10" fill="#ff8c57"><animateMotion dur="16s" repeatCount="indefinite" path="M 60,260 a 220,78 0 1 0 440,0 a 220,78 0 1 0 -440,0" begin="-5s"/></circle><circle r="11" fill="#c18aff"><animateMotion dur="20s" repeatCount="indefinite" path="M 60,260 a 218,78 0 1 0 436,0 a 218,78 0 1 0 -436,0" begin="-9s"/></circle><circle r="10" fill="#ff6f9c"><animateMotion dur="14s" repeatCount="indefinite" path="M 60,260 a 218,78 0 1 0 436,0 a 218,78 0 1 0 -436,0" begin="-3s"/></circle></g>');
}
const canvas = document.createElement("canvas"); canvas.className = "ambient-particles"; canvas.setAttribute("aria-hidden", "true"); document.body.prepend(canvas);
const ctx = canvas.getContext("2d"); let particles = [], frame = 0;
function resizeParticles(){const d=Math.min(devicePixelRatio||1,2);canvas.width=innerWidth*d;canvas.height=innerHeight*d;ctx.setTransform(d,0,0,d,0,0);const n=Math.min(110,Math.max(38,Math.floor(innerWidth/13)));particles=Array.from({length:n},()=>({x:Math.random()*innerWidth,y:Math.random()*innerHeight,r:Math.random()*1.6+.4,vx:(Math.random()-.5)*.18,vy:(Math.random()-.5)*.18,a:Math.random()*.5+.15}));}
function drawParticles(){if(reducedMotion.matches)return;ctx.clearRect(0,0,innerWidth,innerHeight);for(let i=0;i<particles.length;i++){const p=particles[i];p.x=(p.x+p.vx+innerWidth)%innerWidth;p.y=(p.y+p.vy+innerHeight)%innerHeight;ctx.fillStyle=`rgba(143,173,255,${p.a})`;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();for(let j=i+1;j<particles.length;j++){const q=particles[j],dx=p.x-q.x,dy=p.y-q.y,d=Math.hypot(dx,dy);if(d<105){ctx.strokeStyle=`rgba(108,143,235,${.13*(1-d/105)})`;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();}}}frame=requestAnimationFrame(drawParticles);}
function startParticles(){cancelAnimationFrame(frame);resizeParticles();if(!reducedMotion.matches)drawParticles();}
addEventListener("resize",resizeParticles);startParticles();reducedMotion.addEventListener("change",startParticles);
document.querySelectorAll(".orbits ellipse").forEach((ellipse,index)=>{ellipse.classList.add(`orbit-path-${index+1}`);});
const stats=document.createElement("div");stats.className="animated-stats";stats.innerHTML='<div><strong data-count="6">0</strong><span>活跃方向</span></div><div><strong data-count="4">0</strong><span>公开项目</span></div><div><strong data-count="14">0</strong><span>天提交轨迹</span></div>';document.querySelector(".hero-copy")?.append(stats);
function animateCount(el){const target=Number(el.dataset.count);if(reducedMotion.matches){el.textContent=target;return}const start=performance.now();const tick=(now)=>{const p=Math.min(1,(now-start)/900);el.textContent=Math.round((1-Math.pow(1-p,3))*target);if(p<1)requestAnimationFrame(tick)};requestAnimationFrame(tick)}
const revealObserver=new IntersectionObserver((entries)=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add("is-visible");entry.target.querySelectorAll?.("[data-count]").forEach(animateCount);revealObserver.unobserve(entry.target)}}),{threshold:.14});document.querySelectorAll(".section,.direction-card,.activity-card,.chart-card,.about-card,.thought-grid article,.animated-stats").forEach((el)=>{el.classList.add("scroll-reveal");revealObserver.observe(el)});
document.querySelectorAll(".direction-card,.activity-card,.article-card,.about-card").forEach((card)=>{card.addEventListener("pointermove",(event)=>{const r=card.getBoundingClientRect();card.style.setProperty("--mx",`${event.clientX-r.left}px`);card.style.setProperty("--my",`${event.clientY-r.top}px`)});card.addEventListener("pointerleave",()=>{card.style.removeProperty("--mx");card.style.removeProperty("--my")})});
const navLinks = document.querySelector(".nav-links");
if (navLinks && !navLinks.querySelector('[href="#articles"]')) navLinks.insertAdjacentHTML("beforeend", '<a href="#articles">每周文章</a>');
const articleSection = document.createElement("section");
articleSection.id = "articles"; articleSection.className = "shell section articles-section";
articleSection.innerHTML = '<div class="section-heading row"><div><p class="eyebrow">WEEKLY ARTICLES</p><h2>把动态写成，<span>值得阅读的文章。</span></h2><p>每周根据 GitHub 公开活动自动整理，记录真实改动与技术思路。</p></div><span class="tag live-tag"><i></i>自动更新</span></div><div id="article-list" class="article-list"><article class="article-card"><span class="article-kicker">LATEST</span><h3>正在加载每周文章</h3><p>文章会在 GitHub Actions 生成后自动出现在这里。</p></article></div>';
document.querySelector("#about")?.before(articleSection);
    const githubUser = "changhexuefei";
    const githubStatus = document.querySelector("#github-status");
    const activityGrid = document.querySelector("#activity-grid");
    const commitChart = document.querySelector("#commit-chart");
    const commitSummary = document.querySelector("#commit-summary");
    const githubRefreshMs = 10 * 60 * 1000;
    const githubStaleMs = 2 * 60 * 1000;
    let githubLastSync = 0;
    let githubLoading = false;

    function observeNewReveals(scope) {
      scope.querySelectorAll(".reveal").forEach((item) => {
        item.classList.add("visible");
      });
    }

    function formatDate(value) {
      return new Intl.DateTimeFormat("zh-CN", {
        month: "2-digit",
        day: "2-digit"
      }).format(new Date(value));
    }

    function repoDescription(repo) {
      if (repo.description) return repo.description;
      const fallback = {
        SiPhStudio: "近期更新的自有 Kotlin 仓库，适合作为后续项目展示和工程记录的重点入口。",
        "changhexuefei.github.io": "个人主页与 GitHub Pages 门面，承载近期工作、项目方向和可视化动态。"
      };
      return fallback[repo.name] || "公开仓库动态，来自 GitHub 最近更新时间。";
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    function renderRepos(repos) {
      const visibleRepos = repos
        .filter((repo) => !repo.archived)
        .slice(0, 4);

      if (!visibleRepos.length) return;

      activityGrid.innerHTML = visibleRepos.map((repo) => `
        <article class="activity-card reveal visible">
          <h3>${escapeHtml(repo.name)}</h3>
          <p>${escapeHtml(repoDescription(repo))}</p>
          <div class="activity-meta">
            <span>${escapeHtml(repo.language || "Mixed")}</span>
            <span>${formatDate(repo.updated_at)}</span>
            ${repo.fork ? "<span>Fork</span>" : "<span>Original</span>"}
          </div>
          <a class="activity-link" href="${escapeHtml(repo.html_url)}" target="_blank" rel="noopener">查看仓库 ↗</a>
        </article>
      `).join("");
      observeNewReveals(activityGrid);
    }

    function lastNDays(days) {
      const result = [];
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      for (let index = days - 1; index >= 0; index -= 1) {
        const date = new Date(today);
        date.setDate(today.getDate() - index);
        result.push({
          key: `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,"0")}-${String(date.getDate()).padStart(2,"0")}`,
          label: `${date.getMonth() + 1}/${date.getDate()}`,
          count: 0
        });
      }
      return result;
    }

    function renderCommitChart(days) {
      const width = 920;
      const height = 300;
      const pad = { top: 28, right: 28, bottom: 42, left: 44 };
      const innerWidth = width - pad.left - pad.right;
      const innerHeight = height - pad.top - pad.bottom;
      const max = Math.max(1, ...days.map((day) => day.count));
      const points = days.map((day, index) => {
        const x = pad.left + (innerWidth * index) / Math.max(1, days.length - 1);
        const y = pad.top + innerHeight - (day.count / max) * innerHeight;
        return { ...day, x, y };
      });
      const line = points.map((point, index) => `${index === 0 ? "M" : "L"}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ");
      const area = `${line} L${points[points.length - 1].x.toFixed(1)},${(pad.top + innerHeight).toFixed(1)} L${points[0].x.toFixed(1)},${(pad.top + innerHeight).toFixed(1)} Z`;
      const grid = [0, .25, .5, .75, 1].map((ratio) => {
        const y = pad.top + innerHeight * ratio;
        return `<line class="chart-grid-line" x1="${pad.left}" y1="${y}" x2="${width - pad.right}" y2="${y}"></line>`;
      }).join("");
      const dots = points.map((point) => `
        <circle class="chart-dot" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="5"></circle>
        ${point.count ? `<text class="chart-value" x="${point.x.toFixed(1)}" y="${(point.y - 12).toFixed(1)}" text-anchor="middle">${point.count}</text>` : ""}
      `).join("");
      const labels = points
        .filter((_, index) => index === 0 || index === points.length - 1 || index % 3 === 0)
        .map((point) => `<text class="chart-label" x="${point.x.toFixed(1)}" y="${height - 12}" text-anchor="middle">${point.label}</text>`)
        .join("");

      commitChart.innerHTML = `
        ${grid}
        <line class="chart-axis" x1="${pad.left}" y1="${pad.top + innerHeight}" x2="${width - pad.right}" y2="${pad.top + innerHeight}"></line>
        <path class="chart-area" d="${area}"></path>
        <path class="chart-line" d="${line}"></path>
        ${dots}
        ${labels}
      `;
    }

    function commitsByDay(commits) {
      const days = lastNDays(14);
      const counts = new Map(days.map((day) => [day.key, day]));
      commits
        .forEach((commit) => {
          const date = commit.commit?.author?.date || commit.commit?.committer?.date;
          if (!date) return;
          const localDate = new Date(date);
          const key = `${localDate.getFullYear()}-${String(localDate.getMonth()+1).padStart(2,"0")}-${String(localDate.getDate()).padStart(2,"0")}`;
          if (!counts.has(key)) return;
          counts.get(key).count += 1;
        });
      return days;
    }

    async function loadRecentCommits(repos) {
      const since = new Date();
      since.setDate(since.getDate() - 13);
      since.setHours(0, 0, 0, 0);

      const targets = repos
        .filter((repo) => !repo.archived)
        .slice(0, 6);

      const results = await Promise.allSettled(targets.map((repo) => (
        fetch(`https://api.github.com/repos/${githubUser}/${repo.name}/commits?since=${since.toISOString()}&per_page=100`, {
          signal: AbortSignal.timeout(12000),
          headers: { Accept: "application/vnd.github+json" }
        }).then((response) => {
          if (!response.ok) throw new Error("Commits unavailable");
          return response.json();
        })
      )));

      if (results.some(result => result.status === "rejected")) throw new Error("Incomplete commit data");
      return results.flatMap((result) => (
        result.status === "fulfilled" && Array.isArray(result.value) ? result.value : []
      ));
    }

    async function loadGithubActivity(reason = "auto") {
      if (githubLoading) return;
      githubLoading = true;
      
      githubStatus.textContent = reason === "initial"
        ? "正在读取 GitHub 公开动态"
        : "正在自动同步 GitHub 公开动态";

      try {
        const reposResponse = await fetch(`https://api.github.com/users/${githubUser}/repos?sort=updated&per_page=12`, {
          signal: AbortSignal.timeout(12000),
          headers: { Accept: "application/vnd.github+json" }
        });

        if (!reposResponse.ok) {
          throw new Error("GitHub API unavailable");
        }

        const repos = await reposResponse.json();
        renderRepos(repos);
        const commits = await loadRecentCommits(repos);
        const days = commitsByDay(commits);
        const totalCommits = days.reduce((sum, day) => sum + day.count, 0);
        const syncedAt = new Intl.DateTimeFormat("zh-CN", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit"
        }).format(new Date());

        renderRepos(repos);
        renderCommitChart(days);
        githubLastSync = Date.now();
        githubStatus.textContent = `已同步公开仓库 · ${syncedAt} 更新 · 每 10 分钟刷新`;
        commitSummary.textContent = `最近活跃的 6 个公开仓库，近 14 天读取到 ${totalCommits} 条提交记录（每库最多 100 条，包含 Fork 历史）。`;
      } catch (error) {
        commitChart.innerHTML = "";
        githubStatus.textContent = "GitHub 暂时无法连接，项目列表保留当前内容。";
        commitSummary.textContent = "暂时无法读取提交数据，恢复连接后将自动更新。";
      } finally {
        githubLoading = false;
      }
    }

    loadGithubActivity("initial");
    window.setInterval(() => loadGithubActivity("interval"), githubRefreshMs);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible" && Date.now() - githubLastSync > githubStaleMs) {
        loadGithubActivity("visible");
      }
    });
