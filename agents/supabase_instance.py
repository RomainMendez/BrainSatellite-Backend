import os
from supabase import create_client, Client

import logging
logger = logging.getLogger(__file__)

if "SUPABASE_URL" not in os.environ or "SUPABASE_SERVICE_KEY" not in os.environ:
    logger.warning("Failed to set up a Supabase connection, not all API calls will work !")
    supabase: Client|None = None
else:
    url: str = os.environ["SUPABASE_URL"]
    key: str = os.environ["SUPABASE_SERVICE_KEY"]
    supabase: Client|None = create_client(url, key)

def get_supabase() -> Client:
    if supabase != None:
        return supabase
    else:
        logger.error("Failed to retrieve a Supabase instance !")
        return None

