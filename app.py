"""D7 验收服务：传感数据处理 API（标准库 HTTP，零第三方依赖）"""
import json
import logging
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np

from fast_avg import moving_average_fast

logger = logging.getLogger(__name__)
DATA_FILE = Path(__file__).parent / "sensor_data.csv"
PORT = 8000


def load_observed() -> np.ndarray:
    """读取 sensor_data.csv 的 observed 列（跳过表头）"""
    arr = np.genfromtxt(DATA_FILE, delimiter=",", skip_header=1)
    return arr[:, 1]


def compute_summary() -> dict:
    """核心：卷积滑动平均 + 计时，返回 JSON 摘要"""
    observed = load_observed()
    t0 = time.perf_counter()
    sma5 = moving_average_fast(observed, 5)
    elapsed = time.perf_counter() - t0
    logger.info("smooth 计算 %d 点，耗时 %.5fs", len(observed), elapsed)
    return {
        "points": int(len(observed)),
        "sma5_points": int(len(sma5)),
        "last_sma5": round(float(sma5[-1]), 4),
        "compute_seconds": round(elapsed, 5),
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            payload = {"status": "ok", "service": "sensor-api",
                       "time": time.strftime("%F %T")}
            self._reply(200, payload)
        elif self.path == "/smooth":
            self._reply(200, compute_summary())
        else:
            self._reply(404, {"error": "not found", "path": self.path})

    def _reply(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        logger.info("%s %s", self.address_string(), fmt % args)


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    logger.info("服务已启动: http://0.0.0.0:%d  (/health | /smooth)", PORT)
    server.serve_forever()


if __name__ == "__main__":
    main()
EOF
