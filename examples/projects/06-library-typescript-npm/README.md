# 通用项目：开源 TypeScript 库 → 自动发布 npm + Release

## 目标

合并到 `main` 后自动升版本、生成 CHANGELOG、发布 npm 并创建 GitHub Release。

## 文件

```
.github/workflows/
├── ci.yml        # PR 多 Node 版本矩阵检查
└── release.yml   # Changesets 驱动的自动发布
```

## 工作流原理

1. 开发者在功能 PR 中执行 `npx changeset`，写下这次改动的说明（patch / minor / major）。
2. PR 合并到 `main` 后，Changesets 自动创建一个 **"Version Packages"** PR，其中包含版本号变更与 CHANGELOG。
3. 合并该 PR 即触发真正的发布：升版本 → 构建 → `npm publish --provenance` → 创建 GitHub Release 与 tag。

## 首次接入步骤

```bash
npx changeset init          # 生成 .changeset/ 目录
```

在 `package.json` 中补充：

```json
{
  "scripts": {
    "release": "changeset publish"
  }
}
```

## 需要配置的 Secrets

| 名称 | 用途 |
| --- | --- |
| `NPM_TOKEN` | npm Automation Token 或 Granular Access Token |

## 注意事项

- `--provenance` 需要 `id-token: write` 权限，用于生成供应链来源证明。
- npm 账号需开启 2FA；CI 中应使用 Automation Token，而非带 OTP 的普通令牌。
- CI 覆盖多 Node 版本矩阵，Release 只跑单版本，兼顾兼容性验证与发布速度。
- 发布不可逆，务必保证 `ci.yml` 的检查已作为分支保护的 Required 检查。
