#!/bin/bash
# VPS 部署脚本

echo "=== 全球新闻日报 VPS 部署脚本 ==="

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python3"
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"

# 创建虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境并安装依赖
echo "📦 安装依赖..."
source venv/bin/activate
pip install -r requirements.txt

# 创建 .env 文件（如果不存在）
if [ ! -f .env ]; then
    echo "📝 创建 .env 配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，填入你的配置信息"
    echo "   vim .env"
fi

# 测试运行
echo ""
echo "🧪 测试运行..."
python3 main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 测试成功！"
    echo ""
    echo "=== 下一步 ==="
    echo "1. 编辑 .env 文件（如果还没配置）: vim .env"
    echo "2. 设置定时任务: crontab -e"
    echo "   添加以下行（每天早上 8:00 运行）："
    echo "   0 8 * * * cd $(pwd) && ./venv/bin/python3 main.py >> news_digest.log 2>&1"
    echo ""
    echo "3. 查看日志: tail -f news_digest.log"
else
    echo ""
    echo "❌ 测试失败，请检查配置"
fi
