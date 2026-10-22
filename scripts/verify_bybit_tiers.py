"""Script to fetch live Bybit risk-limit tiers and verify continuity across all tier boundaries."""

import json
import sys
import urllib.request
from pathlib import Path
from typing import Any


def fetch_tiers(symbol: str) -> list[dict[str, Any]]:
    url = f"https://api.bybit.com/v5/market/risk-limit?category=linear&symbol={symbol}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "LiqScope-Verification/1.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("retCode") != 0:
        raise RuntimeError(f"Error from Bybit API for {symbol}: {data.get('retMsg')}")
    tiers: list[dict[str, Any]] = data["result"]["list"]
    return tiers


def verify_symbol(symbol: str, out_lines: list[str]) -> bool:
    def log(msg: str = "") -> None:
        print(msg)
        out_lines.append(msg)

    log("=" * 80)
    log(f"FETCHING AND VERIFYING LIVE BYBIT RISK LIMIT TIERS: {symbol}")
    log("=" * 80)
    tiers = fetch_tiers(symbol)
    log(f"Total tiers fetched: {len(tiers)}")

    # Sort strictly by riskLimitValue
    tiers.sort(key=lambda t: float(t["riskLimitValue"]))

    total_boundaries = len(tiers) - 1
    log(f"Total boundaries to evaluate: {total_boundaries}")
    log("-" * 80)

    all_passed = True

    for i in range(total_boundaries):
        t_curr = tiers[i]
        t_next = tiers[i + 1]

        boundary = float(t_curr["riskLimitValue"])
        mmr_curr = float(t_curr["maintenanceMargin"])
        ded_curr = float(t_curr["mmDeduction"]) if t_curr.get("mmDeduction") else 0.0

        mmr_next = float(t_next["maintenanceMargin"])
        ded_next = float(t_next["mmDeduction"]) if t_next.get("mmDeduction") else 0.0

        margin_curr = boundary * mmr_curr - ded_curr
        margin_next = boundary * mmr_next - ded_next

        delta = abs(margin_curr - margin_next)
        is_continuous = delta < 1e-4

        if not is_continuous:
            all_passed = False
            status = "FAIL"
        else:
            status = "PASS"

        id_curr = t_curr["id"]
        id_next = t_next["id"]
        log(
            f"Boundary {i + 1:2d} | Tier {id_curr:2d} -> Tier {id_next:2d} at {boundary:14,.0f} USD:"
        )
        log(
            f"  Tier {id_curr:2d}: {boundary:14,.0f} * {mmr_curr:.4f} - {ded_curr:12,.0f} = {margin_curr:14,.2f} USD"
        )
        log(
            f"  Tier {id_next:2d}: {boundary:14,.0f} * {mmr_next:.4f} - {ded_next:12,.0f} = {margin_next:14,.2f} USD"
        )
        log(f"  Delta: {delta:.6f} USD -> CONTINUOUS: {status}")
        log("-" * 80)

    summary_str = f"SUMMARY FOR {symbol}: {'ALL CONTINUOUS (PASS)' if all_passed else 'DISCONTINUITY FOUND (FAIL)'}"
    log(summary_str)
    log("=" * 80 + "\n")
    return all_passed


def main() -> None:
    symbols = ["BTCUSDT", "ETHUSDT"]
    results = {}
    lines: list[str] = []
    for sym in symbols:
        results[sym] = verify_symbol(sym, lines)

    lines.append("FINAL SUMMARY:")
    print("FINAL SUMMARY:")
    for sym, res in results.items():
        msg = f"  {sym}: {'PASS' if res else 'FAIL'}"
        lines.append(msg)
        print(msg)

    out_file = Path("scripts/verify_bybit_tiers.log")
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[Saved log to {out_file}]")

    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
