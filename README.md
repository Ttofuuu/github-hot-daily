# GitHub Hot Daily

每天定时抓取 GitHub 热门项目，并通过飞书机器人推送中文摘要。

## 功能

- 使用 GitHub Search API 获取近期热门仓库
- 支持飞书机器人推送
- 支持飞书卡片消息
- 支持 AI 中文摘要
- AI 失败时自动回退到默认中文摘要
- 支持 GitHub Actions 定时执行
- 支持手动触发工作流

## 项目结构

```text
.
├── main.py
├── requirements.txt
└── .github/
    └── workflows/
        └── daily.yml
```

## 需要配置的 Secrets

进入仓库：

- `Settings`
- `Secrets and variables`
- `Actions`
- `New repository secret`

添加以下 secrets：

### 必填

#### `FEISHU_WEBHOOK`
飞书群自定义机器人的 Webhook 地址。

示例：

```text
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

#### `GITHUB_TOKEN_CUSTOM`
你自己的 GitHub Personal Access Token，用于调用 GitHub API，避免过低的 rate limit。

### 如果启用 AI 摘要，建议配置

#### `OPENAI_API_KEY`
用于调用大模型生成中文摘要。

### 可选

#### `OPENAI_BASE_URL`
如果你使用兼容 OpenAI API 的服务，可以自定义 Base URL。

默认值通常可为：

```text
https://api.openai.com/v1
```

#### `OPENAI_MODEL`
指定使用的模型名称。

例如：

```text
gpt-4.1-mini
```

## 如何获取飞书 Webhook

1. 新建或打开一个飞书群
2. 进入群设置
3. 添加机器人
4. 选择“自定义机器人”
5. 创建后复制 Webhook 地址
6. 把它保存到 GitHub Secret：`FEISHU_WEBHOOK`

> 建议先不要开启过于复杂的安全校验，等基础流程跑通后再加签名校验。

## 如何创建 GitHub Token

1. 打开 GitHub
2. 进入 `Settings`
3. 进入 `Developer settings`
4. 进入 `Personal access tokens`
5. 创建一个新的 token
6. 保存到仓库 Secret：`GITHUB_TOKEN_CUSTOM`

如果只是读取公开仓库，通常不需要太高权限。

## 如何手动运行

1. 打开仓库的 `Actions`
2. 找到工作流：`Daily GitHub Hot Push`
3. 点击 `Run workflow`
4. 选择 `main` 分支
5. 运行后查看日志
6. 成功后飞书群会收到推送

## 如何修改推送参数

在 `.github/workflows/daily.yml` 里可以修改这些环境变量：

- `TOP_N`：推送多少个项目，默认 `10`
- `DAYS`：统计最近几天创建的项目，默认 `1`
- `LANGUAGE`：按语言过滤，例如 `Python`、`TypeScript`、`Go`、`Rust`
- `ENABLE_AI_SUMMARY`：是否启用 AI 摘要，`true` 或 `false`

### 示例

只看 Python：

```yaml
LANGUAGE: "Python"
```

看最近 7 天：

```yaml
DAYS: "7"
```

关闭 AI 摘要：

```yaml
ENABLE_AI_SUMMARY: "false"
```

## 推荐配置

如果你想让结果更稳定，建议：

- `DAYS: "7"`
- `TOP_N: "10"`
- `ENABLE_AI_SUMMARY: "true"`

## 仓库 Description

请手动把仓库 Description 设置为：

```text
Daily GitHub hot projects pushed to Feishu with Chinese AI summaries.
```

## 说明

这个项目当前通过 GitHub Search API 近似获取“热门项目”。

如果你之后想做得更像 GitHub Trending 页面，还可以继续升级为：

- 直接抓取 GitHub Trending 页面
- 增加历史去重
- 增加 star 增长对比
- 支持多语言分类推送
- 支持更漂亮的飞书卡片样式
