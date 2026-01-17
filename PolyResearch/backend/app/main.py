"""
PolyResearch Backend - FastAPI Application
Provides insights into Polymarket data
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="PolyResearch API",
    description="API for Polymarket insights and analytics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PolyResearch API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
