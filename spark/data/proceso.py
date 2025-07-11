from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
import sys

# Configuración de Druid
DRUID_COORDINATOR_URL = "http://172.16.202.175:8088"  # Reemplaza con tu IP/host
DRUID_DATASOURCE = "spark_datasource"  # Nombre del datasource en Druid

try:
    # Configuración de Spark con el conector Druid
    spark = SparkSession.builder \
        .appName("Spark to Druid Direct") \
        .config("spark.jars.packages", "org.apache.druid:druid-spark-batch_2.12:0.22.0") \
        .getOrCreate()

    # Leer CSV local
    print("=== Leyendo archivo CSV local ===")
    df = spark.read.csv("file:///data/archivo.csv", header=True, inferSchema=True)
    
    # Procesamiento (añadir timestamp)
    df_processed = df.withColumn("timestamp", current_timestamp())
    df_processed.show(5)

    # Escribir directamente a Druid
    print("=== Escribiendo a Druid ===")
    df_processed.write \
        .format("org.apache.druid.spark") \
        .option("druid.coordinator.url", DRUID_COORDINATOR_URL) \
        .option("druid.datasource", DRUID_DATASOURCE) \
        .option("druid.rollup.granularity", "none") \  # O "hour", "day" según necesites
        .mode("append") \
        .save()

    print("¡Escritura a Druid completada exitosamente!")

except Exception as e:
    print(f"Error: {str(e)}", file=sys.stderr)
    raise

finally:
    if 'spark' in locals():
        spark.stop()
