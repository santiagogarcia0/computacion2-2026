from pydantic import BaseModel, Field
from typing import List, Optional


# ==========================
# REQUESTS
# ==========================

class DownloadTaskRequest(BaseModel):
    urls: List[str]


class HashTaskRequest(BaseModel):
    text: str
    iterations: int


class WaitTaskRequest(BaseModel):
    seconds: int


class TaskCreateRequest(BaseModel):
    """
    Request genérico.

    type:
        descargar
        hashear
        esperar
    """

    type: str

    payload: dict

    timeout: Optional[int] = 60


# ==========================
# RESPONSES
# ==========================

class TaskResponse(BaseModel):
    id: str
    status: str