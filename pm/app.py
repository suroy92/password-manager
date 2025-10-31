"""
pywebview bootstrap
"""
import threading, socket, time, os
import webview
import uvicorn

def _free_port() -> int:
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def _run_api(port: int):
    uvicorn.run("pm.api.main:app", host="127.0.0.1", port=port, log_level="info", factory=True)

def main():
    port = int(os.environ.get("PM_UI_PORT", _free_port()))
    t = threading.Thread(target=_run_api, args=(port,), daemon=True)
    t.start()
    time.sleep(0.4)
    webview.create_window("Password Manager", url=f"http://127.0.0.1:{port}/")
    webview.start()

if __name__ == "__main__":
    main()
