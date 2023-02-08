# Harmonic Take Home
## Quickstart
Clone the repo as `harmonic` and then cd in.  If running locally, make sure to create a new python 3.10 virtual environment first.  After setting up, see the [Named Pipe as Message Bus](#named-pipe-as-message-bus) and [API](#api) for usage.  After some data is loaded you can check out [a walkthrough with our data](Exploration%20Cookbook.md) and the [official EdgeDB cheatsheets](https://www.edgedb.com/docs/guides/cheatsheet/index#cheatsheets).

### Docker
Run the following commands
- `docker compose up edgedb`
- (initialize database, generate UI login (make sure to swap port to 10701 when running on host)) ```
docker exec harmonic-edgedb-1 su edgedb -c "\
cd harmonic && edgedb project init --non-interactive ; \
echo harmonic | edgedb instance reset-password -I harmonic --password-from-stdin && \
edgedb instance credentials -I harmonic && \
edgedb ui -I harmonic --print-url"
```
- (loading initial data will be taken care of here) `docker compose up data_services`
- (shell into the container so we can use the API and stream data)`docker exec -it harmonic-data_services-1 /bin/bash`
- (stream the data into the pipe) `./load_data.sh`


### Local
Run the following commands:
- (make sure we are in the repo) `cd harmonic`
- (install edgedb) `curl --proto '=https' --tlsv1.2 -sSf https://sh.edgedb.com | sh` 
- (install data processing tool) `brew install jq` or `sudo apt-get install jq`
- (initialize db) `edgedb project init --non-interactive`
- (set password) `echo "harmonic" | edgedb instance reset-password -I harmonic --password-from-stdin`
- (setup environment variables) `export INGESTION_PIPE=ingestion API_PORT=5001`
- (open ui for query REPL) `edgedb ui`
- (python libraries and tooling) `pip3 install -r requirements.txt`
- (setup our named pipe for communication) `mkfifo $INGESTION_PIPE`
- Run these in seperate tabs with the above environment vars or `(&)` group chain them
  - (monitor pipe and stream in data) `python3 services/ingest.py`
  - (send inital data to pipe) `./load_data.sh`
  - (start REST API to query database) `uvicorn api.main:fast_api --port $API_PORT --reload`

## Deliverables
### Required
- Initialize knowledge graph with sample data (in `data/` dir)
- Support streaming updates (presumably from some data bus)
- Database must support a query explorer to ideate

### Optional
- Expose a REST API

## High Level Design
There are three principle components to this submission:
- The knowledge graph database
- The ingestion service (to support real-time streaming)
- The read-only API to deliver certain relationships without having to learn EdgeQL

## Considerations
### Ingestion
#### Async
In order to support streaming use cases, I went with an asynchronous approach.  Due to the following characteristics:
- single data source (a FIFO object bound to the stdin)
- minimal pre-processing of the data
- low latency of running the database locally
- a simple data model in the current knowledge graph (causing very quick updates to the model) 
the ingestion code will likely behave identically as a synchronous process.  The reason I went with async is that when the data model grows in complexity and size, all of the components will likely take longer to execute/return, which in a synchronous program would severely limit throughput.  By ensuring we are not blocking on I/O calls we can maximize throughput as the system grows.

Some downsides to this approach are: 
- asynchronous code is [notoriously difficult to reason through](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)
- _All_ I/O operations must be non-blocking or it will halt execution and severely limit the usefulness of the approach
- We may have to be careful to [ensure that we don't have backpressure](https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/#bug-1-backpressure) when database writes start taking longer

Both of these are mitigated by the fact that the responsibilities of the ingestion service are limited in scope and the design is very simple.

#### Named Pipe as Message Bus
For the purposes of this take-home, using a full event processing framework like Kafka would be overkill.  However, the application is designed to be able to support that pretty easily.  Instead of using stdin as our input, we would use a Kafka topic.  Instead of using Pydantic to do the validation, we would use Avro schemas.  We would likely use a single topic for all the different message types as we do here, and continue to route messages to the different queries to update the database correctly. 

The benefit here of using Kafka over a named pipe is message persistence, which grants us the ability to replay messages at a later time if we need to.  A named pipe is not a file (even though it looks like one due to UNIX conventions), but just an ephemeral buffer between two processes that flushes when read from.  Not having a record of inter-process communications is very risky.  Since we only have one reader process, if we wanted persistence we could just append all our messages to a log file and read from that file instead of stdin.  All we have to do from there is persist which line of the log we are currently up to date with after reading each line so we know where to pick up from if we have a crash/shutdown.  In the simplest case with a single producer and consumer that's the bulk of what Kafka does anyway.

The bus can be used as such:
`echo '{"type": "Person", "data": {"person_id":110139,"name":"Sarah R. Johnson"}} > $INGESTION_PIPE'`

The four types are `["Person", "Company", "CompanyAcquisition", "PersonEmployment"`]` and their data are formatted like the entries corresponding files in the `data/` directory.

#### Data Validation
I use Pydantic to validate the incoming messages, as well as normalize them to ensure they have the same format when inserted into the database.  The normalization is important since the way the queries are written makes all referenced keys required, even if the values are optional.  Without the normalization, we would have to have some imperative logic that dynamically includes and excludes node parameters if the keys are missing from the message.  Personally, I find that to be much messier than the declarative approach using Pydantic/dataclasses and having all keys show up even if missing from the input message.  Since the database is typed, it does offer its own data validation complete with custom value constraints that we could rely on.  However, since the message data does not replicate the database types in half of the scenarios (CompanyAcquisition and PersonEmployment), it makes sense to at least have structural validation at the ingestion level. 

### Database Choice
In order to align my decision-making process, I referenced the [existing Harmonic API documentation](https://console.harmonic.ai/docs/api-reference/introduction) to get an idea of the characteristics of our final data model.
My takeaways are that there are:
- a limited number of first-class data types (Company, People)
- fairly large amounts of properties per type
- by the nature of the type relationships, and limited depth to the common traversal scenarios I can imagine

In regards to the limited data types, since we don't have particularly heteromorphic data, we would likely benefit from a database that is typed/has a schema.  Schema-less databases are great for document storage and inconsistently structured data, but I get the impression that most of our data will be able to fit quite well into a single model.  We are likely going to want to focus on consistency when it comes to our data.  Both document stores (DynamoDB, MongoDB, CouchBases), and graph databases (Neo4J, ArangoDB, AWS Neptune) generally push schema adherence to the application layer.  

For applications where the data is the product and not a byproduct, I think that enforcing schema adherence (through strong typing) at the database layer is beneficial.  If the functionality that promises data characteristics falls out of sync with the data, it no longer is a promise.  What happens when we change a data constraint but forget to apply it to all existing data with a migration?  For the same reason why we want documentation to colocate with our code, we want validation to colocate with the data. Since we have fairly wide properties, we want to make sure that we have an expressive schema and constraint system.  Postgres is best in class in this regard and has a [wonderful DDL-level constraint system via `CHECK` constraints](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS) that can call user-defined functions to automatically validate all insertions and updates. 

However, since we are dealing with a graph, and may want to traverse among and between data types many times over, using a SQL-based system can get pretty cumbersome.  In general, the performance of a graph database will always win out here, since they store direct references to the node they connect to, whereas a relational database has to seek through indexes to find the result.  However, for a limited-scale dataset like this, I would argue that the more compelling reason to be wary of SQL syntax is ergonomics.  Traversing through a table over and over with joins becomes tedious and confusing very quickly.  Using a database option like EdgeDB with its Graph-Relational hybrid approach to query syntax (with its EdgeQL) that is still built on Postgres as an underlying engine appears to give us the best of both worlds.  [Throughput in a real-world scenario](https://github.com/edgedb/imdbench#raw-sql-full-report) is not far off from the best raw SQL python async driver. 

The benefits of EdgeDB match most of our criteria:
- strong typing (schema enforcement)
- expressive constraints
- concise medium-depth (3-4 level) traversals

The downsides are that while its underlying data storage and query processor is postgres, it's only been in development for a few years and thus does not have the same breadth of features.  Object level security was only added 6 months ago, and is a requirement if the database needs to be frontend facing.  Additionally, it's largely OLTP (transactional) focused at the moment, only recently did they add OLAP (analytical) functionality like grouped aggregations. 

### API
The API is designed to be customer-facing and thus only has GET endpoints.  I saw that the Harmonic API has POST endpoints to support client data enrichment, and I assumed that this would be a different database entirely from the knowledge graph.  EdgeDB does support GrapthQL querying through a native web-facing API, but I chose to spin up an API myself to demonstrate a common workflow that could happen with this data.

With the information provided, I imagine the primary benefit of querying Person and Company objects is the relationship between them.  This is what I focused the API design around.  Either starting from a Company and working towards its employees or starting from a Person and working towards their employers.

Currently, the API would be used like
```
/people -> get all people
/people?name={name} -> search through names case insensitively

/people/{person_id} -> a single Person

/people/{person_id}/employers -> Company details with the "link properties" for that Person.
```

And likewise, the same workflow is for Company objects.
```
/companies
/companies?name=name
/companies/{company_id}
/companies/{company_id}/employees
```

The API can be queried like `httpx -m GET "http://127.0.0.1:5001/companies?name=Microsoft"` when running it locally or when shelled into the services container.

To keep the code at MVP level, the API does not have a default limit or pagination, something any production-facing API would need.

### Exploration
Further exploration can be done on more complicated queries using the REPL interface of the EdgeDB web UI.  I have a few examples in the Exploration Cookbook to act as a jumpstart for how to use EdgeQL.  The basics can be learned in the [Official Tutorial](https://www.edgedb.com/tutorial).  

The UI also provides a useful data explorer, although due to the way that Link Properties (data about the connection between two nodes) are implemented, they don't show up in the explorer, and must be manually queried.