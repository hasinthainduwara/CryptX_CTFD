from flask import Flask, request, render_template, render_template_string, g
import sqlite3
import os

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{default_flag_if_env_missing}")
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "challenge.db")


def get_db():
    """Get a database connection for the current request"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection at the end of each request"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database with sample data"""
    # Remove old database to ensure clean state
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    conn = sqlite3.connect(DATABASE)
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
            db = get_db()
            c = db.cursor()
            c.execute(query)
            user = c.fetchone()

            if user:
                return f"<h1>Success! Welcome, {user[1]}.</h1><p>Here is your flag: <b>{FLAG}</b></p>"
            else:
                error = "Invalid credentials"
        except Exception as e:
            error = f"Database Error: {e}"

    return render_template("index.html", error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
