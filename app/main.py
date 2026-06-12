from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import categories, products, customers, orders, health
from app.repositories import init_dummy_data
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.exceptions.handlers import setup_exception_handlers
from app.middleware import logging_middleware

# Setup logging and exception handlers
setup_logging()
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="A Proof of Concept for a scalable e-commerce backend.",
)
setup_exception_handlers(app)

# CORS — allow the Vite dev server and any explicitly configured frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware
app.middleware("http")(logging_middleware)


@app.on_event("startup")
def on_startup():
    """
    Initialize dummy data when the application starts.
    """
    init_dummy_data()


# Include the v1 routers
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix=settings.API_V1_STR)
app.include_router(customers.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(health.router)


@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}
