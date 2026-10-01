# 完整项目实战（6 个端到端示例）

对应教程「第 12 章 完整项目实战」。按「**前端 / 后端 / 通用**」三类划分，后端再按 **Java / Python / Node** 区分。

## 前端

| 目录 | 技术栈 | 覆盖能力 |
| --- | --- | --- |
| [`01-frontend-react-pages`](./01-frontend-react-pages/) | Vite + React | CI 检查、GitHub Pages 发布、PR 预览环境与清理 |

## 后端

| 目录 | 技术栈 | 覆盖能力 |
| --- | --- | --- |
| [`02-backend-java-springboot`](./02-backend-java-springboot/) | Java + Spring Boot + Maven | JDK 矩阵、真实 PG 测试、多阶段镜像、Flyway 迁移、SSH 部署 |
| [`03-backend-python-fastapi`](./03-backend-python-fastapi/) | Python + FastAPI + PostgreSQL | ruff/mypy、真实 PG 测试、Alembic 迁移、SSH 部署 |
| [`04-backend-node-express`](./04-backend-node-express/) | Node + Express + PostgreSQL | `services` 真实库测试、Prisma 迁移、GHCR、SSH 部署 |

## 通用

| 目录 | 技术栈 | 覆盖能力 |
| --- | --- | --- |
| [`05-pipeline-python-daily`](./05-pipeline-python-daily/) | Python | `schedule` 定时、Artifact 报告留存、企业微信通知 |
| [`06-library-typescript-npm`](./06-library-typescript-npm/) | TypeScript | 多版本矩阵、Changesets 自动发版、npm provenance |

## 三种后端栈的差异对照

| 维度 | Java | Python | Node |
| --- | --- | --- | --- |
| 安装 Action | `actions/setup-java@v4` | `actions/setup-python@v5` | `actions/setup-node@v4` |
| 依赖管理 | Maven / Gradle | pip / uv / Poetry | npm / pnpm / yarn |
| 依赖缓存 | `~/.m2/repository` | `~/.cache/pip` | `~/.npm` |
| 构建产物 | `target/*.jar` | 无（直接跑源码） | `dist/` |
| 数据库迁移 | 启动时 Flyway / Liquibase | 独立 `alembic upgrade head` | 独立 `prisma migrate deploy` |
| 运行镜像基础 | `eclipse-temurin:21-jre` | `python:3.12-slim` | `node:20-slim` |
| 需要 Wrapper | 是（`mvnw` / `gradlew`） | 否 | 否 |

## 使用方式

进入对应项目目录，把其中的 `.github/`（以及 `Dockerfile`）复制到你的项目根目录，再按该目录下 `README.md` 的说明替换占位值并配置 Secrets。

## 通用约定

- 所有工作流均显式声明 `permissions`，遵循权限最小化。
- 所有第三方 Action 均使用主版本号；**生产环境建议进一步锁定到 commit SHA**。
- 涉及部署的工作流均使用 `concurrency` 防止并发冲突。
- 需要人工审批的生产部署使用 `environment: production`，请在仓库 **Settings → Environments** 中配置审批人。
