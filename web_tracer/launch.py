"""launch.py — start the Web Application Tracer service and open the dashboard (T09)."""
from __future__ import annotations

import threading
import time
import webbrowser

import uvicorn

from engine import config


def main() -> None:
    url = f"http://{config.SERVICE_HOST}:{config.SERVICE_PORT}"

    def _open_browser() -> None:
        time.sleep(1.5)
        try:
            webbrowser.open(f"{url}/")
        except Exception:
            pass  # headless environments have no browser; the URL is still printed.

    threading.Thread(target=_open_browser, daemon=True).start()
    print(f"{config.PROJECT_NAME} {config.PROJECT_VERSION} -> {url}/  (docs: {url}/docs)")
    uvicorn.run("backend.web_server:app", host=config.SERVICE_HOST, port=config.SERVICE_PORT, reload=False)


if __name__ == "__main__":
    main()
