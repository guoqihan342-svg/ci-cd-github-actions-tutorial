# 后端项目 · Java：Spring Boot + Maven → Docker → 服务器

## 目标

- PR 阶段在**真实 PostgreSQL** 上跑单元 + 集成测试，并做多 JDK 矩阵验证。
- `main` 分支用**多阶段构建**产出精简镜像，推送到 GHCR 后部署到服务器。

## 文件

```
.github/workflows/
├── ci.yml        # JDK 矩阵 + 真实数据库测试 + 打包
└── deploy.yml    # 多阶段镜像构建 → 推送 → SSH 部署
Dockerfile        # 多阶段构建（Maven 构建 → JRE 运行）
```

## 前置条件

1. **提交 Maven Wrapper**：在项目根目录执行 `mvn wrapper:wrapper`，生成 `mvnw` / `mvnw.cmd` / `.mvn/`。
   CI 中统一用 `./mvnw` 调用，保证 CI 与本地 Maven 版本一致。
2. 服务器上准备 `/opt/my-java-api/docker-compose.yml`：

```yaml
services:
  api:
    image: ghcr.io/<owner>/<repo>:latest
    restart: unless-stopped
    env_file: .env
    ports:
      - "8080:8080"
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
| 多阶段构建 | 构建阶段用 `maven:3.9-eclipse-temurin-21`，运行阶段只留 `eclipse-temurin:21-jre`，镜像从约 700 MB 降到约 200 MB |
| 层缓存 | 先 `COPY pom.xml` + `dependency:go-offline`，再 `COPY src`，代码改动不会导致重装依赖 |
| JVM 内存 | `-XX:MaxRAMPercentage=75` 让堆随容器内存限制自动调整，避免 OOM Kill |
| 数据库迁移 | Java 侧通常交给 **Flyway / Liquibase 在应用启动时执行**，因此迁移必须**向后兼容** |
| JDK 版本 | Spring Boot 3.x 要求 JDK 17+；矩阵用于验证兼容性，应用项目通常固定一个 LTS |
| 构建命令 | `./mvnw -B verify` 跑完整生命周期（含集成测试），比 `mvn test` 更接近可发布状态 |

## 与 Python / Node 后端项目的差异

| 维度 | Java | Python | Node |
| --- | --- | --- | --- |
| 依赖缓存 | `~/.m2/repository` | `~/.cache/pip` | `~/.npm` |
| 构建产物 | `target/*.jar` | 无（直接跑源码） | `dist/` |
| 迁移方式 | 应用启动时 Flyway/Liquibase | 独立 `alembic upgrade head` 步骤 | 独立 `prisma migrate deploy` 步骤 |
| 镜像体积 | 约 200 MB（JRE） | 约 150 MB（slim） | 约 180 MB（node:20-slim） |
