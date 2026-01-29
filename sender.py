# email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.header import Header

class EmailSender:
    def __init__(self, auth_code):
        self.smtp_server = "smtp.qq.com"
        self.sender = "2108796780@qq.com"
        self.auth_code = auth_code  # 这里填刚才生成的授权码
        self.receiver = "chenning_william@163.com"

    def send_email(self, content, subject="DeepSeek AI 屏幕分析报告"):
        """发送邮件逻辑"""
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = self.sender
        message['To'] = self.receiver
        message['Subject'] = Header(subject, 'utf-8')

        try:
            # QQ邮箱必须使用 SSL 端口 465
            server = smtplib.SMTP_SSL(self.smtp_server, 465)
            server.login(self.sender, self.auth_code)
            server.sendmail(self.sender, [self.receiver], message.as_string())
            server.quit()
            print("[✓] 邮件已成功发送至 chenning_william@163.com")
        except Exception as e:
            print(f"[X] 邮件发送失败: {e}")