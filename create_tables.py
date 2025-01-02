import os
import subprocess

# Get the database connection details from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_USER, DB_NAME, DB_PASSWORD]):
    raise ValueError("One or more required environment variables are missing: DB_HOST, DB_USER, DB_NAME, DB_PASSWORD.")

# SQL to create the table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_views (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    view_name VARCHAR(100) NOT NULL
);
"""

def main():
    try:
        # Call `psql` to execute the SQL command
        result = subprocess.run(
            [
                "psql", 
                DATABASE_URL, 
                "-c", CREATE_TABLE_SQL
            ],
            check=True,
            text=True,
            capture_output=True
        )
        print("Table 'user_views' created successfully.")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Error executing psql: {e.stderr}")

if __name__ == "__main__":
    main()
