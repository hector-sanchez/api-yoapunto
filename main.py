from fastapi import FastAPI
from app.api.v1.api import api_router
from database import engine, Base
# Import models to register them with Base
from app.models import club

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="YoApunto API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to YoApunto API"}

# Include API routes
app.include_router(api_router, prefix="/api/v1")
