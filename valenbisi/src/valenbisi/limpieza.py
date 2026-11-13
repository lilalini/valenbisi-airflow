"""Limpieza de las estaciones de Valenbisi."""
import pandas as pd

COLUMNAS = ["number", "address", "open", "available", "free", "total",
            "ticket", "actualizado", "lon", "lat", "pct_libres"]


def limpiar(estaciones: list[dict]) -> pd.DataFrame:
    """De la lista de features de la API a la tabla lecturas."""
    df = pd.json_normalize(estaciones)
    df.columns = df.columns.str.replace("properties.", "")
    df["lon"] = df["geometry.coordinates"].str[0]
    df["lat"] = df["geometry.coordinates"].str[1]
    df["actualizado"] = pd.to_datetime(df["update_jcd"], unit="ms", utc=True)
    df["open"] = df["open"].map({"T": True, "F": False})
    df["ticket"] = df["ticket"].map({"T": True, "F": False})
    df["pct_libres"] = (df["free"] / df["total"] * 100).round(1)
    df = (df.drop_duplicates(subset=["number", "actualizado"])
            .dropna(subset=["available", "free"])
            .query("available >= 0 and free >= 0"))
    return df[COLUMNAS]
