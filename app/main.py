"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_exception_handlers
from app.api.routes import health_router, task_lists_router, tasks_router, users_router
from app.config import settings


def create_app() -> FastAPI:
    """Create FastAPI application."""
    # Initialize FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="A clean architecture Task Management API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        debug=settings.DEBUG,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Include routers
    app.include_router(
        health_router,
        prefix=settings.API_V1_STR,
    )
    app.include_router(
        users_router,
        prefix=settings.API_V1_STR,
    )
    app.include_router(
        task_lists_router,
        prefix=settings.API_V1_STR,
    )
    app.include_router(
        tasks_router,
        prefix=settings.API_V1_STR,
    )

    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Welcome to PyTasks API",
            "docs": "/docs",
            "version": "0.1.0",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
