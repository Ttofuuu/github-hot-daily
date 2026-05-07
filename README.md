# GitHub Hot Daily

每天定时抓取 GitHub 热门项目，并通过钉钉机器人推送中文摘要。

## 功能

- 使用 GitHub Search API 获取近期热门仓库
- 支持钉钉机器人推送
- 支持 AI 中文摘要
- AI 失败时自动回退到默认中文摘要
- 支持 GitHub Actions 定时执行
- 支持手动触发工作流

## 项目结构

```text
.
├── main.py
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

#### `DINGTALK_WEBHOOK`
钉钉群自定义机器人的 Webhook 地址。

示例：

```text
https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxx
```

#### `GH_TOKEN`
你自己的 GitHub Personal Access Token，用于调用 GitHub API，避免过低的 rate limit。

### 可选（钉钉加签）

#### `DINGTALK_SECRET`
如果你在钉钉机器人安全设置中启用了“加签”，就需要配置该 secret。未开启加签时可不填。

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

## 如何创建钉钉自定义机器人

1. 新建或打开一个钉钉群
2. 进入群设置
3. 进入「智能群助手 / 机器人」
4. 添加「自定义机器人」
5. 复制 Webhook 地址，保存到 GitHub Secret：`DINGTALK_WEBHOOK`
6. 如开启“加签”，同时复制签名密钥并保存到 `DINGTALK_SECRET`

> 建议先用不加签模式跑通；若启用加签，务必同时配置 `DINGTALK_SECRET`。

## 如何创建 GitHub Token

1. 打开 GitHub
2. 进入 `Settings`
3. 进入 `Developer settings`
4. 进入 `Personal access tokens`
5. 创建一个新的 token
6. 保存到仓库 Secret：`GH_TOKEN`

如果只是读取公开仓库，通常不需要太高权限。

## 如何手动运行

1. 打开仓库的 `Actions`
2. 找到工作流：`Daily GitHub Hot Push`
3. 点击 `Run workflow`
4. 选择 `main` 分支
5. 运行后查看日志
6. 成功后钉钉群会收到推送

## 如何修改推送参数

在 `.github/workflows/daily.yml` 里可以修改这些环境变量：

- `TOP_N`：推送多少个项目，默认 `10`
- `DAYS`：统计最近几天创建的项目，默认 `7`
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

## GitHub Actions Secrets 清单

最小可用：

- `GH_TOKEN`
- `DINGTALK_WEBHOOK`

可选：

- `DINGTALK_SECRET`（启用钉钉加签时必填）
- `OPENAI_API_KEY`（启用 AI 摘要时必填）
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

## 说明

- 项目继续使用 GitHub Search API 拉取数据逻辑。
- 即使不配置 AI，依然会走规则式中文摘要，适合直接在国内网络环境稳定使用。
