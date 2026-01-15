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

def make_engine():
    url = URL.create(
        drivername="postgresql+pg8000",
        username=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DB,
    )
    # pool_pre_ping ayuda si la conexión se cae
    return create_engine(url, pool_pre_ping=True)

def load_small_table(engine, table: str, path: Path) -> None:
    df = pd.read_csv(path)
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

def load_sales_streaming(engine, table: str, path: Path) -> None:
    # Cargamos en streaming para no matar memoria ni reventar parámetros
    chunk_rows = 2000  # si falla, baja a 1000 o 500
    total = 0

    # 1) Reemplazamos tabla con el primer chunk (if_exists=replace)
    # 2) Luego append para los demás chunks
    first = True

    for chunk in pd.read_csv(path, chunksize=chunk_rows):
        if first:
            if_exists = "replace"
            first = False
        else:
            if_exists = "append"

        # method=None evita el límite de parámetros de pg8000 con multi-insert
        chunk.to_sql(
            name=table,
            con=engine,
            schema="raw",
            if_exists=if_exists,
            index=False,
            chunksize=chunk_rows,
            method=None,
        )

        total += len(chunk)
        if total % 20000 == 0:
            print(f"Loaded raw.{table}: {total:,} rows...")

    print(f"Loaded raw.{table}: {total:,} rows")

def main() -> None:
    print("PROJECT_ROOT:", PROJECT_ROOT)
    print("DATA_DIR:", DATA_DIR)

    if not DATA_DIR.exists():
        raise FileNotFoundError(f"No existe {DATA_DIR}. Genera primero los CSV en data/raw/")

    engine = make_engine()

    # Test conexión
    with engine.connect() as conn:
        conn.execute(text("SELECT 1;"))
    print("✅ Conexión a Postgres OK")

    # Schema raw
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))

    for table, filename in TABLES.items():
        path = DATA_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Falta el archivo: {path}")

        try:
            if table == "sales":
                load_sales_streaming(engine, table, path)
            else:
                load_small_table(engine, table, path)
        except Exception as e:
            # Cerramos engine para evitar transacción pendiente
            engine.dispose()
            raise RuntimeError(f"Error cargando raw.{table} desde {path}: {e}") from e

if __name__ == "__main__":
    main()
