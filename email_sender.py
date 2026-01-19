"""
邮件发送模块 - 发送新闻摘要邮件
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import config


def send_email(subject: str, content: str) -> bool:
    """发送邮件"""
    if not config.SENDER_EMAIL or not config.SENDER_PASSWORD or not config.RECEIVER_EMAIL:
        print("错误: 请在 config.py 中配置邮件信息")
        return False

    try:
        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = config.SENDER_EMAIL
        msg["To"] = config.RECEIVER_EMAIL

        # 将 Markdown 转换为简单 HTML
        html_content = markdown_to_html(content)

        # 添加纯文本和 HTML 版本
        text_part = MIMEText(content, "plain", "utf-8")
        html_part = MIMEText(html_content, "html", "utf-8")

        msg.attach(text_part)
        msg.attach(html_part)

        # 发送邮件
        if config.SMTP_PORT == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, context=context) as server:
                server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
                server.sendmail(config.SENDER_EMAIL, config.RECEIVER_EMAIL, msg.as_string())
        else:
            context = ssl.create_default_context()
            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
                server.sendmail(config.SENDER_EMAIL, config.RECEIVER_EMAIL, msg.as_string())

        print(f"邮件发送成功: {config.RECEIVER_EMAIL}")
        return True

    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


def markdown_to_html(md_text: str) -> str:
    """简单的 Markdown 转 HTML"""
    import re

    html = md_text

    # 标题
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

    # 粗体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # 换行
    html = html.replace('\n', '<br>\n')

    # 包装
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }}
            h2 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-top: 30px;
            }}
            strong {{
                color: #2980b9;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    return html


def send_news_digest(summary: str) -> bool:
    """发送新闻摘要邮件"""
    today = datetime.now().strftime("%Y年%m月%d日")
    subject = f"📰 全球新闻日报 - {today}"
    return send_email(subject, summary)


if __name__ == "__main__":
    # 测试
    test_content = """
## 🇦🇺 澳大利亚新闻

1. **测试新闻** - 这是一条测试新闻

## 📌 今日要点

这是测试邮件。
"""
    print("正在发送测试邮件...")
    send_news_digest(test_content)
