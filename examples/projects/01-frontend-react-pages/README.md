# 前端项目：Vite + React → GitHub Pages + PR 预览

## 目标

- `main` 分支推送后自动构建并发布到 GitHub Pages。
- 每个 PR 自动运行 lint / test / build，并在 PR 下评论预览地址；PR 关闭时清理资源。

## 文件

```
.github/workflows/
├── ci.yml             # PR 与 main 的检查流水线
├── deploy-pages.yml   # 发布到 GitHub Pages
└── preview.yml        # PR 预览环境 + 评论 + 清理
```

## 使用步骤

1. 把 `.github/workflows/` 整个目录复制到项目根目录。
2. 在 `vite.config.ts` 中设置 `base`：

   ```ts
   export default defineConfig({
     base: '/<你的仓库名>/',
     // ...
   })
   ```

   > 若部署到自定义域名或根路径，则设为 `'/'`。此项遗漏会导致 Pages 上静态资源 404。

3. 打开仓库 **Settings → Pages**，将 **Source** 设为 **GitHub Actions**。
4. 把 `preview.yml` 中的 `TODO` 替换为真实的预览托管逻辑（Vercel / Netlify / 自建均可）。

## 注意事项

- 私有仓库使用 Pages 需要套餐支持；公开仓库免费。
- `preview.yml` 中清理 Job 使用 `pull_request_target`，仅用于操作 PR 元数据（评论、销毁资源），**不要**在其中检出并执行 PR 分支的代码。
- 若预览部署需要密钥，来自 fork 的 PR 无法获取 Secrets，需要另行设计（参考教程 9.1、13.2）。
