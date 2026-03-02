"""
Migration script to add new classification columns to the emails table.
Run once: python migrate_emails.py
"""
from sqlalchemy import text
from core.database import engine

ALTER_STATEMENTS = [
    "ALTER TABLE emails ADD COLUMN IF NOT EXISTS summary TEXT",
    "ALTER TABLE emails ADD COLUMN IF NOT EXISTS labels TEXT",
    "ALTER TABLE emails ADD COLUMN IF NOT EXISTS gmail_id VARCHAR",
    "ALTER TABLE emails ADD COLUMN IF NOT EXISTS thread_id VARCHAR",
    "ALTER TABLE emails ADD COLUMN IF NOT EXISTS processed BOOLEAN DEFAULT FALSE",
    "ALTER TABLE emails ADD COLUMN IF NOT EXISTS classification_confidence FLOAT8",
    "ALTER TABLE emails ADD COLUMN IF NOT EXISTS classification_reason TEXT",
]

def run():
    with engine.connect() as conn:
        for stmt in ALTER_STATEMENTS:
            try:
                conn.execute(text(stmt))
                print(f"OK: {stmt}")
            except Exception as e:
                print(f"SKIP: {stmt} -> {e}")
        conn.commit()
    print("\nMigration complete!")

if __name__ == "__main__":
    run()
