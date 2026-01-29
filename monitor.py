# monitor.py
import pyautogui
from pynput import keyboard
import datetime
import os
from analyzer import DeepSeekAnalyzer
from sender import EmailSender  # 导入新模块


class ScreenShotMonitor:
    def __init__(self, ds_api_key, email_auth_code, folder_name="screenshots"):
        self.folder_name = folder_name
        self.analyzer = DeepSeekAnalyzer(ds_api_key)
        self.email_bot = EmailSender(email_auth_code)  # 初始化邮件机器人
        self._ensure_dir()

    def _ensure_dir(self):
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

    def capture_analyze_and_send(self):
        """核心流程：截图 -> AI分析 -> 发送邮件"""
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        path = os.path.abspath(os.path.join(self.folder_name, f"shot_{now_str.replace(':', '-')}.png"))

        # 1. 截图
        pyautogui.screenshot().save(path)
        print(f"\n[*] 截图成功: {path}")

        # 2. 调用 AI 分析文字
        answer = self.analyzer.analyze_image(path)
        print("\n🤖 DeepSeek 建议：")
        print(answer)

        # 3. 发送邮件
        email_content = f"时间: {now_str}\n\nAI 分析建议如下:\n\n{answer}"
        self.email_bot.send_email(email_content)

    def _on_press(self, key):
        if key == keyboard.Key.delete:
            self.capture_analyze_and_send()
        if key == keyboard.Key.esc:
            return False

    def start(self):
        print("🚀 监控已启动。")
        print("按下 [Delete]：截图 + AI分析 + 发送邮件")
        print("按下 [Esc]：退出程序")
        with keyboard.Listener(on_press=self._on_press) as listener:
            listener.join()