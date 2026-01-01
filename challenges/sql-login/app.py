from flask import Flask, request, render_template, render_template_string
import sqlite3
import os

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{default_flag_if_env_missing}")


def get_db():
    """Get a database connection for the current request"""
    conn = sqlite3.connect("challenge.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with sample data"""
    if not os.path.exists("challenge.db"):
        conn = sqlite3.connect("challenge.db")
        c = conn.cursor()
        c.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
        )
        c.execute(
            "INSERT INTO users (username, password) VALUES ('admin', 'super_secret_password_123')"
        )
        c.execute("INSERT INTO users (username, password) VALUES ('guest', 'guest')")
        conn.commit()
        conn.close()


# Initialize DB on startup
init_db()


@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # VULNERABILITY: Direct string concatenation allows SQL Injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        try:
            conn = get_db()
            c = conn.cursor()
            c.execute(query)
            user = c.fetchone()
            conn.close()

            if user:
                return f"<h1>Success! Welcome, {user[1]}.</h1><p>Here is your flag: <b>{FLAG}</b></p>"
            else:
                error = "Invalid credentials"
        except Exception as e:
            error = f"Database Error: {e}"

    return render_template("index.html", error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
