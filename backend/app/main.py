import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logger import logger
from backend.app.api.routes import router as api_router
from backend.app.workers.scanner_worker import scanner_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Launch scanner background worker
    logger.info("Initializing PULSAR AI V2.0 System...")
    worker_task = asyncio.create_task(scanner_worker.start())
    yield
    # Shutdown: Stop scanner background worker
    logger.info("Shutting down PULSAR AI V2.0 System...")
    scanner_worker.stop()
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Quantitative Crypto Futures Analysis and ICT/SMC Signal Platform",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in cloud for easy Vercel frontend connection
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "project": "PULSAR AI V2.0",
        "description": "ICT/SMC Quantitative Crypto Trading Platform",
        "status": "ONLINE",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": str(exc)}
    )
