# main.py
from monitor import ScreenShotMonitor

def main():
    app = ScreenShotMonitor()
    try:
        app.start()
    except Exception as e:
        print(f"程序崩溃: {e}")

if __name__ == "__main__":
    main()