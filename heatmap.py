import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path

# Paths
DATA_FILE = Path("panel_ENE_unificado (2).xlsx")
SHAPE_FILE = Path("regiones.shp")  # Provide a shapefile with Chilean regions

# Load dataset
panel = pd.read_excel(DATA_FILE)

# Filter for Ene-Mar 2025
subset = panel[(panel["Año"] == 2025) & (panel["Trimestre"] == "Ene - Mar")].copy()

# Determine which unemployment rate column to use
for col in ["T_TDO_indicadoresprincipales", "T_TDO_complementarios", "T_TDO"]:
    if col in subset.columns:
        tasa_col = col
        break
else:
    raise ValueError("No se encontró la columna de tasa de desocupación")

# Aggregate by region
region_rates = subset[["region_code", "region_name", tasa_col]].dropna()

# Load shapefile
mapa = gpd.read_file(SHAPE_FILE)

# Join data with geometry
mapa = mapa.merge(region_rates, left_on="region_code", right_on="region_code")

# Plot heatmap
ax = mapa.plot(column=tasa_col, cmap="OrRd", legend=True,
               linewidth=0.5, edgecolor="black")
ax.set_title(f"Tasa de desocupación ({tasa_col})\nEne-Mar 2025")
ax.axis("off")
plt.show()
