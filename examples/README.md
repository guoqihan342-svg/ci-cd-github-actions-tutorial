# 示例文件使用说明

本目录提供可直接复制到项目中使用的 GitHub Actions 配置示例。

## 目录结构

```
examples/
├── github-workflows/            # 复制到项目 .github/workflows/ 下
│   ├── ci-node.yml              # Node.js 完整 CI（lint → 矩阵测试 → 构建产物）
│   ├── ci-python.yml            # Python CI（多版本矩阵 + 覆盖率）
│   ├── docker-build-push.yml    # 打 tag 时构建并推送多架构镜像
│   ├── deploy-ssh.yml           # 通过 SSH 部署到服务器（含 Environment 审批）
│   ├── deploy-pages.yml         # 部署到 GitHub Pages
│   └── reusable-test.yml        # 可复用工作流（被其他工作流调用）
├── github-actions/              # 复制到项目 .github/actions/ 下
│   └── setup-and-build/
│       └── action.yml           # 复合 Action：安装 Node + 装依赖 + 构建
└── projects/                       # 6 个端到端完整项目（对应教程第 12 章）
    ├── 01-frontend-react-pages/    # 前端 · Vite + React → Pages + PR 预览
    ├── 02-backend-java-springboot/ # 后端 · Java（Maven）→ 多阶段镜像 → 服务器
    ├── 03-backend-python-fastapi/  # 后端 · Python（FastAPI）→ 镜像 → 服务器
    ├── 04-backend-node-express/    # 后端 · Node（Express）→ GHCR → 服务器
    ├── 05-pipeline-python-daily/   # 通用 · 定时数据管道 → 报告 + 通知
    └── 06-library-typescript-npm/  # 通用 · 开源库 → Changesets 自动发版
```

## 使用方法

1. 在项目根目录创建 `.github/workflows/`（若不存在）。
2. 将 `github-workflows/` 下需要的文件复制过去，按注释修改参数（镜像名、分支名等）。
3. 若使用复合 Action，把 `github-actions/setup-and-build/` 整个目录复制到项目的 `.github/actions/` 下。
4. 提交并推送到 GitHub，打开仓库 **Actions** 标签页查看运行结果。

## 需要配置的 Secrets

| 工作流 | 需要的 Secret |
| --- | --- |
| `docker-build-push.yml` | `DOCKER_USERNAME`、`DOCKER_PASSWORD` |
| `deploy-ssh.yml` | `SSH_HOST`、`SSH_USER`、`SSH_KEY`、`SSH_PORT` |
| `reusable-test.yml` | `NPM_TOKEN`（可选，仅私有 registry 需要） |

配置路径：仓库 **Settings → Secrets and variables → Actions → New repository secret**。

## 注意事项

- 示例中的分支名（`main`）、镜像名（`yourname/yourapp`）、部署路径（`/var/www/app`）均为占位值，请按实际情况修改。
- `deploy-ssh.yml` 使用 `git reset --hard`，会丢弃服务器上的本地改动，请确认目标目录是纯部署目录。
- 所有示例均显式声明了 `permissions`，遵循权限最小化原则。
