import os
from supabase import create_client, Client
print(os.environ)
url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_SERVICE_KEY"]


supabase: Client = create_client(url, key)

