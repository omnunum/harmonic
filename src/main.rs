use tokio;
use tokio::fs::File;
use tokio::io::AsyncBufReadExt;

use chrono::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
struct Person {
    person_id: i32,
    name: String,
}

#[derive(Debug, Deserialize, Serialize)]
struct CompanyAcquisition {
    parent_company_id: i32,
    acquired_company_id: i32,
    merged_into_parent_company: bool,
}

#[derive(Debug, Deserialize, Serialize)]
struct PersonEmployment {
    company_id: i32,
    person_id: i32,
    employment_title: String,
    start_date: Option<DateTime<Utc>>,
    end_date: Option<DateTime<Utc>>,
}

#[derive(Debug, Deserialize, Serialize)]
struct Company {
    company_id: i32,
    company_name: String,
    headcount: Option<i32>,
}

#[derive(Debug, Deserialize, Serialize)]
enum MessageData {
    Person(Person),
    Company(Company),
    CompanyAcquisition(CompanyAcquisition),
    PersonEmployment(PersonEmployment),
}

#[derive(Debug, Deserialize, Serialize)]
struct Message {
    #[serde(rename = "type")]
    type_: String,
    data: MessageData,
}

async fn open_pipe(pipe_path: String) -> Result<tokio::io::BufReader<File>, Box<dyn std::error::Error>> {
    let file = File::open(pipe_path).await?;
    let reader = tokio::io::BufReader::new(file);
    Ok(reader)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let conn = edgedb_tokio::create_client().await?;
    let pipe_path = std::env::args().nth(1).unwrap_or("/dev/stdin".to_string());
    let mut reader = open_pipe(pipe_path.clone()).await?;
    let mut line = String::new();

    loop {
        match reader.read_line(&mut line).await {
            Ok(0) => {
                // Connection closed, reconnect
                reader = open_pipe(pipe_path.clone()).await?;
                continue;
            }
            Ok(_) => {
                if line.trim().is_empty() {
                    // Message is empty, reconnect
                    reader = open_pipe(pipe_path.clone()).await?;
                    continue;
                }
                println!("Received message: {}", line);
            }
            Err(e) => {
                eprintln!("Error while reading from the pipe: {}", e);
                break;
            }
        }
    }

    Ok(())
}
