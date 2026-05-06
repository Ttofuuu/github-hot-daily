import os
import sys
import json
import requests
from datetime import datetime, timedelta, timezone

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
TOP_N = int(os.getenv("TOP_N", "10"))
LANGUAGE = os.getenv("LANGUAGE", "").strip()
DAYS = int(os.getenv("DAYS", "1"))
ENABLE_AI_SUMMARY = os.getenv("ENABLE_AI_SUMMARY", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-hot-daily-bot"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def fetch_trending_repos(days=1, top_n=10, language=""):
    since_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    query_parts = [f"created:>{since_date}"]
    if language:
        query_parts.append(f"language:{language}")

    query = " ".join(query_parts)

    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": top_n,
    }

    resp = requests.get(url, headers=github_headers(), params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("items", []), since_date, query


def normalize_repo(repo):
    return {
        "name": repo.get("full_name", ""),
        "desc": repo.get("description") or "暂无描述",
        "lang": repo.get("language") or "未知",
        "stars": repo.get("stargazers_count", 0),
        "url": repo.get("html_url", ""),
    }


def fallback_chinese_summary(repos, since_date, days, language=""):
    today_cn = datetime.now().strftime("%Y-%m-%d")
    title = "GitHub 每日热门项目"
    if language:
        title += f"（{language}）"

    lines = [
        f"🚀 {title}",
        f"日期：{today_cn}",
        f"统计范围：最近 {days} 天内创建，并按 Star 排序",
        f"筛选条件：created:>{since_date}" + (f" language:{language}" if language else ""),
        "",
    ]

    if not repos:
        lines.append("今天没有获取到符合条件的热门项目。")
        return "\n".join(lines)

    for idx, repo in enumerate(repos, start=1):
        info = normalize_repo(repo)
        lines.append(f"{idx}. {info['name']}")
        lines.append(f"   ⭐ {info['stars']} | {info['lang']}")
        lines.append(f"   简介：{info['desc']}")
        lines.append(f"   链接：{info['url']}")
        lines.append("")

    lines.extend([
        "观察：",
        "- 最近热门项目通常集中在 AI、开发工具、自动化、安全等方向。",
        f"- 当前已按 {language} 语言过滤。" if language else "- 当前未限制编程语言。",
        "- 已启用兜底摘要模式；若配置 AI，可输出更自然的中文总结。",
    ])
    return "\n".join(lines)


def generate_ai_summary(repos, since_date, days, language=""):
    if not OPENAI_API_KEY:
        raise RuntimeError("ENABLE_AI_SUMMARY=true but OPENAI_API_KEY is missing")

    simplified = [normalize_repo(repo) for repo in repos]
    prompt = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "days": days,
        "since_date": since_date,
        "language_filter": language,
        "repos": simplified,
        "instructions": {
            "language": "zh-CN",
            "style": "简洁、信息密度高、适合IM推送",
            "requirements": [
                "输出纯文本，不要 Markdown 表格",
                "开头给出一句总览",
                "每个项目一行到两行，包含项目名、中文一句话介绍、Star、语言、链接",
                "结尾补一个“今日观察”小结",
                "不要编造仓库功能，只能基于给定信息合理概括"
            ]
        }
    }

    body = {
        "model": OPENAI_MODEL,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": "你是一个技术资讯编辑，负责把 GitHub 热门仓库整理成适合飞书推送的中文日报。"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(prompt, ensure_ascii=False)
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    url = OPENAI_BASE_URL.rstrip("/") + "/responses"
    resp = requests.post(url, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if "output_text" in data and data["output_text"]:
        return data["output_text"]

    output = data.get("output", [])
    collected = []
    for item in output:
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                collected.append(content.get("text", ""))
    text = "\n".join(x for x in collected if x.strip()).strip()
    if not text:
        raise RuntimeError(f"Unexpected AI response: {data}")
    return text


def build_card_payload(text, title="GitHub 每日热门项目"):
    return {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True,
                "enable_forward": True,
            },
            "header": {
                "template": "blue",
                "title": {
                    "tag": "plain_text",
                    "content": title,
                },
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": text.replace("\n", "\n")
                    }
                }
            ]
        }
    }


def send_to_feishu(webhook, payload):
    resp = requests.post(webhook, json=payload, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code", -1) != 0:
        raise RuntimeError(f"Feishu webhook error: {result}")
    return result


def main():
    if not FEISHU_WEBHOOK:
        raise RuntimeError("Missing FEISHU_WEBHOOK environment variable")

    repos, since_date, query = fetch_trending_repos(days=DAYS, top_n=TOP_N, language=LANGUAGE)

    if ENABLE_AI_SUMMARY:
        try:
            text = generate_ai_summary(repos, since_date, DAYS, LANGUAGE)
        except Exception as e:
            print(f"AI summary failed, fallback to default summary: {e}")
            text = fallback_chinese_summary(repos, since_date, DAYS, LANGUAGE)
    else:
        text = fallback_chinese_summary(repos, since_date, DAYS, LANGUAGE)

    title = "GitHub 每日热门项目"
    if LANGUAGE:
        title += f"（{LANGUAGE}）"

    payload = build_card_payload(text, title=title)
    send_to_feishu(FEISHU_WEBHOOK, payload)
    print(f"Push sent successfully. Query={query}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
