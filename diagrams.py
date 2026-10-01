#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""教程配图模块：生成内联 SVG 示意图（浅色主题）。

每个图独立命名 marker id，避免同页多图冲突。
"""
import re

FONT = ("font-family='-apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,"
        "Microsoft YaHei,sans-serif'")

# 调色板（浅色主题）
BOX_F, BOX_S = "#f6f8fa", "#d0d7de"
TXT, MUT = "#1f2328", "#57606a"
BLUE_F, BLUE_S, BLUE_T = "#ddf4ff", "#b6e3ff", "#0969da"
GREEN_F, GREEN_S, GREEN_T = "#dafbe1", "#aceebb", "#1a7f37"
YEL_F, YEL_S, YEL_T = "#fff8c5", "#f0d98c", "#7d4e00"
PUR_F, PUR_S, PUR_T = "#fbefff", "#e2c5ff", "#8250df"
RED_F, RED_S, RED_T = "#ffebe9", "#ffc1bc", "#cf222e"
LINE = "#8c959f"
CANVAS = "#fcfdfe"


# ---------------------------------------------------------------- 基础绘制
def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_open(name, w, h, label):
    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{_esc(label)}">'
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="{CANVAS}"/>'
        f'<defs>'
        f'<marker id="a-{name}" markerWidth="8" markerHeight="8" refX="6.5" refY="3" '
        f'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{LINE}"/></marker>'
        f'<marker id="b-{name}" markerWidth="8" markerHeight="8" refX="6.5" refY="3" '
        f'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{BLUE_T}"/></marker>'
        f'<marker id="g-{name}" markerWidth="8" markerHeight="8" refX="6.5" refY="3" '
        f'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{GREEN_T}"/></marker>'
        f'</defs>'
    )


def title(x, y, text, size=14, color=TXT, weight="700"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" {FONT}>{_esc(text)}</text>')


def txt(x, y, text, size=12, color=MUT, anchor="middle", weight="400"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}" {FONT}>{_esc(text)}</text>')


def box(x, y, w, h, fill=BOX_F, stroke=BOX_S, rx=9, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}"{d}/>')


def cbox(x, y, w, h, main, sub=None, fill=BOX_F, stroke=BOX_S, tcol=TXT,
         fs=13, sfs=10.5, rx=9, dash=None):
    """带标题（可带副标题）的居中盒子。"""
    out = box(x, y, w, h, fill, stroke, rx, dash)
    if sub:
        out += txt(x + w / 2, y + h / 2 - 3, main, fs, tcol, weight="600")
        out += txt(x + w / 2, y + h / 2 + 14, sub, sfs, MUT)
    else:
        out += txt(x + w / 2, y + h / 2 + fs * 0.36, main, fs, tcol, weight="600")
    return out


def arrow(x1, y1, x2, y2, name, kind="a", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}" '
            f'stroke-width="1.5"{d} marker-end="url(#{kind}-{name})"/>')


def barrow(x1, y1, x2, y2, name):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{BLUE_T}" '
            f'stroke-width="1.8" marker-end="url(#b-{name})"/>')


def path(d, name, kind="a", dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.5"{dd} '
            f'marker-end="url(#{kind}-{name})"/>')


def note(x, y, text, size=11, color=MUT, anchor="start"):
    return txt(x, y, text, size, color, anchor)


# ---------------------------------------------------------------- 图 1：CI/CD 流水线
def d_pipeline():
    n = "pipeline"
    labels = ["提交", "检出", "装依赖", "Lint", "构建", "测试", "打包", "部署"]
    s = svg_open(n, 820, 158, "CI/CD 流水线示意")
    s += title(10, 20, "典型 CI/CD 流水线（前一步失败即中断）")
    for i, lb in enumerate(labels):
        x = 10 + i * 101
        acc = i >= 6
        s += cbox(x, 40, 90, 46, lb,
                  fill=BLUE_F if acc else BOX_F,
                  stroke=BLUE_S if acc else BOX_S)
        if i < len(labels) - 1:
            s += arrow(x + 91, 63, x + 100, 63, n)
    s += f'<line x1="10" y1="106" x2="605" y2="106" stroke="{BLUE_T}" stroke-width="2"/>'
    s += txt(307, 124, "持续集成 CI", 11.5, BLUE_T)
    s += f'<line x1="616" y1="106" x2="807" y2="106" stroke="{PUR_T}" stroke-width="2"/>'
    s += txt(711, 124, "持续交付 / 部署 CD", 11.5, PUR_T)
    s += note(10, 148, "前 6 步保证「代码始终可发布」，后 2 步负责「把可发布的东西送上线」。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 2：执行模型
def d_arch():
    n = "arch"
    s = svg_open(n, 820, 430, "GitHub Actions 执行模型")
    s += title(10, 20, "GitHub Actions 执行模型")
    s += cbox(300, 34, 220, 50, "Event 事件触发", "push · PR · schedule · 手动")
    s += arrow(410, 84, 410, 108, n)
    s += cbox(270, 110, 280, 48, "Workflow 工作流", ".github/workflows/ci.yml")
    s += arrow(410, 158, 410, 184, n)
    s += note(422, 175, "拆分为多个 Job（默认并行）", 11)
    s += cbox(230, 186, 360, 52, "Job 任务  × N", "每个 Job 独占一台干净机器",
              YEL_F, YEL_S)
    s += arrow(410, 238, 410, 264, n)
    s += cbox(180, 266, 460, 52, "Steps 步骤（同一 Job 内顺序执行）",
              "checkout → setup → 安装依赖 → 测试 → 构建")
    s += arrow(410, 318, 410, 344, n)
    s += cbox(270, 346, 280, 46, "Runner 运行器", "ubuntu-latest / self-hosted",
              GREEN_F, GREEN_S)
    s += note(10, 418, "关键：Job 之间不共享文件系统；Step 之间不共享 Shell 状态。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 3：CI / 持续交付 / 持续部署
def d_cicd_modes():
    n = "modes"
    s = svg_open(n, 820, 250, "CI、持续交付与持续部署的差异")
    s += title(10, 20, "CI / 持续交付 / 持续部署：差别只在最后一步")

    lanes = [
        ("CI 持续集成", ["提交", "构建", "测试", "打包", None, None]),
        ("持续交付 CD", ["提交", "构建", "测试", "打包", "人工审批", "部署生产"]),
        ("持续部署 CD", ["提交", "构建", "测试", "打包", "自动部署", None]),
    ]
    lane_y = [46, 106, 166]
    bw, gap = 101, 18
    for li, (name, cells) in enumerate(lanes):
        y = lane_y[li]
        s += txt(10, y + 24, name, 12, TXT, anchor="start", weight="600")
        for ci, cell in enumerate(cells):
            x = 100 + ci * (bw + gap)
            if cell is None:
                s += box(x, y, bw, 38, "#ffffff", BOX_S, 8, dash="4 3")
                s += txt(x + bw / 2, y + 24, "—", 12, "#b1b8bf")
            else:
                if cell == "人工审批":
                    f, st, tc = YEL_F, YEL_S, YEL_T
                elif cell in ("部署生产", "自动部署"):
                    f, st, tc = GREEN_F, GREEN_S, GREEN_T
                else:
                    f, st, tc = BOX_F, BOX_S, TXT
                s += cbox(x, y, bw, 38, cell, fill=f, stroke=st, tcol=tc, fs=12)
            if ci < len(cells) - 1 and cells[ci + 1] is not None and cell is not None:
                s += arrow(x + bw + 2, y + 19, x + bw + gap - 2, y + 19, n)
    s += note(10, 232, "「持续交付」与「持续部署」都缩写为 CD，唯一区别是最后一步由人点确认还是自动执行。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 4：触发器分类
def d_triggers():
    n = "trig"
    s = svg_open(n, 820, 320, "工作流触发器分类")
    s += title(10, 20, "on：五类触发器")
    s += cbox(20, 128, 120, 46, "on 触发器", fill=BLUE_F, stroke=BLUE_S, tcol=BLUE_T)
    items = [
        ("代码事件", "push · pull_request · release"),
        ("定时", "schedule（cron，UTC 时区）"),
        ("手动", "workflow_dispatch（可传参）"),
        ("外部系统", "repository_dispatch · workflow_run"),
        ("复用与调用", "workflow_call（被其他工作流调用）"),
    ]
    for i, (t, sub) in enumerate(items):
        y = 20 + i * 58
        s += cbox(200, y, 380, 44, t, sub, fs=13)
        cy = y + 22
        s += path(f"M140,151 H170 V{cy} H196", n)
    s += note(600, 46, "最常用：push / pull_request", 11)
    s += note(600, 64, "注意分支与路径过滤", 11)
    s += note(600, 122, "只在默认分支运行", 11)
    s += note(600, 180, "Actions 页面出现按钮", 11)
    s += note(600, 238, "需要 PAT 或 App token", 11)
    s += note(600, 296, "同组织内复用首选", 11)
    return s + "</svg>"


# ---------------------------------------------------------------- 图 5：上下文数据流
def d_context_flow():
    n = "ctx"
    s = svg_open(n, 820, 260, "上下文与表达式数据流")
    s += title(10, 20, "上下文 → 表达式 → 使用位置")
    s += box(20, 40, 200, 196, BOX_F, BOX_S)
    s += txt(120, 62, "上下文来源", 12.5, TXT, weight="700")
    ctxs = ["github（事件与引用）", "env（环境变量）", "secrets（密钥）",
            "vars（仓库变量）", "needs（上游 Job 输出）", "matrix（矩阵取值）",
            "steps（步骤输出）", "runner（运行器信息）"]
    for i, c in enumerate(ctxs):
        s += txt(32, 84 + i * 19, "· " + c, 10.5, MUT, anchor="start")

    s += cbox(300, 108, 190, 60, "${{ ... }}", "表达式求值",
              BLUE_F, BLUE_S, BLUE_T)
    s += barrow(224, 138, 296, 138, n)
    s += barrow(494, 138, 566, 138, n)

    s += box(570, 40, 230, 196, BOX_F, BOX_S)
    s += txt(685, 62, "使用位置", 12.5, TXT, weight="700")
    uses = ["if: 条件判断", "run: 命令参数", "with: 传给 Action",
            "env: 环境变量", "outputs: 输出", "concurrency: 并发组",
            "matrix: 矩阵取值", "permissions: 权限"]
    for i, u in enumerate(uses):
        s += txt(582, 84 + i * 19, "· " + u, 10.5, MUT, anchor="start")
    s += note(20, 252, "if 条件中通常不写 ${{ }}；secrets 不能直接在 if 中比较。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 6：权限与密钥模型
def d_security_model():
    n = "sec"
    s = svg_open(n, 820, 280, "权限与密钥的分层模型")
    s += title(10, 20, "权限与密钥：四层模型（内层可覆盖外层）")
    s += box(20, 34, 780, 200, "#ffffff", BOX_S, 12)
    s += txt(34, 54, "组织 / 仓库级：Secrets · Variables", 12, TXT, anchor="start", weight="600")

    s += box(52, 64, 716, 156, BOX_F, BOX_S, 11)
    s += txt(66, 84, "Environment 级：production / staging（可设必需审批人、限定分支）",
             11.5, PUR_T, anchor="start", weight="600")

    s += box(84, 94, 652, 116, YEL_F, YEL_S, 10)
    s += txt(98, 114, "Job 级：permissions（GITHUB_TOKEN 最小权限）",
             11.5, YEL_T, anchor="start", weight="600")

    s += box(116, 124, 588, 74, BLUE_F, BLUE_S, 9)
    s += txt(130, 144, "Step 级：env / with 传入", 11.5, BLUE_T, anchor="start", weight="600")
    s += txt(130, 166, "· Secret 在日志中自动打码（显示为 ***）", 10.5, MUT, anchor="start")
    s += txt(130, 184, "· Secret 不能作为 if 的比较对象，也不能作为变量名", 10.5, MUT, anchor="start")
    s += note(20, 258, "原则：权限最小化（默认 contents: read），能不用长期密钥就不用（优先 OIDC）。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 7：矩阵展开
def d_matrix():
    n = "mtx"
    s = svg_open(n, 820, 268, "矩阵构建展开")
    s += title(10, 20, "矩阵：一次定义、多组合并行")
    s += cbox(250, 32, 320, 54, "matrix: os × node-version",
              "2 × 3 = 6 个 Job 并行执行", BLUE_F, BLUE_S, BLUE_T)
    combos = [
        ("ubuntu-latest", "18", False), ("ubuntu-latest", "20", False), ("ubuntu-latest", "22", False),
        ("windows-latest", "18", True), ("windows-latest", "20", False), ("windows-latest", "22", False),
    ]
    bw, bh, gx, gy = 170, 42, 20, 20
    x0 = (820 - (3 * bw + 2 * gx)) / 2
    for i, (os_, nv, exc) in enumerate(combos):
        col, row = i % 3, i // 3
        x = x0 + col * (bw + gx)
        y = 118 + row * (bh + gy)
        s += cbox(x, y, bw, bh, f"{os_} / Node {nv}",
                  fill=RED_F if exc else BOX_F,
                  stroke=RED_S if exc else BOX_S,
                  tcol=RED_T if exc else TXT, fs=11.5)
        if exc:
            s += f'<line x1="{x + 14}" y1="{y + bh - 8}" x2="{x + bw - 14}" y2="{y + 8}" ' \
                 f'stroke="{RED_T}" stroke-width="1.5"/>'
    s += note(20, 250, "exclude 排除无效组合（此处 6 - 1 = 5 个 Job）；include 可为特定组合追加变量或新增组合。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 8：缓存流程
def d_cache_flow():
    n = "cache"
    s = svg_open(n, 820, 372, "缓存命中与未命中流程")
    s += title(10, 20, "缓存：命中走快路径，未命中走慢路径")
    s += cbox(300, 34, 220, 42, "计算 key", "hashFiles 生成稳定哈希")
    s += arrow(410, 76, 410, 100, n)
    s += cbox(300, 100, 220, 42, "查找缓存", "按 key + restore-keys")
    s += path("M410,142 V162 H160 V182", n)
    s += path("M410,142 V162 H660 V182", n)
    s += txt(240, 176, "命中", 11, GREEN_T, anchor="middle", weight="600")
    s += txt(580, 176, "未命中", 11, RED_T, anchor="middle", weight="600")

    s += cbox(60, 182, 200, 42, "恢复缓存", fill=GREEN_F, stroke=GREEN_S, tcol=GREEN_T)
    s += arrow(160, 224, 160, 242, n)
    s += cbox(60, 244, 200, 42, "安装依赖（快）", fill=GREEN_F, stroke=GREEN_S, tcol=GREEN_T)

    s += cbox(560, 182, 200, 42, "安装依赖（慢）", fill=RED_F, stroke=RED_S, tcol=RED_T)
    s += arrow(660, 224, 660, 242, n)
    s += cbox(560, 244, 200, 42, "保存缓存", fill=RED_F, stroke=RED_S, tcol=RED_T)

    s += path("M160,286 V298 H360 V304", n)
    s += path("M660,286 V298 H460 V304", n)
    s += cbox(300, 304, 220, 34, "继续构建 / 测试", fs=12)
    s += note(20, 362, "缓存有分支作用域：默认只能恢复当前分支与默认分支创建的缓存。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 9：Cache vs Artifact
def d_cache_vs_artifact():
    n = "cva"
    s = svg_open(n, 820, 268, "Cache 与 Artifact 的区别")
    s += title(10, 20, "Cache 与 Artifact：目的完全不同")
    rows = [
        ("目的", "加速（复用依赖）", "传递与留存（保存结果）"),
        ("生命周期", "可被命中复用，也可能失效", "明确的保留天数，到期删除"),
        ("典型内容", "node_modules / .m2 / pip 缓存", "构建产物、测试报告、日志"),
        ("使用场景", "同一分支的多次运行之间", "跨 Job 传递、跨运行留存"),
    ]
    s += cbox(20, 36, 240, 40, "Cache", "actions/cache · setup-* 内置", GREEN_F, GREEN_S, GREEN_T, fs=14)
    s += cbox(560, 36, 240, 40, "Artifact", "upload / download-artifact", PUR_F, PUR_S, PUR_T, fs=14)
    for i, (k, a, b) in enumerate(rows):
        y = 92 + i * 40
        s += cbox(20, y, 240, 34, a, fill=BOX_F, stroke=BOX_S, fs=10.5, tcol=MUT)
        s += cbox(560, y, 240, 34, b, fill=BOX_F, stroke=BOX_S, fs=10.5, tcol=MUT)
        s += txt(410, y + 22, k, 12, TXT, weight="600")
    s += note(20, 258, "一句话：要「快」用 Cache，要「留」用 Artifact。Job 之间传文件必须用 Artifact。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 10：Job 依赖编排
def d_job_dag():
    n = "dag"
    s = svg_open(n, 820, 280, "Job 依赖编排")
    s += title(10, 20, "Job 依赖：默认并行，needs 决定串行")
    s += cbox(340, 34, 140, 46, "lint", "无依赖", BLUE_F, BLUE_S, BLUE_T, fs=13)
    s += cbox(160, 122, 160, 46, "test", "needs: [lint]", fs=13)
    s += cbox(500, 122, 160, 46, "build", "needs: [lint]", fs=13)
    s += cbox(320, 210, 180, 48, "deploy", "needs: [test, build]", GREEN_F, GREEN_S, GREEN_T, fs=13)

    s += path("M410,80 V100 H240 V118", n)
    s += path("M410,80 V100 H580 V118", n)
    s += path("M240,168 V188 H410 V206", n)
    s += path("M580,168 V188 H410 V206", n)
    s += txt(730, 138, "test 与 build 可并行", 10.5, MUT, anchor="middle")
    s += txt(730, 156, "（都只依赖 lint）", 10.5, MUT, anchor="middle")
    s += note(20, 272, "Job 之间不共享文件系统：上游产物需用 upload-artifact / download-artifact 传递。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 11：前端 vs 后端
def d_fe_vs_be():
    n = "febe"
    s = svg_open(n, 820, 232, "前端与后端流水线对比")
    s += title(10, 20, "前端交付「文件」，后端交付「进程 / 镜像」")
    lanes = [
        ("前端", ["源码", "依赖安装", "构建", "静态产物", "CDN / Pages"], BLUE_F, BLUE_S, BLUE_T),
        ("后端", ["源码", "依赖安装", "测试(真实DB)", "容器镜像", "容器编排"], GREEN_F, GREEN_S, GREEN_T),
    ]
    bw, gap = 127, 16
    for li, (name, cells, f, st, tc) in enumerate(lanes):
        y = 46 + li * 78
        s += txt(10, y + 24, name, 12.5, TXT, anchor="start", weight="700")
        for ci, cell in enumerate(cells):
            x = 80 + ci * (bw + gap)
            acc = ci >= 3
            s += cbox(x, y, bw, 38, cell,
                      fill=f if acc else BOX_F,
                      stroke=st if acc else BOX_S,
                      tcol=tc if acc else TXT, fs=11)
            if ci < len(cells) - 1:
                s += arrow(x + bw + 1, y + 19, x + bw + gap - 1, y + 19, n)
    s += note(10, 206, "产物形态不同 → 缓存对象、产物留存方式、部署目标、门禁指标全部不同。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 12：四种后端语言
def d_backend_langs():
    n = "langs"
    s = svg_open(n, 820, 272, "四种后端语言的构建链路对照")
    s += title(10, 20, "四种后端语言：从安装到产物")
    heads = ["安装", "依赖安装", "构建", "测试", "产物"]
    cw, gap, x0 = 136, 8, 100
    for i, h in enumerate(heads):
        x = x0 + i * (cw + gap)
        s += cbox(x, 34, cw, 30, h, fill="#eef1f4", stroke=BOX_S, fs=11.5, rx=7)
    rows = [
        ("Java", ["setup-java", "mvn go-offline", "mvn package", "mvn verify", "target/*.jar"], YEL_F, YEL_S, YEL_T),
        ("Python", ["setup-python", "pip install -r", "无需构建", "pytest", "wheel"], BLUE_F, BLUE_S, BLUE_T),
        ("Node", ["setup-node", "npm ci", "npm run build", "npm test", "dist/"], GREEN_F, GREEN_S, GREEN_T),
        ("Go", ["setup-go", "go mod download", "go build", "go test ./...", "二进制"], PUR_F, PUR_S, PUR_T),
    ]
    for ri, (lang, cells, f, st, tc) in enumerate(rows):
        y = 76 + ri * 46
        s += cbox(10, y, 80, 38, lang, fill=f, stroke=st, tcol=tc, fs=12)
        for ci, cell in enumerate(cells):
            x = x0 + ci * (cw + gap)
            s += cbox(x, y, cw, 38, cell, fs=9.5)
    s += note(10, 264, "缓存目录：Java ~/.m2 或 ~/.gradle ｜ Python ~/.cache/pip ｜ Node ~/.npm ｜ Go ~/go/pkg/mod")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 13：排错决策树
def d_troubleshoot():
    n = "trb"
    s = svg_open(n, 820, 268, "排错决策树")
    s += title(10, 20, "工作流异常：先分类，再定位")
    s += cbox(300, 32, 220, 46, "工作流异常", fill=RED_F, stroke=RED_S, tcol=RED_T)
    cols = [
        ("① 根本没触发", ["on 的分支 / 路径过滤不匹配", "文件不在默认分支", "目录拼写或大小写错误"]),
        ("② Job 执行失败", ["看失败步骤日志（从后往前）", "权限不足 → 补 permissions", "命令本身失败 → 本地复现"]),
        ("③ 部署环节异常", ["Secret 名称 / 环境绑定", "等待人工审批未通过", "并发冲突或迁移未执行"]),
    ]
    bw = 250
    x0 = 15
    for i, (t, lines) in enumerate(cols):
        x = x0 + i * 267
        s += path(f"M410,78 V96 H{x + bw / 2} V110", n)
        s += cbox(x, 110, bw, 30, t, fill=YEL_F, stroke=YEL_S, tcol=YEL_T, fs=11.5, rx=7)
        s += box(x, 142, bw, 96, BOX_F, BOX_S, 9)
        for j, ln in enumerate(lines):
            s += txt(x + 12, 164 + j * 22, "· " + ln, 10.5, MUT, anchor="start")
    s += note(10, 260, "通用手段：ACTIONS_STEP_DEBUG=true 打开详细日志；actionlint 静态检查；echo 上下文值定位。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 14：多环境发布
def d_multi_env():
    n = "env"
    s = svg_open(n, 820, 250, "多环境发布")
    s += title(10, 20, "分支 → 环境 → 审批：三者绑定")
    branches = [("develop", 40), ("release/**", 104), ("main", 168)]
    for b, y in branches:
        s += cbox(20, y, 170, 44, b, "分支", fs=12.5)
    s += cbox(380, 62, 220, 60, "staging 环境", "自动部署 · 无审批",
              BLUE_F, BLUE_S, BLUE_T, fs=14)
    s += cbox(380, 152, 220, 60, "production 环境", "需人工审批 · 限定分支",
              GREEN_F, GREEN_S, GREEN_T, fs=14)
    s += path("M190,62 H300 V92 H376", n)
    s += path("M190,126 H300 V92", n)
    s += path("M190,190 H300 V182 H376", n)
    s += note(626, 84, "同名 Secret 在不同环境", 10.5)
    s += note(626, 102, "取不同值，工作流无需改代码", 10.5)
    s += note(626, 174, "把部署 Job 设为 Required 检查", 10.5)
    s += note(626, 192, "可防止绕过流程直接发布", 10.5)
    s += note(20, 240, "environment 名称必须与仓库 Settings → Environments 中创建的名称一致。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 15：PR 预览生命周期
def d_preview_lifecycle():
    n = "prev"
    s = svg_open(n, 820, 236, "PR 预览环境生命周期")
    s += title(10, 20, "PR 预览环境：从创建到销毁")
    steps = [
        ("PR 创建", "opened"),
        ("构建并部署", "独立预览地址"),
        ("评论预览地址", "github-script"),
        ("PR 更新", "synchronize"),
        ("重新部署", "更新同一条评论"),
        ("PR 关闭", "销毁资源"),
    ]
    y = 118
    s += f'<line x1="70" y1="{y}" x2="770" y2="{y}" stroke="{LINE}" stroke-width="2"/>'
    xs = [70, 210, 350, 490, 630, 770]
    for i, ((t, sub), x) in enumerate(zip(steps, xs)):
        last = i == len(steps) - 1
        f, st, tc = (RED_F, RED_S, RED_T) if last else (BLUE_F, BLUE_S, BLUE_T)
        s += f'<circle cx="{x}" cy="{y}" r="7" fill="{f}" stroke="{st}" stroke-width="2"/>'
        if i % 2 == 0:
            s += txt(x, 78, t, 11.5, TXT, weight="600")
            s += txt(x, 94, sub, 10, MUT)
            s += f'<line x1="{x}" y1="104" x2="{x}" y2="{y - 8}" stroke="{LINE}" stroke-dasharray="3 3"/>'
        else:
            s += txt(x, 152, t, 11.5, TXT, weight="600")
            s += txt(x, 168, sub, 10, MUT)
            s += f'<line x1="{x}" y1="{y + 8}" x2="{x}" y2="142" stroke="{LINE}" stroke-dasharray="3 3"/>'
    s += note(10, 200, "要点：先查找已有评论再更新，避免每次 push 刷出新评论；关闭事件负责回收资源。")
    s += note(10, 222, "来自 fork 的 PR 拿不到 Secrets，若预览部署依赖密钥需另行设计。")
    return s + "</svg>"


# ---------------------------------------------------------------- 图 16：GitOps
def d_gitops():
    n = "gitops"
    s = svg_open(n, 820, 236, "GitOps 发布模式")
    s += title(10, 20, "GitOps：CI 产出镜像与清单，集群侧自动同步")
    s += cbox(20, 76, 170, 62, "GitHub Actions", "CI：构建 + 推送",
              BLUE_F, BLUE_S, BLUE_T, fs=12.5)
    s += cbox(240, 34, 170, 52, "镜像仓库", "不可变 tag = sha")
    s += cbox(240, 128, 170, 52, "清单仓库", "manifests / values.yaml")
    s += cbox(470, 76, 150, 62, "ArgoCD / Flux", "拉取并同步")
    s += cbox(670, 76, 130, 62, "K8s 集群", "声明式收敛",
              GREEN_F, GREEN_S, GREEN_T, fs=12.5)
    s += path("M190,92 H215 V60 H236", n)
    s += path("M190,122 H215 V154 H236", n)
    s += path("M410,60 H440 V107 H466", n)
    s += path("M410,154 H440 V107", n)
    s += barrow(620, 107, 666, 107, n)
    s += txt(650, 130, "自动同步", 10, BLUE_T)
    s += note(20, 210, "回滚 = revert 清单仓库的那次提交，集群自动收敛回上一版本，全程可审计。")
    s += note(20, 228, "对比传统模式：CI 不再直接登录生产集群，权限边界更清晰。")
    return s + "</svg>"


DIAGRAMS = {
    "pipeline": d_pipeline,
    "arch": d_arch,
    "cicd-modes": d_cicd_modes,
    "triggers": d_triggers,
    "context-flow": d_context_flow,
    "security-model": d_security_model,
    "matrix": d_matrix,
    "cache-flow": d_cache_flow,
    "cache-vs-artifact": d_cache_vs_artifact,
    "job-dag": d_job_dag,
    "fe-vs-be": d_fe_vs_be,
    "backend-langs": d_backend_langs,
    "troubleshoot-tree": d_troubleshoot,
    "multi-env": d_multi_env,
    "preview-lifecycle": d_preview_lifecycle,
    "gitops": d_gitops,
}


def render(name):
    return DIAGRAMS[name]()


if __name__ == "__main__":
    import xml.etree.ElementTree as ET
    for k in DIAGRAMS:
        svg = render(k)
        try:
            ET.fromstring(svg)
            print(f"OK   {k:22s} {len(svg):6d} bytes")
        except Exception as e:
            print(f"FAIL {k:22s} -> {e}")
