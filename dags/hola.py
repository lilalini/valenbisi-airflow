from datetime import datetime

from airflow.sdk import dag, task


@dag(schedule="@daily", start_date=datetime(2026, 10, 1), catchup=False)
def hola():
    @task
    def saludar() -> str:
        return "Hola desde Airflow"

    @task
    def mostrar(mensaje) -> None:
        print(mensaje.upper())

    mostrar(saludar())


hola()
