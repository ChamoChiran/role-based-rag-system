from fastapi import FastAPI
from app.routers import health, rag

app = FastAPI(
    title="Role-Based RAG API",
    description="Role-based Retrieval-Augmented Generation backend",
    version="0.1.0",
    docs_url="/docs",
)

# Register routers
app.include_router(health.router)
app.include_router(rag.router)

@app.get("/")
def root():
    return {"message": "API is running"}
