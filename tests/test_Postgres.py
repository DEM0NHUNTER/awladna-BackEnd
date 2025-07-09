from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://awladna-db_owner:npg_nRDW3sEjc8QG@ep-autumn-brook-a50jsx9b-pooler.us-east-2.aws.neon.tech/awladna-db?sslmode=require"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("[SUCCESS] Database is active:", result.scalar())
except Exception as e:
    print("[ERROR] Cannot connect to DB:", e)
