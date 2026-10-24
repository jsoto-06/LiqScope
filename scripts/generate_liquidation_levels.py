"""Script de verificación y generación de niveles de liquidación modelados.

Calcula los niveles analíticos de liquidación para Long y Short utilizando:
- MMR supuesto por escalón (MMR < 1/L).
- Invariantes de precio: P_liq_long < P_mark < P_liq_short.
- Distribución de volumen por ponderación de apalancamiento y assumed_long_ratio = 0.50.
- Ejemplo de filtrado por rango [min_price, max_price] con coverage_pct exacto.
"""

from __future__ import annotations


def generate_liquidation_table(
    p_mark: float = 81498.90,
    oi_btc: float = 95448.751,
    assumed_long_ratio: float = 0.50,
    bin_size: float = 50.0,
    min_price: float = 79000.0,
    max_price: float = 83000.0,
) -> None:
    total_oi_usd = round(oi_btc * p_mark, 2)

    brackets: list[tuple[str, int, float, float]] = [
        ("5x", 5, 0.040, 0.15),
        ("10x", 10, 0.020, 0.25),
        ("25x", 25, 0.010, 0.30),
        ("50x", 50, 0.005, 0.20),
        ("100x", 100, 0.004, 0.10),
    ]

    print(f"P_mark: {p_mark:,.2f} USD")
    print(f"Open Interest: {oi_btc:,.3f} BTC -> Total OI USD: {total_oi_usd:,.2f} USD")
    print(f"Assumed Long Ratio: {assumed_long_ratio:.2f} | Bin Size: {bin_size:.1f} USD\n")

    print("=== NIVELES LONG (P_liq < P_mark) ===")
    long_levels = []
    for name, lev, mmr, w in brackets:
        delta = (1.0 / lev) - mmr
        p_liq = p_mark * (1.0 - delta)
        vol = round(total_oi_usd * assumed_long_ratio * w, 2)
        b_min = (p_liq // bin_size) * bin_size
        b_max = b_min + bin_size
        pct = w * assumed_long_ratio * 100
        check = "< P_mark OK" if p_liq < p_mark else ">= P_mark FAIL"
        long_levels.append((name, lev, mmr, delta, p_liq, vol, b_min, b_max, pct))
        print(
            f"{name:>4} | MMR={mmr:.3f} | delta={delta:.3f} ({delta * 100:4.1f}%) | "
            f"liq={p_liq:9.2f} USD ({check}) | vol={vol:16,.2f} USD ({pct:4.1f}% OI) | "
            f"bin=[{b_min:7.1f}, {b_max:7.1f})"
        )

    print("\n=== NIVELES SHORT (P_liq > P_mark) ===")
    short_levels = []
    for name, lev, mmr, w in reversed(brackets):
        delta = (1.0 / lev) - mmr
        p_liq = p_mark * (1.0 + delta)
        vol = round(total_oi_usd * (1.0 - assumed_long_ratio) * w, 2)
        b_min = (p_liq // bin_size) * bin_size
        b_max = b_min + bin_size
        pct = w * (1.0 - assumed_long_ratio) * 100
        check = "> P_mark OK" if p_liq > p_mark else "<= P_mark FAIL"
        short_levels.append((name, lev, mmr, delta, p_liq, vol, b_min, b_max, pct))
        print(
            f"{name:>4} | MMR={mmr:.3f} | delta={delta:.3f} ({delta * 100:4.1f}%) | "
            f"liq={p_liq:9.2f} USD ({check}) | vol={vol:16,.2f} USD ({pct:4.1f}% OI) | "
            f"bin=[{b_min:7.1f}, {b_max:7.1f})"
        )

    print(f"\n=== EJEMPLO FILTRADO [{min_price:.1f}, {max_price:.1f}] ===")
    all_bins = []
    for item in long_levels:
        all_bins.append(("LONG", item[0], item[4], item[5], item[6], item[7], item[8]))
    for item in short_levels:
        all_bins.append(("SHORT", item[0], item[4], item[5], item[6], item[7], item[8]))

    # Inclusión atómica por solapamiento: b_max > min_price y b_min < max_price
    visible_bins = [b for b in all_bins if b[5] > min_price and b[4] < max_price]
    visible_vol = sum(b[3] for b in visible_bins)
    coverage_pct = (visible_vol / total_oi_usd) * 100

    for side, name, _p_liq, vol, b_min, b_max, pct in visible_bins:
        print(
            f"  - Bin [{b_min:7.1f}, {b_max:7.1f}): {vol:16,.2f} USD ({pct:4.1f}% OI) -> {side} {name}"
        )

    print(f"\nVolumen visible: {visible_vol:,.2f} USD")
    print(
        f"Coverage: ({visible_vol:,.2f} / {total_oi_usd:,.2f}) * 100 = {coverage_pct:.6f}% = {coverage_pct:.2f}%"
    )


if __name__ == "__main__":
    generate_liquidation_table()
