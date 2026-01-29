# main.py
from monitor import ScreenShotMonitor


def main():
    # ⚠️ 配置区
    DEEPSEEK_API_KEY = "sk-efe4421346064e71a766d619352df752"
    QQ_EMAIL_AUTH_CODE = "lphtfzmzrjcmfbhe"

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
