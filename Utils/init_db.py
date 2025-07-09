# BackEnd/Utils/init_db.py

from BackEnd.Utils.database import Base, engine
from BackEnd.Models import user, child_profile, chat_log, audit_log


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully.")


if __name__ == "__main__":
    create_tables()
