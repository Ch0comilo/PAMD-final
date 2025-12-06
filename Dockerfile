FROM python:3.11-slim

# Variables de entorno
ENV SPARK_VERSION=3.5.1
ENV HADOOP_VERSION=3
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:${PATH}"

# Instalar Java, herramientas y dependencias del sistema
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    curl \
    tini \
    procps \
    rsync \
    dos2unix \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar Spark
RUN curl -fSL "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    --output spark.tgz \
    && mkdir -p ${SPARK_HOME} \
    && tar -xzf spark.tgz -C ${SPARK_HOME} --strip-components=1 \
    && rm spark.tgz

# Instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Configurar script de inicio
WORKDIR /app
COPY start.sh .

# Convertir formato de línea (CRLF -> LF) y dar permisos
RUN dos2unix start.sh && chmod +x start.sh

# Exponer puertos: Jupyter, Spark UI, Spark Master, MLflow, Spark Worker
EXPOSE 8888 8080 7077 5000 7078

# Entrypoint
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/start.sh"]