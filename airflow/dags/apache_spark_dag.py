from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.sdk import DAG
from datetime import datetime, timedelta



with DAG (
    "main_workflow",
    default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
    },
    description = "The main dataflow which starts with Spark and ends with Superset",
    schedule = timedelta(days = 1),
    start_date = datetime(2025, 7, 10),
    catchup = False,
    tags = ['spark', 'druid', 'superset'],
) as dag:

    task1 = SSHOperator (
        task_id = 'execute_spark_code',
        ssh_conn_id = 'airflow_to_spark',
        command = 'echo Hello from Airflow > /mnt/data/AirflowTest.txt'
    )
