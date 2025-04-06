from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.endpoints.chats import router as chat_router
from app.endpoints.users import router as user_router
from fastapi.middleware.cors import CORSMiddleware
import logging

# Initialize FastAPI app
app = FastAPI()

# Register the router
app.include_router(chat_router, prefix="/api", tags=["chats"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on app startup
@app.on_event("startup")
async def startup():
    logger.info("Starting up and initializing database...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize the database: {e}")

# Dispose of the database engine on app shutdown
@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down and disposing of database engine...")
    await engine.dispose()

# Healthcheck endpoint for verifying database connectivity
@app.get("/healthcheck")
async def healthcheck():
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Include routers
app.include_router(chat_router, prefix="/api")
app.include_router(user_router, prefix="/api")
