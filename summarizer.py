"""
AI 摘要模块 - 使用 DeepSeek API 生成中文新闻摘要
"""

from openai import OpenAI
import config
import time
import re

CATEGORY_TITLES = {
    "finance": "金融财经",
    "politics": "国际政治",
    "tech": "科技动态",
    "crypto": "币圈快讯",
    "other": "其他要闻",
}

CATEGORY_HEADERS = {
    "finance": "## 💰 金融财经",
    "politics": "## 🌍 国际政治",
    "tech": "## 🔬 科技动态",
    "crypto": "## ₿ 币圈快讯",
    "other": "## 📰 其他要闻",
}


def create_client():
    """创建 DeepSeek API 客户端"""
    return OpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL,
        timeout=config.SUMMARY_TIMEOUT
    )


def _call_llm(client: OpenAI, prompt: str) -> str:
    max_retries = config.SUMMARY_MAX_RETRIES
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位专业的双语新闻编辑，擅长将英文新闻翻译总结成简洁的中文。对金融市场、国际政治、科技发展和加密货币领域都有深入了解。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.SUMMARY_TEMPERATURE,
                max_tokens=config.SUMMARY_MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"API 调用失败，{5 * (attempt + 1)} 秒后重试... ({attempt + 1}/{max_retries})")
                time.sleep(5 * (attempt + 1))
            else:
                return f"生成摘要失败: {e}"


def _split_news_by_category(news_text: str) -> dict:
    """按分类标题切分新闻文本"""
    sections = {}
    parts = re.split(r"^=== (.+?) ===\s*$", news_text, flags=re.MULTILINE)
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        sections[title] = body
    return sections


def _summarize_full(client: OpenAI, news_text: str) -> str:
    prompt = f"""你是一位专业的新闻编辑。请将以下分类新闻翻译并总结成中文。

要求：
1. 按照金融、政治、科技、币圈、其他五个主题分类
2. 金融、政治、科技、其他四个分类需要按地区（美国、欧洲、日韩、澳新）分别总结
3. 币圈新闻不分地区，直接总结
4. 每个地区选出 2-4 条最重要的新闻
5. 每条新闻用 1-2 句话概括要点，突出关键数据和影响
6. 使用简洁专业的中文表达
7. 币圈新闻要特别关注价格变动、监管政策、重大项目进展
8. 在最后添加"今日要点"，总结各领域最值得关注的事件

新闻内容：
{news_text}

请严格按以下格式输出：

## 💰 金融财经

### 🇺🇸 美国
1. **新闻标题** - 新闻摘要

### 🇪🇺 欧洲
1. **新闻标题** - 新闻摘要

### 🇯🇵🇰🇷 日韩
1. **新闻标题** - 新闻摘要

### 🇦🇺🇳🇿 澳新
1. **新闻标题** - 新闻摘要

## 🌍 国际政治

### 🇺🇸 美国
1. **新闻标题** - 新闻摘要

### 🇪🇺 欧洲
1. **新闻标题** - 新闻摘要

### 🇯🇵🇰🇷 日韩
1. **新闻标题** - 新闻摘要

### 🇦🇺🇳🇿 澳新
1. **新闻标题** - 新闻摘要

## 🔬 科技动态

### 🇺🇸 美国
1. **新闻标题** - 新闻摘要

### 🇪🇺 欧洲
1. **新闻标题** - 新闻摘要

### 🇯🇵🇰🇷 日韩
1. **新闻标题** - 新闻摘要

### 🇦🇺🇳🇿 澳新
1. **新闻标题** - 新闻摘要

## ₿ 币圈快讯

1. **新闻标题** - 新闻摘要

## 📰 其他要闻

### 🇺🇸 美国
1. **新闻标题** - 新闻摘要

### 🇪🇺 欧洲
1. **新闻标题** - 新闻摘要

### 🇯🇵🇰🇷 日韩
1. **新闻标题** - 新闻摘要

### 🇦🇺🇳🇿 澳新
1. **新闻标题** - 新闻摘要

## 📌 今日要点

- **金融**：一句话总结
- **政治**：一句话总结
- **科技**：一句话总结
- **币圈**：一句话总结
"""
    return _call_llm(client, prompt)


def _summarize_category(client: OpenAI, category_key: str, category_text: str) -> str:
    category_title = CATEGORY_TITLES[category_key]
    header = CATEGORY_HEADERS[category_key]

    if category_key == "crypto":
        format_block = f"""{header}

1. **新闻标题** - 新闻摘要
"""
        rules = "币圈新闻不分地区，选出 3-5 条最重要的新闻。若无内容请写“暂无重要新闻”。"
    else:
        format_block = f"""{header}

### 🇺🇸 美国
1. **新闻标题** - 新闻摘要

### 🇪🇺 欧洲
1. **新闻标题** - 新闻摘要

### 🇯🇵🇰🇷 日韩
1. **新闻标题** - 新闻摘要

### 🇦🇺🇳🇿 澳新
1. **新闻标题** - 新闻摘要
"""
        rules = "每个地区选出 2-4 条最重要的新闻。若某地区无内容请写“暂无重要新闻”。"

    prompt = f"""你是一位专业的新闻编辑。请将以下“{category_title}”分类新闻翻译并总结成中文。

要求：
1. 使用简洁专业的中文表达
2. 每条新闻用 1-2 句话概括要点，突出关键数据和影响
3. {rules}

新闻内容：
{category_text}

请严格按以下格式输出：

{format_block}
"""
    return _call_llm(client, prompt)


def _summarize_key_points(client: OpenAI, category_sections: dict) -> str:
    prompt = f"""请根据以下新闻摘要，生成“今日要点”部分（只输出今日要点，不要重复其他内容）。

摘要内容：
{category_sections}

请严格按以下格式输出：

## 📌 今日要点

- **金融**：一句话总结
- **政治**：一句话总结
- **科技**：一句话总结
- **币圈**：一句话总结
"""
    return _call_llm(client, prompt)


def generate_summary(news_text: str) -> str:
    """使用 DeepSeek 生成中文新闻摘要"""
    client = create_client()

    if len(news_text) <= config.SUMMARY_MAX_INPUT_CHARS:
        return _summarize_full(client, news_text)

    print("新闻内容较长，启用分块总结...")
    sections = _split_news_by_category(news_text)
    category_outputs = {}

    for key in ["finance", "politics", "tech", "crypto", "other"]:
        title = CATEGORY_TITLES[key]
        category_text = sections.get(title, "")
        category_outputs[key] = _summarize_category(client, key, category_text)

    key_points = _summarize_key_points(client, category_outputs)

    return "\n\n".join([
        category_outputs["finance"],
        category_outputs["politics"],
        category_outputs["tech"],
        category_outputs["crypto"],
        category_outputs["other"],
        key_points,
    ])


if __name__ == "__main__":
    test_news = """
    === 金融财经 ===
    --- 🇺🇸 美国 ---
    1. [Bloomberg] Fed signals rate cut
       Federal Reserve officials indicated they may cut interest rates.
    """
    print("正在生成摘要...")
    summary = generate_summary(test_news)
    print(summary)
