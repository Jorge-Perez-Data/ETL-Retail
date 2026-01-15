from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5433"))
PG_DB = os.getenv("PG_DB", "retail")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")


TABLES = {
    "customers": "customers.csv",
    "stores": "stores.csv",
    "products": "products.csv",
    "sales": "sales.csv",
}

def main() -> None:
    print("PROJECT_ROOT:", PROJECT_ROOT)
    print("DATA_DIR:", DATA_DIR)

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"No existe {DATA_DIR}. Genera primero los CSV en data/raw/")

    # ✅ Usa pg8000 (evita el problema UnicodeDecodeError de psycopg2 en Windows)
    url = URL.create(
        drivername="postgresql+pg8000",
        username=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DB,
    )
    engine = create_engine(url)

    # Test conexión
    with engine.connect() as conn:
        conn.execute(text("SELECT 1;"))
    print("✅ Conexión a Postgres OK")

    # Crear schema raw
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))

    # Cargar CSV a raw.<tabla>
    for table, filename in TABLES.items():
        path = DATA_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Falta el archivo: {path}")

        df = pd.read_csv(path)

# Para tablas pequeñas, "multi" va bien.
# Para sales (grande), evitamos multi porque pg8000 tiene límite de parámetros.
        if table == "sales":
            df.to_sql(
                name=table,
                con=engine,
                schema="raw",
                if_exists="replace",
                index=False,
                chunksize=1000,
                method=None,
            )
        else:
            df.to_sql(
                name=table,
                con=engine,
                schema="raw",
                if_exists="replace",
                index=False,
                chunksize=5000,
                method="multi",
            )

        print(f"Loaded raw.{table}: {len(df):,} rows")

    print("Done. Tables loaded into schema raw.")

if __name__ == "__main__":
    main()
