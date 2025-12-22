from fastapi import FastAPI
from recycle.app.routes import health

app = FastAPI(
    title="Rag Based Assistant",
    version="0.1.0",
    docs_url="/docs",
)

app.include_router(health.router, prefix="/health", tags=["Health"])
