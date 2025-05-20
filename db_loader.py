import os
from dotenv import load_dotenv
import mysql.connector

# Load .env variables
load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )

def load_products_from_db():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, name, price, market FROM products"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Run test when executing this file directly
if __name__ == "__main__":
    products = load_products_from_db()
    print(f"Loaded {len(products)} products.")
    for product in products[:5]:  # Show first 5 as a preview
        print(product)
