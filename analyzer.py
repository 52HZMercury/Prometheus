import requests
import easyocr
from google import genai
from config import DEEPSEEK_CONFIG, GEMINI_CONFIG


# --- 模型客户端基类 ---
class LLMClient:
    def ask(self, prompt, system_prompt):
        raise NotImplementedError


# --- DeepSeek 实现 ---
class DeepSeekClient(LLMClient):
    def __init__(self):
        self.conf = DEEPSEEK_CONFIG

    def ask(self, prompt, system_prompt):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.conf['api_key']}"
        }
        payload = {
            "model": self.conf['model'],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(self.conf['base_url'], headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']


# --- Gemini 实现 ---
class GeminiClient(LLMClient):
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_CONFIG['api_key'])

    def ask(self, prompt, system_prompt):
        # 整合系统提示词
        full_prompt = f"{system_prompt}\n\n用户请求：{prompt}"
        response = self.client.models.generate_content(model=GEMINI_CONFIG['model'], contents=full_prompt)
        return response.text


# --- 综合分析器 ---
class MultiModelAnalyzer:
    def __init__(self, provider="deepseek"):
        # 初始化 OCR
        self.reader = easyocr.Reader(['ch_sim', 'en'])

        # 动态选择客户端
        if provider == "deepseek":
            self.client = DeepSeekClient()
        elif provider == "gemini":
            self.client = GeminiClient()
        else:
            raise ValueError(f"不支持的模型厂商: {provider}")

    def _extract_text(self, image_path):
        print(f"[...] 正在识别图片文字 ({image_path})...")
        results = self.reader.readtext(image_path, detail=0)
        return "\n".join(results)

    def analyze_image(self, image_path):
        screen_text = self._extract_text(image_path)
        if not screen_text.strip():
            return "图片中没有检测到可识别的文字。"

        system_prompt = "你是一个资深的电脑技术专家和编程助手。"
        user_prompt = f"我的屏幕截图里有以下内容，请帮我分析并提供解决方案：\n\n{screen_text}"

        try:
            return self.client.ask(user_prompt, system_prompt)
        except Exception as e:
            return f"AI 思考时出错了: {e}"