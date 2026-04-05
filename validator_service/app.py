"""
Service 1: Data Validation Service
Owner: Amy

Purpose:
- Read customer records from the JSON data source
- Validate the required fields
- Mark invalid records as do_not_process
- Trigger the Welcome Letter Service or Offer Letter Service
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, jsonify

app = Flask(__name__)

# File locations inside the Docker container
DATA_FILE = Path(os.getenv("DATA_FILE", "/app/shared/input/customers.json"))
VALIDATED_FILE = Path(os.getenv("VALIDATED_FILE", "/app/shared/validated/validated_customers.json"))
INVALID_FILE = Path(os.getenv("INVALID_FILE", "/app/shared/output/invalid_records.json"))

# URLs for the next services
WELCOME_SERVICE_URL = os.getenv("WELCOME_SERVICE_URL", "http://welcome-service:5001/generate")
OFFER_SERVICE_URL = os.getenv("OFFER_SERVICE_URL", "http://offer-service:5002/generate")
PORT = int(os.getenv("PORT", "5000"))

# Basic validation rules
ACCOUNT_NUMBER_PATTERN = re.compile(r"^\d{8,16}$")
POSTAL_CODE_PATTERN = re.compile(r"^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$")
VALID_LETTER_TYPES = {"welcome", "offer"}
VALID_OFFER_TYPES = {"Credit Card", "Line of Credit"}


def clean_text(value):
    """Convert a value to a trimmed string."""
    if value is None:
        return ""
    return str(value).strip()


def load_customers():
    """Load customer records from the shared JSON file."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {DATA_FILE}")

    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if isinstance(data, dict):
        customers = data.get('customers', [])
    elif isinstance(data, list):
        customers = data
    else:
        raise ValueError("Input JSON must be a list or an object with a 'customers' list.")

    return customers


def validate_record(record):
    """Validate one customer record and return the updated record."""
    cleaned = {}
    for key, value in record.items():
        cleaned[key] = clean_text(value)

    errors = []

    # Step 1: Read the important fields
    first_name = cleaned.get('FIRST_NAME', '')
    last_name = cleaned.get('LAST_NAME', '')
    street_address = cleaned.get('STREET_ADDRESS', '')
    city = cleaned.get('CITY', '')
    postal_code = cleaned.get('POSTAL_CODE', '')
    country = cleaned.get('COUNTRY', '')
    account_number = cleaned.get('ACCOUNT_NUMBER', '')
    letter_type = cleaned.get('LETTER_TYPE', '').lower()
    offer_type = cleaned.get('OFFER_TYPE', '')
    credit_limit = cleaned.get('CREDIT_LIMIT', '')

    # Step 2: Check the required fields
    if first_name == '':
        errors.append('FIRST_NAME is missing or empty.')
    if last_name == '':
        errors.append('LAST_NAME is missing or empty.')
    if street_address == '':
        errors.append('STREET_ADDRESS is missing or empty.')
    if city == '':
        errors.append('CITY is missing or empty.')
    if postal_code == '':
        errors.append('POSTAL_CODE is missing or empty.')
    elif not POSTAL_CODE_PATTERN.match(postal_code):
        errors.append('POSTAL_CODE format is invalid.')
    if country == '':
        errors.append('COUNTRY is missing or empty.')
    if account_number == '':
        errors.append('ACCOUNT_NUMBER is missing or empty.')
    elif not ACCOUNT_NUMBER_PATTERN.match(account_number):
        errors.append('ACCOUNT_NUMBER must contain 8 to 16 digits.')
    if letter_type not in VALID_LETTER_TYPES:
        errors.append("LETTER_TYPE must be 'welcome' or 'offer'.")

    # Step 3: Extra checks for offer letters only
    if letter_type == 'offer':
        if offer_type not in VALID_OFFER_TYPES:
            errors.append("OFFER_TYPE must be 'Credit Card' or 'Line of Credit'.")

        try:
            if float(credit_limit) <= 0:
                errors.append('CREDIT_LIMIT must be greater than 0.')
        except ValueError:
            errors.append('CREDIT_LIMIT must be numeric.')

    # Step 4: Add system fields used by the next services
    cleaned['LETTER_TYPE'] = letter_type
    cleaned['CURRENT_DATE'] = datetime.now().strftime('%B %d, %Y')
    cleaned['validated_at'] = datetime.now().isoformat(timespec='seconds')

    # Step 5: Mark valid or invalid
    if errors:
        cleaned['status'] = 'invalid'
        cleaned['do_not_process'] = True
        cleaned['errors'] = errors
        cleaned['route_to'] = None
    else:
        cleaned['status'] = 'validated'
        cleaned['do_not_process'] = False
        cleaned['errors'] = []
        if letter_type == 'welcome':
            cleaned['route_to'] = 'welcome-service'
        else:
            cleaned['route_to'] = 'offer-service'

    return cleaned


def save_json(path, payload):
    """Save JSON output to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(payload, file, indent=2)


def send_records(service_url, service_name, records):
    """Send valid records to the next service using HTTP."""
    if not records:
        return {
            'service': service_name,
            'triggered': False,
            'reason': 'No validated records for this service.'
        }

    try:
        response = requests.post(service_url, json={'records': records}, timeout=30)
        response.raise_for_status()
        return {
            'service': service_name,
            'triggered': True,
            'status_code': response.status_code,
            'response': response.json()
        }
    except requests.RequestException as error:
        return {
            'service': service_name,
            'triggered': False,
            'error': str(error)
        }


def process_customers():
    """Main workflow for Service 1."""
    # Step 1: Read customer records from the JSON file
    customers = load_customers()

    # Step 2: Validate all records
    validated_customers = []
    for customer in customers:
        validated_customers.append(validate_record(customer))

    # Step 3: Separate the records
    invalid_records = []
    welcome_records = []
    offer_records = []

    for customer in validated_customers:
        if customer['status'] == 'invalid':
            invalid_records.append(customer)
        elif customer['LETTER_TYPE'] == 'welcome':
            welcome_records.append(customer)
        elif customer['LETTER_TYPE'] == 'offer':
            offer_records.append(customer)

    # Step 4: Save validation files
    save_json(
        VALIDATED_FILE,
        {
            'processed_at': datetime.now().isoformat(timespec='seconds'),
            'total_records': len(validated_customers),
            'customers': validated_customers
        }
    )

    save_json(
        INVALID_FILE,
        {
            'processed_at': datetime.now().isoformat(timespec='seconds'),
            'invalid_count': len(invalid_records),
            'invalid_records': invalid_records
        }
    )

    # Step 5: Trigger the next services
    welcome_result = send_records(WELCOME_SERVICE_URL, 'welcome-service', welcome_records)
    offer_result = send_records(OFFER_SERVICE_URL, 'offer-service', offer_records)

    # Step 6: Return a summary
    return {
        'message': 'Validation completed successfully.',
        'summary': {
            'total_records': len(validated_customers),
            'validated_welcome_records': len(welcome_records),
            'validated_offer_records': len(offer_records),
            'invalid_records': len(invalid_records)
        },
        'validated_file': str(VALIDATED_FILE),
        'invalid_file': str(INVALID_FILE),
        'welcome_trigger': welcome_result,
        'offer_trigger': offer_result
    }


@app.get('/health')
def health():
    """Simple health check route."""
    return jsonify({'status': 'ok', 'service': 'validator-service'})


@app.post('/process')
def process():
    """Run the validation and routing workflow."""
    try:
        result = process_customers()
        return jsonify(result), 200
    except Exception as error:
        return jsonify({'status': 'error', 'message': str(error)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
