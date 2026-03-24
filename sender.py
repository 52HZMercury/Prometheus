import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header
from config import EMAIL_CONFIG

# 配置日志：同时输出到文件，方便后台调试
logging.basicConfig(
    filename='prometheus.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

class EmailSender:
    def __init__(self):
        self.conf = EMAIL_CONFIG

    def send_email(self, content, image_path=None, subject="来自Prometheus的报告"):
        receivers = self.conf['receiver']

        # 确保 receivers 是列表格式，兼容单人或多人
        if isinstance(receivers, str):
            receivers = [receivers]

        message = MIMEMultipart()
        message['From'] = self.conf['sender']
        # 邮件头中的 To 需要是逗号分隔的字符串
        message['To'] = ", ".join(receivers)
        message['Subject'] = Header(subject, 'utf-8')

        message.attach(MIMEText(content, 'plain', 'utf-8'))

        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as f:
                    img_attachment = MIMEImage(f.read())
                    filename = os.path.basename(image_path)
                    img_attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                    message.attach(img_attachment)
            except Exception as e:
                logging.info(f"[!] 读取图片附件失败: {e}")

        try:
            server = smtplib.SMTP_SSL(self.conf['smtp_server'], 465)
            server.login(self.conf['sender'], self.conf['auth_code'])
            # 这里传入 receivers 列表，SMTP 会循环发送给每一个人
            server.sendmail(self.conf['sender'], receivers, message.as_string())
            server.quit()
            logging.info(f"[✓] 邮件已成功发送至: {', '.join(receivers)}")
        except Exception as e:
            logging.info(f"[X] 邮件发送失败: {e}")