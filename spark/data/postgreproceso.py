from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp

# Crear sesión de Spark con el conector JDBC de PostgreSQL
spark = SparkSession.builder \
    .appName("CSV to PostgreSQL") \
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.2") \
    .getOrCreate()

# Leer CSV
df = spark.read.csv("/data/archivo.csv", header=True, inferSchema=True)

# Agregar columna de timestamp actual
df_processed = df.withColumn("timestamp", current_timestamp())

# Mostrar algunos resultados
print("=== Datos procesados ===")
df_processed.show(5)
df_processed.printSchema()

# Escribir en PostgreSQL
df_processed.write \
  .format("jdbc") \
  .option("url", "jdbc:postgresql://172.16.202.175:5432/crimesdata") \
  .option("dbtable", "crimes") \
  .option("user", "druid") \
  .option("password", "FoolishPassword") \
  .option("driver", "org.postgresql.Driver") \
  .mode("overwrite") \
  .save()
print("¡Datos enviados a PostgreSQL exitosamente!")

# Detener Spark
spark.stop()

