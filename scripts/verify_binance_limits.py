"""Script to query live Binance Futures exchangeInfo and verify rateLimits."""

import json
import urllib.request
from pathlib import Path
from typing import Any


def verify_binance_rate_limits() -> None:
    lines: list[str] = []

    def log(msg: str = "") -> None:
        print(msg)
        lines.append(msg)

    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "LiqScope-Verification/1.0"},
    )

    log("=" * 80)
    log("BINANCE FUTURES RATE LIMIT VERIFICATION")
    log("=" * 80)
    log(f"Requesting: {url}")

    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8")
        data: dict[str, Any] = json.loads(body)

    rate_limits: list[dict[str, Any]] = data.get("rateLimits", [])
    log(f"Found {len(rate_limits)} rate limit specifications:")
    for rl in rate_limits:
        log(f"  - {rl}")

    weight_limit = next(
        (rl for rl in rate_limits if rl.get("rateLimitType") == "REQUEST_WEIGHT" and rl.get("interval") == "MINUTE"),
        None,
    )

    log("-" * 80)
    if weight_limit:
        limit_val = weight_limit.get("limit")
        log(f"Verified REQUEST_WEIGHT per MINUTE limit: {limit_val}")
        log(f"STATUS: {'PASS' if limit_val == 2400 else 'UNEXPECTED VALUE'}")
    else:
        log("STATUS: FAIL (REQUEST_WEIGHT limit not found)")
    log("=" * 80)

    out_file = Path("scripts/verify_binance_limits.log")
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[Saved log to {out_file}]")


if __name__ == "__main__":
    verify_binance_rate_limits()
