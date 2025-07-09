# BackEnd/tests/test_mongo.py

from pymongo import MongoClient

client = MongoClient("mongodb+srv://Krieg:YnMdXExM2rR72ag@awladna-mongodb.ymlyyhh.mongodb.net/?retryWrites=true&w=majority&appName=awladna-mongodb")
db = client.testdb
collection = db.test_collection

print("Inserting document...")
test_doc = {"name": "testuser", "age": 30}
result = collection.insert_one(test_doc)
print(f"Inserted document ID: {result.inserted_id}")

print("Querying document...")
doc = collection.find_one({"_id": result.inserted_id})
print(f"Queried document: {doc}")

print("Updating document...")
collection.update_one({"_id": result.inserted_id}, {"$set": {"age": 31}})
updated_doc = collection.find_one({"_id": result.inserted_id})
print(f"Updated document: {updated_doc}")

print("Deleting document...")
delete_result = collection.delete_one({"_id": result.inserted_id})
print(f"Deleted count: {delete_result.deleted_count}")

client.close()
