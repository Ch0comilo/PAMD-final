from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    'test_dag_simple',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    t1 = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    t2 = BashOperator(
        task_id='echo_hello',
        bash_command='echo "Hola Airflow!"',
    )

    t1 >> t2