import mysql.connector
from datetime import datetime
import os

# Generate a random 64-byte hex value
def generate_random_hex():
    return os.urandom(32).hex()

# Define your MySQL database connection parameters
db_config = {
    'user': 'root',
    'password': 'G00gl386!',
    'host': 'localhost',
    'database': 'trypy',
}

def save_to_mysql():
    try:
        # Create a connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Get current date and time
        current_datetime = datetime.now()

        # Generate a random 64-byte hex value
        random_hex = generate_random_hex()

        # Insert data into the MySQL table
        cursor.execute("""
            INSERT INTO test_data (timestamp, random_hex)
            VALUES (%s, %s)
        """, (current_datetime, random_hex))

        # Commit the transaction
        connection.commit()

        # Close the connection
        cursor.close()
        connection.close()

        print("Data saved to MySQL database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Save data to MySQL database
save_to_mysql()
