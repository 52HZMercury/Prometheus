import pyautogui
from pynput import keyboard
import datetime
import os
from analyzer import MultiModelAnalyzer
from sender import EmailSender
from config import ACTIVE_MODEL

class ScreenShotMonitor:
    def __init__(self, folder_name="screenshots"):
        self.folder_name = folder_name
        self.analyzer = MultiModelAnalyzer(provider=ACTIVE_MODEL)
        self.email_bot = EmailSender()
        self._ensure_dir()

    def _ensure_dir(self):
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

    def capture_analyze_and_send(self):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
        path = os.path.abspath(os.path.join(self.folder_name, f"shot_{now_str}.png"))

        pyautogui.screenshot().save(path)
        print(f"\n[*] 截图成功: {path}")

        answer = self.analyzer.analyze_image(path)
        print(f"\n🤖 {ACTIVE_MODEL.upper()} 建议：")
        print(answer)

        email_content = f"时间: {now_str}\n\nAI 分析建议如下:\n\n{answer}"
        self.email_bot.send_email(email_content)

    def _on_press(self, key):
        if key == keyboard.Key.delete:
            self.capture_analyze_and_send()
        if key == keyboard.Key.esc:
            return False

    def start(self):
        print(f"🚀 监控已启动 (当前模型: {ACTIVE_MODEL})")
        print("按下 [Delete]：截图 + AI分析 + 发送邮件")
        print("按下 [Esc]：退出程序")
        with keyboard.Listener(on_press=self._on_press) as listener:
            listener.join()