# Retail Synthetic Data Pipeline (2024–2025)


Pipeline de portafolio orientado a Data Engineering:

- Generación de dataset sintético retail con estacionalidad, canal online vs tienda, devoluciones.

- Carga a PostgreSQL en Docker (capa `raw`).

- Transformaciones SQL a `stg` (staging) y `mart` (modelo estrella).

- Checks de calidad.

## Como hacer correr todo en 1 solo paso:

- .\run_pipeline.ps1

## Requisitos

- Docker Desktop

- Python 3.10+

- Paquetes:

&nbsp; ```bash

&nbsp; pip install pandas numpy faker sqlalchemy pg8000



