# mercadolabroal

This repository contains utilities to clean, merge and visualize ENE Excel files.

- `cleaner.py` loads the raw workbooks and produces cleaned workbooks at
  `Datos_ENE_limpios` with standardized variable names.
- `unify_panel.py` merges all cleaned workbooks into a single panel. The
  resulting dataset is stored in `resultados/panel_ENE_unificado.xlsx`.
- `heatmap.py` reads the unified panel and plots a regional heat map of the
  unemployment rate for a selected period.

All scripts expect the directory structure used in the original notebooks and
will read/write files under `/content/drive/MyDrive/Data/Mercado_Laboral/Biobio`.
