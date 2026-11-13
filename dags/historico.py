from datetime import datetime
from airflow.sdk import dag, get_current_context, task

@dag(schedule="0 3 * * *", start_date=datetime(2026, 11, 1),
     catchup=True, max_active_runs=3)
def historico():
    @task
    def extraer() -> str:
        momento = get_current_context()["logical_date"]
        dia = momento.date()
        print(f"Ejecución del {momento:%d/%m a las %H:%M} → datos del {dia}")
        return str(dia)
    extraer()
historico()
