"""
晨读分析短文生成模块

目标：每天选一个“AI × 金融/市场”核心主题，生成 3–5 分钟可朗读的中文分析短文。
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List

from openai import OpenAI

import config


@dataclass(frozen=True)
class NewsItem:
    id: str
    category: str
    region: str
    source: str
    title: str
    summary: str
    link: str


def create_client() -> OpenAI:
    return OpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL,
        timeout=config.MORNING_ARTICLE_TIMEOUT,
    )


def _call_llm(client: OpenAI, *, system: str, user: str, max_tokens: int) -> str:
    for attempt in range(config.MORNING_ARTICLE_MAX_RETRIES):
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=config.MORNING_ARTICLE_TEMPERATURE,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            if attempt >= config.MORNING_ARTICLE_MAX_RETRIES - 1:
                raise
            wait_s = 5 * (attempt + 1)
            print(f"API 调用失败：{exc}，{wait_s}s 后重试... ({attempt+1}/{config.MORNING_ARTICLE_MAX_RETRIES})")
            time.sleep(wait_s)
    return ""


def _extract_json_object(text: str) -> Dict[str, Any]:
    """
    尝试从模型输出中提取 JSON 对象。
    兼容模型把 JSON 包在 ```json``` 或前后附带说明的情况。
    """
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])

    raise ValueError("无法从模型输出解析 JSON")


def _is_ai_related(text: str) -> bool:
    t = text.lower()
    keywords = [
        "ai",
        "a.i.",
        "artificial intelligence",
        "llm",
        "大模型",
        "人工智能",
        "模型",
        "算力",
        "gpu",
        "nvidia",
        "openai",
        "deepmind",
        "anthropic",
        "chatgpt",
        "芯片",
        "数据中心",
        "cloud",
        "推理",
        "训练",
    ]
    return any(k in t for k in keywords)


def _flatten_items(news_data: Dict[str, Dict[str, List[Dict]]]) -> List[NewsItem]:
    items: List[NewsItem] = []
    idx = 1
    for category, regions in news_data.items():
        for region, news_list in regions.items():
            for n in news_list:
                title = (n.get("title") or "").strip()
                summary = (n.get("summary") or "").strip()
                source = (n.get("source") or "").strip()
                link = (n.get("link") or "").strip()
                if not title:
                    continue
                items.append(
                    NewsItem(
                        id=f"N{idx:03d}",
                        category=category,
                        region=region,
                        source=source,
                        title=title,
                        summary=summary,
                        link=link,
                    )
                )
                idx += 1
    return items


def _select_candidates(items: List[NewsItem]) -> List[NewsItem]:
    """
    候选集合：全部 finance + AI 相关 tech（若过少则补足 tech 前几条）。
    """
    finance = [x for x in items if x.category == "finance"]
    tech = [x for x in items if x.category == "tech"]
    ai_tech = [x for x in tech if _is_ai_related(f"{x.title}\n{x.summary}")]

    candidates = finance + ai_tech
    if len(candidates) < 12:
        remaining = [x for x in tech if x not in ai_tech]
        candidates.extend(remaining[: max(0, 12 - len(candidates))])

    # 去重（按 link 或 title）
    seen: set[str] = set()
    deduped: List[NewsItem] = []
    for x in candidates:
        key = x.link or x.title
        if key in seen:
            continue
        seen.add(key)
        deduped.append(x)
    return deduped[:30]


def _items_to_brief_text(items: List[NewsItem]) -> str:
    lines: List[str] = []
    for x in items:
        summary = x.summary.replace("\n", " ").strip()
        summary = re.sub(r"\s+", " ", summary)
        summary = summary[:260]
        lines.append(
            f"{x.id} | {x.category}/{x.region} | {x.source} | {x.title}\n"
            f"摘要: {summary}\n链接: {x.link}"
        )
    return "\n\n".join(lines)


def _plan_topic_and_outline(client: OpenAI, items: List[NewsItem]) -> Dict[str, Any]:
    system = (
        "你是一位中文写作教练 + 宏观与科技投资分析师。"
        "你擅长用框架化语言写出“可朗读、逻辑强、可复述”的短文。"
        "你严禁编造输入中不存在的具体数字与事实；若缺少数据，用定性表述并明确不确定性。"
    )
    user = f"""下面是一组新闻条目（包含标题/摘要/链接）。请你完成“选题+大纲”，并严格输出 JSON（不要输出任何非 JSON 内容）。

目标：选择 1 个“AI × 金融/市场”核心主题，生成 3–5 分钟晨读短文。

要求：
1) 主题必须能形成清晰的因果链（至少 4 个环节）。
2) 大纲必须使用固定框架：导语(3句) / 事实卡片(3条) / 分析主干(因果链+二阶影响+风险反例) / 结论(3句) / 观察清单(3条)。
3) 事实卡片与引用必须来自给定条目，使用条目 id 引用（如 N003）。

输出 JSON schema：
{{
  "theme_title": "一句话标题",
  "thesis": "一句话核心结论",
  "supporting_ids": ["N001","N002"],
  "outline": {{
     "hook_3_sentences": ["...","...","..."],
     "fact_cards": [{{"id":"N001","point":"一句话事实"}}, ...],
     "causal_chain": ["环节1→环节2", "..."],
     "second_order": ["二阶影响1", "二阶影响2"],
     "risks_counterpoints": ["风险/反例1", "风险/反例2"],
     "conclusion_3_sentences": ["...","...","..."],
     "watchlist": ["观察点1","观察点2","观察点3"]
  }}
}}

新闻条目：
{_items_to_brief_text(items)}
"""
    raw = _call_llm(client, system=system, user=user, max_tokens=900)
    data = _extract_json_object(raw)
    if not data.get("supporting_ids"):
        raise ValueError("选题阶段返回不完整 JSON：缺少 supporting_ids")
    return data


def _write_article(client: OpenAI, plan: Dict[str, Any], items_by_id: Dict[str, NewsItem]) -> str:
    system = (
        "你是一位中文写作教练 + 投资研究员。"
        "你写作的文章必须适合朗读，句子不要太长，多用连接词。"
        "严禁编造输入中不存在的具体数字与事实；不确定之处要说清楚。"
    )

    cited_items = []
    for nid in plan.get("supporting_ids", []):
        it = items_by_id.get(nid)
        if not it:
            continue
        cited_items.append(f"{nid}: {it.title} ({it.source}) {it.link}")

    target_min = config.MORNING_ARTICLE_MIN_CHARS
    target_max = config.MORNING_ARTICLE_MAX_CHARS
    user = f"""请根据以下“选题与大纲”写成一篇中文晨读短文。

硬性要求：
1) 总长度控制在 {target_min}–{target_max} 个中文字符左右（不含链接 URL 也可以）。
2) 结构必须严格如下，并使用 Markdown 标题：
   - # 标题
   - ## 30秒导语（3句）
   - ## 事实卡片（3条，必须标注来源 id）
   - ## 分析主干（因果链 → 二阶影响 → 风险/反例）
   - ## 结论（3句）
   - ## 观察清单（3条）
   - ## 参考链接（列出 supporting_ids 对应链接）
3) “事实卡片”里只写输入中明确提到的事实；如果不确定，用“据报道/可能/尚待确认”并标注不确定性。
4) 分析要用框架化语言（例如：驱动因素/传导路径/边际变化/情景假设）。

可引用的新闻（supporting_ids 对应）：
{chr(10).join(cited_items)}

选题与大纲（JSON）：
{json.dumps(plan, ensure_ascii=False)}
"""
    return _call_llm(client, system=system, user=user, max_tokens=config.MORNING_ARTICLE_MAX_TOKENS).strip()


def _enforce_length(client: OpenAI, article: str) -> str:
    chars = len(re.sub(r"\s+", "", article))
    if config.MORNING_ARTICLE_MIN_CHARS <= chars <= config.MORNING_ARTICLE_MAX_CHARS:
        return article

    target = (config.MORNING_ARTICLE_MIN_CHARS + config.MORNING_ARTICLE_MAX_CHARS) // 2
    system = "你是一位严谨的中文编辑，只做压缩/扩写，不引入新事实。"
    user = f"""请把下面文章调整到接近 {target} 个中文字符：
1) 保持原有结构与标题不变
2) 不要添加任何输入中不存在的新事实/数字
3) 如果需要缩短，优先删掉重复修饰；如果需要加长，优先补足逻辑连接与不确定性说明

文章：
{article}
"""
    revised = _call_llm(client, system=system, user=user, max_tokens=config.MORNING_ARTICLE_MAX_TOKENS).strip()
    return revised or article


def generate_morning_article(news_data: Dict[str, Dict[str, List[Dict]]]) -> str:
    client = create_client()

    items = _flatten_items(news_data)
    candidates = _select_candidates(items)
    if len(candidates) < 5:
        raise ValueError("候选新闻过少，无法生成晨读短文")

    items_by_id = {x.id: x for x in candidates}
    plan = _plan_topic_and_outline(client, candidates)
    article = _write_article(client, plan, items_by_id)
    article = _enforce_length(client, article)

    if not article or "##" not in article:
        raise ValueError("生成晨读短文失败：输出为空或结构不完整")
    return article

