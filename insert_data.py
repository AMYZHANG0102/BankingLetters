from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/?replicaSet=rs0")
db = client["banking"]
customers = db["customers"]

customers.insert_many([
    {
        "first_name": "Michael",
        "last_name": "Hassan",
        "account_number": "12345678",
        "address": {
            "street": "123 Main St",
            "city": "Mississauga",
            "postal_code": "L5B1A1",
            "country": "Canada"
        },
        "letter_type": "welcome",
        "status": "pending"
    },
    {
        "first_name": "Alice",
        "last_name": "Smith",
        "account_number": "999",
        "address": {
            "street": "",
            "city": "Toronto",
            "postal_code": "M5V1A1",
            "country": "Canada"
        },
        "letter_type": "offer",
        "credit_limit": 5000,
        "status": "pending"
    }
])

print("Inserted sample customer records.")