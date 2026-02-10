"""
邮件发送模块 - 发送新闻摘要邮件
"""

import smtplib
import ssl
import html
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
    """轻量 Markdown 转 HTML（优先使用 python-markdown；否则退回简化转换）"""
    # 1) Prefer a real Markdown parser if available.
    try:
        import markdown  # type: ignore

        return markdown.markdown(
            md_text or "",
            extensions=["extra", "sane_lists", "nl2br", "smarty"],
            output_format="html5",
        )
    except Exception:
        pass

    # 2) Fallback: escape then re-introduce a small subset of formatting.
    import re

    src = md_text or ""
    out = html.escape(src)

    # Headings (must run before <br>)
    out = re.sub(r"^## (.+)$", r"<h2>\1</h2>", out, flags=re.MULTILINE)
    out = re.sub(r"^### (.+)$", r"<h3>\1</h3>", out, flags=re.MULTILINE)

    # Bold
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)

    # Simple unordered list: "- item"
    def _ul(m: re.Match) -> str:
        items = m.group(0).strip().splitlines()
        lis = "".join(f"<li>{re.sub(r'^-\\s+', '', it)}</li>" for it in items)
        return f"<ul>{lis}</ul>"

    out = re.sub(r"(?:^- .+(?:\n|$))+", _ul, out, flags=re.MULTILINE)

    # Line breaks
    out = out.replace("\n", "<br>\n")

    # 包装
    page = f"""<!DOCTYPE html>
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
        h3 {{
            color: #34495e;
            margin-top: 20px;
        }}
        strong {{
            color: #2980b9;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 6px;
        }}
    </style>
</head>
<body>
    {out}
</body>
</html>"""
    return page


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
