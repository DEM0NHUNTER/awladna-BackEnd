# BackEnd/Models/__init__db.py
from BackEnd.Utils.database import Base, engine

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
