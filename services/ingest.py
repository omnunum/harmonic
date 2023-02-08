import asyncio
import json
import sys
import os

from datetime import datetime

import edgedb
from aiologger import Logger
from pydantic import BaseModel

logger = Logger.with_default_handlers(name='harmonic')

# Pydantic models for validation and sanitization.
# This also allows us to have optional fields that are missing from the JSON
#   and have them be set to None in the database without having to make multiple
#   queries options (complicated) or dynamically create them (less readable).
class Person(BaseModel):
    person_id: int
    name: str


class CompanyAcquisition(BaseModel):
    parent_company_id: int
    acquired_company_id: int
    merged_into_parent_company: bool


class PersonEmployment(BaseModel):
    company_id: int
    person_id: int
    employment_title: str
    start_date: datetime = None
    end_date: datetime = None


class Company(BaseModel):
    company_id: int
    company_name: str
    headcount: int = None

# We don't need to use the model generator for this like we do in the API
#   because we don't need to return the data to the client.  It might be
#   a good idea down the line to use the model generator for this as well
#   to keep the data models consistent and together in one place.
QUERIES = {
    "Person": """
        insert Person {
            person_id := <int32>$person_id,
            name := <str>$name
        };
    """, "Company": """
        insert Company {
            company_id := <int32>$company_id,
            name := <str>$company_name,
            headcount := <optional int32>$headcount
        };
    """, "CompanyAcquisition": """
        update Company 
        filter .company_id = <int32>$acquired_company_id
        set {
            acquired_by := (
                select detached Company 
                filter .company_id = <int32>$parent_company_id
            ),
            merged_into_parent_company := <bool>$merged_into_parent_company
        };
    """, "PersonEmployment": """
        update Company 
        filter .company_id = <int32>$company_id
        set {
            employees += (
                select Person
                filter .person_id = <int32>$person_id
            ) {
                @employment_title := <str>$employment_title,
                @start_date := <optional cal::local_datetime>$start_date,
                @end_date := <optional cal::local_datetime>$end_date
            }
        };
    """
}

# Referenced from https://stackoverflow.com/a/64317899
async def connect_stdin_stdout(loop: asyncio.AbstractEventLoop):
    """Connect async streams to stdin/stdout so we can use them without blocking."""
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(
        lambda: protocol, open(os.environ["INGESTION_PIPE"], "r")
    )
    return reader


def validate_record(record_type: str, record: dict):
    """Validate and sanitize the record based on the record type."""
    if record_type == "Person":
        return Person(**record)
    elif record_type == "Company":
        return Company(**record)
    elif record_type == "CompanyAcquisition":
        return CompanyAcquisition(**record)
    elif record_type == "PersonEmployment":
        return PersonEmployment(**record)
    else:
        raise ValueError(f"Invalid record type: {record_type}")


async def insert_record(client: edgedb.Client, message: str):
    """Parse the message based on type and insert the record into the database."""
    deserialized = json.loads(message)
    record_type, record = deserialized['type'], deserialized['data']
    # For loop is used to auto retry on transaction failure (helps with transient errors)
    async for tx in client.transaction():
        async with tx:
            if record_type not in QUERIES:
                await logger.error(f"No query exists for record type: {record_type}")
                return
            try:
                record = validate_record(record_type, record)
                await client.execute(QUERIES[record_type], **record.dict())
                await logger.debug(f"Updated database with record: {record}")
            # Since we're running a live service we want to log errors and continue
            except edgedb.errors.EdgeDBError as e:
                await logger.exception(f"Error inserting record: {e} {record}")
            except ValueError as e:
                await logger.exception(f"Error validating record: {e} {record}")


async def main():
    """Main control flow for the ingest service. We want to keep the service 
    running indefinitely, continuously read from the named pipe, and insert
    records into the database whenever there is a new message to process."""
    loop = asyncio.get_event_loop()
    await logger.debug("Opening connection")

    client = edgedb.create_async_client(
        host=os.getenv('EDGEDB_HOST', 'localhost'),
        port=os.getenv('EDGEDB_PORT', 5656),
        tls_security="insecure"
    )
    # Whenever the writer on the named pipe closes, we'll get an empty message
    #   and need to reopen the reader in order to have the reader block correctly.
    try:
        while True:
            reader = await connect_stdin_stdout(loop)
            while True:
                await logger.debug("Awaiting message...")
                message = await reader.readline()
                if not message:
                    await logger.warning("Empty message received, reopening reader...")
                    break
                await logger.debug(f"Received message: {message}")
                await insert_record(client, message)
    # Simplest way to handle SIGINT and gracefully exit
    except KeyboardInterrupt:
        pass
    finally:
        await logger.debug("Closing connection")
        await asyncio.wait_for(client.aclose(), timeout=5)
        await logger.debug("Closed connection and exiting")
    loop.close()


if __name__ == "__main__":
    asyncio.run(main())
