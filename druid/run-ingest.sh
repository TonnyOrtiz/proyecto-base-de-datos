#!/bin/bash

# Script para procesar ingesta ciudad por ciudad en Druid
# Este script verifica que Druid esté disponible y luego ejecuta la ingesta

DRUID_URL="http://localhost:8888"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Verificando conectividad con Druid ==="

# Verificar que Druid esté disponible
if ! curl -s "$DRUID_URL/status" > /dev/null; then
    echo "❌ Error: No se puede conectar a Druid en $DRUID_URL"
    echo "Asegúrate de que Druid esté ejecutándose."
    exit 1
fi

echo "✅ Druid está disponible"

# Verificar que existen datos para procesar
DATA_DIR="/data/ingestion/crime_data_latest"
RAW_DATA_DIR="/data/raw"

if [ ! -d "$RAW_DATA_DIR" ]; then
    echo "❌ Error: No se encuentra el directorio de datos raw $RAW_DATA_DIR"
    echo "Asegúrate de que los datos estén en la estructura: /data/raw/[ciudad]/[archivos].csv"
    exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
    echo "❌ Error: No se encuentra el directorio de datos procesados $DATA_DIR"
    echo "Ejecuta primero: sudo docker exec -it spark spark-submit /data/csvproceso.py"
    exit 1
fi

# Contar ciudades disponibles
CITY_COUNT=$(find "$DATA_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)
if [ "$CITY_COUNT" -eq 0 ]; then
    echo "❌ Error: No se encontraron ciudades en $DATA_DIR"
    echo "Ejecuta primero: sudo docker exec -it spark spark-submit /data/csvproceso.py"
    exit 1
fi

echo "✅ Encontradas $CITY_COUNT ciudades para procesar"

# Ejecutar el script de Python para ingesta por ciudad
echo ""
echo "=== Iniciando ingesta por ciudad ==="
python3 "$SCRIPT_DIR/ingest-by-city.py"

echo ""
echo "=== Proceso completado ==="

