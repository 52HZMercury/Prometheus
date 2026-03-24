import pyautogui
from pynput import keyboard
import datetime
import os
import logging
from analyzer import MultiModelAnalyzer
from sender import EmailSender
from config import ACTIVE_MODEL

# 配置日志：同时输出到文件，方便后台调试
logging.basicConfig(
    filename='prometheus.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

class ScreenShotMonitor:
    def __init__(self, folder_name="screenshots"):
        self.folder_name = folder_name
        self.analyzer = MultiModelAnalyzer(provider=ACTIVE_MODEL)
        self.email_bot = EmailSender()
        self._ensure_dir()
        logging.info(f"Prometheus 实例已初始化，当前模型: {ACTIVE_MODEL}")

    def _ensure_dir(self):
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

    def capture_analyze_and_send(self):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
        path = os.path.abspath(os.path.join(self.folder_name, f"shot_{now_str}.png"))

        try:
            # 截图
            pyautogui.screenshot().save(path)
            logging.info(f"截图成功保存至: {path}")

            # AI 分析
            answer = self.analyzer.analyze_image(path)
            logging.info(f"AI 分析完成，使用的供应商: {ACTIVE_MODEL}")

            # 发送邮件
            email_content = f"时间: {now_str}\n\nAI 分析建议如下:\n\n{answer}"
            self.email_bot.send_email(email_content, image_path=path)
            logging.info("分析报告已成功推送到邮件。")

        except Exception as e:
            logging.error(f"处理流程中出现异常: {str(e)}", exc_info=True)

    def _on_press(self, key):
        """
        监听回调，必须包裹在 try 块中，否则任何错误都会导致监听线程终止。
        """
        try:
            if key == keyboard.Key.delete:
                logging.info("检测到 [Delete] 按键，开始执行任务...")
                self.capture_analyze_and_send()
            if key == keyboard.Key.esc:
                logging.info("检测到 [Esc] 按键，程序准备退出。")
                return False
        except Exception as e:
            logging.error(f"按键处理异常: {e}")

    def start(self):
        logging.info("🚀 监控服务已启动")
        print("Prometheus 已在后台运行，请查看 prometheus.log 获取详细状态。")
        with keyboard.Listener(on_press=self._on_press) as listener:
            listener.join()