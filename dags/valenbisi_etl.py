"""ETL de Valenbisi: cada 10 minutos guarda el estado de las estaciones."""
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import Variable, dag, task
from sqlalchemy.dialects.postgresql import insert

from valenbisi.limpieza import limpiar

DATOS = Path("/opt/airflow/data")


def ignorar_repetidas(tabla, conexion, columnas, filas):
    """Método para to_sql: INSERT ... ON CONFLICT DO NOTHING."""
    valores = [dict(zip(columnas, f)) for f in filas]
    sentencia = (insert(tabla.table).values(valores)
                 .on_conflict_do_nothing()
                 .returning(tabla.table.c.number))   # solo las nuevas
    return len(conexion.execute(sentencia).all())


@dag(schedule="*/10 * * * *", start_date=datetime(2026, 10, 1),
     catchup=False, tags=["valenbisi"])
def valenbisi_etl():

    @task
    def extraer() -> str:
        url = Variable.get("valenbisi_url")
        params = {"where": "1=1", "outFields": "*",
                  "f": "geojson", "outSR": 4326}
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        if r.json().get("exceededTransferLimit"):
            raise RuntimeError("Respuesta cortada: hay que paginar")
        momento = datetime.now(timezone.utc)
        ruta = DATOS / "raw" / f"{momento:%Y%m%d_%H%M%S}.json"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(r.text, encoding="utf-8")
        return str(ruta)

    @task
    def transformar(ruta_json) -> str:
        texto = Path(ruta_json).read_text(encoding="utf-8")
        df = limpiar(json.loads(texto)["features"])   # paquete valenbisi
        ruta = Path(ruta_json.replace("/raw/", "/limpio/")).with_suffix(".csv")
        ruta.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(ruta, index=False)
        return str(ruta)

    @task
    def cargar(ruta_csv) -> int:
        df = pd.read_csv(ruta_csv, parse_dates=["actualizado"])
        hook = PostgresHook(postgres_conn_id="valenbisi_db")
        engine = hook.get_sqlalchemy_engine()
        nuevas = df.to_sql("lecturas", engine, if_exists="append", index=False,
                           method=ignorar_repetidas)
        print(f"{nuevas} lecturas nuevas de {len(df)}")
        return nuevas or 0

    cargar(transformar(extraer()))


valenbisi_etl()


