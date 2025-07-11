def extract_data():
    conn = psycopg2.connect(
        host="postgres",  # Nombre del contenedor PostgreSQL
        database="crimedata",
        user="druid",
        password="FoolishPassword"
    )
    df = pd.read_sql("SELECT * FROM processed", conn)
    conn.close()
    return df

def load_to_druid(df):
    spec = {
        "type": "index_parallel",
        "spec": {
            "ioConfig": {
                "type": "index_parallel",
                "inputSource": {
                    "type": "inline",
                    "data": df.to_csv(index=False)  # Envía datos directamente sin CSV
                },
                "inputFormat": {"type": "csv", "columns": list(df.columns)}
            },
            "dataSchema": {
                "dataSource": "mi_datastore",
                "timestampSpec": {"column": "fecha", "format": "iso"},
                "dimensionsSpec": {"dimensions": ["campo1", "campo2"]},
                "granularitySpec": {"segmentGranularity": "day"}
            }
        }
    }
    response = requests.post(
        "http://localhost:8081/druid/indexer/v1/task",
        json=spec,
        headers={"Content-Type": "application/json"}
    )
    print(response.json())

if __name__ == "main":
    data = extract_data()
    load_to_druid(data)
