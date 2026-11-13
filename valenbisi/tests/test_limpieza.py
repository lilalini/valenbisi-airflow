from valenbisi.limpieza import limpiar

def estacion(number, available, free, hora=1792579973000):
    return {"geometry": {"coordinates": [-0.38, 39.48]},
            "properties": {"number": number, "address": "Calle", "open": "T",
                           "ticket": "F", "available": available, "free": free,
                           "total": available + free, "update_jcd": hora}}

def test_quita_repetidas_e_imposibles():
    df = limpiar([estacion(1, 5, 15), estacion(1, 5, 15), estacion(2, -1, 10)])
    assert list(df["number"]) == [1]

def test_tipos_y_porcentaje():
    df = limpiar([estacion(1, 5, 15)])
    assert df["open"].dtype == bool
    assert df["pct_libres"].iloc[0] == 75.0
