#!/bin/bash

# 1. Iniciar Spark Master
echo "Iniciando Spark Master..."
${SPARK_HOME}/sbin/start-master.sh --host 0.0.0.0

# 2. Iniciar Spark Worker (Conectado al master local)
echo "Iniciando Spark Worker..."
${SPARK_HOME}/sbin/start-worker.sh spark://0.0.0.0:7077

# 3. Iniciar MLflow Server (Conectado a Postgres)
echo "Iniciando MLflow Server..."
mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri ${BACKEND_STORE_URI} \
    --default-artifact-root file:///app/mlflow_artifacts &

# 4. Iniciar JupyterLab
echo "Iniciando JupyterLab..."
# Nota: Se agregan paquetes de Delta y Kafka al iniciar para que Spark los descargue
exec jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --NotebookApp.token=${JUPYTER_TOKEN} \
    --notebook-dir=/app/notebooks