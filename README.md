# GitHub Hot Daily

每天定时抓取 GitHub 热门项目，并通过**钉钉机器人**推送中文摘要。

## 功能

- 使用 GitHub Search API 获取近期热门仓库
- 支持钉钉自定义机器人推送（Markdown 消息）
- 支持钉钉加签安全校验（HMAC-SHA256）
- 支持 AI 中文摘要（可选）
- AI 失败时自动回退到规则式中文摘要
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

#### `DINGTALK_WEBHOOK`
钉钉自定义机器人的 Webhook 地址。

示例：

```text
https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### `GH_TOKEN`
你自己的 GitHub Personal Access Token，用于调用 GitHub API，避免过低的 rate limit。

### 可选（推荐配置，用于加签安全校验）

#### `DINGTALK_SECRET`
钉钉机器人开启"加签"后的密钥（以 `SEC` 开头）。

如果你在创建机器人时选择了"加签"安全策略，把该密钥存入此 secret。  
如果未开启加签，可以不填。

### 如果启用 AI 摘要，建议配置

#### `OPENAI_API_KEY`
用于调用大模型生成中文摘要。

### 可选

#### `OPENAI_BASE_URL`
如果你使用兼容 OpenAI API 的服务，可以自定义 Base URL。默认值：

```text
https://api.openai.com/v1
```

#### `OPENAI_MODEL`
指定使用的模型名称。例如：

```text
gpt-4.1-mini
```

## 如何创建钉钉自定义机器人

1. 打开钉钉，进入你想接收通知的群
2. 点击右上角 **群设置** → **智能群助手**（或"机器人"）
3. 点击 **添加机器人**
4. 选择 **自定义**
5. 给机器人起一个名字，例如：`GitHub Hot Daily`
6. **安全设置**选择以下之一：
   - **加签**（推荐）：复制"密钥"（以 `SEC` 开头），保存为 GitHub Secret `DINGTALK_SECRET`
   - **自定义关键词**：填写 `GitHub`，确保推送内容包含该词即可（本项目消息标题固定包含 `GitHub`）
   - **IP 地址段**：不推荐，GitHub Actions 出口 IP 不固定
7. 创建成功后，复制 **Webhook 地址**，保存为 GitHub Secret `DINGTALK_WEBHOOK`

> 加签方式安全性最高，且本项目已内置支持，推荐优先选择。

## 如何创建 GitHub Token

1. 打开 GitHub → `Settings` → `Developer settings` → `Personal access tokens`
2. 创建一个新的 Classic Token（公开仓库不需要特殊权限）
3. 保存到仓库 Secret：`GH_TOKEN`

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

关闭 AI 摘要（不需要 OPENAI_API_KEY）：

```yaml
ENABLE_AI_SUMMARY: "false"
```

## 推荐配置

如果你想让结果更稳定，建议：

- `DAYS: "7"`
- `TOP_N: "10"`
- `ENABLE_AI_SUMMARY: "false"`（先跑通，之后再考虑加 AI）

## 说明

这个项目通过 GitHub Search API 获取热门项目，并生成中文摘要通过钉钉推送。

后续可以继续升级：

- 增加历史去重
- 增加 star 增长对比
- 支持多语言分类推送
- 支持更丰富的钉钉卡片样式
