from pymongo import MongoClient
from pymongo.errors import PyMongoError
import re
import time

MONGO_URI = "mongodb://mongodb:27017/?replicaSet=rs0"
DB_NAME = "banking"
COLLECTION_NAME = "customers"

def is_not_empty(value):
    return isinstance(value, str) and value.strip != ""

def validate_customer(doc):
    errors = []
    
    if not is_not_empty(doc.get("FIRST_NAME")):
        errors.append("First name is required and cannot be empty.")
    
    if not is_not_empty(doc.get("LAST_NAME")):
        errors.append("Last name is required and cannot be empty.")
    
    if not is_not_empty(doc.get("STREET_ADDRESS")):
        errors.append("Street address is required and cannot be empty.")
    
    if not is_not_empty(doc.get("CITY")):
        errors.append("City is required and cannot be empty.")

    if not is_not_empty(doc.get("POSTAL_CODE")):
        errors.append("Postal code is required and cannot be empty.")
    
    if not is_not_empty(doc.get("COUNTRY")):
        errors.append("Country is required and cannot be empty.")
    
    if not is_not_empty(doc.get("ACCOUNT_NUMBER")):
        errors.append("Account number is required and cannot be empty.")
    elif len(str((doc.get("ACCOUNT_NUMBER")))) != 8:
        errors.append("Account number must be exactly 8 digits long.")
    
    if not is_not_empty(doc.get("LETTER_TYPE")):
        errors.append("Letter type is required and cannot be empty.")
    elif doc.get("LETTER_TYPE").lower() not in ["welcome", "offer"]:
        errors.append("Letter type must be either 'welcome' or 'offer'.")
    
    if doc.get("LETTER_TYPE").lower() == "offer":
        if not is_not_empty(doc.get("OFFER_TYPE")):
            errors.append("Offer type is required for offer letters and cannot be empty.")
        elif doc.get("OFFER_TYPE").lower() not in ["credit card", "line of credit"]:
            errors.append("Offer type must be either 'credit card' or 'line of credit'.")
        if not is_not_empty(doc.get("CREDIT_LIMIT")):
            errors.append("Credit limit is required for offer letters and cannot be empty.")
        elif float(doc.get("CREDIT_LIMIT")) <= 0:
            errors.append("Credit limit must be a positive number.")

    return errors

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    print("Service 1 started. Watching for data inserts...")
    
    pipeline = [
        { "$match": {
            "operationType": "insert"
        }}
    ]
    
    while True:
        try:
            with collection.watch(pipeline, full_document="updateLookup") as stream:
                for change in stream:
                    doc = change["fullDocument"]
                    customer_id = doc.get("_id")
                    
                    errors = validate_customer(doc)
                    
                    if errors:
                        collection.update_one(
                            {"_id": customer_id},
                            {
                                "$set": {
                                    "STATUS": "invalid"
                                }
                            }
                        )
                        print(f"ERROR with customer {customer_id}:\n {'\n'.join(errors)}")
                    
                    else:
                        collection.update_one(
                            {"_id": customer_id},
                            {
                                "$set": {
                                    "STATUS": "valid"
                                }
                            }
                        )
                        
                        if doc.get("LETTER_TYPE").lower() == "offer":
                            print(f"Making offer letter for customer {customer_id}...")
                        else:
                            print(f"Making welcome letter for customer {customer_id}...")
        
        except PyMongoError as e:
            print(f"Error watching collection: {e}")

if __name__ == "__main__":
    main()