# analyzer.py
import requests
import easyocr


class DeepSeekAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        # 使用 DeepSeek 的标准文本模型
        self.api_url = "https://api.deepseek.com/chat/completions"
        # 初始化 OCR 阅读器（首次运行会下载模型文件，请耐心等待）
        self.reader = easyocr.Reader(['ch_sim', 'en'])

    def _extract_text(self, image_path):
        """提取图片中的文字"""
        print("[...] 正在识别图片文字...")
        results = self.reader.readtext(image_path, detail=0)
        return "\n".join(results)

    def analyze_image(self, image_path):
        """提取文字并发送给 DeepSeek"""
        # 1. 识字
        screen_text = self._extract_text(image_path)

        if not screen_text.strip():
            return "图片中没有检测到可识别的文字。"

        # 2. 组装请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        prompt = f"我的屏幕截图里有以下内容，请帮我分析并提供解决方案：\n\n{screen_text}"

        payload = {
            "model": "deepseek-chat",  # 使用通用的聊天模型
            # "model": "deepseek-reasoner",  # 思考模式的模型
            "messages": [
                {"role": "system", "content": "你是一个资深的电脑技术专家和编程助手。"},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        try:
            print("[...] 正在请求 DeepSeek 分析文字内容...")
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"DeepSeek 思考时出错了: {e}"