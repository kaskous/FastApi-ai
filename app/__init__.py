from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from app.db import engine, Base, get_db
from app.routes.routes import router as task_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="File Summary API",
        description="API to process files and create summaries using ChatGPT.",
        version="1.0.0",
    )

    # Initialize the database
    Base.metadata.create_all(bind=engine)

    # Register the router
    app.include_router(task_router, prefix="/api")

    return app
