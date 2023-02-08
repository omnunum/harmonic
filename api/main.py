# app/main.py
from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import companies, people

fast_api = FastAPI()

# Set all CORS enabled origins.
fast_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


fast_api.include_router(companies.router)
fast_api.include_router(people.router)