# Apache Superset

## Instalación

En la partición de /mnt/data se clona el repostirio de Apache Superset.

```sh
bash
cd /mnt/data/
git clone https://github.com/apache/superset.git
```

## Ejecución de Superset en Docker

### Aspectos importantes

1. En este caso debdido a la necesidad de poder utilziar super fuera del ambiente local propio de la máquina se eligió utilizar el `docker-compose.yml`.

2. Debido a que por defecto `docker-compose.yml` utiliza en el contenedor `services` el puerto 80 fue necesario cambiar este por el puerto 8888 debido a problemas de disponibilidad de dicho puerto.

3. Al intentar realizar la conexión de Superset con Druid no se habilitaba el botón de conectar, por lo que para intentar que este sirviera se realizó lo siguiente:

* Indicar en el `dockerfile` que lo instale al construir el contenedor, esto mediante añadir la línea de instalación del driver `pydruid`.

```sh
FROM python-common AS lean

# Install Python dependencies using docker/pip-install.sh
COPY requirements/base.txt requirements/
RUN --mount=type=cache,target=${SUPERSET_HOME}/.cache/uv \
    /app/docker/pip-install.sh --requires-build-essential -r requirements/base.txt

# Install Apache Druid Driver
RUN uv pip install pydruid sqlalchemy-druid
```

## Ejecución del Docker Compose

Se ejecutó Superset mediante la utilización de los comandos

```sh
docker compose --build
docker compose up
```

Lo que permite ingresar a la interfaz de Superset mediate la dirección `ip:8888`.

**Nota:** En caso de que se le pida un usuario este es:

```sh
user : admin
password : admin
```

## Parar los contenedores de Docker

En caso de que desea que los volumenes que almacenan los datos de Superset se elimine se utiliza el comando

```sh
docker compose down -v
```

En caso contrario usar

```sh
docker compose down
```

# Permisos en Partición

En `/mnt` se le indicó los siguientes comandos para cambiar el propietario y el grupo del directorio data al usuario actual

```sh
sudo chown -R $USER:$USER data
```

A fin de no tener que ejecutar comandos con privilegios de usuario raíz todos los comandos necesarios para la utilización de la partición.