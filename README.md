# Valenbisi: ETL con Airflow

ETL con Airflow que lleva la disponibilidad de las estaciones de Valenbisi desde la API del Ayuntamiento de València a PostgreSQL. Un DAG con tres tareas (extraer, transformar y cargar) que Airflow ejecuta cada 10 minutos.

## Fuente de los datos

Geoportal del Ayuntamiento de València, dataset «ValenBisi Disponibilidad» del portal de datos abiertos (opendata.vlci.valencia.es). Licencia CC BY 4.0: hay que citar la fuente. Los datos se actualizan cada 10 minutos.

## Qué hace cada tarea

- **extraer:** pide los datos a la API (con tiempo máximo de espera) y guarda la respuesta en bruto en `data/raw/`, con la hora de descarga en el nombre.
- **transformar:** lee el fichero en bruto, lo limpia con la función `limpiar()` del paquete `valenbisi` (tipos correctos, fecha con zona horaria, columnas calculadas) y guarda un CSV en `data/limpio/`.
- **cargar:** inserta el CSV en la tabla `lecturas` de PostgreSQL ignorando las lecturas que ya existen, y escribe en el log cuántas son nuevas.

**DAG `historico` (ejemplo de `catchup`).** Se ejecuta cada día a las 03:00 y empieza el 1 de noviembre de 2026, con `catchup=True` y como máximo 3 ejecuciones a la vez. Solo imprime la fecha lógica de cada ejecución y no guarda nada en la base de datos. Al activarlo, Airflow lanza una ejecución por cada día perdido desde el 1 de noviembre.

## Estructura del repositorio

```
├── dags/valenbisi_etl.py   el ETL, cada 10 minutos
├── dags/historico.py       ejemplo de catchup: imprime la fecha de cada ejecución
├── valenbisi/              paquete de Python propio, sin dependencia de Airflow (con tests)
├── sql/crear_tabla.sql     crea la tabla lecturas al arrancar la base de datos
├── Dockerfile              imagen de Airflow con el paquete instalado
├── compose.yaml            Airflow y las dos bases de datos
└── data/ logs/             los crea Airflow al ejecutar (no se suben)
```

## Puesta en marcha desde cero

Requisitos: Docker (con Docker Desktop abierto), `uv` y Git.

1. Clonar el repositorio y entrar en la carpeta.
2. Crear las carpetas compartidas: `mkdir -p dags logs data sql`.
3. Crear el fichero `.env` (no se sube al repositorio) con `AIRFLOW_UID`, `AIRFLOW__API_AUTH__JWT_SECRET`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `AIRFLOW_CONN_VALENBISI_DB` y `AIRFLOW_VAR_VALENBISI_URL`. La contraseña debe ser la misma en `POSTGRES_PASSWORD` y en la Connection, solo con letras y números.
4. Preparar Airflow: `docker compose up airflow-init` (debe terminar con `exited with code 0`).
5. Arrancar todo: `docker compose up -d --build`.
6. Abrir `http://localhost:8080` y activar el DAG `valenbisi_etl`.

Para parar sin perder datos: `docker compose stop`. No usar `docker compose down -v`, que borra los volúmenes.

## Comprobaciones hechas

- El DAG entero termina en `success`. La primera ejecución cargó 273 lecturas nuevas de 273, con la tabla vacía.
- Repetir el DAG no duplica filas: la segunda ejecución dio 76 lecturas nuevas de 273, y la tabla quedó con 349 filas (273 + 76).

## Contraseñas

Las credenciales están en el fichero `.env`, que no se sube al repositorio. En `compose.yaml` aparece `POSTGRES_PASSWORD: airflow` en el servicio `metadatos`: es la base de datos interna de Airflow, sin ningún puerto publicado, y se ha dejado igual que en el `compose.yaml` de clase.
