# Proyecto Bases de Datos Avanzadas 

### Integrantes
Tonny Ortiz Salazar
Juliana Martinez Aguilar
Andres Serrano Robles
Juan Carlos Sequeira Jiménez


# Manual técnico para la implementación del caso de estudio

En este manual se explicará como implementar toda la arquitectura y levantarla a partir de los archivos de este repositorio. En el presente README se muestra un manual rápido de ejecución, sin embargo, en cada una de las carpetas de las herramientas contiene un manual a detalle con todos los pasos que se debe de realizar para la implementación de la herramienta.

## Inicio Rápido

### Ejecución Manual

1. **Preparar datos:**
```sh
# Levantar Spark
cd spark 
sudo docker build -f Dockerfile.spark
sudo docker compose up -d

# Procesar datos
sudo docker exec -it spark spark-submit /data/csvproceso.py
```

2. **Ingestar en Druid:**
```sh
# Levantar Druid  
cd druid 
sudo docker build -f Dockerfile.druid
sudo docker compose up -d

# Ingestar datos
curl -X POST -H "Content-Type: application/json"   -d @druid-ingest.json   http://localhost:8888/druid/indexer/v1/task
```

## Estructura de Datos

Los datos deben estar organizados como:
```
/proyecto/
├── airflow/
│   ├── config/
│   │   ├── airflow.cfg
│   ├── dags/
│   │    └── apache_spark_dag.py
│   └── docker-compose.yaml
├── druid/
│   ├── config/
│   │    └── spec.json
│   └── docker-compose.yml
├── hadoop/
│   └── docker-compose.yml
├── postgre/
│   ├── docker-compose.yml
│   └── postgresql.
├── shadoop/
│   └── postgresql.conf
├── spark/
│   ├── data/
│   │   ├── cvsproceso.py
│   │   └── postgreproceso.py
│   └── docker-compose.yml
├── superset/
│   └── docker-compose.yml
└── README.md
```

## Contenedores de Docker
- [Spark](./spark/README.MD)
- [Druid](./druid/README.MD)
- [Postgre](./postgre/README.MD)
- [Airflow](./airflow/README.MD)


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

Ahora en adelante puede ejecutar docker sin sudo y todos los volumenes declarados caeran en /mnt/data/docker