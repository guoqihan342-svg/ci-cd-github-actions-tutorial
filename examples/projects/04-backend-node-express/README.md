# 后端项目 · Node：Express + PostgreSQL → GHCR → 服务器

## 目标

- PR 阶段使用**真实的 PostgreSQL** 跑测试（通过 `services`），避免 mock 与生产行为不一致。
- `main` 分支构建镜像推送到 GHCR，部署到服务器，并在启动新容器前执行数据库迁移。

## 文件

```
.github/workflows/
├── ci.yml        # PR 检查 + 真实数据库测试
└── deploy.yml    # 构建镜像 → 部署 → 数据库迁移
```

## 需要在服务器上准备

`/opt/my-api/docker-compose.yml`（示例）：

```yaml
services:
  api:
    image: ghcr.io/<owner>/<repo>:latest
    restart: unless-stopped
    env_file: .env
    ports:
      - "3000:3000"
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

## 需要配置的 Secrets

| 名称 | 用途 |
| --- | --- |
| `SSH_HOST` / `SSH_USER` / `SSH_KEY` | 服务器 SSH 连接 |
| `GHCR_TOKEN` | 服务器拉取私有镜像的令牌 |

## 注意事项

- `${GITHUB_REPOSITORY,,}` 把仓库名转为小写，GHCR 要求镜像路径全小写。
- 迁移在 `docker compose up -d` **之前**执行，避免新代码连到旧表结构。
- `appleboy/ssh-action` 属第三方 Action，生产环境建议锁定到 commit SHA。
- 建议在服务器上用 `:${GITHUB_SHA}` 这样的不可变 tag 部署，便于回滚（参考教程 13.4）。
