#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 diagrams.py 中的 SVG 渲染为 PNG 图片，供 README 展示。

做法：为每张图生成一个独立 HTML（含描述文字 + 内联 SVG），
用 Chrome headless 截取该 HTML 的整页，输出到 images/ 目录。
"""
import os
import shutil
import subprocess
import sys
import tempfile

import diagrams

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
SCALE = 2  # 2 倍图，README 中更清晰

# 图片文件名 -> (图 key, 展示宽度px, 标题, 说明)
SPECS = [
    ("01-cicd-pipeline",            "pipeline",           860, "CI/CD 流水线全景",
     "从提交到部署的 10 个环节，前 6 步属于「持续集成」，后 2 步属于「持续交付 / 部署」。"),
    ("02-actions-execution-model",  "arch",               820, "GitHub Actions 执行模型",
     "Event → Workflow → Job → Step → Runner 的五层结构。"),
    ("03-ci-vs-cd-modes",           "cicd-modes",         860, "CI / 持续交付 / 持续部署的差别",
     "三者差别只在最后一步：是否有人工审批。"),
    ("04-triggers",                 "triggers",           880, "五类触发器",
     "on 的五种触发方式及其适用场景。"),
    ("05-context-flow",             "context-flow",       860, "上下文与表达式数据流",
     "8 类上下文经 ${{ }} 求值后，注入到 8 个使用位置。"),
    ("06-security-model",           "security-model",     860, "权限与密钥的四层模型",
     "组织/仓库 → Environment → Job → Step，内层可覆盖外层。"),
    ("07-matrix",                   "matrix",             860, "矩阵构建：一次定义、多组合并行",
     "2 × 3 = 6 个 Job 并行，exclude 可排除无效组合。"),
    ("08-cache-flow",               "cache-flow",         860, "缓存命中与未命中路径",
     "命中走快路径，未命中走慢路径并写入缓存。"),
    ("09-cache-vs-artifact",        "cache-vs-artifact",  860, "Cache 与 Artifact 的区别",
     "要「快」用 Cache，要「留」用 Artifact。"),
    ("10-job-dag",                  "job-dag",            880, "Job 依赖编排",
     "默认并行，needs 决定串行，形成有向无环图。"),
    ("11-frontend-vs-backend",      "fe-vs-be",           860, "前端 vs 后端流水线",
     "前端交付「文件」，后端交付「进程 / 镜像」。"),
    ("12-backend-languages",        "backend-langs",      860, "Java / Python / Node / Go 构建链路对照",
     "四栈从安装依赖到产出物的横向对照。"),
    ("13-troubleshooting-tree",     "troubleshoot-tree",  860, "排错决策树",
     "工作流异常的三类分支：没触发、Job 失败、部署异常。"),
    ("14-multi-env",                "multi-env",          880, "多环境发布",
     "分支 → 环境 → 审批三者绑定的发布模型。"),
    ("15-pr-preview",               "preview-lifecycle",  860, "PR 预览环境生命周期",
     "从 PR 创建到关闭的资源全生命周期。"),
    ("16-gitops",                   "gitops",             860, "GitOps 发布模式",
     "CI 产出镜像与清单，集群侧自动同步收敛。"),
]

PAGE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 26px 30px 22px; background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Microsoft YaHei", sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .head {{
    display: flex; align-items: baseline; gap: 12px;
    border-bottom: 2px solid #0969da; padding-bottom: 10px; margin-bottom: 18px;
  }}
  .idx {{
    font-size: 13px; font-weight: 700; color: #ffffff; background: #0969da;
    border-radius: 5px; padding: 2px 9px; letter-spacing: .5px;
  }}
  h1 {{ font-size: 19px; margin: 0; color: #1f2328; font-weight: 700; }}
  .desc {{ font-size: 13px; color: #57606a; margin: 0 0 16px; line-height: 1.65; }}
  .frame {{
    border: 1px solid #d0d7de; border-radius: 10px; padding: 8px;
    background: #fcfdfe; width: {w}px;
  }}
  .foot {{
    margin-top: 14px; font-size: 11.5px; color: #8c959f;
    display: flex; justify-content: space-between; width: {w}px;
  }}
  svg {{ display: block; }}
</style></head><body>
  <div class="head"><span class="idx">{num}</span><h1>{title}</h1></div>
  <p class="desc">{desc}</p>
  <div class="frame">{svg}</div>
  <div class="foot"><span>CI/CD 与 GitHub Actions 配置完全教程</span>
  <span>图 {num} / 16</span></div>
</body></html>
"""


def shoot(key, w, out_png, num, title, desc):
    svg = diagrams.render(key)
    tmpdir = tempfile.mkdtemp(prefix="diagshot_")
    try:
        html_path = os.path.join(tmpdir, "page.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(PAGE.format(svg=svg, w=w, num=num, title=title, desc=desc))
        user_dir = os.path.join(tmpdir, "cdp")

        # 首次以固定宽度与足够高度截图，拿到整页高度后再决定是否截断
        cmd = [
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=%d" % SCALE,
            "--default-background-color=FFFFFFFF",
            "--user-data-dir=" + user_dir,
            "--no-first-run", "--no-default-browser-check",
            "--window-size=%d,2000" % (w + 60),
            "--virtual-time-budget=2500",
            "--screenshot=" + out_png,
            "file:///" + html_path.replace("\\", "/"),
        ]
        p = subprocess.run(cmd, capture_output=True, timeout=120)
        if p.returncode != 0 or not os.path.exists(out_png):
            return False, (p.stderr or b"").decode("utf-8", "ignore")[:300]
        return True, os.path.getsize(out_png)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def trim_whitespace(path, keep_scale=SCALE):
    """裁掉底部多余留白（Chrome 的截图高度固定，会出现大片空白）。"""
    try:
        from PIL import Image
    except ImportError:
        return None
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    bg = px[2, 2]
    # 从底部往上找第一条非背景行
    bottom = h
    step = 2
    for y in range(h - 1, 0, -step):
        row_bg = True
        for x in range(0, w, max(1, w // 60)):
            if px[x, y] != bg:
                row_bg = False
                break
        if not row_bg:
            bottom = min(h, y + 24)
            break
    if bottom < h:
        im.crop((0, 0, w, bottom)).save(path)
    return (w, bottom)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    only = sys.argv[1:] or None
    ok_n = 0
    for i, (fname, key, w, title, desc) in enumerate(SPECS, 1):
        if only and fname not in only and key not in only:
            continue
        out = os.path.join(OUT_DIR, fname + ".png")
        ok, info = shoot(key, w, out, "%02d" % i, title, desc)
        if ok:
            t = trim_whitespace(out)
            ok_n += 1
            print("OK   %-30s %8d bytes  trimmed=%s" % (fname + ".png", info, t))
        else:
            print("FAIL %-30s %s" % (fname + ".png", info))
    print("--- %d/%d 张完成 ---" % (ok_n, len(SPECS)))
