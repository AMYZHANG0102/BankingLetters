# Banking Letter Microservices — Final Project 2026

## Project Overview

This project is a small **microservices-based banking letter generation system** built with **Python**, **Flask**, **Docker**, and **Docker Compose**.

The system reads customer data from a shared **JSON** data source, validates each customer record, and generates personalized banking letters based on the requested letter type.

The application supports two types of letters:

1. **Welcome Letter**
   - Used for new customers
   - Does not include any credit-related information

2. **Offer Letter**
   - Used for customers receiving a financial offer
   - Supports:
     - **Credit Card** offers with a credit limit
     - **Line of Credit** offers with a credit limit

This project is implemented as **three separate Dockerized microservices**, with each team member responsible for one service.

---

## Team Members and Responsibilities

### Amy — Service 1: Validator Service
Amy implemented the validation and routing service.

Responsibilities:
- Read customer records from the JSON data source
- Validate all required fields
- Mark invalid records as `do_not_process: true`
- Save validation results and invalid-record results
- Trigger the correct downstream service using HTTP

### Nawaf — Service 2: Welcome Letter Service
Nawaf implemented the welcome letter generation service.

Responsibilities:
- Receive validated welcome-letter records from the validator service
- Open the welcome letter template
- Replace placeholders with customer data
- Generate personalized welcome letters in `.docx` format

### Hira — Service 3: Offer Letter Service
Hira implemented the offer letter generation service.

Responsibilities:
- Receive validated offer-letter records from the validator service
- Open the offer letter template
- Replace placeholders with customer data
- Generate personalized offer letters in `.docx` format

---

## Technologies Used

- Python
- Flask
- Docker
- Docker Compose
- Microsoft Word `.docx` templates
- JSON data source
- AWS Elastic Beanstalk (bonus cloud deployment)

---

## System Architecture

The system is divided into three services:

### 1. Validator Service
This is the entry point of the workflow.

It does the following:
- Reads `shared/input/customers.json`
- Validates all required fields
- Marks invalid records with:

```json
{
  "status": "invalid",
  "do_not_process": true
}
```

- Saves:
  - `shared/validated/validated_customers.json`
  - `shared/output/invalid_records.json`
- Routes valid `welcome` records to the Welcome Letter Service
- Routes valid `offer` records to the Offer Letter Service

### 2. Welcome Letter Service
This service receives valid `welcome` records and generates personalized welcome letters using the provided welcome letter template.

### 3. Offer Letter Service
This service receives valid `offer` records and generates personalized offer letters using the provided offer letter template.

---

## Triggering Mechanism

This project uses **simple HTTP calls between Docker containers**.

Why this approach was chosen:
- easy to understand
- easy to demonstrate in class
- satisfies the microservices triggering requirement
- works well for a small student group project

Workflow summary:
1. Start all services with Docker Compose
2. Trigger the validator service using `POST /process`
3. Validator checks all customer records
4. Invalid records are marked as `do_not_process`
5. Valid welcome records are sent to the Welcome Letter Service
6. Valid offer records are sent to the Offer Letter Service
7. Final letters are generated in `.docx` format

---

## Data Source

This project uses a **JSON** file as the shared data source.

Input file:

```text
shared/input/customers.json
```

The JSON file contains multiple customer records, including both valid and invalid examples for testing the validation logic.

---

## Validation Rules

The validator service checks the following required fields:

- `FIRST_NAME` is present and non-empty
- `LAST_NAME` is present and non-empty
- `ACCOUNT_NUMBER` contains **8 to 16 digits**
- `STREET_ADDRESS` is present and non-empty
- `CITY` is present and non-empty
- `POSTAL_CODE` is present and checked with a basic Canadian postal-code format
- `COUNTRY` is present and non-empty
- `LETTER_TYPE` must be either:
  - `welcome`
  - `offer`

For offer letters, the validator also checks:
- `OFFER_TYPE` must be:
  - `Credit Card`, or
  - `Line of Credit`
- `CREDIT_LIMIT` must be numeric and greater than 0

If any required field is missing or invalid, the record is marked as invalid and is not sent to the letter-generation services.

---

## Templates Used

The project uses two Word templates:

- `welcome_service/template.docx`
- `offer_service/template.docx`

Template placeholders include:

- `{{CURRENT_DATE}}`
- `{{FIRST_NAME}}`
- `{{LAST_NAME}}`
- `{{STREET_ADDRESS}}`
- `{{CITY}}`
- `{{POSTAL_CODE}}`
- `{{COUNTRY}}`
- `{{ACCOUNT_NUMBER}}`
- `{{OFFER_TYPE}}`
- `{{CREDIT_LIMIT}}`

The generator services replace these placeholders with customer data when producing the final personalized letters.

---

## Project Structure

```text
banking_letters_microservices/
├── docker-compose.yml
├── README.md
├── QUICK_RUN.md
├── shared/
│   ├── input/
│   │   └── customers.json
│   ├── output/
│   │   └── letters/
│   └── validated/
├── validator_service/        ← Amy
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── Readme.md
├── welcome_service/          ← Nawaf
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── template.docx
│   └── Readme.md
└── offer_service/            ← Hira
    ├── app.py
    ├── Dockerfile
    ├── requirements.txt
    ├── template.docx
    └── Readme.md
```

---

## Requirements

Before running the project locally, make sure you have:

- Docker Desktop installed and running
- Docker Compose available
- the provided template files in the correct folders
- the `customers.json` file in `shared/input/`

Optional for VS Code import warnings:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask requests python-docx
```

---

## How to Run the Project Locally

### 1. Open a terminal in the project root

The project root is the folder that contains `docker-compose.yml`.

### 2. Build and start the services

```powershell
docker compose up --build
```

This starts:
- `validator-service`
- `welcome-service`
- `offer-service`

### 3. Trigger the validator service

In a second terminal, run:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/process
```

Or with curl:

```bash
curl -X POST http://localhost:5000/process
```

### 4. Check the output files

After the process finishes, check:

- `shared/validated/validated_customers.json`
- `shared/output/invalid_records.json`
- `shared/output/letters/`

Expected result using the sample JSON:
- 2 welcome letters
- 3 offer letters
- 1 invalid record

---

## Health Check Routes

You can test whether each local service is running using:

- Validator Service:
  - `http://localhost:5000/health`
- Welcome Service:
  - `http://localhost:5001/health`
- Offer Service:
  - `http://localhost:5002/health`

---

## Bonus: Cloud Deployment on AWS Elastic Beanstalk

For the bonus portion of the project, the same Dockerized microservices system was deployed to **AWS Elastic Beanstalk**.

### Bonus Goal
The course bonus states that marks may be earned by **using a database or deploying the project in the cloud**. For this project, the cloud-deployment option was chosen.

### Cloud Deployment Summary
- The project was deployed to **AWS Elastic Beanstalk**
- The application remained containerized using Docker
- The **validator service** was exposed as the public cloud entrypoint
- The **welcome** and **offer** services remained internal services that were triggered by the validator service after successful validation

### Cloud Endpoints Used
Health check endpoint:

```text
GET /health
```

Process endpoint:

```text
POST /process
```

### What Was Verified in the Cloud
- the Elastic Beanstalk environment became healthy/green
- the deployed validator service responded successfully to `/health`
- the deployed workflow responded successfully to `POST /process`

This demonstrates that the project was successfully deployed to the cloud and satisfies the bonus requirement.

---

## Demo Flow for Class

A simple demo order is:

1. Explain that the project is split into 3 microservices
2. Show the project folder structure and team ownership
3. Run `docker compose up --build`
4. Show the `/health` routes working locally
5. Trigger `POST /process`
6. Open `validated_customers.json`
7. Open `invalid_records.json`
8. Open the generated `.docx` letters
9. Explain that invalid records were blocked from processing
10. Show the AWS Elastic Beanstalk environment and cloud endpoints for the bonus

---

## Submission Checklist

- [x] Three Python services
- [x] Dockerfiles for all services
- [x] Docker Compose file
- [x] Input JSON data source
- [x] Validation logic
- [x] Invalid record handling
- [x] Welcome letter generation
- [x] Offer letter generation
- [x] README with architecture and run steps
- [x] Quick run guide
- [x] Team member responsibilities documented
- [x] Cloud deployment bonus completed
- [ ] Demo video
- [ ] Final in-class demo

---

## Final Notes

This project was designed to be clear, student-friendly, and easy for a professor to review.
Each microservice is separated clearly so that team ownership is visible during marking, demonstration, and code review.

The core local version and the cloud bonus version both follow the same overall microservices workflow: validate first, block invalid records, and then generate letters only for approved customer records.
