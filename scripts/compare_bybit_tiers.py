"""Script to compare saved Bybit tier fixtures against live API responses."""

import json
import urllib.request
from pathlib import Path
from typing import Any


def compare_symbol(symbol: str) -> tuple[bool, int]:
    url = f"https://api.bybit.com/v5/market/risk-limit?category=linear&symbol={symbol}"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.4.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        live_data: dict[str, Any] = json.loads(resp.read().decode("utf-8"))

    live_tiers = live_data["result"]["list"]

    fixture_path = Path(f"fixtures/bybit_risk_limits_{symbol.lower()}.json")
    saved_data = json.loads(fixture_path.read_text(encoding="utf-8"))
    saved_tiers = saved_data["result"]["list"]

    is_identical = live_tiers == saved_tiers
    count = len(live_tiers)
    return is_identical, count


def main() -> None:
    lines: list[str] = []

    def log(msg: str = "") -> None:
        print(msg)
        lines.append(msg)

    log("=" * 80)
    log("BYBIT RISK LIMIT TIERS COMPARISON (SAVED FIXTURE VS LIVE API)")
    log("=" * 80)

    symbols = ["BTCUSDT", "ETHUSDT"]
    all_ok = True

    for sym in symbols:
        identical, count = compare_symbol(sym)
        log(f"{sym}: {identical} {count}")
        if not (identical and count == 35):
            all_ok = False

    log("-" * 80)
    log(f"FINAL STATUS: {'PASS' if all_ok else 'FAIL'}")
    log("=" * 80)

    out_file = Path("scripts/compare_bybit_tiers.log")
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[Saved log to {out_file}]")


if __name__ == "__main__":
    main()
