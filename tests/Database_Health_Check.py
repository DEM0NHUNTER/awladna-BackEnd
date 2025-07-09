# BackEnd/tests/Database_Health_Check.py

import psycopg2
import redis
from pymongo import MongoClient
import time

# PostgreSQL Configuration
POSTGRES_CONFIG = {
    'dbname': 'awladna',
    'user': 'awladna_user',
    'password': 'StrongPassword123!',
    'host': 'localhost',
    'port': 5432
}

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = 'awladna'

# Redis Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379


def check_postgres():
    try:
        # Test PostgreSQL connection
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cur = conn.cursor()
        # Create a simple test table
        cur.execute("CREATE TABLE IF NOT EXISTS health_check (id SERIAL PRIMARY KEY, status TEXT);")
        cur.execute("INSERT INTO health_check (status) VALUES ('OK') RETURNING id;")
        cur.execute("SELECT * FROM health_check;")
        conn.commit()
        rows = cur.fetchall()
        if rows:
            print("PostgreSQL: Connection successful, table check passed.")
        cur.execute("DROP TABLE health_check;")  # Clean up
        cur.close()
        conn.close()
    except Exception as e:
        print(f"PostgreSQL Error: {e}")


def check_mongo():
    try:
        # Test MongoDB connection
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        test_collection = db["health_check"]
        test_collection.insert_one({"status": "OK"})
        document = test_collection.find_one({"status": "OK"})
        if document:
            print("MongoDB: Connection successful, document check passed.")
        test_collection.delete_many({"status": "OK"})  # Clean up
        client.close()
    except Exception as e:
        print(f"MongoDB Error: {e}")


def check_redis():
    try:
        # Test Redis connection
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        r.set("health_check", "OK")
        value = r.get("health_check")
        if value == b"OK":
            print("Redis: Connection successful, key-value check passed.")
        r.delete("health_check")  # Clean up
    except Exception as e:
        print(f"Redis Error: {e}")


def health_check():
    print("Starting health check...\n")

    # Run checks
    check_postgres()
    check_mongo()
    check_redis()

    print("\nHealth check complete.")


def check_postgres_latency():
    start_time = time.time()
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        latency = time.time() - start_time
        print(f"PostgreSQL Latency: {latency:.4f} seconds")
    except Exception as e:
        print(f"PostgreSQL Latency Error: {e}")


def check_mongo_replica():
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        status = client.admin.command('replSetGetStatus')
        if status["ok"] == 1:
            print("MongoDB Replica Set Status: Healthy")
        else:
            print("MongoDB Replica Set Error.")
        client.close()
    except Exception as e:
        print(f"MongoDB Replica Error: {e}")


if __name__ == "__main__":
    health_check()
