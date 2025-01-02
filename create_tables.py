import os
import subprocess

# Database connection details (retrieved from environment variables)
DATABASE_URL = os.getenv('DATABASE_URL')

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
