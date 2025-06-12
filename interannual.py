"""Compute quarterly and interannual variations for ENE indicators.

This script reads the unified panel created by ``unify_panel.py`` and adds
quarter-on-quarter (``_dq``) and year-on-year (``_da``) percentage change
columns for the selected variables. Results are written to a new Excel file
in the same directory as the input dataset.

Example::

    python interannual.py panel_ENE_unificado.xlsx \
        --columns T_TDO_indicadoresprincipales PDO_TOT_indicadoresprincipales

"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

TRIM_MAP = {
    "Ene - Mar": 1,
    "Abr - Jun": 2,
    "Jul - Sep": 3,
    "Oct - Dic": 4,
}


def load_panel(path: Path, sheet: str) -> pd.DataFrame:
    """Load the panel and ensure a ``Periodo`` column exists."""
    df = pd.read_excel(path, sheet_name=sheet)
    if "Periodo" not in df.columns:
        df["Trimestre_num"] = df["Trimestre"].map(TRIM_MAP)
        df["Periodo"] = pd.PeriodIndex(
            year=df["Año"],
            quarter=df["Trimestre_num"],
            freq="Q",
        )
    return df


def add_variations(df: pd.DataFrame, variables: list[str]) -> pd.DataFrame:
    """Add quarterly and interannual variations for ``variables``."""
    df = df.sort_values(["region_name", "Periodo"]).copy()
    for var in variables:
        df[f"{var}_dq"] = df.groupby("region_name")[var].pct_change() * 100
        df[f"{var}_da"] = df.groupby("region_name")[var].pct_change(4) * 100
    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add quarterly and interannual variation columns to the panel",
    )
    parser.add_argument("panel", help="Path to the unified Excel panel")
    parser.add_argument(
        "--sheet", default="panel_data", help="Name of the sheet to read"
    )
    parser.add_argument(
        "--out",
        help="Output Excel file; defaults to <panel>_variaciones.xlsx",
    )
    parser.add_argument(
        "--columns",
        nargs="*",
        help="Variables for which to compute variations. "
        "Defaults to all numeric columns.",
    )

    args = parser.parse_args()
    panel_path = Path(args.panel)
    out_file = (
        Path(args.out)
        if args.out
        else panel_path.with_name(f"{panel_path.stem}_variaciones{panel_path.suffix}")
    )

    df = load_panel(panel_path, args.sheet)

    vars_list = args.columns
    if not vars_list:
        vars_list = (
            df.select_dtypes("number")
            .columns.difference(["Año", "Trimestre_num"])
            .tolist()
        )

    df = add_variations(df, vars_list)
    df.to_excel(out_file, index=False)
    print(f"Variations saved to {out_file}")


if __name__ == "__main__":
    main()
