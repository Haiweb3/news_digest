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

## 部署到 Render

### 方法一：使用 render.yaml（推荐）

1. Fork 或推送代码到 GitHub
2. 登录 [Render Dashboard](https://dashboard.render.com/)
3. 点击 "New +" → "Blueprint"
4. 连接你的 GitHub 仓库
5. Render 会自动检测 `render.yaml` 并创建服务
6. 在 Environment 中配置以下环境变量：
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `RECEIVER_EMAIL`
   - `DEEPSEEK_API_KEY`
   - `SCHEDULE_DAILY_TIME`（可选，格式：HH:MM）

### 方法二：手动创建

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 点击 "New +" → "Background Worker"
3. 连接你的 GitHub 仓库
4. 配置：
   - **Name**: news-digest
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
5. 添加环境变量（同上）
6. 点击 "Create Background Worker"

### 注意事项

- Render 免费套餐的 Background Worker 会在 15 分钟无活动后休眠
- 如果需要持续运行，建议使用付费套餐
- 定时任务时间在环境变量 `SCHEDULE_DAILY_TIME` 中设置

## License

MIT
