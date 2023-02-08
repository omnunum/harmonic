# app/users.py
from __future__ import annotations

from http import HTTPStatus
import os

import edgedb
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import api.generated_queries as qs

router = APIRouter()
client = edgedb.create_async_client(
    host=os.getenv('EDGEDB_HOST', 'localhost'),
    tls_security="insecure"
)


class RequestData(BaseModel):
    name: str


@router.get("/companies")
async def get_companies(
    name: str = Query(None, max_length=50)
) -> list[qs.GetCompaniesResult]:
    if not name:
        return await qs.get_companies(client)

    companies = await qs.get_companies_by_name(client, name=name)
    if not companies:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Company with name {name} does not exist."},
        )
    return companies

@router.get("/companies/{company_id}")
async def get_companies_by_id(
    company_id: int
) -> qs.GetCompaniesResult:
    company = await qs.get_companies_by_id(client, company_id=company_id)
    if not company:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Company with id {company_id} does not exist."},
        )
    return company

@router.get("/companies/{company_id}/employees")
async def get_companies_by_id_employees(
    company_id: int
) -> list[qs.GetCompaniesByIdEmployeesResult]:
        company = await qs.get_companies_by_id_employees(client, company_id=company_id)
        if not company:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail={"error": f"Company with id {company_id} does not exist."},
            )
        return company