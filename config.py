# config.py

# 核心设置：选择当前使用的 AI 厂商 ("deepseek" 或 "gemini")
ACTIVE_MODEL = "deepseek"
# ACTIVE_MODEL = "gemini"

# 全局超时设置
GLOBAL_TIMEOUT = 150

# DeepSeek 配置
DEEPSEEK_CONFIG = {
    "api_key": "Your-Key",
    "base_url": "https://api.deepseek.com/chat/completions",
    "model": "deepseek-chat"
    # "model": "deepseek-reasoner" # 思考模式
}

# Gemini 配置
GEMINI_CONFIG = {
    "api_key": "Your-Key",
    "model": "gemini-3.1-pro-preview"
    # "model": "gemini-3-flash-preview"
}

# 邮箱配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "sender": "2108796780@qq.com",
    "auth_code": "lphtfzmzrjcmfbhe",
    "receiver": [
        "chenning_william@163.com",
        # "1438615474@qq.com",
        # "2567159157@qq.com",
        # "321907434@qq.com"
    ]
}