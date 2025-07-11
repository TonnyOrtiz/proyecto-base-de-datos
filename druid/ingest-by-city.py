#!/usr/bin/env python3
"""
Script para ingestar datos en Druid ciudad por ciudad.
Esto permite que cada ciudad sobrescriba solo sus propios datos anteriores.
"""

import os
import json
import requests
import time
from pathlib import Path

# Configuración de Druid
DRUID_ROUTER_URL = "http://localhost:8888"
DRUID_INGESTION_ENDPOINT = f"{DRUID_ROUTER_URL}/druid/indexer/v1/task"

def load_base_spec():
    """Cargar la especificación base de ingesta"""
    spec_path = Path(__file__).parent / "ingest-druid.json"
    with open(spec_path, 'r') as f:
        return json.load(f)

def create_city_spec(base_spec, city_name):
    """Crear especificación de ingesta para una ciudad específica"""
    city_spec = base_spec.copy()
    
    # Modificar el inputSource para apuntar solo a la carpeta de la ciudad
    city_spec["spec"]["ioConfig"]["inputSource"]["baseDir"] = f"/data/ingestion/crime_data_latest/{city_name}"
    city_spec["spec"]["ioConfig"]["inputSource"]["filter"] = "*.csv"
    
    # Modificar el dataSource para incluir la ciudad (opcional, o mantener el mismo datasource)
    # city_spec["spec"]["dataSchema"]["dataSource"] = f"crime_reports_{city_name}"
    
    # Asegurar que dropExisting esté en true para sobrescribir datos de la ciudad
    city_spec["spec"]["tuningConfig"]["dropExisting"] = True
    
    # Agregar filtro por ciudad en la granularitySpec para segmentación
    intervals_filter = f"city = '{city_name}'"
    
    return city_spec

def submit_ingestion_task(spec):
    """Enviar tarea de ingesta a Druid"""
    try:
        response = requests.post(
            DRUID_INGESTION_ENDPOINT,
            json=spec,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error enviando tarea: {e}")
        return None

def check_task_status(task_id):
    """Verificar el estado de una tarea"""
    try:
        response = requests.get(f"{DRUID_ROUTER_URL}/druid/indexer/v1/task/{task_id}/status")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error verificando estado: {e}")
        return None

def wait_for_task_completion(task_id, timeout=3600):
    """Esperar a que una tarea se complete"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = check_task_status(task_id)
        if status:
            task_status = status.get("status", {}).get("status", "UNKNOWN")
            print(f"Estado de la tarea {task_id}: {task_status}")
            
            if task_status in ["SUCCESS", "FAILED"]:
                return task_status
        
        time.sleep(10)  # Esperar 10 segundos antes de verificar nuevamente
    
    return "TIMEOUT"

def get_available_cities():
    """Obtener lista de ciudades disponibles en el directorio de datos"""
    latest_path = "/data/ingestion/crime_data_latest"
    cities = []
    
    if os.path.exists(latest_path):
        for item in os.listdir(latest_path):
            item_path = os.path.join(latest_path, item)
            if os.path.isdir(item_path):
                cities.append(item)
    
    return sorted(cities)

def main():
    """Función principal"""
    print("=== Ingesta de datos por ciudad en Druid ===")
    
    # Cargar especificación base
    base_spec = load_base_spec()
    
    # Obtener ciudades disponibles
    cities = get_available_cities()
    
    if not cities:
        print("No se encontraron ciudades para procesar.")
        return
    
    print(f"Ciudades encontradas: {', '.join(cities)}")
    
    successful_cities = []
    failed_cities = []
    
    # Procesar cada ciudad
    for city in cities:
        print(f"\n--- Procesando ciudad: {city} ---")
        
        # Crear especificación para esta ciudad
        city_spec = create_city_spec(base_spec, city)
        
        # Enviar tarea de ingesta
        response = submit_ingestion_task(city_spec)
        
        if response and "task" in response:
            task_id = response["task"]
            print(f"Tarea enviada: {task_id}")
            
            # Esperar a que se complete
            final_status = wait_for_task_completion(task_id)
            
            if final_status == "SUCCESS":
                print(f" Ciudad {city} procesada exitosamente")
                successful_cities.append(city)
            else:
                print(f" Error procesando ciudad {city}: {final_status}")
                failed_cities.append(city)
        else:
            print(f" Error enviando tarea para ciudad {city}")
            failed_cities.append(city)
    
    # Resumen final
    print(f"\n=== Resumen ===")
    print(f"Ciudades procesadas exitosamente: {len(successful_cities)}")
    if successful_cities:
        print(f"  - {', '.join(successful_cities)}")
    
    print(f"Ciudades con errores: {len(failed_cities)}")
    if failed_cities:
        print(f"  - {', '.join(failed_cities)}")

if __name__ == "__main__":
    main()

