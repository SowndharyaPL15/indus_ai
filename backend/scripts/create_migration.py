import subprocess
import os
import sys

def main():
    """Wrapper to run alembic revision --autogenerate."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_migration.py 'migration message'")
        sys.exit(1)
        
    message = sys.argv[1]
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(backend_dir)
    
    print(f"Creating migration: '{message}'")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message],
            check=True
        )
        print("Migration created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
