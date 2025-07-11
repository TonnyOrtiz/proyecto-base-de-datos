# Manual de Druid Docker
En este manual se explica como dar los primeros pasos para desplegar Druid en un contenedor de Docker.

## Como crear y levantar druid

```sh
sudo docker compose up -d
```

## Proceso de Ingesta de Datos por Estado

El sistema ahora procesa datos estado por estado para evitar duplicados y permitir actualizaciones granulares:

### Prerrequisitos
1. Tener Spark ejecutándose:
```sh
cd spark/
sudo docker compose up -d
```

2. Tener Druid ejecutándose:
```sh
cd druid/
sudo docker compose up -d
```

### 1. Preparar datos con Spark
Primero ejecuta el script de procesamiento que genera CSVs por estado:
```sh
# Desde el directorio raíz del proyecto
sudo docker exec -it spark spark-submit /data/csvproceso.py
```

**Nota:** El archivo `csvproceso.py` debe estar en el directorio `spark/data/` del proyecto, ya que este se monta como `/data/` dentro del contenedor de Spark.

Este script:
- Busca carpetas por nombres de estados en `/data/raw`
- Combina todos los CSVs de cada estado
- Genera un CSV por estado en `/data/ingestion/crime_data_latest/[estado]/`
- Agrega columnas `processing_ts` y `state`

### Estructura de datos de entrada esperada:
```
/data/raw/
├── california/
│   ├── archivo_1.csv
│   ├── archivo_2.csv
│   └── archivo_n.csv
├── texas/
│   ├── archivo_1.csv
│   └── archivo_n.csv
└── [otros_estados]/
    └── archivo_n.csv
```

### 2. Ingestar datos en Druid
Ejecuta la ingesta estado por estado:
```sh
# Desde el directorio druid
./run-ingest.sh
```

O directamente con Python:
```sh
python3 ingest-by-city.py
```

Este proceso:
- Verifica conectividad con Druid
- Procesa cada ciudad individualmente
- Sobrescribe solo los datos de la ciudad correspondiente
- Evita duplicados al usar `dropExisting: true`

## (Opcional) Para verificar que los datos llegaron de spark y estan en kaftka
```sh
sudo docker exec -it kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic druid-ingestion-topic \
  --from-beginning --timeout-ms 5000
```

## Configuración de Ingesta

### Archivos importantes:
- `ingest-druid.json`: Configuración base de ingesta
- `ingest-by-city.py`: Script para procesar ciudad por ciudad
- `run-ingest.sh`: Script de bash para ejecutar la ingesta completa

### Estructura de datos generada:
```
/data/ingestion/crime_data_latest/
├── california/
│   └── part-00000-xxx.csv
├── texas/
│   └── part-00000-xxx.csv
└── [otros_estados]/
    └── part-00000-xxx.csv
```

## Pagina web de administración
```
[IP de la VM]:8888
```
No necesita contraseña.

## Como eliminar contenedores de druid
```sh
sudo docker compose down -v
```


