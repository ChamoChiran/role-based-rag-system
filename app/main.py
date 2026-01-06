from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, rag

app = FastAPI(
    title="Role-Based RAG API",
    description="Role-based Retrieval-Augmented Generation backend",
    version="0.1.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(rag.router)

@app.get("/")
def root():
    return {"message": "API is running"}
