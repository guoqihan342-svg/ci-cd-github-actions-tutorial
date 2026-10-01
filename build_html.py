#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""将教程 Markdown 渲染为带样式与目录的单文件 HTML。"""
import re
import unicodedata
import markdown
from markdown.extensions.toc import TocExtension


def slugify_keep_cjk(value, separator):
    """生成保留中文的锚点 id，如 '第-3-章-第一个工作流'。"""
    value = unicodedata.normalize("NFKC", value).strip().lower()
    value = re.sub(r"[^\w\u4e00-\u9fff]+", separator, value, flags=re.UNICODE)
    return re.sub(r"[" + re.escape(separator) + r"]+", separator, value).strip(separator)

SRC = "CI-CD-GitHub配置完全教程.md"
OUT = "CI-CD-GitHub配置完全教程.html"

md_text = open(SRC, encoding="utf-8").read()

# 去掉最前面的 H1 标题（模板里单独渲染）
md_text = re.sub(r"^# .*?\n", "", md_text, count=1)

# 去掉正文中的手写"目录"小节（HTML 已有侧边目录）
md_text = re.sub(r"^## 目录\s*\n.*?\n---\s*\n", "", md_text, count=1, flags=re.S | re.M)

html_body = markdown.markdown(
    md_text,
    extensions=[
        "fenced_code",
        "tables",
        "attr_list",
        "sane_lists",
        "admonition",
        TocExtension(permalink=True, toc_depth="2-3", slugify=slugify_keep_cjk),
    ],
    extension_configs={"codehilite": {"guess_lang": False}},
)

# 从 h2 生成侧边目录
toc_html = ""
toc_items = re.findall(r'<h2 id="([^"]+)">(.*?)<a class="headerlink"', html_body)
if toc_items:
    toc_html = "<ul>" + "".join(
        f'<li><a href="#{i}">{t}</a></li>' for i, t in toc_items
    ) + "</ul>"

import diagrams  # noqa: E402  教程配图模块


def _inject_diagrams(html):
    """把 <!--DIAGRAM:name--> 标记替换为内联 SVG。"""
    used = []

    def repl(m):
        name = m.group(1).strip()
        if name not in diagrams.DIAGRAMS:
            print(f"  !! 未定义的图: {name}")
            return m.group(0)
        used.append(name)
        return f'<div class="diagram">{diagrams.render(name)}</div>'

    html = re.sub(r"(?:<p>)?<!--DIAGRAM:([\w-]+)-->(?:</p>)?", repl, html)
    print(f"  已注入 {len(used)} 张图: {', '.join(used)}")
    return html


html_body = _inject_diagrams(html_body)


TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CI/CD 与 GitHub Actions 配置完全教程</title>
<style>
  :root {
    --bg: #ffffff;
    --bg-soft: #f6f8fa;
    --bg-code: #f6f8fa;
    --text: #1f2328;
    --text-soft: #57606a;
    --border: #d0d7de;
    --accent: #0969da;
    --accent-soft: #ddf4ff;
    --green: #1a7f37;
    --red: #cf222e;
    --purple: #8250df;
    --sidebar-w: 280px;
    --mono: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
            "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    font-family: var(--sans);
    color: var(--text);
    background: var(--bg);
    line-height: 1.75;
    font-size: 16px;
  }
  /* 顶部栏 */
  header.topbar {
    position: sticky; top: 0; z-index: 50;
    background: rgba(255,255,255,.85);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--border);
    padding: 12px 24px;
    display: flex; align-items: center; gap: 12px;
  }
  header.topbar .logo {
    font-weight: 700; font-size: 15px; color: var(--text);
  }
  header.topbar .badge {
    font-size: 12px; padding: 2px 8px; border-radius: 20px;
    background: var(--accent-soft); color: var(--accent);
    border: 1px solid #b6e3ff;
  }
  header.topbar .spacer { flex: 1; }
  header.topbar .hint { font-size: 12px; color: var(--text-soft); }

  .layout { display: flex; align-items: flex-start; }

  /* 侧边目录 */
  aside.toc {
    position: sticky; top: 57px;
    width: var(--sidebar-w); min-width: var(--sidebar-w);
    height: calc(100vh - 57px);
    overflow-y: auto;
    border-right: 1px solid var(--border);
    padding: 24px 16px 60px;
    background: var(--bg-soft);
    font-size: 13.5px;
  }
  aside.toc .toc-title {
    font-size: 12px; text-transform: uppercase; letter-spacing: .06em;
    color: var(--text-soft); font-weight: 700; margin: 0 0 12px 8px;
  }
  aside.toc ul { list-style: none; margin: 0; padding: 0; }
  aside.toc li { margin: 1px 0; }
  aside.toc a {
    display: block; padding: 5px 10px; border-radius: 6px;
    color: var(--text-soft); text-decoration: none;
    border-left: 2px solid transparent;
  }
  aside.toc a:hover { background: #eaeef2; color: var(--text); }
  aside.toc a.active {
    color: var(--accent); background: var(--accent-soft);
    border-left-color: var(--accent); font-weight: 600;
  }

  /* 正文 */
  main {
    flex: 1; min-width: 0;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 48px 120px;
  }
  .hero {
    border: 1px solid var(--border); border-radius: 12px;
    padding: 28px 32px; margin-bottom: 40px;
    background: linear-gradient(135deg, #f6f8fa 0%, #ffffff 60%);
  }
  .hero h1 { margin: 0 0 12px; font-size: 30px; line-height: 1.3; letter-spacing: -.01em; }
  .hero p { margin: 0; color: var(--text-soft); font-size: 15px; }
  .hero .meta { margin-top: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
  .hero .meta span {
    font-size: 12px; padding: 3px 10px; border-radius: 20px;
    background: var(--bg-soft); border: 1px solid var(--border); color: var(--text-soft);
  }

  h2 {
    font-size: 24px; margin: 56px 0 16px; padding-bottom: 10px;
    border-bottom: 1px solid var(--border); letter-spacing: -.01em;
  }
  h3 { font-size: 18px; margin: 32px 0 12px; }
  h4 { font-size: 16px; margin: 24px 0 10px; }
  p { margin: 12px 0; }
  a { color: var(--accent); }
  strong { font-weight: 650; }
  hr { border: none; border-top: 1px solid var(--border); margin: 40px 0; }

  ul, ol { padding-left: 26px; }
  li { margin: 6px 0; }

  blockquote {
    margin: 16px 0; padding: 10px 18px;
    border-left: 3px solid var(--accent);
    background: var(--accent-soft);
    border-radius: 0 8px 8px 0;
    color: #0a3069;
  }
  blockquote p { margin: 6px 0; }

  code {
    font-family: var(--mono); font-size: 85%;
    background: var(--bg-code); padding: .2em .4em;
    border-radius: 6px; border: 1px solid var(--border);
  }
  pre {
    background: var(--bg-code); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px 18px; overflow-x: auto;
    margin: 16px 0; line-height: 1.6;
  }
  pre code {
    background: none; border: none; padding: 0; font-size: 13.5px;
  }

  table {
    border-collapse: collapse; width: 100%; margin: 18px 0;
    font-size: 14.5px; display: block; overflow-x: auto;
  }
  th, td { border: 1px solid var(--border); padding: 9px 14px; text-align: left; vertical-align: top; }
  th { background: var(--bg-soft); font-weight: 650; }
  tr:nth-child(even) td { background: #fbfcfd; }

  .headerlink { display: none; }

  /* 示意图 */
  .diagram {
    margin: 20px 0 26px;
    padding: 18px 16px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: #fcfdfe;
    overflow-x: auto;
  }
  .diagram svg { display: block; min-width: 640px; }

  /* Pygments 高亮（浅色） */
  .codehilite .hll { background-color: #fffbdd; }
  .codehilite .c, .codehilite .c1, .codehilite .cm { color: #6e7781; font-style: italic; }
  .codehilite .k, .codehilite .kn, .codehilite .kd, .codehilite .kc { color: #cf222e; }
  .codehilite .s, .codehilite .s1, .codehilite .s2, .codehilite .sb { color: #0a3069; }
  .codehilite .na, .codehilite .nv { color: #953800; }
  .codehilite .nt { color: #116329; }
  .codehilite .m, .codehilite .mi, .codehilite .mf { color: #0550ae; }
  .codehilite .o, .codehilite .p { color: #24292f; }
  .codehilite .nf { color: #8250df; }

  /* 回到顶部 */
  #toTop {
    position: fixed; right: 24px; bottom: 24px; z-index: 60;
    width: 42px; height: 42px; border-radius: 50%;
    border: 1px solid var(--border); background: #fff; color: var(--text-soft);
    cursor: pointer; display: none; font-size: 18px; line-height: 1;
    box-shadow: 0 4px 12px rgba(0,0,0,.08);
  }
  #toTop:hover { color: var(--accent); border-color: var(--accent); }

  @media (max-width: 1000px) {
    aside.toc { display: none; }
    main { padding: 28px 20px 100px; }
  }
</style>
</head>
<body>
<header class="topbar">
  <span class="logo">CI/CD · GitHub Actions</span>
  <span class="badge">配置教程</span>
  <span class="spacer"></span>
  <span class="hint">按 Ctrl/⌘ + F 可搜索</span>
</header>

<div class="layout">
  <aside class="toc">
    <div class="toc-title">目录</div>
    __TOC__
  </aside>
  <main>
    <div class="hero">
      <h1>CI/CD 与 GitHub Actions 配置完全教程</h1>
      <p>从概念到落地的系统性指南：理解 CI/CD 的本质，掌握 GitHub Actions 的完整配置语法，按「前端 / 后端」与「Java / Python / Node / Go」分栈落地，并能独立搭建生产级流水线。</p>
      <div class="meta">
        <span>13 章正文</span>
        <span>16 张流程图</span>
        <span>前端 / 后端分栈</span>
        <span>4 种后端语言</span>
        <span>6 个完整项目</span>
        <span>32 条 FAQ</span>
      </div>
    </div>
    __BODY__
  </main>
</div>

<button id="toTop" title="回到顶部">↑</button>

<script>
  // 回到顶部
  var toTop = document.getElementById('toTop');
  window.addEventListener('scroll', function () {
    toTop.style.display = window.scrollY > 400 ? 'block' : 'none';
  });
  toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

  // 目录高亮
  var links = Array.prototype.slice.call(document.querySelectorAll('aside.toc a'));
  var targets = links.map(function (a) {
    var id = a.getAttribute('href').slice(1);
    return document.getElementById(id);
  }).filter(Boolean);
  function onScroll() {
    var pos = window.scrollY + 120, cur = null;
    targets.forEach(function (t) { if (t.offsetTop <= pos) cur = t.id; });
    links.forEach(function (a) {
      a.classList.toggle('active', a.getAttribute('href') === '#' + cur);
    });
  }
  window.addEventListener('scroll', onScroll);
  onScroll();
</script>
</body>
</html>
"""

html = TEMPLATE.replace("__TOC__", toc_html).replace("__BODY__", html_body)
open(OUT, "w", encoding="utf-8").write(html)
print(f"generated {OUT} ({len(html)} bytes)")
