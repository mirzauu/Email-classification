import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from core.all_models import *
from core.database import Base

def test_metadata():
    try:
        # Check all tables by compiling them for Postgres
        for table in Base.metadata.sorted_tables:
            CreateTable(table).compile(dialect=postgresql.dialect())
        print("Database metadata created successfully! All SQLAlchemy models and relationships are valid.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error creating database metadata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_metadata()
