import os
import psycopg2

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
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()

        # Execute the SQL to create the table
        cursor.execute("DROP TABLE user_views;")
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()

        print("Table 'user_views' created successfully (or already exists).")

    except Exception as e:
        print(f"Error creating table: {e}")


    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
