# MLOps & Big Data Streaming Pipeline

Este proyecto despliega una arquitectura End-to-End contenerizada para la ingesta, procesamiento y orquestación de modelos de Machine Learning.

## Arquitectura

El entorno levanta los siguientes servicios mediante Docker:

* **Ingesta:** Zookeeper & Kafka
* **Procesamiento:** Apache Spark (Master & Worker) con soporte Delta Lake
* **Desarrollo:** JupyterLab
* **Orquestación:** Apache Airflow
* **Registro de Modelos:** MLflow
* **Metadatos:** PostgreSQL

## Detener entornos anteriores

```bash
docker-compose down
```

## Despliegue

Para iniciar todos los servicios en segundo plano, ejecuta:

```bash
docker-compose up --build -d
```

## Accesos y Credenciales

| **Servicio**     | **URL**         | **Usuario / Token** | **Contraseña** |
| ---------------------- | --------------------- | ------------------------- | --------------------- |
| **JupyterLab**   | http://localhost:8888 | `hola-mundo`            | N/A                   |
| **Airflow UI**   | http://localhost:8081 | `admin`                 | `admin`             |
| **MLflow UI**    | http://localhost:5000 | N/A                       | N/A                   |
| **Spark Master** | http://localhost:8080 | N/A                       | N/A                   |

# Activar simulación Kafka

Una vez ya tengan el entorno Docker hacen lo siguiente:

```bash
docker exec -it python_ml_stack  /bin/bash
```

luego les debe salir algo como:

```bash
root@ab59cf153712:/app# 
```

Ya entraron al Docker de python_ml_stack, luego ejecutan

```bash
pip install sodapy
python /app/notebooks/contract_producer.py
```

Ahora si pueden ejecutar Taller.ipynb
