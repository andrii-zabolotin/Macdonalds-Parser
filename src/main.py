from fastapi import FastAPI

from src.api.products import router as product_router

app = FastAPI(
    title="Macdonalds parser"
)

app.include_router(product_router)
