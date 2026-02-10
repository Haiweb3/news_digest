#!/usr/bin/env python3
"""
晚读分析短文 - 主程序

每天从 finance + tech 新闻中选一个核心主题，生成 3–5 分钟可朗读短文并发邮件。
"""

from datetime import datetime

from email_sender import send_email
from news_fetcher import fetch_all_news
from morning_article import generate_morning_article


def run_once() -> bool:
    print(f"\n{'='*50}")
    print(f"晚读分析短文 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    print("📡 正在获取金融 + 科技新闻...")
    news_data = fetch_all_news(categories=["finance", "tech"])

    print("🤖 正在生成晨读分析短文...")
    try:
        article = generate_morning_article(news_data)
    except Exception as exc:
        print(f"❌ 生成失败: {exc}")
        return False

    today = datetime.now().strftime("%Y年%m月%d日")
    subject = f"🌙 AI×金融晚读 - {today}"

    print("📧 正在发送邮件...")
    success = send_email(subject, article)
    if success:
        print("✅ 发送成功")
    else:
        print("❌ 发送失败")
    return success


if __name__ == "__main__":
    raise SystemExit(0 if run_once() else 1)
