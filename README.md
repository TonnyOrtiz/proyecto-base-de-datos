# Proyecto Bases de Datos Avanzadas 

### Integrantes
Tonny Ortiz Salazar
Juliana
Andres Serrano
Juan Carlos


# Manual técnico para la implementación del caso de estudio

En este manual se explicará como implementar toda la arquitectura y levantarla a partir de los archivos de este repositorio.

## Inicio Rápido

### Pipeline Automatizado (Recomendado)
Para ejecutar todo el proceso de manera automatizada:

```sh
./run-pipeline.sh
```

Este script:
1. ✅ Verifica que los contenedores necesarios estén ejecutándose
2. 🔄 Procesa los datos con Spark (`csvproceso.py`)
3. 📥 Ingesta los datos en Druid estado por estado
4. 📊 Proporciona un resumen del proceso

### Ejecución Manual

1. **Preparar datos:**
```sh
# Levantar Spark
cd spark && sudo docker compose up -d

# Procesar datos
sudo docker exec -it spark spark-submit /data/csvproceso.py
```

2. **Ingestar en Druid:**
```sh
# Levantar Druid  
cd druid && sudo docker compose up -d

# Ingestar datos
cd druid && ./run-ingest.sh
```

## Estructura de Datos

Los datos deben estar organizados como:
```
/data/raw/
├── california/
│   ├── archivo_1.csv
│   └── archivo_n.csv
├── texas/
│   └── archivo_n.csv
└── [otros_estados]/
    └── archivo_n.csv
```

## Contenedores de Docker

- [Spark](./spark/README.MD)
- [Druid](./druid/README.MD)
- [Postgre](./postgre/README.MD)


# Para resolver el problema con los permisos en /mnt/data
```
# 1. Agregar tu usuario al grupo docker (si no lo has hecho)
sudo usermod -aG docker $USER
newgrp docker  # Actualiza la sesión actual

# 2. Aplicar permisos a /mnt/data
sudo chown -R $USER:docker /mnt/data
sudo chmod -R 775 /mnt/data
sudo setfacl -Rdm g:docker:rwx /mnt/data  # Heredar permisos para nuevos archivos

# 3. Verificar
ls -ld /mnt/data  # Debería mostrar $USER:docker y drwxrwxr-x
```
Configura tu /etc/docker/daemon.json
```
{
  "data-root": "/mnt/data/docker",
  "group": "docker"
}
```

Reinicar docker 

```
sudo systemctl restart docker
```

ahora en adelante puede ejecutar docker sin sudo y todos los volumenes declarados caeran en /mnt/data/docker
