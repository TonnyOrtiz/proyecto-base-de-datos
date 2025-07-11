import os
import shutil
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, date_format, lit

spark = SparkSession.builder \
    .appName("CSV to Druid Pipeline") \
    .getOrCreate()

# Directorio base donde están las carpetas de ciudades
base_data_path = "/data/raw"
all_dataframes = []

# Verificar que existe el directorio raw
if not os.path.exists(base_data_path):
    print(f"Error: No se encuentra el directorio {base_data_path}")
    spark.stop()
    exit(1)

# Recorrer todas las carpetas en /data/raw
for city_folder in os.listdir(base_data_path):
    city_path = os.path.join(base_data_path, city_folder)
    
    # Solo procesar si es un directorio
    if os.path.isdir(city_path):
        print(f"Procesando ciudad: {city_folder}")
        
        # Buscar todos los archivos CSV en la carpeta de la ciudad
        csv_files = []
        for file in os.listdir(city_path):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(city_path, file))
        
        if csv_files:
            # Leer todos los CSVs de la ciudad y combinarlos
            city_dfs = []
            for csv_file in csv_files:
                print(f"  - Procesando archivo: {csv_file}")
                df = spark.read.csv(csv_file, header=True, inferSchema=True)
                city_dfs.append(df)
            
            # Combinar todos los archivos de la ciudad
            if len(city_dfs) == 1:
                combined_df = city_dfs[0]
            else:
                combined_df = city_dfs[0]
                for df in city_dfs[1:]:
                    combined_df = combined_df.union(df)
            
            # Agregar columnas de procesamiento y ciudad
            processed_df = combined_df.withColumn("processing_ts", current_timestamp()) \
                                    .withColumn("city", lit(city_folder))
            
            all_dataframes.append(processed_df)
        else:
            print(f"  - No se encontraron archivos CSV en {city_folder}")

# Procesar cada ciudad por separado para generar CSVs individuales
if all_dataframes:
    print(f"Total de ciudades procesadas: {len(all_dataframes)}")
    
    # Obtener timestamp para esta ejecución
    date_str = spark.sql("SELECT date_format(current_timestamp(), 'yyyyMMddHHmm') as dt").collect()[0]['dt']
    
    # Crear directorio base para esta ejecución
    base_output_path = f"/data/ingestion/crime_data_{date_str}"
    os.makedirs(base_output_path, exist_ok=True)
    
    # Preparar directorio latest
    latest_path = "/data/ingestion/crime_data_latest"
    if os.path.exists(latest_path):
        shutil.rmtree(latest_path)
    os.makedirs(latest_path, exist_ok=True)
    
    # Procesar cada ciudad individualmente
    for i, df in enumerate(all_dataframes):
        # Obtener el nombre de la ciudad del DataFrame
        city_name = df.select("city").distinct().collect()[0]["city"]
        
        print(f"Exportando ciudad: {city_name}")
        print(f"  Total de filas para {city_name}: {df.count()}")
        
        # Crear directorio para esta ciudad en ambas ubicaciones
        city_output_path = os.path.join(base_output_path, city_name)
        city_latest_path = os.path.join(latest_path, city_name)
        
        # Exportar CSV para esta ciudad específica
        df.coalesce(1) \
          .write \
          .option("header", "true") \
          .mode("overwrite") \
          .csv(city_output_path)
        
        # Copiar también a latest para que Druid siempre tenga la versión más reciente
        df.coalesce(1) \
          .write \
          .option("header", "true") \
          .mode("overwrite") \
          .csv(city_latest_path)
    
    print(f"CSVs exportados por ciudad en: {base_output_path}")
    print(f"CSVs latest actualizados en: {latest_path}")
else:
    print("No se encontraron datos para procesar")

# Opcional: Ejecutar ingesta a Druid automáticamente (ver método abajo)
spark.stop()

