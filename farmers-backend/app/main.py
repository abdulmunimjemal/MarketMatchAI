from fastapi import FastAPI
from app.routes import farmers, search
from app.utils.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Farmer Profiling System",
    description="MVP for voice-first farmer profiling and hybrid search",
    version="0.1.0"
)

app.include_router(farmers.router, prefix="/api/v1/farmers", tags=["farmers"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])