# app/users.py
import os
from http import HTTPStatus

import edgedb
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import api.generated_queries as qs

router = APIRouter()
client = edgedb.create_async_client(
    host=os.getenv('EDGEDB_HOST', 'localhost'),
    port=int(os.getenv('EDGEDB_PORT', 5656)),
    tls_security="insecure"
)

class RequestData(BaseModel):
    name: str


@router.get("/people")
async def get_people(
    name: str = Query(None, max_length=50)
) -> list[qs.GetPeopleResult]:
    if not name:
        return await qs.get_people(client)

    people = await qs.get_people_by_name(client, name=name)
    if not people:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Person with name {name} does not exist."},
        )
    return people

@router.get("/people/{person_id}")
async def get_people_by_id(
    person_id: int
) -> qs.GetPeopleResult:
    person = await qs.get_people_by_id(client, person_id=person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Person with id {person_id} does not exist."},
        )
    return person

@router.get("/people/{person_id}/employers")
async def get_people_by_id_employers(
    person_id: int
) -> list[qs.GetPeopleByIdEmployersResult]:
    person = await qs.get_people_by_id_employers(client, person_id=person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Person with id {person_id} does not exist."},
        )
    return person