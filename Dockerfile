FROM apache/airflow:3.3.2
COPY valenbisi /tmp/valenbisi
RUN pip install --no-cache-dir "apache-airflow==3.3.2" /tmp/valenbisi
