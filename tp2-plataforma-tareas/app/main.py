from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.tareas import router as tareas_router
from app.api.stats import router as stats_router
from app.core.pool_container import worker_pool
from app.core.shutdown import (
    save_state,
    report_previous_dumps
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Se ejecuta una vez cuando arranca FastAPI.
    """

    report_previous_dumps()

    await worker_pool.start()

    yield

    print("Guardando estado...")

    await save_state()

    print("Shutdown...")


# =====================================
# Crear aplicación FastAPI
# =====================================

app = FastAPI(
    title="TP2 Plataforma Distribuida",
    lifespan=lifespan
)

# =====================================
# Registrar routers
# =====================================

app.include_router(tareas_router)
app.include_router(stats_router)


# =====================================
# Punto de entrada
# =====================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )