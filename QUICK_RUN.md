# Quick Run Guide

This file is the **fastest way to run the project**.

## 1) Open a terminal in the project root
The project root is the folder that contains:

- `docker-compose.yml`
- `validator_service/`
- `welcome_service/`
- `offer_service/`
- `shared/`

## 2) Start Docker Desktop
Make sure Docker Desktop is running before you continue.

## 3) Build and start the containers
Run:

```powershell
docker compose up --build
```

Wait until all 3 services are running.

You should see containers for:

- `validator-service`
- `welcome-service`
- `offer-service`

## 4) Trigger the validator service
Open a **second terminal** in the same project root and run:

### PowerShell
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/process
```

### Or curl
```bash
curl -X POST http://localhost:5000/process
```

## 5) Check the generated files
After the trigger runs, check these folders:

### Validated output
```text
shared/validated/validated_customers.json
```

### Invalid records
```text
shared/output/invalid_records.json
```

### Generated letters
```text
shared/output/letters/
```

## 6) Expected result with the sample JSON
You should get:

- **2 welcome letters**
- **3 offer letters**
- **1 invalid customer record**

## 7) Stop the application
In the terminal where Docker is running, press:

```text
Ctrl + C
```

Then run:

```powershell
docker compose down
```

---

# Quick Health Check Commands

## Check validator service
```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:5000/health
```

## Check welcome service
```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:5001/health
```

## Check offer service
```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:5002/health
```

---

# Common Problems

## Problem: `Import "flask" could not be resolved` or `Import "docx" could not be resolved`
That is usually a **VS Code interpreter issue**, not a project-code issue.

If you want to fix local editor warnings, run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install flask requests python-docx
```

Then in VS Code:

- Press `Ctrl + Shift + P`
- Select `Python: Select Interpreter`
- Choose `.venv`

## Problem: Docker command not working
Make sure Docker Desktop is installed and running.

## Problem: No letters generated
Check:

- `shared/input/customers.json` exists
- `welcome_service/template.docx` exists
- `offer_service/template.docx` exists
- all containers started successfully

---

# Demo Order
If you need a very quick demo flow, use this order:

1. Show the project folders
2. Run `docker compose up --build`
3. Trigger `POST http://localhost:5000/process`
4. Show `validated_customers.json`
5. Show `invalid_records.json`
6. Show generated letters in `shared/output/letters/`
7. Explain that the validator service triggered the welcome and offer services using HTTP between containers
