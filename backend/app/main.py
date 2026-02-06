"""FastAPI application entry for ConceptPilot."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import MongoDB
from app.api.v1.api import api_router

app = FastAPI(title="ConceptPilot API")

# Simple CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """Connect to MongoDB on startup."""
    await MongoDB.connect_db()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Close MongoDB connection on shutdown."""
    await MongoDB.close_db()


@app.get("/", tags=["root"])
async def root() -> dict:
    return {"status": "ok", "service": "ConceptPilot API"}


# Include API routers
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
