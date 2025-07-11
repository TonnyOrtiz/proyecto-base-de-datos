## Para levantarlo
```sh
sudo docker compose up -d
```

## Para ejecutar arhivos .py para spark, procesar los datos y enviarlos a druid
Primero para druid directo
```sh
sudo docker exec -it spark spark-submit --packages org.apache.druid:druid-spark-batch_2.12:0.22.0 /data/proceso.py
```

## Para subir los datos del kafka (no lo he probado)
```sh
curl -X POST -H "Content-Type: application/json" -d @druid/data/spec.json http://localhost:8888/druid/indexer/v1/task
```sh

## Para botarlo
```sh
sudo docker compose down -v
```
