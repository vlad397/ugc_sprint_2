from fastapi import APIRouter

from .bookmarks import router as bookmarks_router
from .film_timestamp import router as film_timestamp_router
from .like import router as like_router
from .review import router as review_router

router = APIRouter(prefix="/v1")
router.include_router(bookmarks_router)
router.include_router(like_router)
router.include_router(film_timestamp_router)
router.include_router(review_router)
