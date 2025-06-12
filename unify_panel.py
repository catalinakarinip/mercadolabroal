"""Build unified ENE panel across cleaned bases"""

from pathlib import Path
import pandas as pd

ROOT = Path("/content/drive/MyDrive/Data/Mercado_Laboral/Biobio")
CLEAN_DIR = ROOT / "Datos_ENE_limpios"
PANEL_FILE = ROOT / "resultados" / "panel_ENE_unificado.xlsx"

TRIM_OK = {"Ene - Mar", "Abr - Jun", "Jul - Sep", "Oct - Dic"}
MAPA = {
    "AP": "Arica y Parinacota",
    "TA": "Tarapacá",
    "AN": "Antofagasta",
    "AT": "Atacama",
    "CO": "Coquimbo",
    "VA": "Valparaíso",
    "RM": "Región Metropolitana",
    "LI": "O’Higgins",
    "ML": "Maule",
    "NB": "Ñuble",
    "BI": "Biobío",
    "AR": "Araucanía",
    "LR": "Los Ríos",
    "LL": "Los Lagos",
    "AI": "Aysén",
    "MA": "Magallanes",
    "AS": "Nacional",
}
REGIONES = set(MAPA.keys())
ID_VARS = ["Año", "Trimestre", "region_code", "region_name"]
TRIM_MAP = {"Ene - Mar": 1, "Abr - Jun": 2, "Jul - Sep": 3, "Oct - Dic": 4}


def cargar_base(path: Path) -> pd.DataFrame:
    xls = pd.ExcelFile(path)
    registros = []
    for hoja in xls.sheet_names:
        if hoja not in REGIONES:
            continue
        df = pd.read_excel(xls, sheet_name=hoja)
        df = df[df["Trimestre"].isin(TRIM_OK)].copy()
        df["region_code"] = hoja
        df["region_name"] = MAPA[hoja]
        registros.append(df)
    if registros:
        return pd.concat(registros, ignore_index=True)
    return pd.DataFrame(columns=ID_VARS)


def construir_panel():
    panel = None
    for archivo in CLEAN_DIR.glob("*_limpia.xlsx"):
        df_base = cargar_base(archivo)
        if df_base.empty:
            continue
        if panel is None:
            panel = df_base
        else:
            panel = pd.merge(panel, df_base, on=ID_VARS, how="outer")
    if panel is None:
        print("No se encontraron archivos limpios")
        return
    panel["Trimestre_num"] = panel["Trimestre"].map(TRIM_MAP)
    panel = (
        panel.sort_values(
            ["Año", "Trimestre_num", "region_code", "region_name"]
        )
        .drop(columns="Trimestre_num")
        .reset_index(drop=True)
    )
    panel["Periodo"] = pd.PeriodIndex(
        year=panel["Año"],
        quarter=panel["Trimestre"].map(TRIM_MAP),
        freq="Q",
    )
    panel["Fecha"] = panel["Periodo"].dt.start_time
    PANEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    if PANEL_FILE.exists():
        print(f"↻  Reemplazando {PANEL_FILE.name}")
    panel.to_excel(PANEL_FILE, index=False)
    print("✅ Panel construido y guardado en:", PANEL_FILE)


if __name__ == "__main__":
    construir_panel()
