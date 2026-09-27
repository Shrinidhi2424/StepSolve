from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router

app = FastAPI(
    title="StepSolve API",
    description="Multi-topic numerical methods calculator backend with step-by-step textbook derivations.",
    version="1.0.0",
)

# Configure CORS for local Next.js frontend (default port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Welcome to StepSolve API",
        "docs": "/docs",
        "topics_endpoint": "/api/topics",
    }
