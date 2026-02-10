# 配置文件
import os


def _load_dotenv(path: str) -> None:
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


_load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 邮件配置
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "")

# 摘要生成配置
SUMMARY_TIMEOUT = float(os.getenv("SUMMARY_TIMEOUT", "180"))
SUMMARY_MAX_TOKENS = int(os.getenv("SUMMARY_MAX_TOKENS", "2000"))
SUMMARY_TEMPERATURE = float(os.getenv("SUMMARY_TEMPERATURE", "0.7"))
SUMMARY_MAX_RETRIES = int(os.getenv("SUMMARY_MAX_RETRIES", "3"))
SUMMARY_MAX_INPUT_CHARS = int(os.getenv("SUMMARY_MAX_INPUT_CHARS", "8000"))

# 晨读分析短文配置（单主题、可朗读）
MORNING_ARTICLE_TIMEOUT = float(os.getenv("MORNING_ARTICLE_TIMEOUT", "180"))
MORNING_ARTICLE_MAX_TOKENS = int(os.getenv("MORNING_ARTICLE_MAX_TOKENS", "1800"))
MORNING_ARTICLE_TEMPERATURE = float(os.getenv("MORNING_ARTICLE_TEMPERATURE", "0.5"))
MORNING_ARTICLE_MAX_RETRIES = int(os.getenv("MORNING_ARTICLE_MAX_RETRIES", "3"))
MORNING_ARTICLE_MIN_CHARS = int(os.getenv("MORNING_ARTICLE_MIN_CHARS", "650"))
MORNING_ARTICLE_MAX_CHARS = int(os.getenv("MORNING_ARTICLE_MAX_CHARS", "1200"))

# RSS 抓取超时（秒）
RSS_TIMEOUT = int(os.getenv("RSS_TIMEOUT", "15"))
RSS_MAX_WORKERS = int(os.getenv("RSS_MAX_WORKERS", "8"))
RSS_MAX_RETRIES = int(os.getenv("RSS_MAX_RETRIES", "2"))
RSS_BACKOFF_SECONDS = float(os.getenv("RSS_BACKOFF_SECONDS", "1.5"))
RSS_USER_AGENT = os.getenv(
    "RSS_USER_AGENT",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
)

# 定时任务配置
# 24小时制 "HH:MM"，为空则不启用内部定时
SCHEDULE_DAILY_TIME = os.getenv("SCHEDULE_DAILY_TIME", "").strip()

# 新闻源配置（按主题和地区分类）
NEWS_SOURCES = {
    # ==================== 金融财经 ====================
    "finance": {
        "usa": [
            {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss"},
            {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
            {"name": "Wall Street Journal", "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"},
        ],
        "europe": [
            {"name": "Financial Times", "url": "https://www.ft.com/rss/home"},
            {"name": "Reuters Business", "url": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"},
        ],
        "japan_korea": [
            {"name": "Nikkei Asia", "url": "https://asia.nikkei.com/rss/feed/nar"},
            {"name": "Korea Economic Daily", "url": "https://www.kedglobal.com/rss/all_news.xml"},
        ],
        "aunz": [
            {"name": "AFR", "url": "https://www.afr.com/rss/feed.xml"},
            {"name": "NZ Herald Business", "url": "https://www.nzherald.co.nz/arc/outboundfeeds/rss/section/business/?outputType=xml"},
        ],
    },

    # ==================== 国际政治 ====================
    "politics": {
        "usa": [
            {"name": "NPR Politics", "url": "https://feeds.npr.org/1014/rss.xml"},
            {"name": "Politico", "url": "https://www.politico.com/rss/politicopicks.xml"},
            {"name": "The Hill", "url": "https://thehill.com/feed/"},
        ],
        "europe": [
            {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
            {"name": "The Guardian World", "url": "https://www.theguardian.com/world/rss"},
            {"name": "DW News", "url": "https://rss.dw.com/rdf/rss-en-all"},
        ],
        "japan_korea": [
            {"name": "NHK World", "url": "https://www3.nhk.or.jp/rss/news/cat0.xml"},
            {"name": "Yonhap News", "url": "https://en.yna.co.kr/RSS/news.xml"},
            {"name": "Japan Times", "url": "https://www.japantimes.co.jp/feed/"},
        ],
        "aunz": [
            {"name": "ABC Australia", "url": "https://www.abc.net.au/news/feed/2942460/rss.xml"},
            {"name": "RNZ News", "url": "https://www.rnz.co.nz/rss/national.xml"},
        ],
    },

    # ==================== 科技动态 ====================
    "tech": {
        "usa": [
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
            {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
            {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
        ],
        "europe": [
            {"name": "The Register", "url": "https://www.theregister.com/headlines.atom"},
            {"name": "Euronews Tech", "url": "https://www.euronews.com/rss?level=vertical&name=next"},
        ],
        "japan_korea": [
            {"name": "Japan Times Tech", "url": "https://www.japantimes.co.jp/feed/"},
            {"name": "Korea Herald Tech", "url": "http://www.koreaherald.com/rss_xml.php"},
        ],
        "aunz": [
            {"name": "iTnews Australia", "url": "https://www.itnews.com.au/rss/feed.xml"},
            {"name": "Stuff NZ Tech", "url": "https://www.stuff.co.nz/rss"},
        ],
    },

    # ==================== 币圈快讯（全球，不分地区）====================
    "crypto": {
        "global": [
            {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"},
            {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss"},
            {"name": "Bitcoin Magazine", "url": "https://bitcoinmagazine.com/feed"},
            {"name": "Decrypt", "url": "https://decrypt.co/feed"},
            {"name": "The Block", "url": "https://www.theblock.co/rss.xml"},
        ],
    },

    # ==================== 其他要闻 ====================
    "other": {
        "usa": [
            {"name": "CNN", "url": "http://rss.cnn.com/rss/edition.rss"},
            {"name": "AP News", "url": "https://apnews.com/index.rss"},
        ],
        "europe": [
            {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/rss.xml"},
            {"name": "France 24", "url": "https://www.france24.com/en/rss"},
        ],
        "japan_korea": [
            {"name": "NHK Japan", "url": "https://www3.nhk.or.jp/rss/news/cat0.xml"},
            {"name": "Korea Times", "url": "https://www.koreatimes.co.kr/www/rss/rss.xml"},
        ],
        "aunz": [
            {"name": "Sydney Morning Herald", "url": "https://www.smh.com.au/rss/feed.xml"},
            {"name": "NZ Herald", "url": "https://www.nzherald.co.nz/arc/outboundfeeds/rss/curated/78/?outputType=xml"},
        ],
    },
}

# 每个来源获取的新闻数量
NEWS_PER_SOURCE = 3
