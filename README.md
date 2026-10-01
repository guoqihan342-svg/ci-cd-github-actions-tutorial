# CI/CD 与 GitHub Actions 配置完全教程

从概念到落地的系统性指南：理解 CI/CD 的本质，掌握 GitHub Actions 的完整配置语法，按「前端 / 后端」与「Java / Python / Node / Go」分栈落地，并能独立搭建生产级流水线。

## 内容概览

| 项目 | 数量 |
| --- | --- |
| 正文章节 | 13 章 + 附录 |
| 正文行数 | 约 3200 行 |
| 流程图 | 16 张（内联 SVG，浅色主题） |
| 代码块 | 107 个 |
| 对照表格 | 23 张 |
| 可复用工作流示例 | 19 个 YAML |
| 端到端项目 | 6 个 |
| FAQ | 32 条 |

## 章节结构

| 章节 | 内容 |
| --- | --- |
| 第 1 章 | 什么是 CI/CD——CI / 持续交付 / 持续部署的区别 |
| 第 2 章 | GitHub Actions 概览——六大组件与执行模型 |
| 第 3 章 | 第一个工作流——目录结构与逐行讲解 |
| 第 4 章 | 工作流语法详解——触发器、jobs、steps、`strategy`、`services`、`container` |
| 第 5 章 | 核心概念深入——上下文与表达式、Secrets、权限、Workflow 命令、OIDC |
| 第 6 章 | 进阶特性——矩阵、缓存、产物、依赖编排、并发、表达式函数、YAML 锚点 |
| 第 7 章 | 实战示例（**按技术栈区分**）——前端 / Java / Python / Node / Go / 容器化 / 部署 |
| 第 8 章 | 复用与组织——可复用工作流、复合 Action |
| 第 9 章 | 安全与最佳实践 |
| 第 10 章 | 排错与调试 |
| 第 11 章 | 业界常见场景（14 个） |
| 第 12 章 | 完整项目实战（**6 个端到端项目**） |
| 第 13 章 | FAQ 常见问题（32 条） |
| 附录 A | 速查表、场景索引、技术栈索引 |

## 阅读方式

推荐打开 **`CI-CD-GitHub配置完全教程.html`**（含全部流程图与侧边目录，双击用浏览器打开即可）。

> 注意：流程图只存在于 HTML 版。Markdown 中对应位置是 `<!--DIAGRAM:xxx-->` 占位注释，在 GitHub 上不可见。

## 目录结构

```
.
├── CI-CD-GitHub配置完全教程.html   # 推荐阅读：含 16 张流程图
├── CI-CD-GitHub配置完全教程.md     # 正文源文件
├── diagrams.py                     # 配图模块：16 张 SVG 的生成代码
├── build_html.py                   # 构建脚本：Markdown → HTML
└── examples/
    ├── README.md
    ├── github-workflows/           # 通用工作流（6 个）
    ├── github-actions/             # 复合 Action 示例
    └── projects/                   # 6 个端到端项目
        ├── 01-frontend-react-pages/
        ├── 02-backend-java-springboot/
        ├── 03-backend-python-fastapi/
        ├── 04-backend-node-express/
        ├── 05-pipeline-python-daily/
        └── 06-library-typescript-npm/
```

## 快速开始

### 使用示例工作流

把需要的文件复制到你的项目：

```bash
# 通用工作流
cp examples/github-workflows/ci-node.yml your-repo/.github/workflows/

# 或整个项目模板
cp -r examples/projects/04-backend-node-express/.github your-repo/
```

各示例目录下的 `README.md` 说明了需要配置的 Secrets 与占位值。

### 重新生成 HTML

修改 Markdown 后：

```bash
pip install markdown pygments
python build_html.py
```

### 新增一张图

1. 在 `diagrams.py` 中新增一个返回 SVG 字符串的函数，并注册到 `DIAGRAMS` 字典；
2. 在 Markdown 对应位置加入 `<!--DIAGRAM:图名-->`；
3. 重新运行 `build_html.py`。

## 技术栈覆盖

- **前端**：React / Vue / Next.js / Nuxt / Angular
- **后端**：Java（Maven / Gradle / Spring Boot）、Python（pip / uv / Poetry / FastAPI / Django）、Node（Express / NestJS）、Go
- **部署**：GitHub Pages、CDN、Docker / GHCR、SSH、K8s + GitOps（ArgoCD / Flux）
- **移动端**：iOS（macOS runner + TestFlight）、Android（Gradle + APK）

## 官方参考

- 工作流语法：https://docs.github.com/actions/reference/workflow-syntax-for-github-actions
- 事件触发：https://docs.github.com/actions/reference/events-that-trigger-workflows

## 许可

本文档为技术教程，可自由用于学习与团队内部培训。
