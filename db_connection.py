"""
db_connection.py — Creates the PyMongo client and database object.
"""
import pymongo

# 1. Define the local MongoDB connection URL
db_url = "mongodb://localhost:27017/"

# 2. Create the client
client = pymongo.MongoClient(db_url)

# 3. Select your specific database
db = client["classicmodels_updated"]

print(f"Connected successfully to MongoDB database: {db.name}")