import requests
import easyocr
import logging
from google import genai
from config import DEEPSEEK_CONFIG, GEMINI_CONFIG, GLOBAL_TIMEOUT


# 配置日志：同时输出到文件，方便后台调试
logging.basicConfig(
    filename='prometheus.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

# --- 模型客户端基类 ---
class LLMClient:
    def ask(self, prompt, system_prompt):
        raise NotImplementedError


# --- DeepSeek 实现 ---
# analyzer.py (部分代码修改)

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
        response = requests.post(
            self.conf['base_url'],
            headers=headers,
            json=payload,
            timeout=GLOBAL_TIMEOUT
        )
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
        logging.info(f"[...] 正在识别图片文字 ({image_path})...")
        results = self.reader.readtext(image_path, detail=0)
        return "\n".join(results)

    def analyze_image(self, image_path):
        screen_text = self._extract_text(image_path)
        if not screen_text.strip():
            return "图片中没有检测到可识别的文字。"

        # system_prompt = "你是一个资深的电脑技术专家和编程助手。"
        # user_prompt = f"我的屏幕截图里有以下内容，请帮我分析并提供解决方案：\n\n{screen_text}"
        system_prompt = (
            "你是一名资深计算机面试教练与算法工程师，擅长处理编程面试中的算法题、"
            "计算机基础选择题、以及人才测评/性格测评题。"
            "你的目标是：先准确识别题目类型，再给出清晰、可执行、面试可直接复述的答案。"
            "回答要求："
            "1) 若是算法题：给出题意理解、解题思路、时间/空间复杂度、Java参考代码、常见追问。"
            "2) 若是选择题：逐项判断并解释为什么对/错，最后给出明确选项。"
            "3) 若是人才测评题：结合求职者目标岗位（默认软件开发）给出稳妥、真诚、职业化的作答建议，"
            "并说明这样回答的面试意图。"
            "4) OCR文本可能有错字或断句错误，请先做合理纠错再作答；不确定时明确说明假设。"
            "5) 输出简洁但完整，优先中文。"
        )
        user_prompt = (
            "以下是从截图OCR提取的面试题文本，请先识别题型（算法题/选择题/人才测评题/其他），"
            "再给出最优作答：\n\n"
            f"{screen_text}"
        )

        try:
            return self.client.ask(user_prompt, system_prompt)
        except Exception as e:
            return f"AI 思考时出错了: {e}"