# 全球新闻日报

自动获取全球新闻（金融、政治、科技、币圈等），按地区分类生成中文摘要并发送邮件。

## 功能特点

- 自动从多个 RSS 源获取新闻
- 使用 DeepSeek AI 生成中文摘要
- 按地区分类新闻内容
- 自动发送邮件日报
- 支持定时任务

## 安装

1. 克隆仓库
```bash
git clone <your-repo-url>
cd news_digest
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

## 配置说明

在 `.env` 文件中配置以下参数：

- `SMTP_SERVER`: SMTP 服务器地址
- `SMTP_PORT`: SMTP 端口
- `SENDER_EMAIL`: 发件人邮箱
- `SENDER_PASSWORD`: 邮箱应用密码
- `RECEIVER_EMAIL`: 收件人邮箱
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥
- `DEEPSEEK_BASE_URL`: DeepSeek API 地址

## 运行

立即运行一次：
```bash
python main.py
```

定时运行（在 config.py 中设置 SCHEDULE_DAILY_TIME）：
```bash
python main.py
```

## 部署

本项目可以部署到 Render 等云平台，实现自动化运行。

## License

MIT
