from fastapi import APIRouter

from src.api.v1.endpoints.archive import router as archive_router
from src.api.v1.endpoints.file import router as file_router
from src.api.v1.endpoints.article import router as article_router
from src.api.v1.endpoints.category import router as category_router
from src.api.v1.endpoints.client import router as client_router
from src.api.v1.endpoints.collect import router as collect_router
from src.api.v1.endpoints.comment import router as comment_router
from src.api.v1.endpoints.dashboard import router as dashboard_router
from src.api.v1.endpoints.friend_link import router as friend_link_router
from src.api.v1.endpoints.like import router as like_router
from src.api.v1.endpoints.message import router as message_router
from src.api.v1.endpoints.tag import router as tag_router
from src.api.v1.endpoints.site import router as site_router
from src.api.v1.endpoints.user import router as user_router

api_v1_router = APIRouter()

api_v1_router.include_router(user_router)
api_v1_router.include_router(article_router)
api_v1_router.include_router(category_router)
api_v1_router.include_router(tag_router)
api_v1_router.include_router(comment_router)
api_v1_router.include_router(like_router)
api_v1_router.include_router(collect_router)
api_v1_router.include_router(message_router)
api_v1_router.include_router(friend_link_router)
api_v1_router.include_router(archive_router)
api_v1_router.include_router(client_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(file_router)
api_v1_router.include_router(site_router)
