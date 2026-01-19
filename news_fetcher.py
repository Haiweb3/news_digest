"""
新闻抓取模块 - 从 RSS 源获取全球新闻（按主题和地区分类）
"""

import feedparser
import re
import socket
from typing import List, Dict
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


def fetch_news_from_rss(url: str, source_name: str, limit: int = 3) -> List[Dict]:
    """从单个 RSS 源获取新闻"""
    news_list = []
    try:
        previous_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(config.RSS_TIMEOUT)
        feed = feedparser.parse(url)
        socket.setdefaulttimeout(previous_timeout)
        for entry in feed.entries[:limit]:
            news_item = {
                "title": entry.get("title", "无标题"),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "source": source_name,
                "published": entry.get("published", ""),
            }
            # 清理 HTML 标签
            if news_item["summary"]:
                news_item["summary"] = re.sub(r'<[^>]+>', '', news_item["summary"])
                news_item["summary"] = news_item["summary"][:500]
            news_list.append(news_item)
    except Exception as e:
        print(f"获取 {source_name} 新闻失败: {e}")
    return news_list


def fetch_all_news() -> Dict[str, Dict[str, List[Dict]]]:
    """获取所有新闻源的新闻，按主题和地区分类"""
    all_news = {}

    for category_key in CATEGORIES.keys():
        all_news[category_key] = {}
        category_sources = config.NEWS_SOURCES.get(category_key, {})

        for region_key in category_sources.keys():
            all_news[category_key][region_key] = []
            for source in category_sources[region_key]:
                news = fetch_news_from_rss(
                    source["url"],
                    source["name"],
                    config.NEWS_PER_SOURCE
                )
                all_news[category_key][region_key].extend(news)
                print(f"从 {source['name']} 获取了 {len(news)} 条新闻")

    return all_news


def format_news_for_summary(news_data: Dict[str, Dict[str, List[Dict]]]) -> str:
    """将新闻格式化为文本，供 AI 总结"""
    text = ""

    for category_key, (category_name, cat_emoji) in CATEGORIES.items():
        category_news = news_data.get(category_key, {})
        if not category_news:
            continue

        text += f"=== {category_name} ===\n\n"

        # 币圈不分地区
        if category_key == "crypto":
            global_news = category_news.get("global", [])
            for i, news in enumerate(global_news, 1):
                text += f"{i}. [{news['source']}] {news['title']}\n"
                text += f"   {news['summary']}\n\n"
        else:
            # 其他分类按地区显示
            for region_key in ["usa", "europe", "japan_korea", "aunz"]:
                region_news = category_news.get(region_key, [])
                if region_news:
                    region_name, region_emoji = REGIONS[region_key]
                    text += f"--- {region_emoji} {region_name} ---\n"
                    for i, news in enumerate(region_news, 1):
                        text += f"{i}. [{news['source']}] {news['title']}\n"
                        text += f"   {news['summary']}\n\n"

        text += "\n"

    return text


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
