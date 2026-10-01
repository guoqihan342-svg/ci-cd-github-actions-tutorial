# 后端项目 · Python：FastAPI + PostgreSQL → Docker → 服务器

## 目标

- PR 阶段在**真实 PostgreSQL** 上跑 pytest，并做代码检查与类型检查。
- `main` 分支构建镜像、在**启动新容器之前**执行 Alembic 迁移，再滚动重启。

## 文件

```
.github/workflows/
├── ci.yml        # 真实数据库测试 + ruff + mypy + Alembic
└── deploy.yml    # 镜像构建 → 推送 → 迁移 → 部署
Dockerfile        # python:3.12-slim
```

## 前置条件

1. 准备 `requirements.txt` 与 `requirements-dev.txt`（建议用 `pip-compile` 生成锁定版本）。
2. 服务器上准备 `/opt/my-py-api/docker-compose.yml`：

```yaml
services:
  api:
    image: ghcr.io/<owner>/<repo>:latest
    restart: unless-stopped
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: postgres:16
    restart: unless-stopped
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

volumes:
  pgdata:
```

3. 配置 Secrets：`SSH_HOST`、`SSH_USER`、`SSH_KEY`、`GHCR_TOKEN`。

## 关键要点

| 要点 | 说明 |
| --- | --- |
| 日志实时性 | `PYTHONUNBUFFERED=1` 必须设置，否则容器日志延迟严重 |
| 层缓存 | 先 `COPY requirements.txt` 装依赖，再 `COPY . .`，代码改动不会重装依赖 |
| 迁移顺序 | `alembic upgrade head` 在 `docker compose up -d` **之前**执行 |
| 优雅退出 | 生产用 `uvicorn --workers N` 或 gunicorn，确保正确处理 `SIGTERM`，避免部署期间丢请求 |
| 依赖锁定 | 提交锁定文件（`requirements.txt` / `uv.lock` / `poetry.lock`），保证构建可复现 |
| 矩阵策略 | 应用项目固定一个 Python 版本即可；多版本矩阵只对"库"必要 |

## 三种依赖管理方式的取舍

| 方式 | 优点 | 适用 |
| --- | --- | --- |
| `pip` + `requirements.txt` | 最通用、零学习成本 | 大多数项目、Docker 构建 |
| `uv` | 极快，锁定与虚拟环境一体化 | 新项目、对 CI 速度敏感 |
| `Poetry` | 依赖与打包统一管理 | 需要发布到 PyPI 的库 |

## 与 Java / Node 后端项目的差异

| 维度 | Python | Java | Node |
| --- | --- | --- | --- |
| 依赖缓存 | `~/.cache/pip` | `~/.m2/repository` | `~/.npm` |
| 构建产物 | 无（直接跑源码） | `target/*.jar` | `dist/` |
| 迁移方式 | 独立 `alembic upgrade head` 步骤 | 启动时 Flyway/Liquibase | 独立 `prisma migrate deploy` 步骤 |
| 镜像基础 | `python:3.12-slim` | `eclipse-temurin:21-jre` | `node:20-slim` |
