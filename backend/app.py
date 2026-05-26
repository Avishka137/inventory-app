from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os

app = Flask(__name__)
CORS(app)
DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")

# ⬇ PASTE YOUR GEMINI KEY HERE (from aistudio.google.com/apikey)
GEMINI_API_KEY = "AIzaSyB44AS5MXOd2in2LaMbx0NIttiD0TvNsbI"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, category TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            price REAL NOT NULL DEFAULT 0.0, description TEXT)""")
        conn.commit()

def row_to_dict(row): return dict(row)

@app.route("/api/products", methods=["GET"])
def get_products():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return jsonify([row_to_dict(r) for r in rows])

@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json()
    if not data.get("name") or not data.get("category"):
        return jsonify({"error": "Name and category are required."}), 400
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO products (name, category, quantity, price, description) VALUES (?,?,?,?,?)",
            (data["name"], data["category"], int(data.get("quantity",0)), float(data.get("price",0.0)), data.get("description","")))
        conn.commit()
        product = conn.execute("SELECT * FROM products WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(row_to_dict(product)), 201

@app.route("/api/products/<int:pid>", methods=["PUT"])
def update_product(pid):
    data = request.get_json()
    if not data.get("name") or not data.get("category"):
        return jsonify({"error": "Name and category are required."}), 400
    with get_db() as conn:
        conn.execute(
            "UPDATE products SET name=?,category=?,quantity=?,price=?,description=? WHERE id=?",
            (data["name"], data["category"], int(data.get("quantity",0)), float(data.get("price",0.0)), data.get("description",""), pid))
        conn.commit()
        updated = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if updated is None: return jsonify({"error": "Not found"}), 404
    return jsonify(row_to_dict(updated))

@app.route("/api/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    with get_db() as conn:
        if not conn.execute("SELECT id FROM products WHERE id=?", (pid,)).fetchone():
            return jsonify({"error": "Not found"}), 404
        conn.execute("DELETE FROM products WHERE id=?", (pid,))
        conn.commit()
    return jsonify({"message": "Deleted."})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY category, name").fetchall()
    products = [row_to_dict(r) for r in rows]

    if products:
        lines = []
        for p in products:
            line = f"- {p['name']} | Category: {p['category']} | Qty: {p['quantity']} | Price: ${p['price']:.2f}"
            if p['description']: line += f" | {p['description']}"
            lines.append(line)
        total_value = sum(p['quantity'] * p['price'] for p in products)
        low_stock = [p['name'] for p in products if p['quantity'] < 6]
        summary = f"""Total products: {len(products)}
Total inventory value: ${total_value:.2f}
Low stock (qty < 5): {', '.join(low_stock) if low_stock else 'None'}

Products:
{chr(10).join(lines)}"""
    else:
        summary = "Inventory is empty."

    system_prompt = f"""You are a helpful inventory assistant. Answer clearly and concisely.
Current inventory:
{summary}"""

    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction=system_prompt),
            contents=user_message
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    print("✅  Database ready.")
    print("🚀  Flask running at http://localhost:5000")
    app.run(debug=True, port=5000)