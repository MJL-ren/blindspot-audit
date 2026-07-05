"""metrics-board API server.

Serves job metrics from SQLite and the static dashboard page.
Endpoints are deliberately small and well-behaved: parameterized SQL,
input validation, JSON errors with status codes, and logging.
"""

import logging
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
log = logging.getLogger("metrics-board")
DB_PATH = "metrics.db"


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/jobs")
def list_jobs():
    limit = request.args.get("limit", default=50, type=int)
    if not 1 <= limit <= 500:
        return jsonify(error="limit must be between 1 and 500"), 400
    with db() as conn:
        rows = conn.execute(
            "SELECT id, name, status, duration_ms, finished_at"
            " FROM jobs ORDER BY finished_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return jsonify(jobs=[dict(r) for r in rows])


@app.post("/api/jobs/<int:job_id>/rerun")
def rerun_job(job_id: int):
    with db() as conn:
        row = conn.execute(
            "SELECT id FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()
        if row is None:
            return jsonify(error="job not found"), 404
        conn.execute(
            "UPDATE jobs SET status = 'queued' WHERE id = ?", (job_id,)
        )
    log.info("job %s queued for rerun", job_id)
    return jsonify(ok=True)


@app.delete("/api/jobs/<int:job_id>")
def delete_job(job_id: int):
    with db() as conn:
        cur = conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        if cur.rowcount == 0:
            return jsonify(error="job not found"), 404
    log.info("job %s deleted", job_id)
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(port=8080)
