import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from models import Base

# 1. Handle folder tree jumps securely to load local environment configurations
current_file_path = Path(__file__).resolve()
root_folder = current_file_path.parent.parent
env_local_path = root_folder / ".env.local"

if env_local_path.exists():
    load_dotenv(dotenv_path=env_local_path)

# 2. Fetch the connection variable
url = os.getenv("TRIPPEN_POSTGRES_URL") 

if not url:
    raise RuntimeError("CRITICAL ERROR: 'TRIPPEN_POSTGRES_URL' environment variable is not set.")

# --- THE DRIVER & INTEGRATION FIX ---
# Split the URL at the '?' mark to throw away the invalid parameters causing the "supa" crash
if "?" in url:
    clean_base_url, query_params = url.split("?", 1)
else:
    clean_base_url = url

# Rewrite standard prefixes to explicitly match modern SQLAlchemy driver targets (+psycopg)
if clean_base_url.startswith("postgres://"):
    url = clean_base_url.replace("postgres://", "postgresql+psycopg://", 1)
elif clean_base_url.startswith("postgresql://"):
    url = clean_base_url.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    url = clean_base_url

# Append ONLY clean, compliant SQL arguments that are fully supported by psycopg
url += "?sslmode=require"
# ------------------------------------

print(f"Using Sanitized DB URL: {url}")  

# Force NullPool because serverless architectures connect to Supabase's transaction pooler (6543)
engine = create_engine(
    url,
    poolclass=NullPool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

init_db()

