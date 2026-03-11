import smtplib
from email.mime.text import MIMEText
from email.header import Header
from config import EMAIL_CONFIG

class EmailSender:
    def __init__(self):
        self.conf = EMAIL_CONFIG

    def send_email(self, content, subject="AI 屏幕分析报告"):
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = self.conf['sender']
        message['To'] = self.conf['receiver']
        message['Subject'] = Header(subject, 'utf-8')

        try:
            server = smtplib.SMTP_SSL(self.conf['smtp_server'], 465)
            server.login(self.conf['sender'], self.conf['auth_code'])
            server.sendmail(self.conf['sender'], [self.conf['receiver']], message.as_string())
            server.quit()
            print(f"[✓] 邮件已成功发送至 {self.conf['receiver']}")
        except Exception as e:
            print(f"[X] 邮件发送失败: {e}")