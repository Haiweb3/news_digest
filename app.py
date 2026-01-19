#!/usr/bin/env python3
"""
Flask Web Server - 用于通过 HTTP 触发新闻摘要任务
"""

from flask import Flask, jsonify, request
import os
from main import run_once

app = Flask(__name__)

# 从环境变量获取密钥，用于验证请求
SECRET_KEY = os.getenv("TRIGGER_SECRET_KEY", "your-secret-key-here")


@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "Global News Digest",
        "message": "Service is running. Use /trigger endpoint to run the news digest."
    })


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/trigger')
def trigger():
    """触发新闻摘要任务"""
    # 可选：验证请求密钥
    request_key = request.args.get('key', '')
    if SECRET_KEY and request_key != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        success = run_once()
        if success:
            return jsonify({
                "status": "success",
                "message": "News digest sent successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to send news digest"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
