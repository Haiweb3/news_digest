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

## 部署到 Render（免费方案）

本项目已修改为 Web Service 形式，可以使用 Render 的免费计划部署。

### 步骤 1：部署到 Render

1. 访问 [Render Dashboard](https://dashboard.render.com/)
2. 点击 "New +" → "Blueprint"
3. 连接你的 GitHub 仓库
4. 选择 `news_digest` 仓库
5. Render 会自动检测 `render.yaml`
6. 配置环境变量：
   - `SMTP_SERVER`: smtp.gmail.com
   - `SMTP_PORT`: 465
   - `SENDER_EMAIL`: 你的发件邮箱
   - `SENDER_PASSWORD`: 你的邮箱应用密码
   - `RECEIVER_EMAIL`: 收件邮箱
   - `DEEPSEEK_API_KEY`: 你的 DeepSeek API 密钥
   - `DEEPSEEK_BASE_URL`: https://api.deepseek.com
   - `TRIGGER_SECRET_KEY`: 设置一个密钥（用于保护触发端点）
7. 点击 "Apply" 创建服务

### 步骤 2：设置定时触发

部署完成后，你会得到一个 URL，例如：`https://news-digest.onrender.com`

使用免费的定时服务来定时触发：

#### 方案 A：使用 cron-job.org（推荐）

1. 访问 https://cron-job.org/
2. 注册免费账号
3. 创建新的 Cron Job：
   - **Title**: News Digest Daily
   - **URL**: `https://your-app.onrender.com/trigger?key=你的TRIGGER_SECRET_KEY`
   - **Schedule**: 每天 08:00（或你想要的时间）
4. 保存并启用

#### 方案 B：使用 EasyCron

1. 访问 https://www.easycron.com/
2. 注册免费账号
3. 创建 Cron Job，URL 同上

#### 方案 C：使用 GitHub Actions

在你的仓库中添加 `.github/workflows/daily-news.yml`：

```yaml
name: Daily News Digest
on:
  schedule:
    - cron: '0 0 * * *'  # 每天 UTC 00:00
  workflow_dispatch:  # 允许手动触发

jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger News Digest
        run: |
          curl "https://your-app.onrender.com/trigger?key=${{ secrets.TRIGGER_SECRET_KEY }}"
```

### 测试部署

部署完成后，访问：
- `https://your-app.onrender.com/` - 查看服务状态
- `https://your-app.onrender.com/health` - 健康检查
- `https://your-app.onrender.com/trigger?key=你的密钥` - 手动触发新闻摘要

### 注意事项

- Render 免费计划的 Web Service 会在 15 分钟无活动后休眠
- 第一次请求可能需要等待服务唤醒（约 30-60 秒）
- 定时触发器会自动唤醒服务并执行任务

## 本地运行

立即运行一次：
```bash
python main.py
```

运行 Web 服务器：
```bash
python app.py
```

然后访问 `http://localhost:10000/trigger` 来触发任务。

## License

MIT
