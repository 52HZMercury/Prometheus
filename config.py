# config.py

import os


# AI 提供商："deepseek" 或 "kimi"
AI_PROVIDER = "deepseek"

# OCR 开关：False 时直接把截图发送给多模态模型；True 时先在本地提取文字
OCR_ENABLED = False

# 图片输入模式："base64"、"files_api" 或 "auto"
# auto 会对不超过 32 MiB 的图片使用 Base64，更大的图片使用 Files API
IMAGE_INPUT_MODE = "auto"

# Files API 上传文件的有效期：3 小时
FILE_EXPIRES_AFTER_SECONDS = 10800

# 全局超时设置
GLOBAL_TIMEOUT = 150

# DeepSeek 配置
DEEPSEEK_CONFIG = {
    "api_key": "$api_key$",
    "chat_url": "https://api.deepseek.com/chat/completions",
    "files_url": "https://api.deepseek.com/files",
    "model": "deepseek-v4-flash-vision-exp",
}

# Kimi 配置
# 推荐通过环境变量 MOONSHOT_API_KEY 提供密钥，也可以直接替换占位符
KIMI_CONFIG = {
    "api_key": "$api_key$",
    "chat_url": "https://api.moonshot.cn/v1/chat/completions",
    "files_url": "https://api.moonshot.cn/v1/files",
    "model": "kimi-k2.6",
}

# 邮箱配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "sender": "2108796780@qq.com",
    "auth_code": "lphtfzmzrjcmfbhe",
    "receiver": [
        # "321907434@qq.com"
        "chenning_william@163.com"
        # "1438615474@qq.com",
        # "2567159157@qq.com", #豪
        # "jingying.zhao110@outlook.com",
        # "2197359276@qq.com" #王梦华
    ],
}
