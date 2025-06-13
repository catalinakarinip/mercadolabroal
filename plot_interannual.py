#!/usr/bin/env python3
"""Plot interannual variation of unemployment rate.

This script reads the unified ENE panel and generates a line plot of the
interannual variation (year-on-year percentage change) of the unemployment
rate for Nacional and Biob\xc3\xado. The resulting figure is saved as a PNG
file.
"""

from pathlib import Path
import argparse

import pandas as pd
import matplotlib.pyplot as plt

# Colour palette allowed for the project
PALETTE = [
    "#4c5256",
    "#2e3351",
    "#161233",
    "#3e3cca",
    "#c0c8eb",
    "#798dbf",
    "#ac78ff",
    "#48aee8",
]


def load_panel(path: Path) -> pd.DataFrame:
    """Read the Excel panel."""
    df = pd.read_excel(path)
    return df


def compute_interannual(series: pd.Series) -> pd.Series:
    """Return year-on-year percentage variation for a time series."""
    return series.pct_change(4) * 100


def main(panel_path: Path, out_file: Path) -> None:
    df = load_panel(panel_path)

    # Parse date to datetime and sort
    df["Fecha"] = pd.PeriodIndex(df["Fecha"], freq="Q").to_timestamp("Q")
    df.sort_values("Fecha", inplace=True)

    nacional = df[df["region_name"] == "Nacional"].copy()
    biobio = df[df["region_name"] == "Biob\xc3\xado"].copy()

    nacional["variacion"] = compute_interannual(
        nacional["T_TDO_indicadoresprincipales"]
    )
    biobio["variacion"] = compute_interannual(
        biobio["T_TDO_indicadoresprincipales"]
    )

    plt.figure(figsize=(8, 4))
    plt.plot(
        nacional["Fecha"],
        nacional["variacion"],
        label="Nacional",
        color=PALETTE[3],
    )
    plt.plot(
        biobio["Fecha"],
        biobio["variacion"],
        label="Biob\xc3\xado",
        color=PALETTE[6],
    )
    plt.axhline(0, color=PALETTE[0], linewidth=1)
    plt.title(
        "Variaci\xc3\xb3n interanual tasa de desocupaci\xc3\xb3n\nTrimestres m\xc3\xb3viles",
        fontname="DM Sans",
        fontsize=14,
    )
    plt.ylabel("%", fontname="DM Sans")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot interannual variation of the unemployment rate",
    )
    parser.add_argument(
        "panel",
        nargs="?",
        default="panel_ENE_unificado (5).xlsx",
        help="Excel panel to read",
    )
    parser.add_argument(
        "--out",
        default="variacion_tdo.png",
        help="Path of the output PNG",
    )
    args = parser.parse_args()
    main(Path(args.panel), Path(args.out))
