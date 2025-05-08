from pydantic import BaseModel

class ExtractEntitiesStep(BaseModel):
    entities: list[str]