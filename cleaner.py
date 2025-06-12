"""Clean ENE Excel files with optimized routines."""

from pathlib import Path
import pandas as pd
import re

ROOT = Path("/content/drive/MyDrive/Data/Mercado_Laboral/Biobio")
ORIG_DIR = ROOT / "Datos_ENE_originales"
CLEAN_DIR = ROOT / "Datos_ENE_limpios"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

MAP_FILE = ROOT / "resultados/variables_por_base.xlsx"
MAP_SHEET = 0


def load_abbreviations() -> dict:
    df_map = (
        pd.read_excel(MAP_FILE, sheet_name=MAP_SHEET, usecols="A:C")
        .rename(columns=str.lower)
        .dropna()
    )
    df_map["base"] = (
        df_map["base"].str.strip().str.replace(".xlsx", "", regex=False).str.lower()
    )
    df_map["var_original"] = df_map["var_original"].str.strip()
    df_map["abreviatura"] = df_map["abreviatura"].str.strip()
    return {(r.base, r.var_original): r.abreviatura for r in df_map.itertuples()}


ID_VARS = ["Año", "Trimestre"]
HOJAS_OBJETIVO = {
    "AS",
    "AP",
    "TA",
    "AN",
    "AT",
    "CO",
    "VA",
    "RM",
    "LI",
    "ML",
    "NB",
    "BI",
    "AR",
    "LR",
    "LL",
    "AI",
    "MA",
}


LATIN_NUMBER_RE = re.compile(r"^\d{1,3}(\.\d{3})*(,\d+)?$")


def texto_a_numero(valor: str):
    if pd.isna(valor):
        return None
    texto = str(valor)
    if LATIN_NUMBER_RE.match(texto):
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


def limpiar_hoja(df: pd.DataFrame, base_alias: str, abbr: dict) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip()
    columnas_a_borrar = []
    renombres = {}
    columnas = list(df.columns)

    for i, col in enumerate(columnas):
        if col in ID_VARS or "Unnamed" not in col:
            continue
        anterior = columnas[i - 1].strip() if i > 0 else ""
        if anterior in ID_VARS or not anterior:
            columnas_a_borrar.append(col)
            continue
        alias = abbr.get((base_alias, anterior))
        if alias:
            renombres[col] = f"{alias}_{base_alias}"
        else:
            columnas_a_borrar.append(col)

    df = df.drop(columns=columnas_a_borrar, errors="ignore").rename(columns=renombres)
    df = df[df[ID_VARS[0]].notna() | df[ID_VARS[1]].notna()].reset_index(drop=True)

    # Normalize quarter names so they match TRIM_OK in unify_panel.py
    quarter_map = {
        "1": "Ene - Mar",
        "2": "Abr - Jun",
        "3": "Jul - Sep",
        "4": "Oct - Dic",
        "ene-mar": "Ene - Mar",
        "abr-jun": "Abr - Jun",
        "jul-sep": "Jul - Sep",
        "oct-dic": "Oct - Dic",
        "ene - mar": "Ene - Mar",
        "abr - jun": "Abr - Jun",
        "jul - sep": "Jul - Sep",
        "oct - dic": "Oct - Dic",
    }
    df["Trimestre"] = (
        df["Trimestre"].astype(str).str.strip().str.lower().replace(quarter_map)
    )
    df["Año"] = pd.to_numeric(df["Año"], errors="coerce")

    for col in renombres.values():
        df[col] = df[col].apply(texto_a_numero)

    return df[[*ID_VARS, *renombres.values()]]


def procesar_archivos():
    abbr = load_abbreviations()
    for src in ORIG_DIR.glob("*.xlsx"):
        base_alias = src.stem.split("_")[0].lower()
        dest = CLEAN_DIR / f"{base_alias}_limpia.xlsx"
        if dest.exists():
            print(f"↻  Reemplazando {dest.name}")
        else:
            print(f"→ Procesando {src.name} (base={base_alias})")
        xls = pd.ExcelFile(src)
        with pd.ExcelWriter(dest, engine="openpyxl") as xlw:
            hojas_guardadas = 0
            for hoja in xls.sheet_names:
                if hoja not in HOJAS_OBJETIVO:
                    continue
                try:
                    raw = xls.parse(hoja, header=5, dtype=str)
                    limpio = limpiar_hoja(raw, base_alias, abbr)
                    if not limpio.empty:
                        limpio.to_excel(xlw, sheet_name=hoja, index=False)
                        hojas_guardadas += 1
                except Exception as e:
                    print(f"⚠️ Error en hoja '{hoja}': {e}")
            if hojas_guardadas == 0:
                print(f"⚠️ Ninguna hoja válida guardada en {src.name}")
    print("\n✅ Limpieza completada. Archivos en:", CLEAN_DIR)


if __name__ == "__main__":
    procesar_archivos()
