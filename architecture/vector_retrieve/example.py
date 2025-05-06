import requests

from supabase import create_client, Client
import psycopg2
from datetime import datetime

EMBEDDINGS_API_SERVER_FQDN = "http://192.168.0.185:10000"


def get_embeddings(prompt: str, fqdn=EMBEDDINGS_API_SERVER_FQDN) -> list[float]:
    response = requests.post(f"{fqdn}/v1/get_embeddings", json={"queries": [prompt]})
    return response.json()["vectors"][0]


def process_prompt_for_memory(supabase_client: Client, prompt_id: str):
    response = (
        supabase_client.table("promptMemory").select("*").eq("id", prompt_id).execute()
    )
    data_as_dict = response.data[0]
    prompt: str = data_as_dict["prompt"]
    embeddings: list[float] = get_embeddings(prompt)
    data_as_dict["embeddings"] = embeddings
    supabase_client.table("promptMemory").update(data_as_dict).eq(
        "id", prompt_id
    ).execute()


SQL_QUERY_TEMPLATE = """
SELECT agent, content, version, created_at
FROM \"promptMemory\" 
WHERE user_id=%s 
AND agent LIKE %s
AND version LIKE %s
ORDER BY embeddings <-> %s::vector 
LIMIT 10
"""
def query_memory(connection_string: str, prompt: str, user_id: str, agent:str = "%", version: str = "%") -> list[tuple[str, dict, str, datetime]]:
    """Queries PostgresSQL for the nearest neighbor of a given prompt, for a given user."""
    embeddings: list[float] = get_embeddings(prompt)
    postgres_connection = psycopg2.connect(connection_string)
    cur = postgres_connection.cursor()
    
    cur.execute(SQL_QUERY_TEMPLATE, (user_id, agent, version, embeddings,))
    result = cur.fetchall()

    cur.close()
    postgres_connection.close()

    return result