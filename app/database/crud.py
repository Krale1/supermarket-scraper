from app.database.models import get_connection

def save_products(products):
    conn = get_connection()
    cursor = conn.cursor()

    for product in products:
        try:
            price = int(float(product["cena"].replace(",", ".").split()[0]))
        except:
            price = None

        cursor.execute("""
            INSERT INTO products (name, price, description, market)
            VALUES (%s, %s, %s, %s)
        """, (
            product["ime_na_artikal"],
            price,
            product.get("opis", ""),
            product.get("market", "Unknown")
        ))

    conn.commit()
    cursor.close()
    conn.close()

def get_all_products(search=None, sort_by="price", order="asc", limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT name AS ime_na_artikal, price, description AS opis, market FROM products"
    params = []

    if search:
        query += " WHERE name LIKE %s"
        params.append(f"%{search}%")

    if sort_by in ["price", "name"]:
        query += f" ORDER BY { 'price' if sort_by == 'price' else 'name' } { 'ASC' if order == 'asc' else 'DESC' }"

    # ✅ Apply LIMIT/OFFSET only if limit is provided
    if limit is not None:
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    for r in results:
        if r["price"] is not None:
            r["cena"] = f"{r['price']} ден."
        else:
            r["cena"] = "N/A"

    return results

def delete_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products")
    conn.commit()
    cursor.close()
    conn.close()

def count_products(search=None):
    conn = get_connection()
    cursor = conn.cursor()

    if search:
        cursor.execute("SELECT COUNT(*) FROM products WHERE name LIKE %s", (f"%{search}%",))
    else:
        cursor.execute("SELECT COUNT(*) FROM products")

    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count
