from pydantic import BaseModel
from typing import Literal

class ThinkingTransaction(BaseModel):
    kind: Literal["ExtractEntitiesStep"]



class ExtractEntitiesStep(BaseModel):
    entities: list[str]