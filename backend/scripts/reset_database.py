import asyncio
import os
import sys

def main():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_dir)

    os.environ["APP_ENV"] = "development"

    from app.db.init_db import drop_tables_dev_only, create_tables

    async def reset():
        print("Resetting database...")
        await drop_tables_dev_only()
        await create_tables()
        print("Database reset complete.")

    try:
        asyncio.run(reset())
    except Exception as e:
        print(f"Error resetting database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
