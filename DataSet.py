import pandas as pd
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import urllib3
 
# Désactiver les avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 
# Connexion à Elasticsearch
es = Elasticsearch(
    ["https://192.168.5.30:9200"],
    basic_auth=("elastic", "BdKIa7rf124gEGBt7u3e"),
    verify_certs=False
)
 
# Définir la période : les 7 derniers jours
now = datetime.utcnow()
last_week = now - timedelta(days=7)
 
# Format Elasticsearch (ISO 8601)
start_time = last_week.strftime('%Y-%m-%dT%H:%M:%S')
end_time = now.strftime('%Y-%m-%dT%H:%M:%S')
 
# Requête Elasticsearch
query = {
    "size": 10000,
    "_source": [
        "@timestamp", "src_ip", "dest_ip", "src_port", "dest_port",
        "protocol", "signature", "category", "severity", "user_agent", "message"
    ],
    "query": {
        "range": {
            "@timestamp": {
                "gte": start_time,
                "lte": end_time
            }
        }
    }
}
 
# Effectuer la requête sur les index commençant par "f"
response = es.search(index="f*", body=query)
 
# Extraire les données
data = []
for hit in response["hits"]["hits"]:
    source = hit["_source"]
    data.append({
        "timestamp": source.get("@timestamp", ""),
        "src_ip": source.get("src_ip", ""),
        "dest_ip": source.get("dest_ip", ""),
        "src_port": source.get("src_port", ""),
        "dest_port": source.get("dest_port", ""),
        "protocol": source.get("protocol", ""),
        "signature": source.get("signature", ""),
        "category": source.get("category", ""),
        "severity": source.get("severity", ""),
        "user_agent": source.get("user_agent", ""),
        "message": source.get("message", "")
    })
 
# Convertir en DataFrame et sauvegarder
df = pd.DataFrame(data)
df.to_csv("DataSet.csv", index=False)
 
print("[✔] Données extraites avec succès depuis Elasticsearch et enregistrées dans DataSet.csv")
