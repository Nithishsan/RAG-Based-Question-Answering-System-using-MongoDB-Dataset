from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pymysql
from dotenv import load_dotenv
from pathlib import Path
# Base credentials (without specifying the database)
BASE_DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306"


# Target database name
DATABASE_NAME = "movieset"
DATABASE_URL = f"{BASE_DATABASE_URL}/{DATABASE_NAME}"

# Step 1: Connect to MySQL without selecting a DB
engine_no_db = create_engine(BASE_DATABASE_URL, echo=True)

# Step 2: Check and create the database if it doesn't exist
with engine_no_db.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))

# Step 3: Now connect to the actual database
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
