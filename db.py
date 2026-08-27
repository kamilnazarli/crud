import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

def get_connection():
    return psycopg.connect(DATABASE_URL)

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)
            cur.execute("SELECT COUNT(*) FROM tasks")
            count = cur.fetchone()[0]
            if count == 0:
                cur.execute("""
                    INSERT INTO tasks (title, done) VALUES
                    ('Buy milk', FALSE),
                    ('Write report', FALSE),
                    ('Walk the dog', TRUE)
                """)
        conn.commit()

def get_all_tasks():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks")
            res = cur.fetchall()
        conn.commit()
    return res

def get_task_by_id(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (id,))
            res = cur.fetchone()
        conn.commit()
    return res