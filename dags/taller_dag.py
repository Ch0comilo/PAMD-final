from airflow import DAG
from airflow.sensors.python import PythonSensor
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# ================================
#   CONFIGURACIÓN GENERAL DEL DAG
# ================================
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

dag = DAG(
    "pipeline_contratos",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
)

# ==========================================
#     1. SENSOR: REVISAR NUEVOS DATOS
# ==========================================
def verificar_datos():
    """
    Aquí iría tu consulta real a Spark/Delta.
    Por ahora retorna True para que el DAG cargue.
    """
    return True

sensor_silver = PythonSensor(
    task_id="esperar_nuevos_datos",
    python_callable=verificar_datos,
    poke_interval=60,
    timeout=3600,
    mode="poke",
    dag=dag
)

# ==========================================
#     2. TAREA SEMANAL (RETRAINING)
# ==========================================
retrain_model = BashOperator(
    task_id="retrain_model_weekly",
    bash_command="spark-submit /opt/scripts/retrain_model.py",
    dag=dag
)

# ==========================================
#     3. TAREA DIARIA (INFERENCIA)
# ==========================================
daily_inference = BashOperator(
    task_id="run_inference_daily",
    bash_command="spark-submit /opt/scripts/inference_daily.py",
    dag=dag
)

# DEPENDENCIAS
sensor_silver >> daily_inference
retrain_model
