"""
新闻抓取模块 - 从 RSS 源获取全球新闻（按主题和地区分类）
"""

from __future__ import annotations

import feedparser
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import config

# 主题分类配置
CATEGORIES = {
    "finance": ("金融财经", "💰"),
    "politics": ("国际政治", "🌍"),
    "tech": ("科技动态", "🔬"),
    "crypto": ("币圈快讯", "₿"),
    "other": ("其他要闻", "📰")
}

# 地区分类配置
REGIONS = {
    "usa": ("美国", "🇺🇸"),
    "europe": ("欧洲", "🇪🇺"),
    "japan_korea": ("日韩", "🇯🇵🇰🇷"),
    "aunz": ("澳新", "🇦🇺🇳🇿"),
    "global": ("全球", "🌐")
}


def _clean_text(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _normalize_key(link: str, title: str) -> str:
    link = (link or "").strip()
    if link:
        return f"link:{link}"
    return f"title:{(title or '').strip().lower()}"


def fetch_news_from_rss(url: str, source_name: str, limit: int = 3) -> List[Dict]:
    """从单个 RSS 源获取新闻（带超时与轻量重试）"""
    last_err: Exception | None = None
    for attempt in range(config.RSS_MAX_RETRIES + 1):
        try:
            req = Request(url, headers={"User-Agent": config.RSS_USER_AGENT})
            with urlopen(req, timeout=config.RSS_TIMEOUT) as resp:
                raw = resp.read()

            feed = feedparser.parse(raw)
            # feedparser 可能会设置 bozo=1 表示解析异常；不强制失败，尽量吃到 entries。
            news_list: List[Dict] = []
            for entry in feed.entries[:limit]:
                title = entry.get("title", "无标题")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", "")) or ""
                news_item = {
                    "title": _clean_text(title)[:200],
                    "link": (link or "").strip(),
                    "summary": _clean_text(summary)[:500],
                    "source": source_name,
                    "published": entry.get("published", "") or "",
                }
                news_list.append(news_item)
            return news_list

        except (HTTPError, URLError, TimeoutError, Exception) as e:
            last_err = e
            if attempt < config.RSS_MAX_RETRIES:
                time.sleep(config.RSS_BACKOFF_SECONDS * (attempt + 1))
                continue
            print(f"获取 {source_name} 新闻失败: {e}")
            return []

    # 理论上不会到这里
    print(f"获取 {source_name} 新闻失败: {last_err}")
    return []


def _dedup_in_place(all_news: Dict[str, Dict[str, List[Dict]]]) -> None:
    for category_key, regions in all_news.items():
        for region_key, items in regions.items():
            seen: set[str] = set()
            out: List[Dict] = []
            for it in items:
                k = _normalize_key(it.get("link", ""), it.get("title", ""))
                if k in seen:
                    continue
                seen.add(k)
                out.append(it)
            all_news[category_key][region_key] = out


def fetch_all_news(categories: List[str] | None = None) -> Dict[str, Dict[str, List[Dict]]]:
    """获取新闻源的新闻，按主题和地区分类

    Args:
        categories: 需要抓取的分类 key 列表（如 ["finance", "tech"]）。
            为空则抓取全部分类。
    """
    all_news = {}

    selected_categories = categories or list(CATEGORIES.keys())

    tasks: List[Tuple[str, str, str, str]] = []  # (category_key, region_key, source_name, url)
    for category_key in selected_categories:
        if category_key not in CATEGORIES:
            continue
        all_news[category_key] = {}
        category_sources = config.NEWS_SOURCES.get(category_key, {})
        for region_key, sources in category_sources.items():
            all_news[category_key][region_key] = []
            for source in sources:
                tasks.append((category_key, region_key, source["name"], source["url"]))

    with ThreadPoolExecutor(max_workers=config.RSS_MAX_WORKERS) as ex:
        future_map = {
            ex.submit(fetch_news_from_rss, url, source_name, config.NEWS_PER_SOURCE): (category_key, region_key, source_name)
            for (category_key, region_key, source_name, url) in tasks
        }

        for fut in as_completed(future_map):
            category_key, region_key, source_name = future_map[fut]
            try:
                news = fut.result()
            except Exception as e:
                print(f"获取 {source_name} 新闻失败: {e}")
                news = []
            all_news[category_key][region_key].extend(news)
            print(f"从 {source_name} 获取了 {len(news)} 条新闻")

    _dedup_in_place(all_news)
    return all_news


def format_news_for_summary(news_data: Dict[str, Dict[str, List[Dict]]]) -> str:
    """将新闻格式化为文本，供 AI 总结"""
    parts: List[str] = []

    for category_key, (category_name, cat_emoji) in CATEGORIES.items():
        category_news = news_data.get(category_key, {})
        if not category_news:
            continue

        parts.append(f"=== {category_name} ===\n")

        # 币圈不分地区
        if category_key == "crypto":
            global_news = category_news.get("global", [])
            for i, news in enumerate(global_news, 1):
                parts.append(f"{i}. [{news['source']}] {news['title']}")
                parts.append(f"   {news['summary']}\n")
        else:
            # 其他分类按地区显示
            for region_key in ["usa", "europe", "japan_korea", "aunz"]:
                region_news = category_news.get(region_key, [])
                if region_news:
                    region_name, region_emoji = REGIONS[region_key]
                    parts.append(f"--- {region_emoji} {region_name} ---")
                    for i, news in enumerate(region_news, 1):
                        parts.append(f"{i}. [{news['source']}] {news['title']}")
                        parts.append(f"   {news['summary']}\n")

        parts.append("")

    return "\n".join(parts)


def count_total_news(news_data: Dict[str, Dict[str, List[Dict]]]) -> int:
    """统计总新闻数"""
    total = 0
    for category_news in news_data.values():
        for region_news in category_news.values():
            total += len(region_news)
    return total


def print_news_stats(news_data: Dict[str, Dict[str, List[Dict]]]):
    """打印新闻统计"""
    for cat_key, (cat_name, cat_emoji) in CATEGORIES.items():
        category_news = news_data.get(cat_key, {})
        cat_total = sum(len(r) for r in category_news.values())
        print(f"   {cat_emoji} {cat_name}: {cat_total} 条")

        if cat_key != "crypto":
            for region_key in ["usa", "europe", "japan_korea", "aunz"]:
                region_news = category_news.get(region_key, [])
                if region_news:
                    region_name, region_emoji = REGIONS[region_key]
                    print(f"      {region_emoji} {region_name}: {len(region_news)} 条")


if __name__ == "__main__":
    print("正在获取新闻...")
    news = fetch_all_news()
    print("\n" + "="*50)
    print(f"共获取 {count_total_news(news)} 条新闻")
    print_news_stats(news)
    print("="*50)
