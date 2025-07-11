# Apache Spark

## Para levantar los contenedores de spark
```sh
sudo docker compose up -d
```

## Para procesar los datos y enviarlos a Druid 
```sh
sudo docker exec -it spark spark-submit /data/csvproceso.py
```

## Para procesar los datos y enviarlos a PostgreSQL
```sh
sudo docker exec -it spark spark-submit /data/postgreproceso.py
```

## Para eliminar a los contenedores
```sh
sudo docker compose down -v
```