# mercadolabroal

This repository contains utilities to clean, merge and visualize ENE Excel files.

- `cleaner.py` loads the raw workbooks and produces cleaned workbooks at
  `Datos_ENE_limpios` with standardized variable names. During this step the
  quarter column is normalised so later scripts can recognise temporal
  information.
- `unify_panel.py` merges all cleaned workbooks into a single panel. The
  resulting dataset is stored in `resultados/panel_ENE_unificado.xlsx`. It also
  creates `Periodo` and `Fecha` columns for time series analysis.
- `heatmap.py` reads the unified panel and plots a regional heat map of the
  unemployment rate for a selected period.
- `interannual.py` computes quarterly and year-on-year percentage changes for
  selected indicators and saves the result alongside the panel.
- `plot_interannual.py` plots the year-on-year variation of the unemployment
  rate for Nacional and Biobío using the unified panel.

All scripts expect the directory structure used in the original notebooks and
will read/write files under `/content/drive/MyDrive/Data/Mercado_Laboral/Biobio`.
