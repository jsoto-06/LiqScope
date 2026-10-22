"""Script to calculate and verify Hyperliquid rate-limit weight budget."""

from pathlib import Path


def calculate_budget() -> None:
    lines: list[str] = []

    def log(msg: str = "") -> None:
        print(msg)
        lines.append(msg)

    log("=" * 80)
    log("HYPERLIQUID WEIGHT BUDGET VERIFICATION")
    log("=" * 80)
    log("Official Documentation Sources:")
    log(
        "  - Rate Limits: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits"
    )
    log("    Citation: 'REST requests share an aggregated weight limit of 1200 per minute.'")
    log("    Citation: 'The following info requests have weight 2: ... clearinghouseState ...'")
    log(
        "    Citation: 'All other documented info requests have weight 20.' (applies to metaAndAssetCtxs)"
    )
    log("-" * 80)

    rate_limit_per_min = 1200
    weight_clearinghouse = 2
    weight_meta_asset_ctxs = 20

    # Architecture configuration parameters
    max_tracked_addresses = 20
    meta_poll_interval_sec = 15.0
    wallet_poll_interval_sec = 10.0

    # Calls per minute
    meta_calls_per_min = 60.0 / meta_poll_interval_sec
    wallet_polls_per_min = 60.0 / wallet_poll_interval_sec

    # Weight per minute
    meta_weight_per_min = meta_calls_per_min * weight_meta_asset_ctxs
    wallet_weight_per_min = wallet_polls_per_min * max_tracked_addresses * weight_clearinghouse
    total_weight_per_min = meta_weight_per_min + wallet_weight_per_min

    consumption_pct = (total_weight_per_min / rate_limit_per_min) * 100.0
    safety_margin_pct = 100.0 - consumption_pct

    log("Budget Breakdown:")
    log(f"  Rate Limit per IP:            {rate_limit_per_min} weight / min")
    log(f"  Max Tracked Addresses:        {max_tracked_addresses} wallets")
    log(
        f"  Meta poll interval:           {meta_poll_interval_sec:.1f} s ({meta_calls_per_min:.1f} calls/min)"
    )
    log(f"  Meta weight consumption:      {meta_weight_per_min:.1f} weight / min")
    log(
        f"  Wallet poll interval:         {wallet_poll_interval_sec:.1f} s ({wallet_polls_per_min:.1f} calls/min per wallet)"
    )
    log(f"  Wallet weight consumption:    {wallet_weight_per_min:.1f} weight / min")
    log(f"  Total Weight Consumption:     {total_weight_per_min:.1f} weight / min")
    log(f"  Budget Utilization:           {consumption_pct:.2f}%")
    log(f"  Safety Margin:                {safety_margin_pct:.2f}%")
    log("-" * 80)

    is_safe = total_weight_per_min < rate_limit_per_min
    log(f"STATUS: {'PASS (SAFE MARGIN)' if is_safe else 'FAIL (OVER BUDGET)'}")
    log("=" * 80)

    out_file = Path("scripts/verify_hyperliquid_budget.log")
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[Saved log to {out_file}]")


if __name__ == "__main__":
    calculate_budget()
