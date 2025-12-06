import json
import time
import pandas as pd
from sodapy import Socrata
from kafka import KafkaProducer

# --- CONFIGURACIÓN DE KAFKA ---
KAFKA_BROKER = 'kafka:29092' 
KAFKA_TOPIC = 'contratos-publicos' 
PRODUCER_DELAY_SECONDS = 0.5 

try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1)
    )
    print(f"✅ Productor de Kafka conectado a {KAFKA_BROKER}")
except Exception as e:
    print(f"❌ Error al conectar con Kafka: {e}")
    exit()

# --- CONFIGURACIÓN DE SOCRATA Y FILTROS ---
SOCRATA_DOMAIN = "www.datos.gov.co"
SOCRATA_DATASET_ID = "jbjy-vk9h" # Contratos SECOP I
client = Socrata(SOCRATA_DOMAIN, None, timeout=120)

# Departamentos del Eje Cafetero para el filtro WHERE de la API
# Nota: La API requiere nombres en mayúsculas y sin acentos.
DEPARTMENTS = ["CALDAS", "QUINDIO", "RISARALDA", "TOLIMA", "ANTIOQUIA", "VALLE DEL CAUCA"]
DEPARTMENTS_STR = ", ".join([f"'{d}'" for d in DEPARTMENTS]) 

# Mapeo de columnas: API Field Name (SOQL) -> Alias (Kafka JSON Key)
# Seleccionamos un subconjunto relevante de la lista completa proporcionada.
COLUMNS_MAP = {
    # CRÍTICAS (Se mantienen para ML)
    "id_contrato": "id_contrato", 
    "objeto_del_contrato": "objeto_contrato",
    "nombre_entidad": "entidad",
    "codigo_de_categoria_principal": "codigo_unspsc",
    "duraci_n_del_contrato": "duracion_dias", 
    "valor_del_contrato": "valor_contrato",
    "fecha_de_firma": "fecha_firma", 
    "departamento": "departamento", 
    
    # RUIDOSAS / AUXILIARES (Se eliminan en la Fase 2)
    "nit_entidad": "nit_entidad", 
    "localizaci_n": "localizacion", 
    "sector": "sector",
    "es_pyme": "es_pyme",
    "valor_facturado": "valor_facturado",
    "urlproceso": "urlproceso",
}

COLUMNS_SOQL = ", ".join([f"{soql_col} AS {alias}" for soql_col, alias in COLUMNS_MAP.items()])

def fetch_and_stream_data():
    """Descarga datos de Socrata, filtra y los envía a Kafka."""
    
    print(f"Buscando contratos en departamentos: {', '.join(DEPARTMENTS)}")
    
    LIMIT = 5000 
    
    query = f"""
        SELECT 
            {COLUMNS_SOQL}
        WHERE 
            departamento IN ({DEPARTMENTS_STR}) AND valor_del_contrato IS NOT NULL
        ORDER BY 
            fecha_de_firma DESC
        LIMIT {LIMIT}
    """
    
    try:
        results = client.get(SOCRATA_DATASET_ID, query=query)
        
        if not results:
            print("🚨 No se encontraron contratos con los filtros especificados.")
            return

        print(f"✅ Descargados {len(results)} contratos. Iniciando streaming...")

        for i, record in enumerate(results):
            
            # Asegurar conversión de tipos para consistencia
            try:
                record['valor_contrato'] = float(record.get('valor_contrato', 0.0))
            except (ValueError, TypeError):
                record['valor_contrato'] = 0.0
                
            try:
                record['duracion_dias'] = int(record.get('duracion_dias', 0))
            except (ValueError, TypeError):
                record['duracion_dias'] = 0
            
            contract_id = record.get("id_contrato", f"NOID-{i}")

            producer.send(
                KAFKA_TOPIC, 
                key=contract_id.encode('utf-8'), 
                value=record
            )
            
            print(f"-> Contrato enviado ({i+1}/{LIMIT}): ID {contract_id} | Depto: {record.get('departamento', 'N/A')}")
            
            time.sleep(PRODUCER_DELAY_SECONDS)
            
    except Exception as e:
        print(f"\n❌ Error durante la descarga o streaming: {e}")
    finally:
        producer.close()
        print("Productor de Kafka cerrado.")


if __name__ == "__main__":
    print("Esperando 5 segundos para asegurar que Kafka está listo...")
    time.sleep(5) 
    fetch_and_stream_data()