# main.py
from monitor import ScreenShotMonitor


def main():
    # 配置区
    DEEPSEEK_API_KEY = ""  # 配置deepseek的api key
    QQ_EMAIL_AUTH_CODE = ""  # 配置QQ邮箱的授权码

    app = ScreenShotMonitor(
        ds_api_key=DEEPSEEK_API_KEY,
        email_auth_code=QQ_EMAIL_AUTH_CODE
    )

    try:
        app.start()
    except Exception as e:
        print(f"程序崩溃: {e}")


if __name__ == "__main__":
    main()
