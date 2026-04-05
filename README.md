# Banking Letter Microservices — Final Project 2026

## Project Overview

This project is a small microservices-based banking letter generation system built with **Python**, **Flask**, **Docker**, and **Docker Compose**.

The system reads customer data from a shared JSON file, validates the records, and generates personalized banking letters based on the customer's letter type.

The project supports two kinds of letters:

1. **Welcome Letter**
   - Used for new customers
   - Does not include credit-related information

2. **Offer Letter**
   - Used for customers receiving a financial offer
   - Supports:
     - **Credit Card** offer with a credit limit
     - **Line of Credit** offer with a credit limit

This project is designed as **three separate microservices**, with each team member responsible for one service.

---

## Team Members and Responsibilities

### Amy — Service 1: Validator Service
Amy implemented the validation service.

Responsibilities:
- Reads customer records from the JSON data source
- Validates all required fields
- Marks invalid records as `do_not_process: true`
- Saves validation results to output files
- Triggers the correct downstream service using HTTP

### Nawaf — Service 2: Welcome Letter Service
Nawaf implemented the welcome letter service.

Responsibilities:
- Receives validated welcome-letter records from the validator service
- Opens the welcome letter template
- Replaces placeholders with customer data
- Generates personalized welcome letters in `.docx` format

### Hira — Service 3: Offer Letter Service
Hira implemented the offer letter service.

Responsibilities:
- Receives validated offer-letter records from the validator service
- Opens the offer letter template
- Replaces placeholders with customer data
- Generates personalized offer letters in `.docx` format

---

## How the Application Works

### Step 1 — Validator Service
The validator service is the entry point of the workflow.

It does the following:
- Reads `shared/input/customers.json`
- Checks whether each required field is present and valid
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
- Sends valid welcome records to the Welcome Letter Service
- Sends valid offer records to the Offer Letter Service

### Step 2 — Welcome Letter Service
The welcome service receives valid `welcome` records from the validator service and generates personalized welcome letters from the provided Word template.

### Step 3 — Offer Letter Service
The offer service receives valid `offer` records from the validator service and generates personalized offer letters from the provided Word template.

---

## Triggering Mechanism

This project uses **simple HTTP calls between Docker containers**.

Why this approach was chosen:
- easy to understand
- easy to demonstrate in class
- satisfies the microservices triggering requirement
- works well for a small student group project

Workflow summary:
1. Start all containers with Docker Compose
2. Trigger the validator service using `POST /process`
3. Validator checks all customer records
4. Validator marks invalid records so they are not processed
5. Validator sends valid records to the correct generator service
6. Generator services create the final letters

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

---

## Templates Used

The project uses two Word templates:

- `welcome_service/template.docx`
- `offer_service/template.docx`

The templates use placeholders such as:

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

The welcome and offer services replace these placeholders with customer data when generating letters.

---

## Project Structure

```text
banking_letters_microservices/
│
├── docker-compose.yml
├── README.md
├── QUICK_RUN.md
├── shared/
│   ├── input/
│   │   └── customers.json
│   ├── validated/
│   └── output/
│       └── letters/
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

Before running the project, make sure you have:

- **Docker Desktop** installed and running
- **Docker Compose** available
- the provided template files placed in the correct folders
- the `customers.json` file in `shared/input/`

If you want VS Code to stop showing missing import warnings for `flask`, `requests`, or `docx`, create a local Python virtual environment and install the packages locally as well:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask requests python-docx
```

---

## How to Run the Project

### 1. Open a terminal in the project root

The project root is the folder that contains `docker-compose.yml`.

### 2. Build and start the services

```powershell
docker compose up --build
```

This starts:
- `validator-service` on port `5000`
- `welcome-service` on port `5001`
- `offer-service` on port `5002`

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

After the process finishes, check these locations:

- `shared/validated/validated_customers.json`
- `shared/output/invalid_records.json`
- `shared/output/letters/`

Expected result using the sample JSON:
- 2 welcome letters
- 3 offer letters
- 1 invalid record

---

## Health Check Routes

You can test whether each service is running with these URLs:

- Validator Service:
  - `http://localhost:5000/health`
- Welcome Service:
  - `http://localhost:5001/health`
- Offer Service:
  - `http://localhost:5002/health`

---

## Demo Flow for Class

A simple demo order would be:

1. Explain that the project is split into 3 services
2. Show the folder structure and team ownership
3. Run `docker compose up --build`
4. Show the `/health` routes working
5. Trigger `POST /process`
6. Open `validated_customers.json`
7. Open `invalid_records.json`
8. Open the generated `.docx` letters
9. Explain that invalid records were safely blocked from processing

---

## AWS Bonus Idea

The easiest cloud bonus path is to deploy the same Dockerized project to **AWS Elastic Beanstalk** or to a more advanced stack like **Amazon ECS Fargate + ECR**.

For this project, Elastic Beanstalk is the simplest bonus option because the application is already containerized and uses Docker Compose locally.

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
- [ ] Demo video
- [ ] Final in-class demo

---

## Final Notes

This project was written to be clear, student-friendly, and easy for a professor to review.
Each service is kept separate so that team ownership is easy to understand during marking and demonstration.
