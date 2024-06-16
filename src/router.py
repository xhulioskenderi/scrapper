from fastapi import APIRouter
from src.endpoints import articles, dummy_endpoints

api_router = APIRouter()


api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(dummy_endpoints.router, prefix="/articles", tags=["articles"])
