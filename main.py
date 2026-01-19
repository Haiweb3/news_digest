#!/usr/bin/env python3
"""
全球新闻日报 - 主程序
每天自动获取全球新闻（金融、政治、科技、币圈等），按地区分类生成中文摘要并发送邮件
"""

import sys
import time
from datetime import datetime, timedelta

from news_fetcher import fetch_all_news, format_news_for_summary, count_total_news, print_news_stats
from summarizer import generate_summary
from email_sender import send_news_digest
from config import SCHEDULE_DAILY_TIME


def run_once():
    print(f"\n{'='*50}")
    print(f"全球新闻日报 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    # 1. 获取新闻
    print("📡 正在获取新闻...")
    news_data = fetch_all_news()

    total_news = count_total_news(news_data)
    if total_news == 0:
        print("❌ 未获取到任何新闻，程序退出")
        return False

    print(f"\n✅ 共获取 {total_news} 条新闻")
    print_news_stats(news_data)
    print()

    # 2. 格式化新闻
    news_text = format_news_for_summary(news_data)

    # 3. 生成中文摘要
    print("🤖 正在使用 DeepSeek 生成中文摘要...")
    summary = generate_summary(news_text)

    if summary.startswith("生成摘要失败"):
        print(f"❌ {summary}")
        return False

    print("✅ 摘要生成完成\n")
    print("-" * 50)
    print(summary)
    print("-" * 50 + "\n")

    # 4. 发送邮件
    print("📧 正在发送邮件...")
    success = send_news_digest(summary)

    if success:
        print("\n✅ 新闻日报发送成功！")
        return True
    else:
        print("\n❌ 邮件发送失败，请检查配置")
        return False


def parse_daily_time(value):
    try:
        parts = value.split(":")
        if len(parts) != 2:
            return None
        hour = int(parts[0])
        minute = int(parts[1])
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            return None
        return hour, minute
    except ValueError:
        return None


def run_scheduler(daily_time):
    parsed = parse_daily_time(daily_time)
    if not parsed:
        print(f"❌ SCHEDULE_DAILY_TIME 格式错误: {daily_time}，应为 24 小时制 HH:MM")
        sys.exit(1)

    hour, minute = parsed
    print(f"🕒 已启用定时任务，每天 {hour:02d}:{minute:02d} 执行")

    while True:
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run = next_run + timedelta(days=1)

        sleep_seconds = (next_run - now).total_seconds()
        print(f"⏳ 下次执行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            print("\n🛑 已停止定时任务")
            sys.exit(0)

        if not run_once():
            print("⚠️ 本次任务执行失败，将在下次计划时间重试")


if __name__ == "__main__":
    if SCHEDULE_DAILY_TIME:
        run_scheduler(SCHEDULE_DAILY_TIME)
    else:
        sys.exit(0 if run_once() else 1)
