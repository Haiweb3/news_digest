#!/bin/bash
# 运行脚本 - 用于 cron 或 launchd 定时任务

# 切换到工作目录
cd /Users/phn/news_digest || exit 1

# 检查 venv 是否可用（venv 移动后通常失效），如果不可用则重新创建
./venv/bin/python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Detected broken venv, reinstalling..." >> news_digest.log
    rm -rf venv
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

# 运行主程序
./venv/bin/python3 main.py >> news_digest.log 2>&1
