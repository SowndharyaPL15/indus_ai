import subprocess
import os
import sys

def main():
    """Wrapper to run alembic upgrade head."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(backend_dir)
    
    print("Upgrading database to head...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True
        )
        print("Database upgraded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
