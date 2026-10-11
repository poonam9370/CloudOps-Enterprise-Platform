from flask import Flask, jsonify, request
import os
import psycopg

app = Flask(__name__)

def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "cloudops_db"),
        user=os.getenv("DB_USER", "cloudops_user"),
        password=os.getenv("DB_PASSWORD", "cloudops_local_pass")
    )

@app.route("/")
def home():
    return """
    <h1>CloudOps Enterprise Platform</h1>
    <h2>Employee Management System</h2>
    <p>Application is running successfully!</p>
    <p>PostgreSQL database is configured.</p>
    """

@app.route("/health")
def health():
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        return jsonify({
            "status": "healthy",
            "database": "connected"
        })
    except Exception:
        app.logger.exception("Database health check failed")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 503

@app.route("/employees", methods=["GET"])
def get_employees():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS employees (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(150) UNIQUE NOT NULL,
                        department VARCHAR(100) NOT NULL
                    )
                """)
                cur.execute("""
                    SELECT id, name, email, department
                    FROM employees ORDER BY id
                """)
                rows = cur.fetchall()

        return jsonify([
            {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "department": row[3]
            }
            for row in rows
        ])
    except Exception:
        app.logger.exception("Could not retrieve employees")
        return jsonify({"error": "Unable to retrieve employees"}), 500

@app.route("/employees", methods=["POST"])
def add_employee():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    department = data.get("department")

    if not all(isinstance(v, str) and v.strip()
               for v in (name, email, department)):
        return jsonify({
            "error": "name, email and department are required"
        }), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS employees (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(150) UNIQUE NOT NULL,
                        department VARCHAR(100) NOT NULL
                    )
                """)
                cur.execute("""
                    INSERT INTO employees (name, email, department)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (name.strip(), email.strip(), department.strip()))
                employee_id = cur.fetchone()[0]

        return jsonify({
            "message": "Employee added successfully",
            "id": employee_id
        }), 201
    except psycopg.errors.UniqueViolation:
        return jsonify({"error": "Email already exists"}), 409
    except Exception:
        app.logger.exception("Could not add employee")
        return jsonify({"error": "Unable to add employee"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)