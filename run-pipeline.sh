#!/bin/bash

# Script principal para ejecutar el pipeline completo de procesamiento de datos
# Desde datos raw hasta ingesta en Druid

set -e  # Salir si cualquier comando falla

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Iniciando pipeline de procesamiento de datos..."

# Función para verificar si un contenedor está ejecutándose
check_container() {
    local container_name=$1
    if ! docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        return 1
    fi
    return 0
}

# Verificar que Spark esté ejecutándose
echo -e "\n${YELLOW}📋 Verificando contenedores...${NC}"
if ! check_container "spark"; then
    echo -e "${RED}❌ El contenedor 'spark' no está ejecutándose${NC}"
    echo "💡 Ejecuta: cd spark && sudo docker compose up -d"
    exit 1
fi
echo -e "${GREEN}✅ Spark está ejecutándose${NC}"

# Verificar que Druid esté disponible
if ! check_container "druid-router"; then
    echo -e "${YELLOW}⚠️  El contenedor 'druid-router' no está ejecutándose${NC}"
    echo "💡 Ejecuta: cd druid && sudo docker compose up -d"
    echo "🔄 Continuando con el procesamiento de datos..."
fi

# Verificar estructura de datos
echo -e "\n${YELLOW}📂 Verificando estructura de datos...${NC}"
if [ ! -d "/mnt/data/raw" ] && [ ! -d "/data/raw" ]; then
    echo -e "${RED}❌ No se encuentra el directorio de datos raw${NC}"
    echo "💡 Asegúrate de que los datos estén en /data/raw/[estado]/[archivos].csv"
    exit 1
fi

DATA_RAW_PATH="/mnt/data/raw"
if [ ! -d "$DATA_RAW_PATH" ]; then
    DATA_RAW_PATH="/data/raw"
fi

STATE_COUNT=$(find "$DATA_RAW_PATH" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
if [ "$STATE_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ No se encontraron estados en $DATA_RAW_PATH${NC}"
    echo "💡 Estructura esperada: $DATA_RAW_PATH/[estado]/[archivos].csv"
    exit 1
fi

echo -e "${GREEN}✅ Encontrados $STATE_COUNT estados para procesar${NC}"

# Paso 1: Procesar datos con Spark
echo -e "\n${YELLOW}⚙️  Paso 1: Procesando datos con Spark...${NC}"
echo "🔄 Ejecutando: sudo docker exec -it spark spark-submit /data/csvproceso.py"

if sudo docker exec -it spark spark-submit /data/csvproceso.py; then
    echo -e "${GREEN}✅ Procesamiento con Spark completado${NC}"
else
    echo -e "${RED}❌ Error en el procesamiento con Spark${NC}"
    exit 1
fi

# Verificar que se generaron los datos procesados
PROCESSED_DATA_PATH="/mnt/data/ingestion/crime_data_latest"
if [ ! -d "$PROCESSED_DATA_PATH" ]; then
    PROCESSED_DATA_PATH="/data/ingestion/crime_data_latest"
fi

if [ ! -d "$PROCESSED_DATA_PATH" ]; then
    echo -e "${RED}❌ No se generaron datos procesados${NC}"
    exit 1
fi

PROCESSED_STATE_COUNT=$(find "$PROCESSED_DATA_PATH" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
echo -e "${GREEN}✅ Se generaron datos para $PROCESSED_STATE_COUNT estados${NC}"

# Paso 2: Ingestar en Druid (opcional, solo si Druid está disponible)
if check_container "druid-router"; then
    echo -e "\n${YELLOW}📥 Paso 2: Ingesta en Druid...${NC}"
    
    # Verificar conectividad con Druid
    if curl -s "http://localhost:8888/status" > /dev/null; then
        echo -e "${GREEN}✅ Druid está disponible${NC}"
        echo "🔄 Ejecutando ingesta por estado..."
        
        cd "$SCRIPT_DIR/druid"
        if ./run-ingest.sh; then
            echo -e "${GREEN}✅ Ingesta en Druid completada${NC}"
        else
            echo -e "${RED}❌ Error en la ingesta de Druid${NC}"
            echo "💡 Puedes ejecutar manualmente: cd druid && ./run-ingest.sh"
        fi
    else
        echo -e "${YELLOW}⚠️  No se puede conectar a Druid en localhost:8888${NC}"
        echo "💡 Verifica que Druid esté completamente iniciado"
    fi
else
    echo -e "\n${YELLOW}⚠️  Druid no está ejecutándose, omitiendo ingesta${NC}"
    echo "💡 Para ingestar después: cd druid && ./run-ingest.sh"
fi

echo -e "\n${GREEN}🎉 Pipeline completado exitosamente!${NC}"
echo -e "\n📊 Resumen:"
echo -e "   - Estados procesados: $PROCESSED_STATE_COUNT"
echo -e "   - Datos disponibles en: $PROCESSED_DATA_PATH"
if check_container "druid-router"; then
    echo -e "   - Interfaz de Druid: http://localhost:8888"
fi
