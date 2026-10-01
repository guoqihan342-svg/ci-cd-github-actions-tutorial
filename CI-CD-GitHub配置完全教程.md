# CI/CD 与 GitHub Actions 配置完全教程

> 一份从概念到落地的系统性指南：理解 CI/CD 的本质，掌握 GitHub Actions 的完整配置语法，并能独立搭建生产级流水线。
>
> 适用对象：后端 / 前端 / 全栈 / DevOps 工程师，以及需要为团队搭建自动化流程的技术负责人。
> 阅读前提：了解 Git 基本操作（commit / push / branch / pull request），会写 YAML 更佳。

---

## 目录

1. [第 1 章 什么是 CI/CD](#第-1-章-什么是-cicd)
2. [第 2 章 GitHub Actions 概览](#第-2-章-github-actions-概览)
3. [第 3 章 第一个工作流](#第-3-章-第一个工作流)
4. [第 4 章 工作流语法详解](#第-4-章-工作流语法详解)
5. [第 5 章 核心概念深入](#第-5-章-核心概念深入)
6. [第 6 章 进阶特性](#第-6-章-进阶特性)
7. [第 7 章 实战示例](#第-7-章-实战示例)
8. [第 8 章 复用与组织](#第-8-章-复用与组织)
9. [第 9 章 安全与最佳实践](#第-9-章-安全与最佳实践)
10. [第 10 章 排错与调试](#第-10-章-排错与调试)
11. [第 11 章 业界常见场景](#第-11-章-业界常见场景)
12. [第 12 章 完整项目实战](#第-12-章-完整项目实战)
13. [第 13 章 FAQ 常见问题](#第-13-章-faq-常见问题)
14. [附录 A 速查表](#附录-a-速查表)

---

## 第 1 章 什么是 CI/CD

### 1.1 三个核心概念

<!--DIAGRAM:cicd-modes-->

CI/CD 是三个相邻但含义不同的术语的组合：

| 缩写 | 全称 | 中文 | 本质 |
| --- | --- | --- | --- |
| **CI** | Continuous Integration | 持续集成 | 开发者频繁地把代码合并到主干，每次合并都自动触发**构建 + 测试**，尽早发现冲突与缺陷 |
| **CD** | Continuous Delivery | 持续交付 | 在 CI 基础上，保证代码随时处于**可发布**状态，产物自动打包，但**上线需人工点确认** |
| **CD** | Continuous Deployment | 持续部署 | 在持续交付基础上更进一步，**通过测试即自动上线**，全程无人工干预 |

> 关键区分：**持续交付**与**持续部署**都缩写为 CD。区别只有一点 —— 最后一步"部署到生产"是自动还是手动。

### 1.2 没有 CI/CD 时会发生什么

传统"手工发布"模式的典型问题：

1. **集成地狱**：多人各自开发数周后合并，冲突集中爆发，修复成本极高。
2. **环境漂移**：本地能跑、测试环境报错、生产又不一样，"在我机器上是好的"成为常态。
3. **发布恐惧**：发布流程冗长且依赖个别"知道怎么操作"的人，每次上线都是高风险事件。
4. **反馈滞后**：Bug 在合并数天后才被发现，回溯成本成倍增长。

### 1.3 CI/CD 流水线的典型阶段

<!--DIAGRAM:pipeline-->

一条完整的流水线通常按以下顺序推进，前一步失败即中断：

```
代码提交 → 检出代码 → 安装依赖 → 代码检查(Lint) → 构建(Build)
        → 单元测试 → 集成测试 → 打包产物 → 部署(预发) → 验收 → 部署(生产)
```

其中：

- **快速反馈优先**：把耗时最短、最容易失败的检查（Lint、单元测试）放在最前面。
- **同类环境一致**：CI 中运行的步骤，应尽可能与生产部署使用的命令一致。
- **失败即停止**：任何一步失败，后续步骤不再执行（除非显式配置 `if: always()`）。

---

## 第 2 章 GitHub Actions 概览

### 2.1 它是什么

GitHub Actions 是 GitHub 内置的 **CI/CD 与自动化平台**。只要代码托管在 GitHub，就可以在仓库中直接定义流水线，无需自建 Jenkins 之类的服务器。它与 Pull Request、Issue、Release 等 GitHub 事件天然打通。

### 2.2 六个核心组件

理解下面六个概念，就理解了 GitHub Actions 的全部骨架：

| 组件 | 英文 | 说明 |
| --- | --- | --- |
| **工作流** | Workflow | 一个可配置的自动化流程，用一个 YAML 文件描述，存放于 `.github/workflows/` |
| **事件** | Event | 触发工作流的条件，如 `push`、`pull_request`、`schedule`、`workflow_dispatch` |
| **任务** | Job | 工作流中的一组步骤。默认**并行**执行；多个 Job 运行在各自独立的虚拟机中 |
| **步骤** | Step | Job 内的最小执行单元，可以是一条命令（`run`）或一个动作（`uses`） |
| **动作** | Action | 可复用的最小功能单元，如 `actions/checkout`、`actions/setup-node` |
| **运行器** | Runner | 执行 Job 的服务器。GitHub 提供托管运行器，也可自建 self-hosted runner |

### 2.3 运行机制（关键心智模型）

<!--DIAGRAM:arch-->

理解以下三点，可避免绝大多数配置错误：

1. **每个 Job 是一个全新的、干净的机器**。Job 之间不共享文件系统、不共享已安装的依赖。若 Job B 需要 Job A 的产物，必须通过 **Artifacts** 或 **Cache** 显式传递。
2. **同一 Job 内的 Step 共享同一个工作区**，前一步生成的文件，后一步可直接访问。
3. **Step 之间默认不共享 Shell 状态**。`export FOO=bar` 在下一个 step 中**不会**生效，必须写入 `$GITHUB_ENV`。

### 2.4 计费与免费额度

- **公开仓库**：使用 GitHub 托管的运行器**完全免费**。
- **私有仓库**：每月有一定的免费分钟数（不同套餐额度不同），超出后按分钟计费；不同操作系统单价不同，Linux 最便宜。
- **自建运行器（self-hosted）**：不消耗 GitHub 分钟数，但需自行维护机器与安全。

---

## 第 3 章 第一个工作流

### 3.1 目录结构

在仓库**根目录**下创建：

```
your-repo/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── src/
└── ...
```

规则：

- 目录必须精确为 `.github/workflows/`（大小写敏感）。
- 每个文件是一个独立工作流，文件后缀为 `.yml` 或 `.yaml`。
- 一个仓库可以有任意多个工作流文件。

### 3.2 Hello World 工作流

创建 `.github/workflows/hello.yml`：

```yaml
name: Hello CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - name: 打印问候
        run: echo "Hello, GitHub Actions!"
      - name: 查看环境
        run: |
          echo "运行器系统: $RUNNER_OS"
          echo "触发者: ${{ github.actor }}"
```

把它 push 到 `main` 分支，打开仓库的 **Actions** 标签页，即可看到运行记录。

### 3.3 逐行讲解

| 代码 | 含义 |
| --- | --- |
| `name: Hello CI` | 工作流显示名称，可省略（省略则用文件路径作名字） |
| `on:` | 触发器配置块 |
| `push: branches: [main]` | 仅在向 `main` 分支推送时触发 |
| `pull_request: branches: [main]` | 当有 PR 目标为 `main` 时触发 |
| `jobs:` | 任务集合 |
| `greet:` | Job 的 ID（自定义标识符，用于 Job 间引用） |
| `runs-on: ubuntu-latest` | 指定运行器系统镜像 |
| `steps:` | 步骤列表，**按顺序执行** |
| `- name:` | 步骤的可读名称（可选，但强烈建议写） |
| `run: \|` | 执行多行 Shell 命令 |
| `${{ ... }}` | 表达式语法，用于引用上下文变量 |

---

## 第 4 章 工作流语法详解

下面按 YAML 的层级，自上而下讲解每个关键字段。

### 4.1 name

```yaml
name: CI Pipeline
```

可选。出现在 Actions 页面左侧列表，以及 PR 检查列表中。

### 4.2 on —— 触发器（重点）

<!--DIAGRAM:triggers-->

`on` 决定工作流"何时跑"。常用类型如下：

**① 分支/路径过滤**

```yaml
on:
  push:
    branches:
      - main
      - 'release/**'      # 支持通配符
    branches-ignore:
      - 'docs/**'
    paths:
      - 'src/**'          # 仅当这些路径变化时触发
      - 'package.json'
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

> 注意：`branches` 与 `branches-ignore` **不能同时使用**；`paths` 与 `paths-ignore` 亦然。

**② PR 事件**

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
```

`pull_request` 触发的是**合并后的模拟结果**（merge commit），而非分支本身；若想直接测试分支 HEAD，用 `pull_request_target`（但需注意其安全模型，见第 9 章）。

**③ 定时任务（Cron）**

```yaml
on:
  schedule:
    # 分 时 日 月 周，使用 UTC 时间
    - cron: '0 2 * * *'      # 每天 UTC 02:00（北京时间 10:00）
```

> 定时任务只在**默认分支**上运行；且 GitHub 高负载时可能延迟数分钟。

**④ 手动触发**

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: '部署环境'
        required: true
        default: 'staging'
        type: choice
        options: [staging, production]
      dry_run:
        type: boolean
        default: false
```

配置后，Actions 页面会出现 **Run workflow** 按钮，可手动填入参数。

**⑤ 其他常用事件**

```yaml
on:
  release:
    types: [published]
  workflow_run:                 # 由另一个工作流完成后触发
    workflows: ["CI"]
    types: [completed]
  repository_dispatch:          # 外部系统通过 API 触发
    types: [deploy]
```

### 4.3 jobs

```yaml
jobs:
  build:
    name: 构建
    runs-on: ubuntu-latest
    needs: [lint]              # 依赖其他 Job
    if: github.ref == 'refs/heads/main'
    timeout-minutes: 30
    strategy:
      matrix:
        node-version: [18, 20, 22]
    steps:
      - run: echo "构建中"
```

关键字段：

| 字段 | 作用 |
| --- | --- |
| `runs-on` | 运行器类型（见 4.5） |
| `needs` | 声明依赖的 Job，实现串行/编排 |
| `if` | 条件表达式，为 false 则跳过该 Job |
| `strategy.matrix` | 矩阵构建（见 6.1） |
| `strategy.fail-fast` | 矩阵中某组合失败是否取消其他组合，默认 `true` |
| `timeout-minutes` | Job 超时时间，默认 360 分钟 |
| `continue-on-error` | 该 Job 失败是否不阻塞整个工作流 |
| `env` | Job 级环境变量 |
| `outputs` | 供下游 Job 读取的输出 |

### 4.4 steps

Step 分两种：

**① 执行命令（run）**

```yaml
- name: 运行测试
  run: npm test
  working-directory: ./packages/core   # 指定工作目录
  shell: bash                          # 指定 shell
  env:
    NODE_ENV: test
```

**② 使用动作（uses）**

```yaml
- name: 检出代码
  uses: actions/checkout@v4
  with:
    fetch-depth: 0          # 传给 action 的输入参数
```

其他常用属性：

```yaml
- name: 即使前面失败也执行
  if: always()              # 或 failure() / success() / cancelled()
  run: echo "清理中"

- name: 允许失败
  continue-on-error: true
  run: npm run optional-check

- id: build_step            # 设置 id，便于后续引用其 outputs
  run: echo "version=1.2.3" >> $GITHUB_OUTPUT
```

### 4.5 runs-on —— 运行器选择

**GitHub 托管运行器**（常用标签）：

| 标签 | 系统 |
| --- | --- |
| `ubuntu-latest` / `ubuntu-22.04` | Ubuntu Linux（最常用、最便宜） |
| `windows-latest` | Windows Server |
| `macos-latest` | macOS（ARM，可构建 iOS） |
| `macos-13` | macOS Intel |

**自建运行器**：在机器上安装 runner 后，可打自定义标签：

```yaml
runs-on: [self-hosted, linux, x64, gpu]
```

### 4.6 env —— 环境变量

变量可在三个层级定义，作用域由内向外覆盖：

```yaml
env:                          # 工作流级
  APP_NAME: my-app

jobs:
  build:
    env:                      # Job 级
      NODE_ENV: production
    steps:
      - env:                  # Step 级（优先级最高）
          DEBUG: 'true'
        run: echo "$APP_NAME / $NODE_ENV / $DEBUG"
```

**在步骤间传递变量**（必须写入 `$GITHUB_ENV`）：

```yaml
- run: echo "VERSION=1.2.3" >> $GITHUB_ENV
- run: echo "版本是 $VERSION"     # 下一个 step 可以读到
```

---

### 4.7 strategy —— 矩阵与执行策略全字段

```yaml
strategy:
  fail-fast: false          # 某个组合失败时，是否取消其余组合（默认 true）
  max-parallel: 2           # 同时运行的组合上限（默认不限）
  matrix:
    os: [ ubuntu-latest, windows-latest ]
    node-version: [ 18, 20, 22 ]
    include:                # 追加变量，或新增组合
      - os: ubuntu-latest
        node-version: 20
        experimental: true
    exclude:                # 排除组合
      - os: windows-latest
        node-version: 18
```

| 字段 | 默认 | 作用 | 常见用法 |
| --- | --- | --- | --- |
| `fail-fast` | `true` | 任一组合失败即取消其余组合 | 设为 `false` 以拿到完整的失败矩阵 |
| `max-parallel` | 不限 | 限制同时运行的组合数 | 保护算力有限的自建 Runner 或外部 API 配额 |
| `matrix` | — | 组合维度定义 | 见 6.1 |
| `matrix.include` | — | 追加变量或新增组合 | 给特定组合打标记，如 `experimental: true` |
| `matrix.exclude` | — | 排除组合 | 剔除无效或已知失败的组合 |

> 组合数 = 各维度取值数相乘，减去 `exclude` 命中的数量，再加上 `include` 新增的组合数。

**成本提醒**：矩阵是 CI 费用增长最快的来源。推荐「分级矩阵」——PR 只跑 1~2 个关键组合，合并到 `main` 后再跑全量。

### 4.8 services —— 服务容器

`services` 让 Job 在运行时旁边拉起额外的 Docker 容器，最常用于**让集成测试连上真实数据库**。

```yaml
jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - run: psql "postgresql://postgres:postgres@localhost:5432/test" -c 'select 1'
```

要点：

- **必须配健康检查**：`--health-cmd` 等参数让 GitHub 等待服务真正就绪后再开始执行步骤。缺少它会出现"数据库还没起来"的偶发失败。
- 服务容器与 Job 通过 `localhost:<端口>` 通信；若 Job 本身跑在容器里（见 4.9），则要用**服务名**作为主机名。
- 服务容器在该 Job 结束后销毁，**不会**跨 Job 复用。
- 常用镜像：`postgres`、`mysql`、`redis`、`mongo`、`rabbitmq`、`localstack`。

| 常见服务 | 镜像 | 健康检查命令 |
| --- | --- | --- |
| PostgreSQL | `postgres:16` | `pg_isready` |
| MySQL | `mysql:8` | `mysqladmin ping -h localhost` |
| Redis | `redis:7` | `redis-cli ping` |
| MongoDB | `mongo:7` | `mongosh --eval "db.runCommand('ping')"` |

### 4.9 container 与 defaults

**`container`：让整个 Job 在指定镜像内运行**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: node:20-bookworm
      env:
        NODE_ENV: test
      options: --cpus 2
    steps:
      - run: node -v
```

适用场景：需要与生产一致的系统库；或使用自建 Runner 但想隔离依赖。

> 注意：Job 使用 `container` 后，访问 `services` 要用**服务名**而非 `localhost`；且 `container` 仅支持 Linux 运行器。

**`defaults`：统一默认值**

```yaml
defaults:
  run:
    shell: bash                  # 统一 shell（Windows 上尤其有用）
    working-directory: ./app

jobs:
  build:
    runs-on: windows-latest
    defaults:
      run:
        shell: bash             # Job 级覆盖工作流级
    steps:
      - run: pwd
```

要点：`defaults` 能省去每个 step 重复写 `working-directory`，但一旦设置，**所有** `run` 步骤都会受影响，需确认脚本里的相对路径假设仍然成立。

---

## 第 5 章 核心概念深入

### 5.1 上下文（Contexts）与表达式

<!--DIAGRAM:context-flow-->

`${{ ... }}` 中可以访问大量内置上下文：

| 上下文 | 常用字段 | 说明 |
| --- | --- | --- |
| `github` | `github.ref`、`github.sha`、`github.actor`、`github.event_name`、`github.repository` | 当前事件信息 |
| `env` | `env.MY_VAR` | 环境变量 |
| `secrets` | `secrets.TOKEN` | 密钥（见 5.2） |
| `vars` | `vars.REGION` | 仓库/组织级变量 |
| `runner` | `runner.os`、`runner.temp` | 运行器信息 |
| `needs` | `needs.build.outputs.x` | 上游 Job 输出 |
| `matrix` | `matrix.node-version` | 矩阵当前取值 |
| `steps` | `steps.id.outputs.x`、`steps.id.conclusion` | 某步骤的输出/结果 |
| `job` | `job.status` | 当前 Job 状态 |

**表达式运算符**：

```yaml
if: github.ref == 'refs/heads/main' && !contains(github.event.head_commit.message, '[skip ci]')
```

支持：`==` `!=` `>` `<` `&&` `||` `!`、`contains()`、`startsWith()`、`endsWith()`、`format()`、`join()`、`toJSON()`、`fromJSON()`、`hashFiles()`。

> 常见坑：**`if` 条件里通常不要写 `${{ }}`**。`if: github.ref == 'refs/heads/main'` 是正确写法；`if: ${{ github.ref == ... }}` 虽也可运行，但在某些位置会出错。

### 5.2 Secrets —— 密钥管理

**原则：任何敏感信息都不得写进代码或 YAML。**

配置位置：仓库 **Settings → Secrets and variables → Actions → New repository secret**。

```yaml
- name: 登录镜像仓库
  run: echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
```

要点：

- Secret 在日志中会被自动打码（显示为 `***`）。
- Secret **不能**直接在 `if` 中比较，也不能作为 `run` 的环境变量名。
- 传给 action 时通过 `with:` 或 `env:` 传入：

```yaml
- uses: some/action@v1
  with:
    token: ${{ secrets.MY_TOKEN }}
```

**环境级 Secret**：可在 GitHub 的 **Environments** 中为 `production` / `staging` 分别配置，同名 Secret 在不同环境取值不同，配合审批使用效果最佳。

### 5.3 Variables —— 非敏感配置

与 Secret 类似，但用于非敏感值（如区域、域名）。配置于同一页面，通过 `vars` 上下文读取：

```yaml
- run: echo "部署到 ${{ vars.REGION }}"
```

### 5.4 permissions —— 权限最小化

<!--DIAGRAM:security-model-->

默认情况下 `GITHUB_TOKEN` 权限较宽。**最佳实践是显式声明最小权限**：

```yaml
permissions:
  contents: read            # 工作流级默认

jobs:
  deploy:
    permissions:
      contents: write       # 仅该 Job 需要写权限
      id-token: write       # 用于 OIDC 云厂商免密登录
      packages: write       # 推送 GitHub Packages
```

常见取值：`read` / `write` / `none`，作用于 `contents`、`packages`、`id-token`、`pull-requests`、`issues`、`deployments` 等。

---

### 5.5 Workflow 命令 —— 日志与输出控制

在 `run` 中向标准输出写入特定格式的字符串，即可控制日志展示与后续行为：

| 命令 | 作用 |
| --- | --- |
| `echo "::group::标题"` … `echo "::endgroup::"` | 折叠日志分组，长输出更易读 |
| `echo "::add-mask::$VALUE"` | 把某个值加入掩码列表，之后日志中显示为 `***` |
| `echo "::error file=app.js,line=10::消息"` | 在 PR 的 Files changed 中标注错误行 |
| `echo "::warning::消息"` | 输出警告标注 |
| `echo "::notice::消息"` | 输出提示标注 |
| `echo "::set-output name=x::y"` | **已废弃**，改用 `$GITHUB_OUTPUT` |
| `echo "::save-state name=x::y"` | **已废弃**，改用 `$GITHUB_STATE` |

```yaml
- name: 带分组的测试
  run: |
    echo "::group::安装依赖"
    npm ci
    echo "::endgroup::"

    echo "::group::运行测试"
    npm test
    echo "::endgroup::"
```

要点：`::add-mask::` 适合**动态生成**的敏感值（如运行时才拿到的临时令牌）——静态 Secret 由 GitHub 自动掩码，运行时产生的值需要手动加掩码。

### 5.6 OIDC 免密登录云厂商

传统做法是把云厂商的长期密钥存进 Secrets。**OIDC（OpenID Connect）**可以完全省掉长期密钥：GitHub 在运行时签发一个短期、可验证的身份令牌，云厂商校验后临时授权。

```yaml
permissions:
  id-token: write        # 必须：允许签发 OIDC 令牌
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-deploy
          aws-region: ap-northeast-1

      - run: aws s3 sync dist/ s3://my-bucket
```

要点：

- **优势**：没有长期密钥可泄漏；令牌有效期以分钟计；可在云侧按仓库、分支、环境精确限定信任范围。
- 云侧需配置信任策略，限定类似 `repo:my-org/my-repo:ref:refs/heads/main` 的条件，避免任意分支都能扮演该角色。
- 三大云均支持：AWS（`aws-actions/configure-aws-credentials`）、GCP（`google-github-actions/auth`）、Azure（`azure/login`）。

### 5.7 GITHUB_TOKEN 权限全表

`GITHUB_TOKEN` 是每次运行自动生成的临时令牌，默认权限取决于仓库设置，**最佳实践是显式声明**。

```yaml
permissions: read-all        # 或 write-all（不推荐）
# 或逐项声明：
permissions:
  contents: read
  pull-requests: write
  id-token: write
```

| 权限项 | 控制范围 | 常见需要它的场景 |
| --- | --- | --- |
| `contents` | 仓库代码、Release、tag | 推送代码、创建 Release（`write`） |
| `pull-requests` | PR 评论、标签、状态 | 在 PR 上评论预览地址（`write`） |
| `issues` | Issue 评论与标签 | 自动打标签、关闭 Issue（`write`） |
| `packages` | GitHub Packages | 推送镜像 / 包到 GHCR（`write`） |
| `id-token` | OIDC 令牌签发 | 云厂商免密登录、npm provenance（`write`） |
| `deployments` | 部署记录 | 使用 `environment` 记录部署（`write`） |
| `security-events` | 代码扫描结果 | 上传 CodeQL / SARIF 结果（`write`） |
| `actions` | 管理工作流运行 | 取消或重跑工作流（`write`） |
| `statuses` / `checks` | 提交状态与检查 | 自定义检查状态（`write`） |

要点：

- 取值只有 `read` / `write` / `none` 三种；一旦显式声明 `permissions`，**未列出的项会变为 `none`**。
- 权限不足的典型报错是 `Resource not accessible by integration`。
- `GITHUB_TOKEN` **无法触发新的工作流运行**（刻意的防循环设计）；确实需要时使用 PAT 或 GitHub App token。

---

## 第 6 章 进阶特性

### 6.1 矩阵构建（Matrix）

<!--DIAGRAM:matrix-->

一次定义、多组合并行测试：

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        node-version: [18, 20, 22]
        exclude:
          - os: windows-latest
            node-version: 18
        include:
          - os: ubuntu-latest
            node-version: 20
            experimental: true
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
```

- 组合数 = 各维度取值数量相乘（此处 2×3 = 6，减去 exclude 1 = 5）。
- `include` 可为特定组合追加变量，或新增组合。
- `max-parallel` 可限制并发组合数。

### 6.2 缓存（Cache）—— 加速依赖安装

<!--DIAGRAM:cache-flow-->

以 Node 为例，缓存 `~/.npm`：

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-npm-
```

**更简洁的做法**：`actions/setup-node` 内置缓存：

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: npm        # 或 yarn / pnpm
```

Python 同理：

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: pip        # 或 pipenv / poetry
```

**Java（Maven / Gradle）**：

```yaml
# Maven
- uses: actions/setup-java@v4
  with:
    distribution: temurin
    java-version: '21'
    cache: maven          # 自动缓存 ~/.m2/repository

# Gradle：推荐用官方 Action，比手写缓存更可靠
- uses: gradle/actions/setup-gradle@v4
```

**Go**：

```yaml
- uses: actions/setup-go@v5
  with:
    go-version: '1.22'
    cache: true           # 自动缓存 ~/go/pkg/mod
```

**各语言缓存目录对照**

| 语言 | 缓存目录 | 由谁自动处理 |
| --- | --- | --- |
| Node | `~/.npm` | `setup-node` 的 `cache:` |
| Python | `~/.cache/pip` | `setup-python` 的 `cache:` |
| Java / Maven | `~/.m2/repository` | `setup-java` 的 `cache: maven` |
| Java / Gradle | `~/.gradle/caches` | `gradle/actions/setup-gradle` |
| Go | `~/go/pkg/mod` | `setup-go` 的 `cache: true` |

**缓存键设计原则**：`key` 应包含**操作系统 + 依赖清单文件的哈希**（如 `hashFiles('**/package-lock.json')`、`hashFiles('**/pom.xml')`）。这样依赖一变，缓存自动失效并重建。

### 6.3 产物（Artifacts）

<!--DIAGRAM:cache-vs-artifact-->

跨 Job 或跨运行传递文件（如构建结果、测试报告、日志）：

```yaml
# 上传
- uses: actions/upload-artifact@v4
  with:
    name: dist
    path: dist/
    retention-days: 7

# 在另一个 Job 中下载
- uses: actions/download-artifact@v4
  with:
    name: dist
    path: dist/
```

**Cache 与 Artifact 的区别**：

| | Cache | Artifact |
| --- | --- | --- |
| 目的 | 加速（复用依赖） | 传递/留存（保存结果） |
| 生命周期 | 可被命中复用，也可能失效 | 明确保留天数 |
| 典型内容 | node_modules、pip 缓存 | 构建产物、测试报告 |

### 6.4 条件与依赖编排

<!--DIAGRAM:job-dag-->

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [ ... ]

  test:
    needs: [lint]              # 等 lint 完成
    runs-on: ubuntu-latest
    steps: [ ... ]

  deploy:
    needs: [test]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps: [ ... ]
```

**步骤级条件**：

```yaml
- name: 上传覆盖率
  if: always()
  uses: codecov/codecov-action@v4
```

常用状态函数：`success()`（默认）、`failure()`、`cancelled()`、`always()`。

### 6.5 并发控制（Concurrency）

避免同一分支的重复运行互相争抢资源：

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true      # 新运行取消旧运行
```

> 部署场景中，`cancel-in-progress` 应谨慎设为 `true`——中断一次进行中的部署可能留下不一致状态。

---

### 6.6 表达式函数全表

| 函数 | 说明 | 示例 |
| --- | --- | --- |
| `contains(a, b)` | 包含判断（字符串或数组） | `contains(github.event.head_commit.message, '[skip ci]')` |
| `startsWith(a, b)` | 前缀判断 | `startsWith(github.ref, 'refs/tags/v')` |
| `endsWith(a, b)` | 后缀判断 | `endsWith(github.ref, '-rc')` |
| `format(fmt, ...)` | 字符串格式化 | `format('{0}-{1}', runner.os, github.run_id)` |
| `join(arr, sep)` | 数组拼接 | `join(matrix.os, ',')` |
| `toJSON(v)` | 转为 JSON 字符串 | `toJSON(github)` |
| `fromJSON(s)` | 解析 JSON 字符串 | `fromJSON(vars.CONFIG).region` |
| `hashFiles(glob)` | 对匹配文件计算 SHA-256 | `hashFiles('**/package-lock.json')` |
| `success()` / `failure()` | 当前 Job 之前步骤的状态 | `if: failure()` |
| `cancelled()` / `always()` | 是否被取消 / 恒为真 | `if: always()` |

**三个高价值用法**

```yaml
# 1. 从 commit message 中提取版本号
- run: echo "VERSION=$(echo '${{ github.event.head_commit.message }}' | grep -oP 'v\d+\.\d+\.\d+')" >> $GITHUB_ENV

# 2. 用 JSON 变量做条件开关
- if: fromJSON(vars.FEATURES).enableDeploy == true
  run: ./deploy.sh

# 3. 打印整个 github 上下文，用于定位字段名
- run: echo '${{ toJSON(github) }}'
```

> 注意：`if` 中的表达式**不需要**再包一层 `${{ }}`；而 `run` / `with` / `env` 中**必须**用 `${{ }}`。

### 6.7 YAML 锚点复用

GitHub Actions 支持标准 YAML 锚点（`&` 定义、`*` 引用），可在同一文件内复用重复片段。注意：**锚点不能跨文件**。

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - &checkout
        uses: actions/checkout@v4
      - &setup-node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build

  e2e:
    runs-on: ubuntu-latest
    steps:
      - *checkout
      - *setup-node
      - run: npx playwright test
```

要点：

- 适合"每个 Job 开头都要 checkout + setup"这类重复模板。
- 可读性会下降，团队内需约定使用边界；跨文件复用请改用**可复用工作流**或**复合 Action**（第 8 章）。
- 部分静态检查工具对锚点支持有限，引入前确认团队工具链。

### 6.8 缓存深入：作用域与限制

**作用域规则（最容易被误解的一点）**

| 规则 | 说明 |
| --- | --- |
| 分支隔离 | 缓存创建时归属于**当前分支**；默认只能恢复"当前分支 + 默认分支"创建的缓存 |
| 跨分支恢复 | PR 分支首次运行通常**无法命中**，因为该分支尚无缓存 |
| 逐级回退 | `restore-keys` 按前缀逐级尝试，如 `linux-npm-` 可命中 `linux-npm-abc123` |
| 容量上限 | 单仓库缓存总量约 **10 GB**，超出后按最后访问时间淘汰 |
| 有效期 | 缓存 **7 天**未被访问会被清理 |

**推荐的 key 设计**

```yaml
- id: cache
  uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-npm-
```

设计要点：

1. `key` 包含**操作系统**——不同系统的依赖二进制不兼容。
2. `key` 包含**依赖清单的哈希**——依赖变了就重建，没变就复用。
3. `restore-keys` 提供**前缀回退**——精确 key 未命中时仍可复用一个较旧缓存，只做增量更新。
4. **不要把 `github.run_id`、时间戳等每次变化的值放进 key**，否则缓存永远不命中。
5. 缓存 `node_modules` 需谨慎（与 OS / Node 版本强绑定）；缓存**包管理器的下载缓存目录**更稳妥。

**排查缓存问题**

```yaml
- name: 查看缓存命中情况
  run: echo "命中: ${{ steps.cache.outputs.cache-hit }}"
```

---

## 第 7 章 实战示例

> **为什么按栈分开写**：前端与后端的流水线关注点不同，Java / Python / Node / Go 在依赖管理与构建工具上也各有差异。照搬其他栈的配置，最容易在**缓存路径、构建命令、产物目录**三处踩坑。
>
> 本章先给对照表，再逐栈给出可直接使用的完整配置。

### 7.1 前端 vs 后端：流水线关注点差异

<!--DIAGRAM:fe-vs-be-->

| 维度 | 前端 | 后端 |
| --- | --- | --- |
| 依赖管理 | npm / yarn / pnpm | Maven / Gradle；pip / uv / Poetry；go mod |
| 主要产物 | 静态文件（`dist/`、`build/`、`.next/`） | 可执行包（jar / wheel / 二进制）、容器镜像 |
| 测试重点 | 单元 + 组件 + E2E（Playwright / Cypress） | 单元 + 集成（真实数据库）+ 契约测试 |
| 缓存对象 | 包管理器缓存目录（`~/.npm`） | `~/.m2/repository`、`~/.gradle/caches`、`~/.cache/pip`、`~/go/pkg/mod` |
| 部署方式 | CDN / 对象存储 / 边缘（Pages、Vercel、Netlify） | 容器 + 编排（Docker、K8s）/ 服务器进程 |
| 特有门禁 | 包体积、Lighthouse 性能、视觉回归 | 接口兼容性、数据库迁移、健康检查与灰度 |
| 主要环境风险 | 构建期注入的 API 地址、`base` 子路径 | 连接串、配置中心、时区与字符集 |

> 一句话概括：**前端交付"文件"，后端交付"进程/镜像"。** 这决定了两者的产物形态、缓存策略与部署方式完全不同。

### 7.2 四种后端语言速查

<!--DIAGRAM:backend-langs-->

| 语言 | 安装 Action | 依赖安装 | 缓存目录 | 构建 | 测试 | 典型产物 |
| --- | --- | --- | --- | --- | --- | --- |
| **Java** | `actions/setup-java@v4` | `mvn -B dependency:go-offline` / `./gradlew dependencies` | `~/.m2/repository` / `~/.gradle/caches` | `mvn -B package` / `./gradlew build` | `mvn -B verify` / `./gradlew test` | `target/*.jar` / `build/libs/*.jar` |
| **Python** | `actions/setup-python@v5` | `pip install -r requirements.txt` / `uv sync` / `poetry install` | `~/.cache/pip` / `~/.cache/uv` | 通常无需构建（或 `python -m build`） | `pytest` | wheel / 源码 |
| **Node** | `actions/setup-node@v4` | `npm ci` / `pnpm i --frozen-lockfile` | `~/.npm` | `npm run build` | `npm test` | `dist/` |
| **Go** | `actions/setup-go@v5` | `go mod download` | `~/go/pkg/mod` | `go build` | `go test ./...` | 单个二进制 |

> 上表「缓存目录」列无需手写 `actions/cache`：`setup-java` / `setup-python` / `setup-node` / `setup-go` 的 `cache:` 参数会自动处理。

### 7.3 前端 · Node 生态（React / Vue / Next.js）

```yaml
name: Frontend CI

on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: read

concurrency:
  group: fe-${{ github.ref }}
  cancel-in-progress: true

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 安装 pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - run: pnpm install --frozen-lockfile
      - run: pnpm run lint --if-present
      - run: pnpm run test --if-present
      - run: pnpm run build

      - name: 上传构建产物
        uses: actions/upload-artifact@v4
        with:
          name: web-dist
          path: dist
```

**按框架调整的三处**

| 框架 | 构建命令 | 产物目录 | 备注 |
| --- | --- | --- | --- |
| Vite（React / Vue） | `npm run build` | `dist/` | 子路径部署需设 `base` |
| Next.js | `next build` | `.next/` | 静态导出 `output: 'export'` → `out/` |
| Nuxt | `nuxt build` | `.output/` | SSR 部署需 Node 运行时 |
| Angular | `ng build` | `dist/<app>/` | 注意 `--base-href` |
| Create React App | `npm run build` | `build/` | 已停止维护，建议迁移 |

**E2E 测试（Playwright）**

```yaml
      - name: 安装浏览器
        run: npx playwright install --with-deps chromium

      - name: 运行 E2E
        run: npx playwright test

      - name: 上传测试报告
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
```

要点：

- 前端构建会把 `VITE_*` / `NEXT_PUBLIC_*` 等变量**编译进产物**，因此它们不是真正的密钥，不要放敏感信息。
- 构建期注入的 API 地址需按环境区分（见 11.1）。
- 部署到子路径（如 GitHub Pages）时必须正确设置 `base` / `baseHref`，否则资源 404。

### 7.4 后端 · Java（Maven / Gradle / Spring Boot）

**Maven 版**

```yaml
name: Java CI (Maven)

on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        java-version: [ '17', '21' ]
    steps:
      - uses: actions/checkout@v4

      - name: 安装 JDK ${{ matrix.java-version }}
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: ${{ matrix.java-version }}
          cache: maven

      - name: 编译并运行测试
        run: mvn -B verify

      - name: 上传测试报告
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: surefire-jdk${{ matrix.java-version }}
          path: target/surefire-reports/
          retention-days: 7

      - name: 打包
        run: mvn -B -DskipTests package

      - name: 上传 jar
        uses: actions/upload-artifact@v4
        with:
          name: app-jar-jdk${{ matrix.java-version }}
          path: target/*.jar
```

**Gradle 版**

```yaml
name: Java CI (Gradle)

on:
  pull_request:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'

      - name: 配置 Gradle（内置缓存）
        uses: gradle/actions/setup-gradle@v4

      - run: ./gradlew build --no-daemon

      - uses: actions/upload-artifact@v4
        with:
          name: app-jar
          path: build/libs/*.jar
```

**Spring Boot 直接打容器镜像**

```yaml
      - name: 构建镜像
        run: mvn -B spring-boot:build-image -DskipTests \
             -Dspring-boot.build-image.imageName=registry.example.com/my-app:${{ github.sha }}
```

**发布到 GitHub Packages（Maven）**

```yaml
      - name: 配置 Maven 仓库凭据
        run: |
          mkdir -p ~/.m2
          cat > ~/.m2/settings.xml <<'EOF'
          <settings>
            <servers>
              <server>
                <id>github</id>
                <username>${env.GITHUB_ACTOR}</username>
                <password>${env.GITHUB_TOKEN}</password>
              </server>
            </servers>
          </settings>
          EOF

      - run: mvn -B deploy
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

要点：

- **务必提交 Wrapper**：Maven 的 `mvnw`、Gradle 的 `gradlew`。CI 用 `./mvnw` / `./gradlew` 调用，可保证 CI 与本地构建工具版本一致。Gradle 建议用 `gradle/actions/setup-gradle` 而非手写缓存。
- `-B`（batch mode）关闭交互式输出与下载进度条，避免日志被刷屏。
- `mvn verify` 会跑完整生命周期（含集成测试），比 `mvn test` 更接近"可发布"状态。
- Spring Boot 3.x 要求 **JDK 17+**；多 JDK 矩阵用于验证兼容性，应用项目通常固定一个 LTS 版本即可。
- Java 项目的数据库迁移一般交给 **Flyway / Liquibase**，在应用启动时自动执行（见 12.2）。

### 7.5 后端 · Python（pip / uv / Poetry；FastAPI / Django）

**pip + requirements.txt（最通用）**

```yaml
name: Python CI

on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: [ '3.10', '3.11', '3.12' ]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: 安装依赖
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: 代码检查
        run: ruff check .

      - name: 类型检查
        run: mypy app

      - name: 运行测试
        run: pytest -q --cov=app --cov-report=xml

      - name: 上传覆盖率
        if: matrix.python-version == '3.12'
        uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage.xml
```

**uv（现代、极快，推荐新项目使用）**

```yaml
      - name: 安装 uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - run: uv sync --frozen
      - run: uv run pytest -q
```

**Poetry**

```yaml
      - run: pipx install poetry

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: poetry

      - run: poetry install --no-interaction
      - run: poetry run pytest -q
```

**构建并发布到 PyPI**

```yaml
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

要点：

- **锁定依赖**：生产项目应提交 `requirements.txt`（由 `pip-compile` 生成）、`uv.lock` 或 `poetry.lock`，保证构建可复现。
- `setup-python` 的 `cache:` 需与工具匹配：`pip` / `pipenv` / `poetry`；用 uv 时改由 `setup-uv` 的 `enable-cache` 处理。
- **多版本矩阵只对"库"必要**；"应用"通常固定一个 Python 版本即可，避免无谓的 CI 成本。
- FastAPI / Django 的集成测试同样可用 `services` 起真实 PostgreSQL（见 12.3）。
- 生产部署用 `uvicorn` / `gunicorn`，并确保正确处理 `SIGTERM` 以实现优雅退出。

### 7.6 后端 · Node.js（Express / NestJS）

```yaml
name: Node Backend CI

on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        ports: [ '5432:5432' ]
        options: >-
          --health-cmd pg_isready --health-interval 10s
          --health-timeout 5s --health-retries 5

    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run lint --if-present
      - run: npm test
      - run: npm run build --if-present
```

要点：

- 后端 Node 与前端 Node 的关键区别：**后端交付"可运行的服务 + 容器镜像"，前端交付"静态文件"**。因此后端不要把 `dist/` 上传到 CDN，而是打进镜像。
- NestJS 用 `nest build`，产物在 `dist/`；务必确认 `package.json` 的 `main` 指向编译后入口。
- 用 `npm ci`（而非 `npm install`）保证 lock 文件与依赖严格一致。

### 7.7 后端 · Go

```yaml
name: Go CI

on:
  pull_request:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
          cache: true

      - run: go mod download
      - run: go vet ./...
      - run: go test ./... -race -coverprofile=coverage.out
      - run: go build -o bin/app ./cmd/app

      - uses: actions/upload-artifact@v4
        with:
          name: go-binary
          path: bin/app
```

要点：

- `-race` 开启竞态检测，CI 中值得开启（会略微拖慢测试）。
- 需要多平台二进制时加矩阵：`env: { GOOS: linux, GOARCH: arm64 }`。
- 依赖缓存由 `setup-go` 的 `cache: true` 自动处理，无需手写 `actions/cache`。

### 7.8 容器化：构建并推送镜像

```yaml
name: Docker Build & Push

on:
  push:
    tags: [ 'v*' ]

jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        run: echo "image=ghcr.io/${GITHUB_REPOSITORY,,}:${GITHUB_SHA}" >> $GITHUB_OUTPUT

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.image }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

要点：

- `${GITHUB_REPOSITORY,,}` 把仓库名转为小写——GHCR 要求镜像路径全小写。
- **Java / Python 都建议用多阶段构建**：构建阶段用完整工具链镜像，运行阶段只留运行时，可显著减小镜像体积（见 12.2、12.3 的 Dockerfile）。
- `cache-from/to: type=gha` 复用 Actions 缓存加速分层构建。
- 镜像 tag 使用 `github.sha` 保证不可变，便于回滚。

### 7.9 部署到服务器（SSH）

```yaml
name: Deploy via SSH

on:
  push:
    branches: [ main ]

concurrency:
  group: deploy-production
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: 配置 SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -p "${{ secrets.SSH_PORT }}" -H "${{ secrets.SSH_HOST }}" >> ~/.ssh/known_hosts

      - name: 远程部署
        run: |
          ssh -p "${{ secrets.SSH_PORT }}" "${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }}" '
            set -e
            cd /opt/app
            git fetch --all
            git reset --hard origin/main
            ./deploy.sh
          '
```

要点：

- 远程脚本开头写 `set -e`，遇错即停，避免"实际失败却返回 0"。
- `git reset --hard` 会丢弃服务器上的本地改动，请确认该目录是纯部署目录。
- 更安全的替代方案：云厂商 OIDC 免密登录，或 `appleboy/ssh-action`（生产环境建议锁定到 commit SHA）。

### 7.10 部署到 GitHub Pages（前端静态站点）

```yaml
name: Deploy Pages

on:
  push:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

要点：需在 **Settings → Pages** 将 Source 设为 **GitHub Actions**；部署到子路径时记得设置 `base`。

---

## 第 8 章 复用与组织

### 8.1 可复用工作流（Reusable Workflows）

把通用流水线抽成独立工作流，供其他仓库/工作流调用。被调用方需声明 `workflow_call`：

```yaml
# .github/workflows/reusable-test.yml
name: Reusable Test

on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: '20'
    secrets:
      NPM_TOKEN:
        required: false

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      - run: npm ci
      - run: npm test
```

调用方：

```yaml
jobs:
  call-test:
    uses: ./.github/workflows/reusable-test.yml      # 同仓库用相对路径
    with:
      node-version: '20'
    secrets: inherit                                  # 继承调用方 Secrets
```

跨仓库调用：`uses: owner/repo/.github/workflows/reusable-test.yml@main`。

### 8.2 复合 Action（Composite Action）

把多个步骤封装成一个自定义动作，放在仓库的 `.github/actions/<name>/action.yml`：

```yaml
name: 'Setup and Build'
description: '安装依赖并构建'
inputs:
  node-version:
    description: 'Node 版本'
    required: false
    default: '20'
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: npm
    - run: npm ci
      shell: bash
    - run: npm run build
      shell: bash
```

使用：

```yaml
- uses: actions/checkout@v4
- uses: ./.github/actions/setup-and-build
  with:
    node-version: '20'
```

> 复合 Action 中每个 `run` 步骤**必须**显式指定 `shell`。

---

## 第 9 章 安全与最佳实践

### 9.1 十条核心实践

1. **权限最小化**：显式声明 `permissions`，默认给 `contents: read`，需要时才提权。
2. **固定 Action 版本**：优先用完整版本号或 commit SHA（`actions/checkout@v4` 优于 `@main`）。第三方 Action 建议锁定 SHA。
3. **Secret 不落盘**：不要 `echo $SECRET > file` 后提交；日志打码不等于文件安全。
4. **谨慎使用 `pull_request_target`**：它拥有写权限且在目标分支上下文中运行，若 checkout 了不可信 PR 的代码并执行，等于执行任意代码。**绝不要在 `pull_request_target` 中检出并运行 PR 分支的脚本。**
5. **保护生产环境**：用 GitHub **Environments** 配置必需审批人、限定可部署分支、设置等待时间。
6. **优先 OIDC 而非长期密钥**：云厂商（AWS/GCP/Azure）支持 OIDC 免密登录，避免长期密钥泄露。
7. **限制并发**：用 `concurrency` 防止重复部署。
8. **缓存投毒防护**：缓存 key 不要包含可被 PR 篡改的内容。
9. **锁定依赖版本**：CI 中使用 `npm ci`（而非 `npm install`）、`pip install -r requirements.txt` 配合锁定文件，保证可复现。
10. **审计与通知**：开启 Dependabot、Secret Scanning、Code Scanning；配置失败通知。

### 9.2 环境（Environments）配置示例

```yaml
jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    steps:
      - run: echo "部署到生产，已通过审批"
```

在 **Settings → Environments → production** 中可配置：

- **Required reviewers**：部署前需人工审批。
- **Wait timer**：延迟 N 分钟执行。
- **Deployment branches**：仅允许 `main` 等分支部署。

### 9.3 依赖自动化：Dependabot

`.github/dependabot.yml`：

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## 第 10 章 排错与调试

### 10.1 打开调试日志

在仓库 **Settings → Secrets and variables → Actions → Variables** 中添加：

- `ACTIONS_STEP_DEBUG = true`：输出步骤级详细日志。
- `ACTIONS_RUNNER_DEBUG = true`：输出运行器级日志。

### 10.2 本地验证 YAML 语法

工作流文件本质是 YAML，缩进错误是最常见的问题来源。可用 Python 快速校验：

```bash
python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo OK
```

或使用 `actionlint`（官方推荐的静态检查工具）：

```bash
# 安装后
actionlint .github/workflows/*.yml
```

### 10.3 常见错误速查

| 现象 | 可能原因 | 解决 |
| --- | --- | --- |
| 工作流根本不触发 | 分支/路径过滤不匹配；文件不在默认分支 | 检查 `on` 配置；确认文件已推到默认分支 |
| `Permission denied` 推送失败 | `GITHUB_TOKEN` 权限不足 | 增加 `permissions: contents: write` |
| Secret 读取为空 | Secret 名拼写错误；PR 来自 fork 无 Secret | 核对名称；fork PR 默认不注入 Secret |
| Job 间文件找不到 | 每个 Job 是独立机器 | 用 `upload-artifact` / `download-artifact` 传递 |
| 变量在下个 step 为空 | Shell 状态不跨 step | 写入 `$GITHUB_ENV` |
| 缓存永远未命中 | key 每次变化 | key 用 `hashFiles()` 生成稳定哈希 |
| YAML 报语法错误 | 缩进用了 Tab 或空格数不一致 | 统一用 2 空格缩进 |
| 部署卡住无输出 | 命令等待交互输入 | 加 `-y` / `--non-interactive` 等参数 |
| macOS 构建超时 | 免费额度消耗快 | 评估是否用 Linux，或自建 runner |

### 10.4 排查思路

<!--DIAGRAM:troubleshoot-tree-->

1. **先看哪个 Job、哪个 Step 失败**，Actions 页面会精确标红。
2. **展开失败步骤日志**，从最后几行往前读。
3. **本地复现**：用相同命令在本地跑一遍，多数问题可定位。
4. **最小化复现**：注释掉其他步骤，只留失败步骤，逐个加回。
5. **检查上下文值**：临时插入 `- run: echo "${{ toJSON(github) }}"` 打印上下文。

---

## 第 11 章 业界常见场景

> 本章把前面的语法组合成真实团队里反复出现的模式。每个场景给出「适用条件 + 关键配置 + 注意事项」，可按需取用。

### 11.1 多环境发布（dev / staging / production）

<!--DIAGRAM:multi-env-->

**适用**：有独立测试环境与生产环境，需要分级发布。

**核心做法**：用「分支 → 环境名 → 手动审批」三者绑定。

```yaml
name: Multi-Env Deploy

on:
  push:
    branches: [ develop, 'release/**', main ]

jobs:
  resolve-env:
    runs-on: ubuntu-latest
    outputs:
      env-name: ${{ steps.pick.outputs.name }}
    steps:
      - id: pick
        run: |
          case "${GITHUB_REF_NAME}" in
            develop)   echo "name=staging"    >> $GITHUB_OUTPUT ;;
            release/*) echo "name=staging"    >> $GITHUB_OUTPUT ;;
            main)      echo "name=production" >> $GITHUB_OUTPUT ;;
            *)         echo "name=none"       >> $GITHUB_OUTPUT ;;
          esac

  deploy:
    needs: resolve-env
    if: needs.resolve-env.outputs.env-name != 'none'
    runs-on: ubuntu-latest
    environment: ${{ needs.resolve-env.outputs.env-name }}   # 关键：绑定环境
    steps:
      - run: echo "部署到 ${{ needs.resolve-env.outputs.env-name }}"
```

要点：

- `environment` 的名称必须与 GitHub **Settings → Environments** 中创建的名称一致；在该环境上配置 **Required reviewers**，即可实现"生产必须人工点确认"。
- 同一个 Secret 名（如 `API_BASE`）可在不同环境配置不同值，工作流代码无需改动。
- 把该部署 Job 设为分支保护的 **Required 检查**，防止有人绕过流程直接发布。

### 11.2 PR 预览环境（Preview Deployment）

<!--DIAGRAM:preview-lifecycle-->

**适用**：前端 / 全栈项目，希望每个 PR 都有独立可访问的预览地址。

```yaml
name: Preview

on:
  pull_request:
    types: [ opened, synchronize, reopened ]

permissions:
  contents: read
  pull-requests: write

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci && npm run build

      - name: 部署预览
        id: deploy
        run: |
          # 替换为你的预览托管（Vercel / Netlify / 自建）
          echo "url=https://pr-${{ github.event.number }}.preview.example.com" >> $GITHUB_OUTPUT

      - name: 在 PR 上评论预览地址
        uses: actions/github-script@v7
        with:
          script: |
            const body = `预览环境已就绪：${{ steps.deploy.outputs.url }}`;
            const { owner, repo } = context.repo;
            const issue_number = context.issue.number;
            const { data: comments } = await github.rest.issues.listComments({ owner, repo, issue_number });
            const mine = comments.find(c => c.body.includes('预览环境已就绪'));
            if (mine) {
              await github.rest.issues.updateComment({ owner, repo, comment_id: mine.id, body });
            } else {
              await github.rest.issues.createComment({ owner, repo, issue_number, body });
            }
```

要点：

- 采用"先查已有评论、再更新"的策略，避免每次 push 都刷出新评论。
- PR 关闭时应销毁预览资源：再加一个 `on: pull_request: types: [closed]` 的清理 Job。
- 来自 fork 的 PR **拿不到 Secrets**；若预览部署依赖密钥，需评估 `pull_request_target` 的风险（见 9.1）。

### 11.3 Monorepo 增量构建

**适用**：一个仓库多个包 / 应用，希望只构建受影响的包。

**手段一：路径过滤（最简单）**

```yaml
on:
  pull_request:
    paths:
      - 'packages/web/**'
      - 'packages/ui/**'
      - 'package-lock.json'
```

**手段二：按变更计算受影响包**

```yaml
- name: 计算变更的包
  id: changed
  run: |
    BASE="${{ github.base_ref || 'main' }}"
    git fetch origin "$BASE" --depth=1
    PKGS=$(git diff --name-only "origin/$BASE"...HEAD | cut -d/ -f2 | sort -u | tr '\n' ' ')
    echo "packages=$PKGS" >> $GITHUB_OUTPUT
```

**手段三：交给工具（Turborepo / Nx）**

```yaml
- run: npx turbo run build test --filter='...[origin/main]'
```

要点：

- **路径过滤的坑**：被过滤掉的检查不会出现在 PR 上，而它若被设为 Required 检查，会导致 PR 永远无法合并。稳妥做法是"检查始终运行，在 Job 内部判断是否需要跳过"。
- 增量构建的收益取决于缓存命中率，务必配合 `actions/cache`（见 6.2）。

### 11.4 前端静态站点与 CDN 缓存刷新

**适用**：SPA / 静态站点发布到对象存储 + CDN。

```yaml
- name: 构建
  run: npm ci && npm run build

- name: 同步到对象存储
  run: aws s3 sync dist/ s3://my-bucket --delete

- name: 刷新 CDN
  run: aws cloudfront create-invalidation \
        --distribution-id "${{ secrets.CF_DIST_ID }}" --paths '/*'
```

要点：

- 若静态资源文件名自带内容哈希，只需刷新 `index.html`，可显著降低刷新成本。
- `--delete` 会删除目标端多余文件，务必确认该 bucket 专用于此站点。

### 11.5 容器化微服务与 GitOps

<!--DIAGRAM:gitops-->

**适用**：多服务、需要声明式发布与一键回滚。

```yaml
jobs:
  build:
    strategy:
      matrix:
        service: [ gateway, orders, users ]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v6
        with:
          context: ./services/${{ matrix.service }}
          push: true
          tags: registry.example.com/${{ matrix.service }}:${{ github.sha }}

  bump-manifest:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          repository: my-org/k8s-manifests
          token: ${{ secrets.GITOPS_TOKEN }}
      - run: |
          for s in gateway orders users; do
            yq -i ".image.tag = \"${GITHUB_SHA}\"" "apps/$s/values.yaml"
          done
          git commit -am "chore: bump to ${GITHUB_SHA}" && git push
```

要点：

- **GitOps 模式**：CI 只负责产出镜像并更新「清单仓库」，集群侧由 ArgoCD / Flux 拉取同步。回滚 = revert 一次提交，天然可审计。
- 镜像 tag 使用 `github.sha` 保证不可变，避免 `latest` 带来的部署不确定性。

### 11.6 移动端 App 构建与分发

**iOS（必须使用 macOS 运行器）**

```yaml
jobs:
  ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci && cd ios && pod install

      - name: 导入签名证书
        uses: apple-actions/import-codesign-certs@v3
        with:
          p12-file-base64: ${{ secrets.IOS_P12_BASE64 }}
          p12-password: ${{ secrets.IOS_P12_PASSWORD }}

      - run: xcodebuild -workspace ios/App.xcworkspace -scheme App \
              -archivePath build/App.xcarchive archive
      - run: xcodebuild -exportArchive -archivePath build/App.xcarchive \
              -exportPath build -exportOptionsPlist ExportOptions.plist

      - name: 上传 TestFlight
        run: xcrun altool --upload-app -f build/App.ipa -t ios \
              -u "${{ secrets.ASC_USER }}" -p "${{ secrets.ASC_PASSWORD }}"
```

**Android**

```yaml
jobs:
  android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - run: cd android && ./gradlew assembleRelease
      - uses: actions/upload-artifact@v4
        with:
          name: apk
          path: android/app/build/outputs/apk/release/*.apk
```

要点：

- macOS 运行器单价最高、消耗额度最快，仅在必须构建 iOS 时使用。
- 签名证书以 Base64 存入 Secrets，**绝不能**提交进仓库。
- Android 内测包可用 Firebase App Distribution 分发，免去手动传包。

### 11.7 定时任务与数据管道

**适用**：每日报表、数据同步、爬虫、清理任务。

```yaml
name: Daily Pipeline

on:
  schedule:
    - cron: '0 1 * * *'        # 每天 UTC 01:00（北京时间 09:00）
  workflow_dispatch:            # 保留手动触发，便于失败后重跑

jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12', cache: pip }
      - run: pip install -r requirements.txt

      - name: 执行管道
        run: python -m pipeline.run
        env:
          DB_URL: ${{ secrets.DB_URL }}

      - name: 上传报告
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: report
          path: output/report.html
```

要点：

- 定时任务**只在默认分支上运行**；修改后必须合并到默认分支才生效。
- GitHub 高负载时可能延迟数分钟，**不要**把它当作精确调度器；关键任务应设置超时与失败告警。
- 仓库连续 **60 天无活动**时，定时任务会被自动禁用，需留意。
- 需要分钟级精度或失败重试时，改用外部调度器触发 `workflow_dispatch` / `repository_dispatch`。

### 11.8 开源库自动发布

**适用**：npm / PyPI 包，希望"合并 PR 即自动发版"。

```yaml
name: Release

on:
  push:
    branches: [ main ]

permissions:
  contents: write
  pull-requests: write
  id-token: write            # npm provenance 需要

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          registry-url: https://registry.npmjs.org
          cache: npm
      - run: npm ci && npm run build

      - uses: changesets/action@v1
        with:
          publish: npm run release -- --provenance
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

要点：

- 推荐用 **Changesets** 管理版本与 CHANGELOG：开发者执行 `npx changeset` 写变更说明 → 合并后自动开出 "Version Packages" PR → 合并该 PR 即完成发布。
- `--provenance` 生成来源证明（供应链可信度），需要 `id-token: write`。
- 发布不可逆，务必在发布前跑完整测试。

### 11.9 安全与合规门禁

```yaml
name: Security

on:
  push: { branches: [ main ] }
  pull_request:
  schedule:
    - cron: '0 3 * * 1'        # 每周一次全量扫描

permissions:
  contents: read
  security-events: write

jobs:
  codeql:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: { languages: javascript-typescript }
      - uses: github/codeql-action/analyze@v3

  deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm audit --audit-level=high
```

要点：

- 组合使用：CodeQL（代码缺陷）、Dependabot（依赖更新）、Secret Scanning（密钥泄漏）、`npm audit` / `pip-audit`（已知漏洞）、许可证检查（`license-checker`）。
- 扫描结果会写入 GitHub **Security** 标签页；可设为分支保护的 Required 检查，实现"存在高危漏洞时禁止合并"。

### 11.10 通知集成（企业微信 / 钉钉 / Slack）

```yaml
- name: 通知企业微信
  if: always()
  run: |
    STATUS="${{ job.status }}"
    curl -s -X POST "${{ secrets.WECOM_WEBHOOK }}" \
      -H 'Content-Type: application/json' \
      -d "{\"msgtype\":\"markdown\",\"markdown\":{\"content\":\"**CI ${STATUS}**\\n仓库: ${{ github.repository }}\\n分支: ${{ github.ref_name }}\\n提交: ${{ github.sha }}\"}}"
```

要点：

- 放在独立 Job 或步骤中并使用 `if: always()`，确保成功与失败都会通知。
- Webhook URL 属于敏感信息，必须放入 Secrets。
- 失败通知建议只发给相关人（按分支/模块路由），避免全员刷屏。

### 11.11 性能与体积门禁

```yaml
- name: Lighthouse CI
  run: |
    npm i -g @lhci/cli
    lhci autorun
  env:
    LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_TOKEN }}

- name: 包体积检查
  run: npx size-limit
```

要点：

- 把性能 / 体积阈值写进配置，超出即失败，防止性能在迭代中悄悄劣化。
- 这类检查成本较高，建议只对"会影响的路径"运行。

### 11.12 数据库迁移

```yaml
- name: 执行数据库迁移
  run: npx prisma migrate deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

要点：

- 迁移必须**向后兼容**：先加列、后删列，保证滚动发布期间新旧代码共存不出错。
- 迁移在部署**之前**执行；破坏性变更拆成多步、跨多次发布完成。
- 生产迁移前务必先备份，并保留回滚脚本。

### 11.13 自建 Runner 与成本优化

```yaml
runs-on: [ self-hosted, linux, x64 ]
```

要点：

- 适用场景：需要更大算力（GPU）、需要访问内网资源、或用量大想节省费用。
- **安全红线**：绝不要在**公开仓库**上让自建 Runner 执行不受信任的 PR 代码——这等同于把机器交给外部执行任意命令。公开仓库请使用 GitHub 托管运行器。
- 成本优化四件事：矩阵裁剪、提升缓存命中率、`paths` 过滤、用 `concurrency` 及时取消无用运行。

### 11.14 多仓库联动

```yaml
# 在 A 仓库触发 B 仓库的工作流
- run: |
    curl -X POST \
      -H "Authorization: Bearer ${{ secrets.CROSS_REPO_TOKEN }}" \
      -H "Accept: application/vnd.github+json" \
      https://api.github.com/repos/my-org/repo-b/dispatches \
      -d '{"event_type":"dependency-updated","client_payload":{"version":"1.2.3"}}'
```

```yaml
# B 仓库接收
on:
  repository_dispatch:
    types: [ dependency-updated ]
```

要点：

- 跨仓库调用需要 PAT 或 GitHub App token，权限按最小化配置，并设置有效期。
- 同一组织内也可用 `workflow_call` 直接复用工作流，比 `repository_dispatch` 更简单。

---

## 第 12 章 完整项目实战

> 6 个端到端项目，按「**前端 / 后端 / 通用**」三类划分；后端再按 **Java / Python / Node** 三种技术栈区分。
>
> 可直接复制的文件位于 `examples/projects/`，目录名与技术栈一一对应。

| 项目 | 分类 | 技术栈 | 核心链路 |
| --- | --- | --- | --- |
| 12.1 | 前端 | Vite + React | CI → GitHub Pages → PR 预览 |
| 12.2 | 后端 | Java + Spring Boot + Maven | 矩阵测试 → 镜像 → SSH 部署 |
| 12.3 | 后端 | Python + FastAPI + PostgreSQL | 真实库测试 → Alembic 迁移 → 部署 |
| 12.4 | 后端 | Node + Express + PostgreSQL | `services` 测试 → GHCR → 部署 |
| 12.5 | 通用 | Python 数据管道 | 定时任务 → 报告产物 → 通知 |
| 12.6 | 通用 | TypeScript 库 | 矩阵 CI → Changesets 自动发版 |

### 12.1 前端项目：Vite + React → GitHub Pages + PR 预览

**目标**：`main` 推送后自动构建并发布到 GitHub Pages；每个 PR 自动跑检查并评论预览地址，PR 关闭时清理资源。

**目录结构**

```
01-frontend-react-pages/
├── .github/workflows/
│   ├── ci.yml
│   ├── deploy-pages.yml
│   └── preview.yml
├── src/
├── vite.config.ts
└── package.json
```

**`.github/workflows/ci.yml`**

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run lint --if-present
      - run: npm run test --if-present
      - run: npm run build
```

**`.github/workflows/deploy-pages.yml`**：复用 7.10 的配置。

**`.github/workflows/preview.yml`**

```yaml
name: PR Preview

on:
  pull_request:
    types: [ opened, synchronize, reopened, closed ]

permissions:
  contents: read
  pull-requests: write

jobs:
  preview:
    if: github.event.action != 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run build

      - name: 部署预览
        id: deploy
        run: echo "url=https://pr-${{ github.event.number }}.preview.example.com" >> $GITHUB_OUTPUT

      - name: 在 PR 上评论预览地址
        uses: actions/github-script@v7
        with:
          script: |
            const body = `预览环境已就绪：${{ steps.deploy.outputs.url }}`;
            const { owner, repo } = context.repo;
            const issue_number = context.issue.number;
            const { data: comments } = await github.rest.issues.listComments({ owner, repo, issue_number });
            const mine = comments.find(c => c.body.includes('预览环境已就绪'));
            if (mine) {
              await github.rest.issues.updateComment({ owner, repo, comment_id: mine.id, body });
            } else {
              await github.rest.issues.createComment({ owner, repo, issue_number, body });
            }

  cleanup:
    if: github.event.action == 'closed'
    runs-on: ubuntu-latest
    steps:
      - run: echo "TODO: 销毁 pr-${{ github.event.number }} 的预览资源"
```

**关键要点**

1. `vite.config.ts` 中必须设置 `base: '/<仓库名>/'`，否则 Pages 子路径下静态资源 404。
2. 需在 **Settings → Pages** 将 Source 设为 **GitHub Actions**。
3. 清理 Job 使用 `pull_request` 的 `closed` 事件而非 `pull_request_target`，避免不必要的写权限暴露。

### 12.2 后端项目 · Java：Spring Boot + Maven → Docker → 服务器

**目标**：PR 阶段在真实 PostgreSQL 上跑单元 + 集成测试；`main` 构建多阶段镜像并部署到服务器。

**目录结构**

```
02-backend-java-springboot/
├── .github/workflows/
│   ├── ci.yml
│   └── deploy.yml
├── src/main/java/...
├── src/test/java/...
├── pom.xml
├── Dockerfile
└── docker-compose.yml
```

**`.github/workflows/ci.yml`**

```yaml
name: Java API CI

on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        java-version: [ '17', '21' ]

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        ports: [ '5432:5432' ]
        options: >-
          --health-cmd pg_isready --health-interval 10s
          --health-timeout 5s --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: ${{ matrix.java-version }}
          cache: maven

      - name: 编译并运行测试
        run: ./mvnw -B verify
        env:
          SPRING_DATASOURCE_URL: jdbc:postgresql://localhost:5432/test
          SPRING_DATASOURCE_USERNAME: postgres
          SPRING_DATASOURCE_PASSWORD: postgres

      - name: 上传测试报告
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: surefire-jdk${{ matrix.java-version }}
          path: target/surefire-reports/
          retention-days: 7

      - name: 打包
        run: ./mvnw -B -DskipTests package

      - uses: actions/upload-artifact@v4
        with:
          name: app-jar-jdk${{ matrix.java-version }}
          path: target/*.jar
```

**`.github/workflows/deploy.yml`**

```yaml
name: Deploy Java API

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  packages: write

concurrency:
  group: deploy-java-api
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.meta.outputs.image }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        run: echo "image=ghcr.io/${GITHUB_REPOSITORY,,}:${GITHUB_SHA}" >> $GITHUB_OUTPUT
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.image }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: 部署到服务器
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            set -e
            cd /opt/my-java-api
            echo "${{ secrets.GHCR_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
            docker compose pull
            # Flyway 在应用启动时自动执行迁移，务必保证迁移向后兼容
            docker compose up -d --remove-orphans
            docker image prune -f
```

**Dockerfile（多阶段构建）**

```dockerfile
# ---- 构建阶段 ----
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src
# 先复制 pom.xml 并预下载依赖，让依赖层可被缓存
COPY pom.xml .
RUN mvn -B -q dependency:go-offline
COPY src ./src
RUN mvn -B -q -DskipTests package

# ---- 运行阶段 ----
FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /src/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]
```

**关键要点**

1. **提交 Maven Wrapper（`mvnw`）**，CI 用 `./mvnw` 调用，保证 CI 与本地 Maven 版本一致。
2. 多阶段构建把镜像从"含完整 Maven + JDK"（约 700 MB）降到"仅 JRE"（约 200 MB）。
3. `-XX:MaxRAMPercentage=75` 让 JVM 堆随容器内存限制自动调整，避免容器被 OOM Kill。
4. Java 侧的数据库迁移通常由 **Flyway / Liquibase 在应用启动时执行**，因此必须保证迁移**向后兼容**，否则滚动发布期间新旧实例会冲突。
5. `./mvnw -B verify` 会跑完整生命周期（含集成测试），比 `mvn test` 更接近可发布状态。

### 12.3 后端项目 · Python：FastAPI + PostgreSQL → Docker → 服务器

**目标**：PR 用真实 PostgreSQL 跑 pytest；`main` 构建镜像、在启动新容器前执行 Alembic 迁移。

**目录结构**

```
03-backend-python-fastapi/
├── .github/workflows/
│   ├── ci.yml
│   └── deploy.yml
├── app/
├── alembic/
├── tests/
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
└── docker-compose.yml
```

**`.github/workflows/ci.yml`**

```yaml
name: FastAPI CI

on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        ports: [ '5432:5432' ]
        options: >-
          --health-cmd pg_isready --health-interval 10s
          --health-timeout 5s --health-retries 5

    env:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: 安装依赖
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt -r requirements-dev.txt

      - name: 代码检查与类型检查
        run: |
          ruff check .
          mypy app

      - name: 执行数据库迁移
        run: alembic upgrade head

      - name: 运行测试
        run: pytest -q --cov=app --cov-report=xml

      - name: 上传覆盖率
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage.xml
```

**`.github/workflows/deploy.yml`**

```yaml
name: Deploy FastAPI

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  packages: write

concurrency:
  group: deploy-py-api
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.meta.outputs.image }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        run: echo "image=ghcr.io/${GITHUB_REPOSITORY,,}:${GITHUB_SHA}" >> $GITHUB_OUTPUT
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.image }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: 部署到服务器
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            set -e
            cd /opt/my-py-api
            echo "${{ secrets.GHCR_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
            docker compose pull
            # 迁移必须在启动新容器之前执行
            docker compose run --rm api alembic upgrade head
            docker compose up -d --remove-orphans
            docker image prune -f
```

**Dockerfile**

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 先复制依赖清单并安装，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**关键要点**

1. `PYTHONUNBUFFERED=1` 让日志实时输出，否则容器日志会严重延迟，排查问题时很痛苦。
2. 先 `COPY requirements.txt` 再装依赖，之后才 `COPY . .`——依赖层可被缓存，代码改动不会导致重装依赖。
3. **Alembic 迁移在 `docker compose up -d` 之前执行**，避免新代码连到旧表结构。
4. 生产环境用 `uvicorn --workers N` 或 `gunicorn -k uvicorn.workers.UvicornWorker`，并确保应用正确处理 `SIGTERM` 以优雅退出。
5. 与 Java 的区别：Java 常把迁移交给应用启动时的 Flyway，Python 更常见的是**独立迁移步骤**；两种方式都可行，关键是**迁移必须向后兼容**。

### 12.4 后端项目 · Node：Express + PostgreSQL → GHCR → 服务器

**目标**：PR 阶段用 `services` 起真实数据库跑测试；`main` 构建镜像推送到 GHCR，部署到服务器并执行迁移。

**目录结构**

```
04-backend-node-express/
├── .github/workflows/
│   ├── ci.yml
│   └── deploy.yml
├── src/
├── prisma/schema.prisma
├── Dockerfile
├── docker-compose.yml
└── package.json
```

**`.github/workflows/ci.yml`**

```yaml
name: API CI

on:
  pull_request:
  push:
    branches: [ main ]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        ports: [ '5432:5432' ]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx prisma migrate deploy
      - run: npm test
```

**`.github/workflows/deploy.yml`**

```yaml
name: Deploy API

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  packages: write

concurrency:
  group: deploy-api
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.meta.outputs.image }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        run: echo "image=ghcr.io/${GITHUB_REPOSITORY,,}:${GITHUB_SHA}" >> $GITHUB_OUTPUT
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.image }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: 部署到服务器
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            set -e
            cd /opt/my-api
            echo "${{ secrets.GHCR_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
            docker compose pull
            docker compose run --rm api npx prisma migrate deploy
            docker compose up -d
            docker image prune -f
```

**关键要点**

1. `${GITHUB_REPOSITORY,,}` 转小写——GHCR 要求镜像路径全小写。
2. 迁移在 `docker compose up -d` **之前**执行，避免新代码连到旧表结构。
3. 服务器侧只需一个 `docker-compose.yml`，部署逻辑尽量收敛到镜像内。
4. `appleboy/ssh-action` 属第三方 Action，生产环境建议锁定到 commit SHA。

### 12.5 通用项目：Python 定时数据管道 → 每日报告

**目标**：每天拉取数据、生成 HTML 报告、上传产物并推送企业微信通知。

**目录结构**

```
05-pipeline-python-daily/
├── .github/workflows/daily.yml
├── src/pipeline/
├── requirements.txt
└── output/            # 运行时生成，不入库
```

**`.github/workflows/daily.yml`**

```yaml
name: Daily Report

on:
  schedule:
    - cron: '0 1 * * *'        # 每天 UTC 01:00（北京时间 09:00）
  workflow_dispatch:

permissions:
  contents: read

jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - run: pip install -r requirements.txt

      - name: 运行管道
        run: python -m pipeline.run
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DB_URL: ${{ secrets.DB_URL }}

      - name: 上传报告
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: daily-report-${{ github.run_number }}
          path: output/
          retention-days: 30

      - name: 推送企业微信
        if: always()
        run: |
          curl -s -X POST "${{ secrets.WECOM_WEBHOOK }}" \
            -H 'Content-Type: application/json' \
            -d "{\"msgtype\":\"markdown\",\"markdown\":{\"content\":\"**每日报告 ${{ job.status }}**\\n运行号: ${{ github.run_number }}\\n报告见 Actions 产物\"}}"
```

**关键要点**

1. 两个 `if: always()` 保证失败时也能拿到日志与部分产物，并收到通知。
2. 产物保留 30 天，过期自动清理，避免长期占用配额。
3. 定时任务只在**默认分支**运行，且仓库连续 60 天无活动会被自动禁用。
4. 需要分钟级精度或失败自动重试时，改用外部调度器触发 `workflow_dispatch`。

### 12.6 通用项目：开源 TypeScript 库 → 自动发布 npm + Release

**目标**：合并到 `main` 后自动升版本、生成 CHANGELOG、发布 npm 并打 tag。

**目录结构**

```
06-library-typescript-npm/
├── .github/workflows/
│   ├── ci.yml
│   └── release.yml
├── .changeset/
├── src/
├── package.json
└── tsconfig.json
```

**`.github/workflows/ci.yml`**

```yaml
name: CI

on:
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        node-version: [ 18, 20, 22 ]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm
      - run: npm ci
      - run: npm run lint --if-present
      - run: npm run test --if-present
      - run: npm run build
```

**`.github/workflows/release.yml`**

```yaml
name: Release

on:
  push:
    branches: [ main ]

permissions:
  contents: write
  pull-requests: write
  id-token: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          registry-url: https://registry.npmjs.org
          cache: npm
      - run: npm ci
      - run: npm run build

      - uses: changesets/action@v1
        with:
          publish: npm run release -- --provenance
          title: "chore: release"
          commit: "chore: release"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**关键要点**

1. 流程为：开发者 `npx changeset` 写变更说明 → 合并后自动开 "Version Packages" PR → 合并该 PR 即发布。
2. `--provenance` 需要 `id-token: write` 权限。
3. npm 账号需开启 2FA，并在 CI 中使用 Automation Token。
4. CI 覆盖多 Node 版本矩阵，Release 只跑单版本，兼顾兼容性与发布速度。

---

## 第 13 章 FAQ 常见问题

> 按主题分组，每条为「问题 → 原因 → 解决」。遇到报错时可先在此检索。

### 13.1 触发与运行

**Q1：工作流完全不触发，Actions 页面没有任何记录。**

三个常见原因：① `on` 的分支 / 路径过滤不匹配；② 文件不在**默认分支**上（`schedule`、`workflow_dispatch` 等事件要求工作流文件存在于默认分支）；③ 文件名或目录拼写错误（必须是 `.github/workflows/`，注意大小写）。

**Q2：明明 push 了，为什么没跑？**

先看是否命中 `paths` / `branches` 过滤；再确认该提交是否只改动了 `paths-ignore` 中的文件。若工作流使用了 `if` 条件，条件为 false 时 Job 会被**跳过**（显示为灰色而非失败）。

**Q3：如何临时跳过 CI？**

在提交信息中加入 `[skip ci]`（或 `[ci skip]`、`[no ci]`）。注意：仅对 `push` / `pull_request` 生效，且会影响**该次提交触发的全部工作流**，不要用它来跳过部分检查。

**Q4：定时任务为什么不按时执行？**

三个可能：① cron 使用 **UTC** 时区，需自行换算；② GitHub 高负载时会延迟数分钟到数十分钟；③ 仓库超过 60 天无活动，定时任务被自动禁用（重新启用即可）。需要精确调度时请改用外部调度器。

**Q5：如何只让打 tag 时触发？**

```yaml
on:
  push:
    tags: [ 'v*' ]
```

**Q6：如何手动触发并传入参数？**

配置 `workflow_dispatch` 的 `inputs`，然后在 Actions 页面点击 **Run workflow** 填写参数；参数通过 `${{ inputs.xxx }}` 读取（见 4.2）。

**Q7：如何让某个 Job 只在特定条件下运行？**

在 Job 上加 `if`：

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

**Q8：如何只重跑失败的 Job？**

在 Actions 运行详情页右上角选择 **Re-run failed jobs**，可复用成功的 Job 结果，节省时间与额度。

### 13.2 变量、密钥与权限

**Q9：`secrets.XXX` 读出来是空的？**

① 名称拼写不一致（Secret 名大小写敏感）；② 该工作流来自 **fork 的 PR**，出于安全 GitHub 不向 fork PR 注入 Secret；③ Secret 配置在了 `environment` 上，但 Job 未声明对应的 `environment`。

**Q10：`GITHUB_TOKEN` 和 PAT 有什么区别？**

`GITHUB_TOKEN` 是每次运行自动生成的临时令牌，仅在本次运行内有效、权限可精细控制，**推荐优先使用**；PAT（个人访问令牌）是长期凭证，权限大、风险高，仅在必须跨仓库或触发其他工作流时使用，并应设置最短有效期。

**Q11：报错 `Resource not accessible by integration`？**

`GITHUB_TOKEN` 权限不足。在 `permissions` 中补上所需权限，例如写 PR 评论需要 `pull-requests: write`，推送代码需要 `contents: write`。

**Q12：如何在 step 之间传递变量？**

```yaml
- run: echo "VERSION=1.2.3" >> $GITHUB_ENV      # 传给后续步骤
- run: echo "art=dist.zip"  >> $GITHUB_OUTPUT   # 作为本步骤输出（需 id）
```

**Q13：Secret 能直接写在 `if` 条件里吗？**

**不能**。GitHub 明确禁止在 `if` 中直接引用 `secrets`。需要判断时应先把 Secret 通过 `env` 注入，再判断环境变量。

**Q14：环境变量的优先级是怎样的？**

Step 级 > Job 级 > 工作流级 > 系统默认。同名的内层覆盖外层。

### 13.3 依赖、缓存与产物

**Q15：缓存永远不命中？**

① `key` 中包含每次都变化的值（如 `github.run_id`）——应使用 `hashFiles('**/package-lock.json')` 这类稳定哈希；② 缓存有**分支作用域**：默认只能恢复当前分支与默认分支创建的缓存，PR 分支首次运行通常未命中属正常现象。

**Q16：Job 之间如何共享文件？**

Job 之间**不共享文件系统**。必须通过 `actions/upload-artifact` 上传、在下一个 Job 用 `actions/download-artifact` 下载（见 6.3）。

**Q17：要不要缓存 `node_modules`？**

不建议。`node_modules` 与操作系统、Node 版本、架构强绑定，跨环境复用容易出诡异问题。推荐缓存**包管理器的缓存目录**（`~/.npm`、`~/.cache/pip`）——`setup-node` / `setup-python` 的 `cache:` 参数已内置该行为。

**Q18：Artifact 和 Cache 怎么选？**

Cache 用于**加速**（可被复用、可能失效）；Artifact 用于**传递与留存**（明确保留天数）。构建产物、测试报告用 Artifact；依赖缓存用 Cache。

**Q19：上传产物报 `no files found`？**

`path` 写错或构建未产出该目录。调试时先用 `ls -R` 确认路径；可设 `if-no-files-found: error` 让问题显式失败而非静默跳过。

### 13.4 部署与发布

**Q20：生产发布如何强制人工审批？**

在 **Settings → Environments** 创建 `production`，配置 **Required reviewers**，工作流中声明 `environment: production`。此后每次部署都会暂停等待审批。

**Q21：如何防止并发部署互相覆盖？**

```yaml
concurrency:
  group: deploy-production
  cancel-in-progress: false      # 部署场景不要取消进行中的运行
```

**Q22：部署失败如何回滚？**

推荐两条路径：① **GitOps**——回滚 = revert 清单仓库的提交；② **不可变镜像 tag**——重新部署上一个 `github.sha` 对应的镜像。前提是每次发布都保留了可追溯的版本标识。

**Q23：如何在部署中使用 SSH 密钥？**

把私钥内容存入 Secrets，在运行器中写入 `~/.ssh/id_rsa` 并 `chmod 600`，同时用 `ssh-keyscan` 写入 `known_hosts`（见 7.4）。更安全的替代是云厂商 OIDC 免密登录。

**Q24：镜像 tag 用什么？**

优先使用 `github.sha`（不可变、可追溯到具体提交）或语义化版本号。**避免**用 `latest`——它无法定位具体版本，回滚时无从下手。

### 13.5 性能与成本

**Q25：如何缩短 CI 时间？**

按收益排序：① 提升缓存命中率；② 用 `concurrency` 取消无用运行；③ 用 `paths` 过滤只跑相关任务；④ 合理并行（拆分 Job）；⑤ 矩阵裁剪（PR 跑关键组合，`main` 跑全量）；⑥ 优先 Linux 运行器；⑦ 避免在多个 Job 中重复安装同一套依赖。

**Q26：免费额度怎么算？会意外超支吗？**

公开仓库使用 GitHub 托管运行器**完全免费**；私有仓库按套餐提供每月免费分钟数，超出后按操作系统单价计费（Linux 最便宜、macOS 最贵）。建议在账单设置中把 **spending limit 设为 0**，超出即停止而非产生费用。

**Q27：构建时内存溢出（OOM）怎么办？**

Node 项目可提高堆上限：`env: { NODE_OPTIONS: '--max-old-space-size=4096' }`；或改用内存更大的运行器；也可把构建拆分为多个更小的步骤。

**Q28：矩阵组合太多，跑得又慢又贵怎么办？**

用 `exclude` 排除无效组合，用 `max-parallel` 限制并发；更常见的策略是**分级矩阵**——PR 只跑 1~2 个关键组合，合并到 `main` 后再跑全量组合。

### 13.6 安全

**Q29：第三方 Action 怎么用才安全？**

① 优先选择官方（`actions/*`）或已认证发布者；② 生产环境锁定到**完整版本号或 commit SHA**，不要用 `@main`；③ 使用前阅读其 `action.yml`，确认它不会读取你不希望它接触的 Secrets；④ 配置 `permissions` 限制其可用的令牌权限。

**Q30：`pull_request_target` 有什么风险？**

它拥有**写权限**，且在**目标分支的上下文**中运行。若在其中检出并执行 PR 分支的代码（如 `npm install`、`npm test`），等于让外部提交在你的仓库权限下执行任意命令，可能导致 Secrets 泄漏与仓库被篡改。**安全用法**：只在 `pull_request_target` 中操作 PR 元数据（打标签、评论），绝不执行 PR 分支的代码。

**Q31：自建 Runner 安全吗？**

取决于用途。**公开仓库**上绝不能让自建 Runner 执行不受信任的 PR 代码。私有仓库中使用时，也应让 Runner 运行在隔离的、权限最小的环境中，并定期更新。

**Q32：如何避免密钥泄漏？**

① 全部使用 Secrets，绝不硬编码；② 优先使用 OIDC 免密登录替代长期密钥；③ 不要 `echo` 输出密钥（即便日志会打码，也不应依赖）；④ 开启 **Secret Scanning** 与 **Push Protection**；⑤ 定期轮换密钥；⑥ 遵循最小权限原则。

---

## 附录 A 速查表

### A.1 常用官方 Action

| Action | 用途 |
| --- | --- |
| `actions/checkout@v4` | 检出仓库代码（几乎每个 Job 的第一步） |
| `actions/setup-node@v4` | 安装 Node 并配置缓存 |
| `actions/setup-python@v5` | 安装 Python 并配置缓存 |
| `actions/setup-java@v4` | 安装 JDK |
| `actions/cache@v4` | 通用缓存 |
| `actions/upload-artifact@v4` | 上传产物 |
| `actions/download-artifact@v4` | 下载产物 |
| `docker/build-push-action@v6` | 构建并推送镜像 |
| `docker/login-action@v3` | 登录镜像仓库 |

### A.2 常用内置环境变量

| 变量 | 含义 |
| --- | --- |
| `GITHUB_WORKSPACE` | 工作区目录 |
| `GITHUB_SHA` | 触发提交的 SHA |
| `GITHUB_REF` | 触发引用，如 `refs/heads/main` |
| `GITHUB_ENV` | 写入此处可向后续步骤传递变量 |
| `GITHUB_OUTPUT` | 写入此处可设置步骤输出 |
| `GITHUB_PATH` | 写入此处可追加 PATH |
| `RUNNER_OS` | 运行器操作系统 |

### A.3 触发器速记

```yaml
on:
  push:                 # 推送
  pull_request:         # PR
  schedule:             # 定时
  workflow_dispatch:    # 手动
  release:              # 发布
  workflow_call:        # 被复用工作流调用
  workflow_run:         # 其他工作流完成后
  repository_dispatch:  # 外部 API 触发
```

### A.4 学习路径建议

1. **入门**：先跑通第 3 章 Hello World，再按自己的技术栈选读 7.3（前端）/ 7.4（Java）/ 7.5（Python）/ 7.6（Node）/ 7.7（Go）。
2. **进阶**：掌握矩阵、缓存、产物、条件依赖（第 6 章）。
3. **落地**：把测试、构建、部署串成完整流水线（7.8–7.10），并加上环境审批与权限控制（第 9 章）。
4. **实战**：对照第 11 章找到匹配自己项目形态的场景，或直接复用第 12 章的六个完整项目。
5. **优化**：引入可复用工作流、复合 Action、Dependabot，形成团队规范（第 8、9 章）；按第 13 章排查问题、按 11.13 节控制成本。

### A.5 场景索引（按需求快速定位）

| 你的需求 | 对应章节 |
| --- | --- |
| 每次 push 自动跑测试 | 3.2；前端 7.3；Java 7.4；Python 7.5；Node 7.6；Go 7.7 |
| 多环境 / 生产需人工审批 | 9.2、11.1 |
| 每个 PR 一个预览地址 | 11.2、12.1 |
| 一个仓库多个包，只构建改动的 | 11.3 |
| 前端发布到 Pages / CDN | 7.10、11.4、12.1 |
| 后端构建镜像并部署到服务器 | 7.8、7.9；Java 12.2；Python 12.3；Node 12.4 |
| 多服务 / 声明式发布与回滚 | 11.5 |
| 构建 iOS / Android 包 | 11.6 |
| 每天定时跑数据任务 | 11.7、12.5 |
| 自动发布 npm / PyPI / Maven 包 | 11.8、7.4、7.5、12.6 |
| 代码 / 依赖安全扫描 | 9.3、11.9 |
| 失败时通知企业微信 / 钉钉 | 11.10 |
| 性能与包体积不能退化 | 11.11 |
| 部署前执行数据库迁移 | 11.12；Java 12.2；Python 12.3；Node 12.4 |
| 想省钱 / 需要大算力 | 11.13、13.5 |
| 多个仓库联动发布 | 11.14 |
| 遇到具体报错 | 10.3、第 13 章 |

### A.6 技术栈索引（按栈快速定位）

| 技术栈 | 依赖 / 构建工具 | 相关章节 |
| --- | --- | --- |
| 前端 · React / Vue / Next.js / Nuxt / Angular | npm / yarn / pnpm | 7.1、7.3、11.4、12.1 |
| 后端 · Java（Maven） | `mvn verify` / `mvn package` | 7.2、7.4、12.2 |
| 后端 · Java（Gradle） | `./gradlew build` | 7.4 |
| 后端 · Spring Boot | `spring-boot:build-image`、Flyway | 7.4、12.2 |
| 后端 · Python（pip / uv / Poetry） | `pytest` | 7.2、7.5、12.3 |
| 后端 · FastAPI / Django | `pytest`、Alembic | 7.5、12.3 |
| 后端 · Node（Express / NestJS） | `npm ci` / `npm test` | 7.2、7.6、12.4 |
| 后端 · Go | `go test` / `go build` | 7.2、7.7 |
| 容器化（通用） | `docker/build-push-action` | 7.8、11.5 |
| 静态站点 / CDN | GitHub Pages、S3 + CloudFront | 7.10、11.4 |
| 移动端 iOS / Android | `xcodebuild`、`gradlew assembleRelease` | 11.6 |

---

> 本文档基于 GitHub Actions 现行语法编写。官方参考：
> - 工作流语法：https://docs.github.com/actions/reference/workflow-syntax-for-github-actions
> - 事件触发：https://docs.github.com/actions/reference/events-that-trigger-workflows
