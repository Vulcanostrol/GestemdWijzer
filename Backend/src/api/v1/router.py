# -*- coding: utf-8 -*-
from fastapi import APIRouter

from src.api.v1.votes.router import router as votes_router

api_router = APIRouter()

api_router.include_router(votes_router, prefix="/votes", tags=["votes"])
