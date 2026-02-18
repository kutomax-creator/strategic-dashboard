"""
Strategic Dashboard - Desktop Launcher
pywebview でネイティブウィンドウ内に Streamlit を表示する。
ブラウザを経由しないため、localhost ブロック環境でも動作する。
"""
import subprocess
import sys
import os
import threading
import time
import urllib.request
import webview

PORT = 8502
URL = f"http://127.0.0.1:{PORT}"
APP_DIR = os.path.dirname(os.path.abspath(__file__))


def start_streamlit():
    """Streamlit サーバーをバックグラウンドで起動"""
    subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run",
            os.path.join(APP_DIR, "app_new.py"),
            "--server.port", str(PORT),
            "--server.headless", "true",
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats", "false",
            "--global.developmentMode", "false",
        ],
        cwd=APP_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_server(timeout=30):
    """サーバーが応答するまで待機"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(URL, timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def on_closed():
    """ウィンドウを閉じたら Streamlit も停止"""
    import signal
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    # Streamlit をバックグラウンドスレッドで起動
    threading.Thread(target=start_streamlit, daemon=True).start()

    # サーバー起動を待機
    if not wait_for_server():
        print("ERROR: Streamlit server failed to start")
        sys.exit(1)

    # ネイティブウィンドウで表示
    window = webview.create_window(
        "Strategic Dashboard",
        URL,
        width=1440,
        height=900,
        min_size=(1024, 700),
    )
    webview.start()
