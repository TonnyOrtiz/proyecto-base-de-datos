# Manual de Postgre Docker
En este manual se explica como dar los primeros pasos para desplegar Druid en un contenedor de Docker.

## Como crear y levantar druid

```sh
sudo docker compose up -d
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

